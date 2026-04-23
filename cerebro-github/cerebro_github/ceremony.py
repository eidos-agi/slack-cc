"""Ceremony logic — the opinionated workflow that tools call."""

from . import gh
from .config import (
    GH_ORG, PROJECT_ID, ASSIGNEE, TIER_MAP, PROTECTED_BRANCHES,
    STATUS_FIELD_ID, STATUS_TODO, STATUS_IN_PROGRESS, STATUS_DONE,
    CI_NON_FAILURE_CONCLUSIONS, T1_SERVICES,
)
from . import gate
from .topology import Service, SERVICES, DEPLOY_ORDER


def create_work(
    title: str,
    repo: str,
    body: str = "",
    milestone_repo: str | None = None,
    milestone_number: int | None = None,
    status: str = "todo",
) -> dict:
    """Create issue → link as sub-issue → add to project.

    Returns {number, url, project_item_id}.
    """
    if repo not in TIER_MAP:
        raise ValueError(f"Unknown repo '{repo}'. Add it to config.TIER_MAP first.")

    # 1. Create the issue
    issue = gh.create_issue(GH_ORG, repo, title, body or title, ASSIGNEE)

    # 2. Add to project (via GraphQL — gh project item-add is unreliable)
    item_id = gh.add_to_project(PROJECT_ID, issue["node_id"])

    # 3. Set status
    status_option = STATUS_IN_PROGRESS if status == "in_progress" else STATUS_TODO
    gh.set_project_field(PROJECT_ID, item_id, STATUS_FIELD_ID, status_option)

    # 4. Link as sub-issue if milestone provided
    sub_issue_link = None
    if milestone_repo and milestone_number:
        parent_node = gh.get_issue_node_id(GH_ORG, milestone_repo, milestone_number)
        sub_issue_link = gh.add_sub_issue(parent_node, issue["node_id"])

    return {
        "number": issue["number"],
        "url": issue["url"],
        "project_item_id": item_id,
        "sub_issue": sub_issue_link,
    }


def close_work(repo: str, number: int, reason: str = "completed") -> dict:
    """Close an issue without a PR (resolved by conversation, won't fix, etc.).

    Also sets project status to Done.
    """
    if repo not in TIER_MAP:
        raise ValueError(f"Unknown repo '{repo}'. Add it to config.TIER_MAP first.")

    # 1. Close the issue
    gh.close_issue(GH_ORG, repo, number, reason=reason)

    # 2. Try to update project status to Done
    try:
        node_id = gh.get_issue_node_id(GH_ORG, repo, number)
        item_id = gh.add_to_project(PROJECT_ID, node_id)
        gh.set_project_field(PROJECT_ID, item_id, STATUS_FIELD_ID, STATUS_DONE)
    except Exception:
        pass

    return {"closed": True, "repo": repo, "number": number, "reason": reason}


def open_pr(
    repo: str,
    branch: str,
    closes: int,
    title: str | None = None,
    body: str = "",
    base: str = "develop",
) -> dict:
    """Create PR with Closes #N → verify issue in project → return PR + CI status.

    Returns {number, url, checks}.
    """
    if repo not in TIER_MAP:
        raise ValueError(f"Unknown repo '{repo}'. Add it to config.TIER_MAP first.")

    # 1. Verify the issue exists by getting its node ID
    issue_node = gh.get_issue_node_id(GH_ORG, repo, closes)

    # 2. Ensure issue is in the project
    gh.add_to_project(PROJECT_ID, issue_node)

    # 3. Build PR body with Closes #N
    pr_body = f"Closes #{closes}\n\n{body}".strip()
    if not title:
        title = f"Fix #{closes}"

    # 4. Create the PR
    pr = gh.create_pr(GH_ORG, repo, branch, base, title, pr_body)

    # 5. Check CI (best effort — may still be pending)
    try:
        checks = gh.get_pr_checks(GH_ORG, repo, pr["number"])
    except Exception:
        checks = []

    return {
        "number": pr["number"],
        "url": pr["url"],
        "checks": checks,
    }


