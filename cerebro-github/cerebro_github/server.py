"""MCP server — exposes ceremony as tools."""

from mcp.server.fastmcp import FastMCP

from . import ceremony
from . import gh
from . import meta
from . import mission

mcp = FastMCP("cerebro-github")


@mcp.tool()
def create_work(
    title: str,
    repo: str,
    body: str = "",
    milestone_repo: str = "",
    milestone_number: int = 0,
    status: str = "todo",
) -> dict:
    """Create an issue, link it to a milestone, and add it to the project board.

    This is step 1 of the ceremony: create the work item BEFORE writing code.

    Args:
        title: Issue title (e.g., "Write SageIntacctConnector class")
        repo: Repository name (e.g., "data-daemon", "cerebro")
        body: Issue body/description
        milestone_repo: Repo containing the parent milestone issue (optional)
        milestone_number: Issue number of the parent milestone (optional)
        status: "todo" or "in_progress"
    """
    return ceremony.create_work(
        title=title,
        repo=repo,
        body=body,
        milestone_repo=milestone_repo or None,
        milestone_number=milestone_number or None,
        status=status,
    )


@mcp.tool()
def close_work(repo: str, number: int, reason: str = "completed") -> dict:
    """Close an issue without a PR.

    Use when work is resolved by conversation, marked won't-fix,
    or superseded. Sets project status to Done.

    Args:
        repo: Repository name
        number: Issue number
        reason: "completed" or "not_planned"
    """
    return ceremony.close_work(repo=repo, number=number, reason=reason)


@mcp.tool()
def open_pr(
    repo: str,
    branch: str,
    closes: int,
    title: str = "",
    body: str = "",
    base: str = "develop",
) -> dict:
    """Create a PR that closes an issue. Ensures issue is in the project board.

    This is step 2 of the ceremony: code is done, open the PR.
    The issue MUST already exist (use create_work first).

    Args:
        repo: Repository name (e.g., "data-daemon")
        branch: Feature branch name (e.g., "feat/sage-connector")
        closes: Issue number this PR closes
        title: PR title (defaults to issue reference)
        body: Additional PR body text (Closes #N is auto-prepended)
        base: Base branch to merge into (default: develop)
    """
    return ceremony.open_pr(
        repo=repo,
        branch=branch,
        closes=closes,
        title=title or None,
        body=body,
        base=base,
    )


@mcp.tool()
def check_ci(repo: str, pr_number: int, wait: bool = False) -> dict:
    """Check CI status on a pull request.

    Returns which checks passed, failed, or are still pending.

    With wait=True, blocks for up to 60 seconds polling every 15s.
    If checks are still pending, returns with recall=True — call
    check_ci(wait=True) again. This replaces rapid-fire polling
    with 3-5 paced calls for a typical 3-minute CI run.

    ALWAYS use wait=True after opening a PR. Never rapid-poll.

    Args:
        repo: Repository name
        pr_number: Pull request number
        wait: If True, block up to 60s polling internally (default: False)
    """
    return ceremony.check_ci(repo=repo, pr_number=pr_number, wait=wait)


@mcp.tool()
def merge_pr(repo: str, pr_number: int, gate_token: str = "", rhea_decision: str = "") -> dict:
    """Merge a pull request with safety checks and Rhea gating.

    For T1 repos merging to main (production): returns a Rhea gate on first
    call. Run mcp__rhea__rhea_challenge with the returned challenge_prompt,
    then call again with gate_token and rhea_decision to execute.

    For all other merges: executes immediately.

    Args:
        repo: Repository name
        pr_number: Pull request number
        gate_token: Token from a prior gate call (T1→main only)
        rhea_decision: Output from Rhea challenge (T1→main only)
    """
    return ceremony.merge_pr(
        repo=repo, pr_number=pr_number,
        gate_token=gate_token, rhea_decision=rhea_decision,
    )


@mcp.tool()
def rate_status() -> dict:
    """Check GitHub API rate limit budget.

    Shows remaining REST and GraphQL quota, floors, and whether
    it's safe to continue. The governor blocks calls when quota
    drops below the floor — check this if you're getting RateLimitError.

    Also reports auth mode: "github_app" (own bucket) or "pat" (Daniel's bucket).
    """
    from . import app_auth
    status = gh.rate_status()
    status["auth_mode"] = "github_app" if app_auth.is_app_auth_configured() else "pat"
    return status


