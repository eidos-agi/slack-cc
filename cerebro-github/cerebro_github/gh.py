"""Thin wrapper around gh CLI — all GitHub operations go through here."""

import json
import subprocess


def _run(args: list[str], check: bool = True) -> str:
    """Run a gh command and return stdout."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True, text=True, timeout=30,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}... failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _run_json(args: list[str]) -> dict | list:
    """Run a gh command that returns JSON."""
    return json.loads(_run(args))


def _graphql(query: str) -> dict:
    """Run a GraphQL query against GitHub API."""
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
    # --jq returns a raw string, not JSON — use _run not _run_json
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


# ── Search ──────────────────────────────────────────────

def list_open_prs(org: str) -> list[dict]:
    return _run_json([
        "search", "prs",
        "--owner", org,
        "--state", "open",
        "--json", "repository,number,title,url,updatedAt,author",
        "--jq", "sort_by(.repository.name)",
    ])