def _classify_checks(checks: list[dict]) -> dict:
    """Classify CI checks into passed/failed/skipped/pending."""
    passed = []
    failed = []
    skipped = []
    pending = []
    for c in checks:
        conclusion = c.get("conclusion") or ""
        status = c.get("status") or ""
        name = c.get("name", "unknown")

        if conclusion == "SUCCESS":
            passed.append(name)
        elif conclusion == "FAILURE":
            failed.append(name)
        elif conclusion in ("SKIPPED", "NEUTRAL"):
            skipped.append(name)
        elif status in ("IN_PROGRESS", "QUEUED", "PENDING"):
            pending.append(name)
        else:
            pending.append(name)

    # all_green = no failures and no pending. Skipped checks are OK.
    all_green = len(failed) == 0 and len(pending) == 0
    result: dict = {
        "all_green": all_green,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pending": pending,
    }
    if pending and not failed:
        result["wait_advisory"] = (
            f"{len(pending)} check(s) still running. "
            "CI typically takes 2-3 minutes. "
            "Wait at least 60 seconds before checking again."
        )
    return result


def check_ci(repo: str, pr_number: int) -> dict:
    """Check CI status on a PR.

    Returns {all_green, passed, failed, skipped, pending}.
    SKIPPED checks don't block merging.
    """
    checks = gh.get_pr_checks(GH_ORG, repo, pr_number)
    return _classify_checks(checks)


def merge_pr(repo: str, pr_number: int, gate_token: str = "", rhea_decision: str = "") -> dict:
    """Verify CI → verify branch safety → gate if T1→main → squash merge.

    For T1 repos merging to main: returns a Rhea gate instead of executing.
    Pass gate_token + rhea_decision from the gate to proceed.
    """
    # 1. Check CI
    ci = check_ci(repo, pr_number)
    if not ci["all_green"]:
        return {
            "merged": False,
            "reason": f"CI not green. Failed: {ci['failed']}. Pending: {ci['pending']}.",
            "checks": ci,
        }

    # 2. Check branch safety
    head = gh.get_pr_head(GH_ORG, repo, pr_number)
    base = gh._run([
        "pr", "view", str(pr_number),
        "--repo", f"{GH_ORG}/{repo}",
        "--json", "baseRefName",
        "--jq", ".baseRefName",
    ])
    delete_branch = head not in PROTECTED_BRANCHES

    # 3. Gate check: T1 repo merging to main requires Rhea review
    tier = TIER_MAP.get(repo, 3)
    if tier == 1 and base == "main":
        if not gate_token or not rhea_decision:
            # First call — return the gate, don't execute
            return gate.build_merge_gate(repo, pr_number, base)

        # Second call — validate token and decision
        # Rebuild context with the ORIGINAL timestamp from the token
        # (otherwise the hash changes between the two calls)
        # Extract the original timestamp from the gate token so the hash matches
        token_timestamp = float(gate_token.split("-")[-1]) if gate_token.count("-") == 2 else 0.0
        gate_context = gate.GateContext(
            action="merge_to_production",
            repo=repo,
            tier=tier,
            environment="production",
            pr_number=pr_number,
            what_changes=f"Merging PR #{pr_number} to {base} on {repo}",
            deploy_target=SERVICES.get(repo, Service(name=repo, repo=repo)).domains.get("production", ""),
            rollback_path=f"git revert on {base}, or Railway rollback via railguey",
            upstream_dependencies=DEPLOY_ORDER[:DEPLOY_ORDER.index(repo)] if repo in DEPLOY_ORDER else [],
            timestamp=token_timestamp,
        )

        # Validate gate token (checks hash + expiry)
        token_valid, token_reason = gate.validate_gate_token(gate_token, gate_context)
        if not token_valid:
            return {"merged": False, "reason": f"Gate token invalid: {token_reason}"}

        # Validate Rhea decision (checks structure)
        decision_valid, decision_reason = gate.validate_rhea_decision(rhea_decision)
        if not decision_valid:
            return {"merged": False, "reason": f"Rhea decision invalid: {decision_reason}"}

    # 4. Execute merge
    if not delete_branch:
        gh.merge_pr(GH_ORG, repo, pr_number, method="squash", delete_branch=False)
        return {
            "merged": True,
            "head_branch": head,
            "branch_deleted": False,
            "note": f"Branch '{head}' is protected — kept alive.",
            "checks": ci,
            "gated": tier == 1 and base == "main",
        }

    gh.merge_pr(GH_ORG, repo, pr_number, method="squash", delete_branch=True)
    return {
        "merged": True,
        "head_branch": head,
        "branch_deleted": True,
        "checks": ci,
        "gated": tier == 1 and base == "main",
    }


