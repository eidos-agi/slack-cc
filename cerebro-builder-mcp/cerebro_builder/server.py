"""MCP server — the mayor's office.

The mayor holds the mission and tells the agent what to do.
The mayor does NOT execute — no shell calls, no API calls.
The agent uses child MCPs (cerebro-github, railguey, ike-md, wrike, rhea) to execute.

State lives in ike.md. The mayor reads ike to know what's current.
The mayor holds guardrails and routing. Everything else is delegated.

The mayor's job:
  1. Know the mission (local)
  2. Know what's next (reads ike)
  3. Check if proposed work is aligned (guardrails + ike state)
  4. Tell the agent which child to use and in what order
  5. Flag when Rhea should intervene
"""

from mcp.server.fastmcp import FastMCP

from .mission import (
    mission_check, mission_status, get_current_milestone,
    get_next_tasks, MISSION, GUARDRAILS,
)
from .topology import CHANGE_LIFECYCLE, SERVICES, ENVIRONMENTS, DEPLOY_ORDER, VENDOR_CREDENTIALS

mcp = FastMCP("cerebro-builder")


# ── Builder ceremony — convene and adjourn ───────────────


@mcp.tool()
def convene() -> dict:
    """The mayor calls the session to order.

    Run at session start BEFORE whats_next(). Roll call:
    ike state, learnings, personas, git, milestone, blocking PRs.

    Writes a convene record to the builder's session log.
    Returns pass/fail for each check. Fix failures before starting.
    """
    from .ceremony import run_convene
    return run_convene()


@mcp.tool()
def adjourn(summary: str = "", next_actions: list[str] | None = None) -> dict:
    """The mayor closes the session. Gavel down.

    Run BEFORE the cockpit /land skill. Verifies work is committed,
    ike is updated, learnings saved, PRs opened, stakeholders notified.

    Writes an adjourn record to the builder's session log with
    what was accomplished and what's next.

    Args:
        summary: What was accomplished this session
        next_actions: Concrete next steps for the next convene
    """
    from .ceremony import run_adjourn
    return run_adjourn(summary, next_actions or [])


# ── Mission ─────────────────────────────────────────────


@mcp.tool()
def check_mission(proposed_task: str) -> dict:
    """Is this task advancing the mission?

    Reads ike.md for current milestone and open tasks.
    If drifting toward infrastructure, returns rhea_required=true.

    Args:
        proposed_task: What you're about to do
    """
    return mission_check(proposed_task)


@mcp.tool()
def get_mission() -> dict:
    """Full mission briefing from ike.md — milestones, progress, guardrails.

    Call at session start (takeoff) and before landing.
    """
    return mission_status()


@mcp.tool()
def whats_next() -> dict:
    """What should the agent work on right now?

    Reads ike.md for the current milestone and highest-priority open tasks.
    Returns task titles, definition of done, and which children to use.
    """
    current = get_current_milestone()
    tasks = get_next_tasks()

    if not current and not tasks:
        return {"done": True, "message": "All milestones complete."}

    # Get definition of done from the top task
    top_task = tasks[0] if tasks else None
    dod = top_task.get("definition_of_done", []) if top_task else []

    return {
        "mission": MISSION["statement"],
        "north_star": MISSION["north_star"],
        "current_milestone": current.get("title") if current else None,
        "next_task": {
            "id": top_task.get("id"),
            "title": top_task.get("title"),
            "definition_of_done": dod,
        } if top_task else None,
        "upcoming_tasks": [
            {"id": t.get("id"), "title": t.get("title")}
            for t in tasks[1:5]
        ],
        "guardrails": [g["test"] for g in GUARDRAILS],
        "children": {
            "ike-md": "Use to update task status as you work (task_edit status='In Progress'/'Done')",
            "cerebro-github": "Use for issues, PRs, CI, merge",
            "railguey": "Use for deploy status, logs, variables",
            "rhea": "Use when stakes are high or you're unsure",
        },
    }


# ── Shipping ────────────────────────────────────────────


