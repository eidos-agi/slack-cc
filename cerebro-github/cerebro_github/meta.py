"""Meta-ceremony — the ceremony that knows itself."""

import json as json_mod
from . import gh
from .config import GH_ORG, TIER_MAP, LEDGER_PATH
from .topology import ENVIRONMENTS, SERVICES, VENDOR_CREDENTIALS, DEPLOY_ORDER, CHANGE_LIFECYCLE
from .mission import mission_status, MISSION

# ── The Ledger ──────────────────────────────────────────────────
# Every ceremony rule traces back to an incident. The ledger is the
# institutional memory. New agents read it. Old agents add to it.
# Persisted to ledger.json — survives process restarts.

_DEFAULT_LEDGER = [
    {
        "rule": "Issue before PR",
        "tool": "create_work",
        "incident": "Session 22: opened 9 PRs with no linked issues. Project board showed empty 'Linked pull requests' column. Daniel caught it.",
        "date": "2026-04-10",
        "cost": "Rebuilt all 9 PRs to reference issues. ~30 minutes of rework.",
        "principle": "Work that isn't tracked doesn't exist. The project board is how Daniel sees progress.",
    },
    {
        "rule": "Check CI after every PR",
        "tool": "check_ci",
        "incident": "Session 22: opened 8 PRs, walked away. 4 had failing CI (pre-existing lint errors + wrong CI template on cerebro-migrations). Daniel caught it.",
        "date": "2026-04-10",
        "cost": "Had to fix lint across 4 repos and remove bad CI template. ~45 minutes.",
        "principle": "CI you don't check is CI you don't have.",
    },
    {
        "rule": "Never delete long-lived branches",
        "tool": "merge_pr",
        "incident": "Session 21: ran gh pr merge 1 --delete-branch on a develop→main PR. Deleted the develop branch from cerebro-migrations remote.",
        "date": "2026-04-09",
        "cost": "Had to recreate develop. Built gh-guard.sh and Claude hook to prevent recurrence.",
        "principle": "Destruction is irreversible. Guard rails beat memory.",
    },
    {
        "rule": "Add issue to project via GraphQL, not gh CLI",
        "tool": "create_work",
        "incident": "Session 22: gh project item-add returned success but items didn't appear. Pagination hid them (default limit 30, had 47 items). GraphQL mutation is reliable.",
        "date": "2026-04-10",
        "cost": "Thought items were missing, re-added multiple times, confused Daniel.",
        "principle": "If a tool silently fails, use a lower-level tool that gives you a receipt.",
    },
    {
        "rule": "Tier-appropriate ceremony",
        "tool": "create_work",
        "incident": "Session 22: bootstrap-repo.sh installed Node.js CI on cerebro-migrations (a SQL repo with package.json for supabase CLI). All 3 CI checks failed.",
        "date": "2026-04-10",
        "cost": "Had to remove bad ci.yml and fix language detection heuristic.",
        "principle": "One size fits nobody. Classify first, then apply.",
    },
    {
        "rule": "NEXT_PUBLIC vars need a rebuild",
        "tool": "health_check",
        "incident": "Session 22: set NEXT_PUBLIC_ENV_LABEL in Railway. Banner didn't appear. NEXT_PUBLIC_* is baked at build time — setting the var without a code push doesn't trigger a rebuild.",
        "date": "2026-04-10",
        "cost": "20 minutes debugging before realizing Railway doesn't rebuild on env var changes alone.",
        "principle": "Build-time vars need build-time changes. Runtime vars take effect immediately. Know which is which.",
    },
    {
        "rule": "Wrike stays executive-level, GitHub has the detail",
        "tool": "changelog",
        "incident": "Session 22: Daniel asked 'are you covering the rear?' — Wrike hadn't been updated while GitHub had 30+ items. The two systems drifted.",
        "date": "2026-04-10",
        "cost": "Trust gap. Michael sees Wrike, not GitHub. If Wrike is stale, Michael thinks nothing happened.",
        "principle": "Two systems = two audiences. Bridge them or they drift.",
    },
]


def _load_ledger() -> list[dict]:
    """Load ledger from disk, falling back to defaults."""
    if LEDGER_PATH.is_file():
        try:
            return json_mod.loads(LEDGER_PATH.read_text())
        except Exception:
            pass
    return list(_DEFAULT_LEDGER)