def dashboard() -> dict:
    """All open PRs across the org with CI status.

    Returns {prs[], count}.
    """
    prs = gh.list_open_prs(GH_ORG)
    result = []
    for pr in prs:
        repo_name = pr["repository"]["name"]
        pr_num = pr["number"]
        try:
            checks = gh.get_pr_checks(GH_ORG, repo_name, pr_num)
            classified = _classify_checks(checks)
        except Exception:
            checks = []
            classified = {"all_green": False, "passed": [], "failed": [], "skipped": [], "pending": []}

        result.append({
            "repo": repo_name,
            "number": pr_num,
            "title": pr["title"],
            "url": pr["url"],
            "all_green": classified["all_green"],
            "checks": [
                {"name": c["name"], "conclusion": c.get("conclusion", c.get("status", "unknown"))}
                for c in checks
            ],
        })

    return {"prs": result, "count": len(result)}


def bulk_merge(repos_and_prs: list[dict] | None = None, dry_run: bool = True) -> dict:
    """Merge green PRs. Dry run by default — must explicitly set dry_run=False.

    Returns preview of what would merge (dry_run=True) or actual results (dry_run=False).
    """
    if repos_and_prs is None:
        all_prs = gh.list_open_prs(GH_ORG)
        repos_and_prs = [
            {"repo": pr["repository"]["name"], "pr": pr["number"], "title": pr["title"]}
            for pr in all_prs
        ]

    results = []
    for item in repos_and_prs:
        repo = item["repo"]
        pr_num = item["pr"]
        title = item.get("title", "")

        # Always check CI first
        try:
            ci = check_ci(repo, pr_num)
        except Exception as e:
            results.append({"repo": repo, "pr": pr_num, "title": title, "would_merge": False, "merged": False, "reason": str(e)})
            continue

        if not ci["all_green"]:
            results.append({
                "repo": repo, "pr": pr_num, "title": title,
                "would_merge": False, "merged": False,
                "reason": f"CI not green. Failed: {ci['failed']}. Pending: {ci['pending']}.",
            })
            continue

        if dry_run:
            results.append({
                "repo": repo, "pr": pr_num, "title": title,
                "would_merge": True, "merged": False,
                "reason": "Dry run — pass dry_run=False to actually merge.",
            })
        else:
            try:
                merge_result = merge_pr(repo, pr_num)
                results.append({"repo": repo, "pr": pr_num, "title": title, **merge_result})
            except Exception as e:
                results.append({"repo": repo, "pr": pr_num, "title": title, "would_merge": True, "merged": False, "reason": str(e)})

    would_merge = [r for r in results if r.get("would_merge") or r.get("merged")]
    skipped = [r for r in results if not r.get("would_merge") and not r.get("merged")]
    merged = [r for r in results if r.get("merged")]

    return {
        "dry_run": dry_run,
        "results": results,
        "would_merge_count": len(would_merge),
        "skipped_count": len(skipped),
        "merged_count": len(merged),
    }