@mcp.tool()
def how_to_ship(repo: str) -> dict:
    """How to ship a change on this repo — the full ceremony, step by step.

    Returns which child MCPs to call and in what order, based on
    the repo's tier and the deploy topology.

    Args:
        repo: Repository name (e.g., "cerebro", "data-daemon")
    """
    from .config import TIER_MAP

    tier = TIER_MAP.get(repo, 3)
    svc = SERVICES.get(repo)
    env_info = {
        name: {"domain": svc.domains.get(name, "") if svc else ""}
        for name in ENVIRONMENTS
    }

    steps = [
        f"1. cerebro-github: create_work(title, repo='{repo}')",
        "2. Write code on a feature branch",
        f"3. cerebro-github: open_pr(repo='{repo}', branch='feat/...', closes=N)",
        f"4. cerebro-github: check_ci(repo='{repo}', pr_number=N) — wait for green",
    ]

    if tier == 1:
        steps.append(f"5. cerebro-github: merge_pr(repo='{repo}', pr_number=N) — merges to develop")
        steps.append(f"6. railguey: check staging deploy at {env_info.get('develop', {}).get('domain', 'staging')}")
        steps.append("7. Verify feature works on staging")
        steps.append("8. To promote: create develop→main PR, requires Rhea challenge (T1 gate)")
        steps.append(f"9. railguey: verify production deploy at {env_info.get('production', {}).get('domain', 'production')}")
        steps.append("10. wrike: update stakeholder card with what shipped")
    else:
        steps.append(f"5. cerebro-github: merge_pr(repo='{repo}', pr_number=N)")
        if svc and any(svc.domains.values()):
            steps.append("6. Verify deploy if this repo has a service")

    # Deploy ordering
    deploy_context = None
    if repo in DEPLOY_ORDER:
        idx = DEPLOY_ORDER.index(repo)
        before = DEPLOY_ORDER[:idx]
        after = DEPLOY_ORDER[idx + 1:]
        if before:
            deploy_context = f"Deploy AFTER: {', '.join(before)}"
        if after:
            deploy_context = (deploy_context or "") + f" | Deploy BEFORE: {', '.join(after)}"

    return {
        "repo": repo,
        "tier": tier,
        "steps": steps,
        "deploy_order": deploy_context,
        "environments": env_info,
    }


@mcp.tool()
def how_to_migrate() -> dict:
    """How to write and deploy a database migration via cerebro-migrations.

    Returns the exact workflow: write SQL, test locally, create PR,
    verify on staging via Supabase CLI.
    """
    return {
        "repo": "cerebro-migrations",
        "workspace": "/home/dev/repos/cerebro-migrations",
        "migration_dir": "supabase/migrations/",
        "naming": "YYYYMMDDHHMMSS_description.sql (e.g., 20260413120000_sage_silver_views.sql)",
        "workflow": [
            "1. Write the migration SQL in supabase/migrations/",
            "2. Test locally: supabase db reset (rebuilds from all migrations)",
            "3. cerebro-github: create_work(title, repo='cerebro-migrations')",
            "4. git checkout -b feat/description origin/develop",
            "5. git add && git commit && git push",
            "6. cerebro-github: open_pr(repo='cerebro-migrations', branch='feat/...', closes=N)",
            "7. cerebro-github: check_ci — CI runs 'Fresh database' and 'RBAC contract' checks",
            "8. cerebro-github: merge_pr — merges to develop",
            "9. Apply to staging: supabase db push --linked (staging project ref: izmuckuepryqneebwwol)",
            "10. VERIFY: query staging Supabase to confirm views exist and return data",
        ],
        "conventions": {
            "schemas": "sage_bronze (raw), sage_silver (typed), sage_gold (aggregated)",
            "rls": "All tables need RLS policies or explicit rls_disabled_in_public exemption",
            "soft_deletes": "WHERE deleted_at IS NULL on all views",
            "entity_column": "All tables include entity TEXT CHECK IN ('ntx', 'hometown', 'memphis')",
        },
        "existing_migrations": [
            "20260410060000_sage_bronze_rewrite.sql — 7 bronze tables with raw_data JSONB",
        ],
        "children": {
            "cerebro-github": "PR ceremony for the migration repo",
            "railguey": "NOT used for migrations — Supabase deploys via CLI, not Railway",
        },
    }


