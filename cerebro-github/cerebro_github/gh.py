"""Thin wrapper around gh CLI — all GitHub operations go through here.

Rate governor: checks actual remaining quota from GitHub's rate limit
API before allowing calls. Works as middleware — every call flows
through _run, every call is governed. Doesn't assume it's the only
consumer; reads reality from GitHub's headers.

Auth: if CEREBRO_GITHUB_APP_* env vars are set, all calls use a GitHub
App installation token (separate rate limit bucket from Daniel's PAT).
Otherwise falls back to gh CLI's default auth.
"""

import json
import os
import subprocess
import time

from . import app_auth


# ── Rate Governor ──────────────────────────────────────────

class RateLimitError(RuntimeError):
    """Raised when the rate governor blocks a call to protect quota."""
    def __init__(self, kind: str, remaining: int, resets_at: int):
        resets_in = max(0, resets_at - int(time.time()))
        super().__init__(
            f"Rate governor: {kind} quota too low "
            f"({remaining} remaining, resets in {resets_in}s). "
            "Back off and retry after the reset window."
        )
        self.kind = kind
        self.remaining = remaining
        self.resets_in = resets_in


class _RateGovernor:
    """Reads GitHub's actual rate limit before allowing calls.

    Reserves a floor of remaining calls — if we're below the floor,
    block. This protects against exhaustion regardless of what other
    processes are consuming the API.

    REST floor: 200 (keep headroom for CI, webhooks, other tools)
    GraphQL floor: 500 (mutations cost variable points)

    Rate limit is checked at most once per 30 seconds to avoid
    burning calls just to check the limit.
    """

    def __init__(self):
        self.rest_remaining: int | None = None
        self.rest_reset: int = 0
        self.graphql_remaining: int | None = None
        self.graphql_reset: int = 0
        self.last_check: float = 0
        self.check_interval = 30  # seconds between limit checks
        self.rest_floor = 200
        self.graphql_floor = 500

    def _refresh(self) -> None:
        """Fetch actual rate limits from GitHub.

        REST limits come from the rate_limit REST endpoint.
        GraphQL limits come from a GraphQL introspection query
        (the REST endpoint doesn't report GraphQL quota).
        """
        now = time.time()
        if now - self.last_check < self.check_interval:
            return

        env = _gh_env()

        try:
            # REST quota
            result = subprocess.run(
                ["gh", "api", "rate_limit"],
                capture_output=True, text=True, timeout=10,
                env=env,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                rate = data.get("rate", {})
                self.rest_remaining = rate.get("remaining")
                self.rest_reset = rate.get("reset", 0)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
            pass

        try:
            # GraphQL quota — must query via GraphQL itself
            result = subprocess.run(
                ["gh", "api", "graphql", "-f",
                 "query={ rateLimit { remaining resetAt } }"],
                capture_output=True, text=True, timeout=10,
                env=env,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                rl = data.get("data", {}).get("rateLimit", {})
                self.graphql_remaining = rl.get("remaining")
                reset_at = rl.get("resetAt", "")
                if reset_at:
                    from datetime import datetime, timezone
                    dt = datetime.fromisoformat(reset_at.replace("Z", "+00:00"))
                    self.graphql_reset = int(dt.timestamp())
        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
            pass

        self.last_check = now

    def check_rest(self) -> None:
        self._refresh()
        if self.rest_remaining is not None and self.rest_remaining < self.rest_floor:
            raise RateLimitError("REST", self.rest_remaining, self.rest_reset)

    def check_graphql(self) -> None:
        self._refresh()
        if self.graphql_remaining is not None and self.graphql_remaining < self.graphql_floor:
            raise RateLimitError("GraphQL", self.graphql_remaining, self.graphql_reset)

    def status(self) -> dict:
        self._refresh()
        return {
            "rest": {
                "remaining": self.rest_remaining,
                "floor": self.rest_floor,
                "reset": self.rest_reset,
                "safe": (self.rest_remaining or 0) >= self.rest_floor,
            },
            "graphql": {
                "remaining": self.graphql_remaining,
                "floor": self.graphql_floor,
                "reset": self.graphql_reset,
                "safe": (self.graphql_remaining or 0) >= self.graphql_floor,
            },
        }


_governor = _RateGovernor()


def rate_status() -> dict:
    """Return current rate governor status. Exposed as a tool."""
    return _governor.status()


# ── Core runners ───────────────────────────────────────────

def _gh_env() -> dict[str, str]:
    """Build environment for gh subprocess.

    If GitHub App auth is configured, injects GH_TOKEN so the gh CLI
    uses the app's installation token (separate rate limit bucket).
    """
    env = os.environ.copy()
    token = app_auth.get_token()
    if token:
        env["GH_TOKEN"] = token
    return env


def _run(args: list[str], check: bool = True) -> str:
    """Run a gh command and return stdout. Rate-governed."""
    _governor.check_rest()
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True, text=True, timeout=30,
        env=_gh_env(),
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}... failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _run_json(args: list[str]) -> dict | list:
    """Run a gh command that returns JSON."""
    return json.loads(_run(args))


def _graphql(query: str) -> dict:
    """Run a GraphQL query against GitHub API. Rate-governed (separate budget)."""
    _governor.check_graphql()
    raw = _run(["api", "graphql", "-f", f"query={query}"])
    return json.loads(raw)


# ── Issues ──────────────────────────────────────────────

def create_issue(org: str, repo: str, title: str, body: str, assignee: str) -> dict:
    """Create an issue and return {number, url, node_id}."""
    url = _run([
        "issue", "create",
        "--repo", f"{org}/{repo}",
        "--title", title,
        "--body", body,
        "--assignee", assignee,
    ])
    number = int(url.rstrip("/").split("/")[-1])
    node_id = _run([
        "api", f"repos/{org}/{repo}/issues/{number}",
        "--jq", ".node_id",
    ])
    return {"number": number, "url": url, "node_id": node_id}


def close_issue(org: str, repo: str, number: int, reason: str = "completed") -> None:
    _run(["issue", "close", str(number), "--repo", f"{org}/{repo}", "--reason", reason])


def get_issue_node_id(org: str, repo: str, number: int) -> str:
    return _run(["api", f"repos/{org}/{repo}/issues/{number}", "--jq", ".node_id"])


# ── Sub-issues ──────────────────────────────────────────

def add_sub_issue(parent_node_id: str, child_node_id: str) -> dict:
    result = _graphql(f"""
        mutation {{
            addSubIssue(input: {{issueId: "{parent_node_id}", subIssueId: "{child_node_id}"}}) {{
                issue {{ number title }}
                subIssue {{ number title }}
            }}
        }}
    """)
    return result.get("data", {}).get("addSubIssue", {})


# ── Project ─────────────────────────────────────────────

def add_to_project(project_id: str, content_node_id: str) -> str:
    """Add an issue/PR to the project. Returns item ID."""
    result = _graphql(f"""
        mutation {{
            addProjectV2ItemById(input: {{projectId: "{project_id}", contentId: "{content_node_id}"}}) {{
                item {{ id }}
            }}
        }}
    """)
    return result["data"]["addProjectV2ItemById"]["item"]["id"]


def set_project_field(project_id: str, item_id: str, field_id: str, value: str, field_type: str = "single_select") -> None:
    if field_type == "single_select":
        _graphql(f"""
            mutation {{
                updateProjectV2ItemFieldValue(input: {{
                    projectId: "{project_id}",
                    itemId: "{item_id}",
                    fieldId: "{field_id}",
                    value: {{singleSelectOptionId: "{value}"}}
                }}) {{ projectV2Item {{ id }} }}
            }}
        """)
    elif field_type == "date":
        _graphql(f"""
            mutation {{
                updateProjectV2ItemFieldValue(input: {{
                    projectId: "{project_id}",
                    itemId: "{item_id}",
                    fieldId: "{field_id}",
                    value: {{date: "{value}"}}
                }}) {{ projectV2Item {{ id }} }}
            }}
        """)


# ── Pull Requests ───────────────────────────────────────

def create_pr(org: str, repo: str, head: str, base: str, title: str, body: str) -> dict:
    url = _run([
        "pr", "create",
        "--repo", f"{org}/{repo}",
        "--head", head,
        "--base", base,
        "--title", title,
        "--body", body,
    ])
    number = int(url.rstrip("/").split("/")[-1])
    return {"number": number, "url": url}


def get_pr_checks(org: str, repo: str, pr_number: int) -> list[dict]:
    return _run_json([
        "pr", "view", str(pr_number),
        "--repo", f"{org}/{repo}",
        "--json", "statusCheckRollup",
        "--jq", "[.statusCheckRollup[] | {name: .name, status: .status, conclusion: .conclusion}]",
    ])


def get_pr_head(org: str, repo: str, pr_number: int) -> str:
    return _run([
        "pr", "view", str(pr_number),
        "--repo", f"{org}/{repo}",
        "--json", "headRefName",
        "--jq", ".headRefName",
    ])


def merge_pr(org: str, repo: str, pr_number: int, method: str = "squash", delete_branch: bool = True) -> str:
    args = [
        "pr", "merge", str(pr_number),
        "--repo", f"{org}/{repo}",
        f"--{method}",
    ]
    if delete_branch:
        args.append("--delete-branch")
    return _run(args)


# ── Workflows / CI ─────────────────────────────────────

def rerun_workflow(org: str, repo: str, run_id: int) -> str:
    """Re-run a failed workflow run."""
    return _run(["api", f"repos/{org}/{repo}/actions/runs/{run_id}/rerun",
                 "--method", "POST"])


def get_failed_runs(org: str, repo: str, limit: int = 5) -> list[dict]:
    """Get recent failed workflow runs."""
    return _run_json([
        "api", f"repos/{org}/{repo}/actions/runs",
        "--jq", f"[.workflow_runs[:20] | .[] | select(.conclusion==\"failure\") | {{id: .id, name: .name, branch: .head_branch, created: .created_at, url: .html_url}}][:{ limit }]",
    ])


def trigger_workflow(org: str, repo: str, workflow: str, ref: str = "main", inputs: dict | None = None) -> str:
    """Trigger a workflow_dispatch event."""
    args = ["api", f"repos/{org}/{repo}/actions/workflows/{workflow}/dispatches",
            "--method", "POST",
            "-f", f"ref={ref}"]
    for k, v in (inputs or {}).items():
        args.extend(["-f", f"inputs[{k}]={v}"])
    return _run(args)


# ── Releases ───────────────────────────────────────────

def create_release(org: str, repo: str, tag: str, name: str, body: str,
                   target: str = "main", draft: bool = False, prerelease: bool = False) -> dict:
    """Create a GitHub release with a tag."""
    args = [
        "release", "create", tag,
        "--repo", f"{org}/{repo}",
        "--title", name,
        "--notes", body,
        "--target", target,
    ]
    if draft:
        args.append("--draft")
    if prerelease:
        args.append("--prerelease")
    url = _run(args)
    return {"tag": tag, "url": url}


def list_releases(org: str, repo: str, limit: int = 5) -> list[dict]:
    """List recent releases."""
    return _run_json([
        "release", "list",
        "--repo", f"{org}/{repo}",
        "--limit", str(limit),
        "--json", "tagName,name,publishedAt,isDraft,isPrerelease,url",
    ])


# ── Search ──────────────────────────────────────────────

def list_open_prs(org: str) -> list[dict]:
    return _run_json([
        "search", "prs",
        "--owner", org,
        "--state", "open",
        "--json", "repository,number,title,url,updatedAt,author",
        "--jq", "sort_by(.repository.name)",
    ])