@mcp.tool()
def dashboard() -> dict:
    """Show all open PRs across the Greenmark org with CI status.

    Returns a table of every open PR, which repo it's in,
    and whether CI is passing.
    """
    return ceremony.dashboard()


@mcp.tool()
def bulk_merge(repos_and_prs: list[dict] | None = None, dry_run: bool = True) -> dict:
    """Preview or execute merging green PRs across the org.

    DRY RUN BY DEFAULT. Shows what would merge without doing it.
    Set dry_run=False to actually merge.

    Args:
        repos_and_prs: Optional list of {"repo": "name", "pr": number}.
                       If omitted, considers ALL open PRs across the org.
        dry_run: If True (default), preview only. If False, actually merge.
    """
    return ceremony.bulk_merge(repos_and_prs, dry_run=dry_run)


@mcp.tool()
def health_check() -> dict:
    """Post-merge verification: are deploys healthy?

    Checks all open PRs for conflicts, verifies recent deploys via
    railguey (if available), flags stale PRs (>3 days), and reports
    any issues that should have auto-closed but didn't.
    """
    return ceremony.health_check()


@mcp.tool()
def changelog(since: str = "", repo: str = "") -> dict:
    """What shipped since a given date?

    Collects merged PRs and closed issues across the org (or one repo)
    since the given date. Useful for weekly standups and Wrike updates.

    Args:
        since: ISO date (e.g., "2026-04-07"). Defaults to 7 days ago.
        repo: Optional repo name to scope to. Omit for org-wide.
    """
    return ceremony.changelog(since=since, repo=repo)


@mcp.tool()
def stale() -> dict:
    """Find stale work: PRs and issues untouched for 3+ days.

    Returns open PRs not updated in 3 days, open issues not updated
    in 7 days, and milestone sub-issues that are overdue.
    """
    return ceremony.stale()


# ── Mission tools — strategic coherence ──────────────────


@mcp.tool()
def mission_check(proposed_task: str) -> dict:
    """Check if a proposed task advances the mission.

    Call this BEFORE starting any work. Returns whether the task
    is on the critical path, and if not, asks why you're doing it.

    Args:
        proposed_task: What you're about to do (e.g., "build silver views", "refactor CI")
    """
    return mission.mission_check(proposed_task)


@mcp.tool()
def mission_status() -> dict:
    """Full mission status — milestones, progress, guardrails, drift warning.

    Call at takeoff and landing to maintain strategic coherence.
    """
    return mission.mission_status()


# ── Meta tools — the ceremony that knows itself ──────────


@mcp.tool()
def onboard() -> dict:
    """Full ceremony briefing for a new AI session.

    Call this at the start of any session touching Greenmark repos.
    Returns: what tools exist, why each exists (the incident that
    created it), the workflow order, and the repo tier map.
    """
    return meta.onboard()


@mcp.tool()
def why(tool_name: str) -> dict:
    """Explain why a ceremony tool exists.

    Every tool traces to a real incident. This returns the incident,
    the cost, and the principle behind the rule.

    Args:
        tool_name: Name of the tool (e.g., "create_work", "merge_pr")
    """
    return meta.why(tool_name)


@mcp.tool()
def retro(days: int = 7) -> dict:
    """Review recent work and identify ceremony gaps.

    Finds: PRs without issues, unfixed CI failures, stale work,
    deploy health issues. Run this before starting new work to
    clean up debt from previous sessions.

    Args:
        days: How far back to look (default: 7)
    """
    return meta.retro(days=days)


@mcp.tool()
def learn(rule: str, incident: str, tool: str = "", cost: str = "", principle: str = "") -> dict:
    """Record a new ceremony lesson from an incident.

    When a mistake reveals a missing ceremony step, call this to
    add it to the ledger. Future sessions will see it in onboard().

    Args:
        rule: The ceremony rule (e.g., "Always check deploy after merge")
        incident: What happened (e.g., "Merged PR but deploy failed silently")
        tool: Which tool this relates to (optional)
        cost: What it cost to fix (optional)
        principle: The underlying principle (optional)
    """
    return meta.learn(rule=rule, incident=incident, tool=tool, cost=cost, principle=principle)