def health_check() -> dict:
    """Post-merge verification: conflicts, stale PRs, deploy status for all T1 services."""
    from datetime import datetime, timezone, timedelta

    all_prs = gh.list_open_prs(GH_ORG)
    issues = []

    for pr in all_prs:
        repo = pr["repository"]["name"]
        pr_num = pr["number"]

        # Check mergeability
        try:
            state = gh._run_json([
                "pr", "view", str(pr_num),
                "--repo", f"{GH_ORG}/{repo}",
                "--json", "mergeable,mergeStateStatus",
            ])
            if state.get("mergeable") == "CONFLICTING":
                issues.append({
                    "type": "conflict",
                    "repo": repo,
                    "pr": pr_num,
                    "title": pr["title"],
                })
        except Exception:
            pass

        # Check staleness (>3 days)
        updated = datetime.fromisoformat(pr["updatedAt"].replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - updated
        if age > timedelta(days=3):
            issues.append({
                "type": "stale_pr",
                "repo": repo,
                "pr": pr_num,
                "title": pr["title"],
                "days_stale": age.days,
            })

    # Check Railway deploy status for all T1 services via railguey
    import subprocess
    import json as json_mod
    deploy_statuses = []
    for service_name, workspace_path in T1_SERVICES.items():
        try:
            result = subprocess.run(
                ["railguey", "deployments", workspace_path, service_name],
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode == 0:
                deps = json_mod.loads(result.stdout)
                latest = deps.get("deployments", [{}])[0]
                deploy_statuses.append({
                    "service": service_name,
                    "status": latest.get("status"),
                    "deployed_at": latest.get("createdAt"),
                    "url": latest.get("staticUrl"),
                })
        except Exception:
            deploy_statuses.append({
                "service": service_name,
                "status": "unknown",
                "error": "Could not query railguey",
            })

    return {
        "issues": issues,
        "issue_count": len(issues),
        "deploy_statuses": deploy_statuses,
        "healthy": len(issues) == 0,
    }


def changelog(since: str = "", repo: str = "") -> dict:
    """What shipped since a date? Merged PRs + closed issues."""
    from datetime import datetime, timezone, timedelta

    if not since:
        since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    if repo:
        repos = [repo]
    else:
        repos = list(TIER_MAP.keys())

    entries = []
    for r in repos:
        try:
            prs = gh._run_json([
                "pr", "list",
                "--repo", f"{GH_ORG}/{r}",
                "--state", "merged",
                "--search", f"merged:>={since}",
                "--json", "number,title,mergedAt,author",
                "--jq", ".",
            ])
            for pr in prs:
                entries.append({
                    "type": "pr_merged",
                    "repo": r,
                    "number": pr["number"],
                    "title": pr["title"],
                    "date": pr.get("mergedAt", ""),
                    "author": pr.get("author", {}).get("login", ""),
                })
        except Exception:
            pass

        try:
            issues_list = gh._run_json([
                "issue", "list",
                "--repo", f"{GH_ORG}/{r}",
                "--state", "closed",
                "--search", f"closed:>={since}",
                "--json", "number,title,closedAt",
                "--jq", ".",
            ])
            for issue in issues_list:
                entries.append({
                    "type": "issue_closed",
                    "repo": r,
                    "number": issue["number"],
                    "title": issue["title"],
                    "date": issue.get("closedAt", ""),
                })
        except Exception:
            pass

    entries.sort(key=lambda e: e.get("date", ""), reverse=True)

    return {
        "since": since,
        "entries": entries,
        "count": len(entries),
    }


def stale() -> dict:
    """Find stale work across the org."""
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    stale_items = []

    # Stale PRs (>3 days)
    all_prs = gh.list_open_prs(GH_ORG)
    for pr in all_prs:
        updated = datetime.fromisoformat(pr["updatedAt"].replace("Z", "+00:00"))
        age = now - updated
        if age > timedelta(days=3):
            stale_items.append({
                "type": "stale_pr",
                "repo": pr["repository"]["name"],
                "number": pr["number"],
                "title": pr["title"],
                "days": age.days,
                "url": pr["url"],
            })

    # Stale issues (>7 days) — check T1 repos only
    for repo in [r for r, t in TIER_MAP.items() if t == 1]:
        try:
            issues_list = gh._run_json([
                "issue", "list",
                "--repo", f"{GH_ORG}/{repo}",
                "--state", "open",
                "--json", "number,title,updatedAt,url",
                "--jq", ".",
            ])
            for issue in issues_list:
                updated = datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00"))
                age = now - updated
                if age > timedelta(days=7):
                    stale_items.append({
                        "type": "stale_issue",
                        "repo": repo,
                        "number": issue["number"],
                        "title": issue["title"],
                        "days": age.days,
                        "url": issue["url"],
                    })
        except Exception:
            pass

    stale_items.sort(key=lambda x: x["days"], reverse=True)

    return {
        "stale_items": stale_items,
        "count": len(stale_items),
    }