# ── Quality control ─────────────────────────────────────


@mcp.tool()
def verify_milestone(milestone_id: str) -> dict:
    """Quality control — is a milestone actually done?

    Reads the milestone's tasks from ike.md, checks which are done,
    and returns the definition of done for incomplete tasks.

    Args:
        milestone_id: e.g., "MS-0004" or "M-04"
    """
    from .mission import _read_ike_tasks, _read_ike_milestones

    # Normalize ID
    if milestone_id.startswith("M-"):
        num = milestone_id.split("-")[1]
        milestone_id = f"MS-{num.zfill(4)}"

    milestones = _read_ike_milestones()
    milestone = next((m for m in milestones if m.get("id") == milestone_id), None)
    if not milestone:
        return {"error": f"Unknown milestone: {milestone_id}. Known: {[m.get('id') for m in milestones]}"}

    # Get tasks linked to this milestone
    all_tasks = _read_ike_tasks()
    linked = [t for t in all_tasks if t.get("milestone", "").startswith(milestone_id[:7])]

    done_tasks = [t for t in linked if t.get("in_completed") or t.get("status", "").lower() in ("done", "completed")]
    open_tasks = [t for t in linked if t not in done_tasks]

    return {
        "milestone": milestone_id,
        "title": milestone.get("title"),
        "status": milestone.get("status"),
        "tasks_done": len(done_tasks),
        "tasks_open": len(open_tasks),
        "tasks_total": len(linked),
        "open_tasks": [
            {
                "id": t.get("id"),
                "title": t.get("title"),
                "definition_of_done": t.get("definition_of_done", []),
            }
            for t in open_tasks
        ],
        "all_done": len(open_tasks) == 0 and len(linked) > 0,
        "instructions": (
            "All tasks done — mark the milestone closed via ike-md: milestone_close()"
            if len(open_tasks) == 0 and len(linked) > 0
            else "Complete the open tasks above. Use ike-md: task_complete() as each finishes."
        ),
    }


# ── Topology ────────────────────────────────────────────


@mcp.tool()
def get_topology() -> dict:
    """The full system topology — environments, services, credentials, deploy order."""
    return {
        "environments": {
            name: {
                "supabase_ref": env.supabase.ref if env.supabase else None,
                "railway_token_env": env.railway_token_env,
            }
            for name, env in ENVIRONMENTS.items()
        },
        "services": {
            name: {"repo": svc.repo, "domains": svc.domains}
            for name, svc in SERVICES.items()
        },
        "vendor_credentials": [
            {"vendor": vc.vendor, "env_vars": vc.env_vars, "same_both_envs": vc.same_both_envs, "notes": vc.notes}
            for vc in VENDOR_CREDENTIALS
        ],
        "deploy_order": DEPLOY_ORDER,
        "lifecycle": CHANGE_LIFECYCLE,
    }


# ── Ariadne — "Are we even doing the right thing?" ──────


@mcp.tool()
def ariadne(task_title: str, approach: str = "") -> dict:
    """Challenge the APPROACH before writing code.

    Ariadne is not Rhea. Rhea asks "is this safe?" Ariadne asks
    "is this the right way to solve this problem?"

    Two layers:
    - Pattern memory: known mistakes from learnings.json (fast)
    - Her own mind: full-context reasoning via Rhea (thorough)

    Always requires Rhea. Patterns catch known mistakes.
    Rhea catches the novel ones.

    Args:
        task_title: What you're about to do
        approach: How you plan to do it (more detail = better challenge)
    """
    from .ariadne import ariadne_challenge
    return ariadne_challenge(task_title, approach)


@mcp.tool()
def ariadne_learn(lesson: str, trigger_words: list[str], source: str = "") -> dict:
    """Teach Ariadne a new pattern from a mistake or near-miss.

    When something goes wrong — or almost goes wrong — call this
    to add it to her memory. Next time someone tries the same
    approach, she'll warn them.

    Args:
        lesson: What went wrong and why (be specific)
        trigger_words: Words that should trigger this warning in future
        source: Where this lesson came from (session, incident, etc.)
    """
    from .ariadne import ariadne_learn as _learn
    return _learn(lesson, trigger_words, source)