def _save_ledger(ledger: list[dict]) -> None:
    """Persist ledger to disk."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json_mod.dumps(ledger, indent=2) + "\n")


# Module-level ledger — loaded once, saved on learn()
LEDGER = _load_ledger()


def onboard() -> dict:
    """Full ceremony briefing for a new AI session.

    Returns the complete ceremony: what tools exist, why each exists,
    the incident that created it, and the workflow order.
    """
    ms = mission_status()

    return {
        "greeting": (
            "You're working in the Greenmark Cerebro engineering ecosystem. "
            "This MCP server encodes the full engineering ceremony — from idea to "
            "verified-in-production to visible-to-stakeholders. Every rule traces to "
            "an incident. Read the ledger to understand why."
        ),
        "mission": ms["mission"],
        "mission_progress": ms["progress"],
        "current_milestone": ms["current"],
        "drift_warning": ms["drift_warning"],
        "lifecycle": CHANGE_LIFECYCLE,
        "org": GH_ORG,
        "repos": {name: f"T{tier}" for name, tier in sorted(TIER_MAP.items())},
        "ledger": LEDGER,
        "infrastructure": {
            "environments": {name: {
                "supabase_ref": env.supabase.ref if env.supabase else None,
                "railway_token_env": env.railway_token_env,
            } for name, env in ENVIRONMENTS.items()},
            "services": {name: {
                "repo": svc.repo,
                "domains": svc.domains,
            } for name, svc in SERVICES.items()},
            "vendor_credentials": [{
                "vendor": vc.vendor,
                "env_vars": vc.env_vars,
                "same_both_envs": vc.same_both_envs,
                "notes": vc.notes,
            } for vc in VENDOR_CREDENTIALS],
            "deploy_order": DEPLOY_ORDER,
        },
        "tools": [
            "create_work", "close_work", "open_pr", "check_ci", "merge_pr",
            "dashboard", "bulk_merge", "health_check", "changelog", "stale",
            "onboard", "why", "retro", "learn",
        ],
    }


def why(tool_name: str) -> dict:
    """Explain why a ceremony tool exists — the incident behind it.

    Every tool traces to a real mistake. This is the institutional memory.
    """
    matching = [entry for entry in LEDGER if entry["tool"] == tool_name]
    if not matching:
        return {
            "tool": tool_name,
            "ledger_entries": [],
            "note": f"No incident history for '{tool_name}'. It may be preventive rather than reactive.",
        }
    return {
        "tool": tool_name,
        "ledger_entries": matching,
    }


def retro(days: int = 7) -> dict:
    """Review recent work and identify ceremony gaps.

    Checks: PRs without issues, issues not in project, CI failures
    left unfixed, stale work, deploy status.
    """
    from datetime import datetime, timezone, timedelta
    from . import ceremony

    findings = []

    # 1. Open PRs without "Closes #" in body
    all_prs = gh.list_open_prs(GH_ORG)
    for pr in all_prs:
        repo = pr["repository"]["name"]
        pr_num = pr["number"]
        try:
            body = gh._run([
                "pr", "view", str(pr_num),
                "--repo", f"{GH_ORG}/{repo}",
                "--json", "body",
                "--jq", ".body",
            ])
            if not any(kw in body.lower() for kw in ["closes #", "fixes #", "resolves #"]):
                findings.append({
                    "type": "pr_no_issue",
                    "repo": repo,
                    "pr": pr_num,
                    "title": pr["title"],
                    "fix": "Add 'Closes #N' to the PR body, or create an issue first.",
                })
        except Exception:
            pass

    # 2. CI failures left unfixed
    for pr in all_prs:
        repo = pr["repository"]["name"]
        pr_num = pr["number"]
        try:
            ci = ceremony.check_ci(repo, pr_num)
            if ci["failed"]:
                findings.append({
                    "type": "ci_failure",
                    "repo": repo,
                    "pr": pr_num,
                    "title": pr["title"],
                    "failed_checks": ci["failed"],
                    "fix": "Fix the failing checks before merging.",
                })
        except Exception:
            pass

    # 3. Stale work
    stale_data = ceremony.stale()

    # 4. Deploy health
    health = ceremony.health_check()

    return {
        "findings": findings,
        "finding_count": len(findings),
        "stale": stale_data,
        "health": health,
        "recommendation": (
            "Clean findings first, then proceed with new work. "
            "Ceremony debt compounds — every unfixed finding makes the next session messier."
        ),
    }


def learn(rule: str, incident: str, tool: str = "", cost: str = "", principle: str = "") -> dict:
    """Record a new ceremony lesson from an incident.

    This adds to the ledger so future sessions know why the rule exists.
    The ledger is in-memory for now — persists via the source code.
    Call this when a new mistake reveals a missing ceremony step.

    Returns the new ledger entry and instructions for making it permanent.
    """
    from datetime import datetime, timezone
    entry = {
        "rule": rule,
        "tool": tool or "general",
        "incident": incident,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "cost": cost or "unknown",
        "principle": principle or rule,
    }
    LEDGER.append(entry)
    _save_ledger(LEDGER)

    return {
        "entry": entry,
        "ledger_size": len(LEDGER),
        "persisted_to": str(LEDGER_PATH),
    }