# ── Loop contract ───────────────────────────────────────


@mcp.tool()
def pre_advance_checks(task_title: str) -> dict:
    """What must pass before this task can be marked complete?

    Returns concrete checks based on task type (migration, connector,
    dashboard, verification). If rhea_required, the agent must run
    adversarial review before calling task_complete().

    Call this BEFORE completing any task. The stupidity catcher.

    Args:
        task_title: The ike task title
    """
    from .loop import get_pre_advance_checks
    return get_pre_advance_checks(task_title)


@mcp.tool()
def loop_contract() -> dict:
    """The full loop iteration contract — what happens every cycle.

    Returns the 8-step loop, abort conditions, and stupidity catchers.
    Use this to understand the autonomous execution protocol.
    """
    from .loop import LOOP_CONTRACT
    return LOOP_CONTRACT


# ── Forge routing ───────────────────────────────────────

FORGE_ROUTES = {
    "vendor_research": {
        "forge": "connection-forge",
        "mcp": "N/A — cockpit skill /vendor-research",
        "when": "Researching a new vendor API before building a connector",
        "produces": "api-data-model.md in the infra repo",
    },
    "architectural_decision": {
        "forge": "Eidos trilogy: research.md → visionlog → ike.md",
        "mcp": "mcp__research-md, mcp__visionlog, mcp__ike-md",
        "when": "Making a decision with consequences (technology, architecture, strategy)",
        "produces": "Research project → ADR in visionlog → tasks in ike.md",
    },
    "database_migration": {
        "forge": "cerebro-migrations",
        "mcp": "cerebro-github (PR ceremony) + supabase CLI (deploy)",
        "when": "Creating or modifying database schemas, views, functions, or RLS policies",
        "produces": "SQL migration file → PR → applied to staging/production Supabase",
    },
    "code_refactor": {
        "forge": "refactor-forge",
        "mcp": "N/A — GitHub tool (eidos-agi/refactor-forge)",
        "when": "Restructuring code that must maintain behavioral parity",
        "produces": "Golden fixtures → refactored code → parity tests",
    },
    "metrics_excel": {
        "forge": "warp-speed forges",
        "mcp": "N/A — cerebro-warp-speed-excel pipeline",
        "when": "Generating Alex's Greenmark_Metrics spreadsheet",
        "produces": "Excel workbook from SQLite gold tables",
    },
    "weekly_report": {
        "forge": "weekly-update pipeline",
        "mcp": "N/A — cockpit skill /weekly-update",
        "when": "Generating weekly engineering report for stakeholders",
        "produces": "Markdown report in weekly-updates repo",
    },
    "adversarial_review": {
        "forge": "Rhea",
        "mcp": "mcp__rhea__rhea_challenge",
        "when": "High-stakes decision, production merge, or when you're unsure",
        "produces": "Dreamer/Doubter/Decider ruling with confidence level",
    },
    "task_execution": {
        "forge": "ike.md",
        "mcp": "mcp__ike-md",
        "when": "Breaking work into tasks, tracking progress, managing milestones",
        "produces": "TASK files with acceptance criteria and definition of done",
    },
    "stakeholder_update": {
        "forge": "Wrike",
        "mcp": "mcp__wrike",
        "when": "Updating Michael/Alex on progress (executive-level, Daniel's voice)",
        "produces": "Wrike task comments/descriptions — no AI-generated content",
    },
}


@mcp.tool()
def which_forge(situation: str) -> dict:
    """Which forge or tool should the agent use for this situation?

    Args:
        situation: What you're trying to do
    """
    situation_lower = situation.lower()

    matches = []
    for key, route in FORGE_ROUTES.items():
        when_lower = route["when"].lower()
        key_words = key.replace("_", " ").split()
        if any(kw in situation_lower for kw in key_words) or any(word in situation_lower for word in when_lower.split() if len(word) > 4):
            matches.append(route)

    if not matches:
        matches = [FORGE_ROUTES["task_execution"]]

    return {
        "situation": situation,
        "recommended_forges": matches,
        "all_forges": list(FORGE_ROUTES.keys()),
    }
