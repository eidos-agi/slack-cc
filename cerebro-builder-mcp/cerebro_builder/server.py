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

mcp = FastMCP(
    "cerebro-builder",
    instructions=(
        "cerebro-builder is the session orchestrator — the mayor's office. "
        "It holds the mission, guardrails, and tells you what to work on next. "
        "Use `convene` to start a work session, `adjourn` to end it. "
        "Use `whats_next` to get prioritized tasks, `check_mission` to validate alignment. "
        "Use `docs` to search the knowledge base, `get_topology` for service/deploy topology. "
        "Use `how_to_ship` and `how_to_migrate` for deployment ceremony. "
        "\n\n"
        "WHEN TO USE WHICH MCP:\n"
        "- cerebro-builder: session orchestration, mission, what to work on, guardrails, knowledge base\n"
        "- cerebro-web-builder: shipping code (ship_to_staging, promote_to_production), "
        "deploy topology, browser login, page smoke tests, deploy status\n"
        "- cerebro-verifier: data correctness — are the NUMBERS right? "
        "Ground truth SQL comparison, golden fixtures, KPI extraction, evidence trails\n"
        "- cerebro-data-engineer: warehouse operations — query gold views, check freshness, "
        "run parity checks, diagnose pipeline issues\n"
        "- cerebro-github: git ceremony — issues, PRs, CI, merges, changelog\n\n"
        "For full ecosystem documentation, use cerebro-docs.\n\n"
        "MANDATORY BEFORE DEPLOY OPERATIONS:\n"
        "Before merging a PR, applying a migration, deploying a service, or triggering "
        "an extraction, you MUST call cerebro-docs.workflow() to load the deployment "
        "procedure. Specifically:\n"
        "- Before merging to data-daemon: workflow('deploy_data_daemon')\n"
        "- Before applying any migration: workflow('apply_migration')\n"
        "- Before shipping cerebro changes: workflow('ship_to_staging') or workflow('promote_to_production')\n"
        "- Before onboarding a new vendor API key: workflow('vendor_api_onboarding')\n"
        "Do NOT rely on memory or assumptions about how deploys work. Read the workflow first. Every time."
    ),
)


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


@mcp.tool()
def beepboop() -> dict:
    """One-word session cycle trigger.

    Call when the pilot says "beepboop". Finishes in-flight work,
    adjourns, and reconvenes cleanly.

    The agent should:
    1. Finish or checkpoint any in-flight work
    2. Call adjourn() with the summary and next_actions from this response
    3. IF context is long/bloated, run /compact first (NOT /clear)
    4. Call convene() → whats_next() → resume

    Compact is a suggestion when context has grown stale, not a
    mandatory step. If context is fresh, skip straight to convene.
    """
    from .ceremony import _latest_session
    from .mission import get_current_milestone, get_next_tasks

    session = _latest_session()
    milestone = get_current_milestone()
    tasks = get_next_tasks()

    import subprocess
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
            cwd="/home/dev/repos/greenmark-cockpit",
        )
        dirty_files = [l.strip() for l in r.stdout.strip().split("\n") if l.strip()]
    except Exception:
        dirty_files = []

    open_prs = []
    for repo in ["cerebro", "cerebro-migrations", "data-daemon", "greenmark-cockpit"]:
        try:
            r = subprocess.run(
                ["gh", "pr", "list", "--repo", f"greenmark-waste-solutions/{repo}",
                 "--state", "open", "--json", "number,title,url", "--limit", "5"],
                capture_output=True, text=True, timeout=10,
            )
            if r.returncode == 0 and r.stdout.strip():
                import json
                prs = json.loads(r.stdout)
                for pr in prs:
                    open_prs.append({"repo": repo, **pr})
        except Exception:
            pass

    return {
        "phase": "beepboop",
        "message": (
            "Session cycle. Agent: finish in-flight work, "
            "then call adjourn() with the summary and next_actions below. "
            "If context is long, run /compact (NOT /clear) before reconvening. "
            "Then convene() → whats_next() → resume."
        ),
        "current_milestone": milestone.get("title") if milestone else None,
        "open_tasks": len(tasks),
        "dirty_files": dirty_files,
        "open_prs": open_prs,
        "session_id": session["id"] if session else None,
        "instructions": [
            "1. Commit any uncommitted work" if dirty_files else "1. Git is clean",
            "2. Call adjourn(summary=<what you did>, next_actions=<concrete next steps>)",
            "3. If context is bloated, run /compact (NOT /clear) — otherwise skip",
            "4. convene() → whats_next() → execute",
        ],
    }


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
            "cerebro-github": "Use for issues, PRs, CI, merge — everything goes through the project board (Project #1)",
            "railguey": "Use for deploy status, logs, variables",
            "rhea": "Use when stakes are high or you're unsure",
        },
    }


# ── Wrike — stakeholder updates ────────────────────────


# Michael's Wrike card map for Cerebro vendor integrations.
# Structure: Weekly Review - Accounting → Special Projects → Cerebro → {vendor}
WRIKE_CEREBRO_CARDS = {
    "cerebro": {"id": "MAAAAAEE1lfX", "title": "Cerebro", "note": "Parent card. Post general Cerebro updates here."},
    "sage": {"id": "MAAAAAEICsDm", "title": "Sage", "note": "DONE. Post completion/maintenance updates."},
    "navusoft": {"id": "MAAAAAEICX2B", "title": "Navusoft", "note": "Waiting on vendor contract. Post vendor comms updates."},
    "fleetio": {"id": "MAAAAAEICX2_", "title": "FleetIO", "note": "Approved 4/17. Post integration progress."},
    "paylocity": {"id": "MAAAAAEICX3c", "title": "Paylocity", "note": "Future. No updates yet."},
    "hubspot": {"id": "MAAAAAEICX3u", "title": "HubSpot", "note": "Deprioritized per Michael 4/6."},
}

# AIC business card (management fees, non-Cerebro AIC updates)
WRIKE_AIC_CARD = {"id": "IEAGTFSIKRSDDOEL", "title": "AIC Related", "note": "AIC management fees and business. NOT for Cerebro data integration."}


@mcp.tool()
def wrike_update(vendor: str = "", summary: str = "") -> dict:
    """Where and how to post a stakeholder update on Wrike.

    Call this BEFORE posting to Wrike. Returns:
    - Which card to update (task ID + title)
    - The format Michael expects (date + bullets)
    - What NOT to do (don't create tasks, don't use AIC Related for Cerebro)

    Args:
        vendor: Which vendor this update is about (sage, fleetio, navusoft, etc.)
                Leave empty for general Cerebro updates.
        summary: What you want to say (optional — for format preview)
    """
    import datetime

    date_str = datetime.date.today().strftime("%-m.%-d")

    card = WRIKE_CEREBRO_CARDS.get(vendor.lower(), WRIKE_CEREBRO_CARDS["cerebro"])

    result = {
        "card": card,
        "tool": "mcp__wrike__add_comment",
        "tool_args": {
            "taskId": card["id"],
            "plainText": False,  # HTML format — matches Michael's existing style
        },
        "format": {
            "structure": (
                "1. BLUF (Bottom Line Up Front) — bold, one line: what Michael needs to know or do\n"
                "2. Details — bullet list with context\n"
                "3. Link to GitHub if relevant"
            ),
            "html_template": (
                '<b>{date} — {bluf}</b><br />'
                '<ul>'
                '<li>{detail_1}</li>'
                '<li>{detail_2}</li>'
                '</ul>'
                '{optional_link}'
            ),
            "example_html": (
                f'<b>{date_str} — Need Fleetio admin to generate API key (2 min).</b><br />'
                '<ul>'
                '<li>Michael approved Fleetio integration. API access is self-service from the Fleetio dashboard.</li>'
                '<li>Rate limits confirmed: Professional 50 req/min, Premium 250 req/min.</li>'
                '<li>Connector build is 1-2 days once we have credentials.</li>'
                '</ul>'
                'Full steps: <a href="https://github.com/greenmark-waste-solutions/cerebro/issues/77">cerebro#77</a>'
            ),
            "html_reference": {
                "bold": "<b>text</b>",
                "line_break": "<br />",
                "bullet_list": "<ul><li>item</li></ul>",
                "link": '<a href="URL">text</a>',
                "mention_user": '<a class="stream-user-id avatar" rel="USER_ID">@Name</a>',
            },
            "known_user_ids": {
                "Michael Nguyen": "KUAU4MMG",
                "Alex Kaye": "KUAVODQT",
            },
        },
        "rules": [
            "BLUF first — Michael should know the ask or status in the first bold line",
            "NEVER create new Wrike tasks or projects — comment on existing cards only",
            "Use HTML formatting (plainText: false) — bold dates, bullet lists, links",
            "Keep it to 3-5 bullets max. Michael scans these in weekly review.",
            "Write in Daniel's voice — casual, direct, no corporate fluff",
            "Link to GitHub for details (don't dump technical info into Wrike)",
            "Don't post if nothing changed since last comment on this card",
            f"AIC Related ({WRIKE_AIC_CARD['id']}) is for AIC business (fees), NOT Cerebro tech updates",
        ],
        "all_cards": {k: v["title"] for k, v in WRIKE_CEREBRO_CARDS.items()},
    }

    if summary:
        result["draft_html"] = (
            f'<b>{date_str} — {summary}</b><br />'
        )

    return result


# ── Self-improvement ───────────────────────────────────


@mcp.tool()
def improve_builder() -> dict:
    """The builder builds the builder.

    Call at adjourn time. Reads the last 5 session logs, compiles them
    into a friction report, and returns a prompt for Rhea to analyze.

    The agent then calls mcp__rhea__rhea_challenge with the returned
    prompt. Rhea reasons about what tooling gap caused the most friction
    and proposes a concrete improvement the builder author didn't anticipate.

    This is NOT keyword matching — it's adversarial reasoning over real
    session history. The improvement should be novel, not obvious.
    """
    from .ceremony import _load_session_history

    sessions = _load_session_history(last_n=5)
    if len(sessions) < 2:
        return {"proposal": None, "reason": "Not enough session history to analyze (need 2+)"}

    # Compile session digest for Rhea
    digest_parts = []
    for s in sessions:
        summary = s.get("summary") or "(no summary)"
        actions = s.get("next_actions") or []
        learnings = s.get("learnings_added") or []

        digest_parts.append(
            f"Session {s.get('id', '?')}:\n"
            f"  Summary: {summary}\n"
            f"  Next actions: {actions}\n"
            f"  Learnings added: {[l.get('lesson', '')[:80] for l in learnings]}"
        )

    digest = "\n\n".join(digest_parts)

    # Build the current tool inventory
    tool_list = [
        "convene() — roll call + C-01 through C-11 checks",
        "adjourn() — session close + minutes",
        "whats_next() — impact-scored task ordering",
        "check_mission() — alignment check for proposed work",
        "wrike_update() — tells agent where/how to post stakeholder updates",
        "improve_builder() — this tool (self-improvement)",
        "how_to_ship() — ceremony for code changes",
        "pre_advance_checks() — checks before completing a task",
        "which_forge() — routes work to the right MCP",
        "ariadne / ariadne_learn — serendipity + learning from mistakes",
        "docs() — knowledge base search",
    ]

    rhea_prompt = f"""You are reviewing the cerebro-builder MCP's effectiveness as an agent orchestrator.

Below are the last {len(sessions)} session logs from a beepboop loop. Each session is one convene→execute→adjourn cycle.

SESSION HISTORY:
{digest}

CURRENT BUILDER TOOLS:
{chr(10).join(f'  - {t}' for t in tool_list)}

QUESTION: What is the single biggest tooling gap that caused friction across these sessions?

Rules:
- Don't propose tools that already exist (check the tool list above)
- The gap must be evidenced by something that actually went wrong or was harder than it should have been
- Propose ONE concrete tool: name, what it does, what file it goes in, and WHY it would have prevented the friction you identified
- "Concrete" means: function signature, 2-3 sentence behavior description, which session(s) it would have helped
- Don't propose vague improvements like "better monitoring" — propose a specific callable tool
- Novel means: something the builder's author wouldn't have thought to build. The obvious stuff is already there."""

    return {
        "sessions_analyzed": len(sessions),
        "digest_preview": digest[:500] + "..." if len(digest) > 500 else digest,
        "rhea_prompt": rhea_prompt,
        "instruction": (
            "Call mcp__rhea__rhea_challenge with this rhea_prompt. "
            "Stakes: medium. The Dreamer proposes improvements, the Doubter "
            "challenges whether they'd actually help, the Decider picks one. "
            "Then build whatever the Decider approves — or explain why not."
        ),
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

    # Map repos to cerebro-docs workflows
    docs_workflows = {
        "data-daemon": "deploy_data_daemon",
        "cerebro": "ship_to_staging",
        "cerebro-migrations": "apply_migration",
    }
    docs_workflow = docs_workflows.get(repo)

    return {
        "repo": repo,
        "tier": tier,
        "steps": steps,
        "deploy_order": deploy_context,
        "environments": env_info,
        "prerequisite": (
            f"BEFORE EXECUTING: call mcp__cerebro-docs__workflow(name='{docs_workflow}') "
            f"to load the full deployment procedure with gotchas and failure modes."
        ) if docs_workflow else None,
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
        "prerequisite": (
            "BEFORE EXECUTING: call mcp__cerebro-docs__workflow(name='apply_migration') "
            "to load the full migration procedure. NEVER apply DDL via raw psql."
        ),
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


# ── Documentation — searchable builder knowledge ──────


@mcp.tool()
def docs(query: str = "") -> dict:
    """Search the builder's knowledge base.

    Two modes — like a book:
      docs("")              Table of Contents — browse all docs by title
      docs("project board") Index — find where a concept is explained

    Use this when you need to understand how systems relate, what the
    ceremony requires, who sees what, or how information flows.
    Results include references (line numbers where terms appear).

    Args:
        query: Keywords to search (title, tags, content). Empty = list all.
    """
    from .docs import search_docs, list_docs

    if not query.strip():
        # Table of Contents
        all_docs = list_docs()
        return {
            "mode": "table_of_contents",
            "count": len(all_docs),
            "docs": all_docs,
            "usage": "Pass keywords to search the index: docs('project board'), docs('hierarchy'), etc.",
        }

    # Index — search by keyword
    results = search_docs(query)
    if not results:
        all_docs = list_docs()
        return {
            "mode": "index",
            "query": query,
            "count": 0,
            "results": [],
            "table_of_contents": all_docs,
            "hint": f"No docs matched '{query}'. Try broader terms.",
        }

    return {
        "mode": "index",
        "query": query,
        "count": len(results),
        "results": results,
    }


# ── Session planning — 6-phase template ──────────────────


@mcp.tool()
def plan_session(
    scope: str,
    budget_hours: float = 4.0,
    build_a_goal: str = "",
    build_a_steps: list[str] | None = None,
    build_a_gate: str = "",
    build_a_kill: str = "",
    build_a_artifact: str = "",
    build_b_goal: str = "",
    build_b_steps: list[str] | None = None,
    build_b_gate: str = "",
    build_b_kill: str = "",
    build_b_artifact: str = "",
    observation_query: str = "",
    render_markdown: bool = False,
) -> dict:
    """Produce a 6-phase session plan bound to a specific scope + budget.

    This codifies the framework derived from session-29's failure modes:
    observation before construction, one scope per session, kill criteria
    per phase, single atomic deploy, non-negotiable /land at phase 5.

    The mayor does NOT execute the plan — it returns structure. The agent
    writes the plan to .ike/sessions/<date>.md and checks off phases as
    they complete. Enforcement is by nudge (future phase_gate tool),
    never by block.

    Phases:
      0. Pre-flight       — contracts, bookmark, env, health
      1. Observation      — verify assumption with real data
      2. Build A          — first scoped deliverable
      3. Build B          — second scoped deliverable
      4. Deploy           — atomic deploy + live verify
      5. Land             — trilogy capture, /land, bookmark

    Args:
        scope: One-sentence statement of what this session delivers.
               Multi-goal scopes trigger a warning.
        budget_hours: Total budget. Template default sums to ~3.5h.
               <3h scales phases down; >5h warns (split session).
        build_a_goal / steps / gate / kill / artifact: Override Phase 2
               content. All optional — unset phases get template defaults.
        build_b_goal / steps / gate / kill / artifact: Same for Phase 3.
        observation_query: Optional SQL or command string captured
               verbatim for Phase 1 so there's no ambiguity.
        render_markdown: If true, include the plan as markdown in the
               response under key `markdown` — ready to paste into
               .ike/sessions/<date>.md.
    """
    from .planning import plan_session as make_plan, render_plan_markdown

    build_a = None
    if any([build_a_goal, build_a_steps, build_a_gate, build_a_kill, build_a_artifact]):
        build_a = {
            k: v for k, v in [
                ("goal", build_a_goal),
                ("steps", build_a_steps),
                ("gate", build_a_gate),
                ("kill", build_a_kill),
                ("artifact", build_a_artifact),
            ] if v
        }

    build_b = None
    if any([build_b_goal, build_b_steps, build_b_gate, build_b_kill, build_b_artifact]):
        build_b = {
            k: v for k, v in [
                ("goal", build_b_goal),
                ("steps", build_b_steps),
                ("gate", build_b_gate),
                ("kill", build_b_kill),
                ("artifact", build_b_artifact),
            ] if v
        }

    plan = make_plan(
        scope=scope,
        budget_hours=budget_hours,
        build_a=build_a,
        build_b=build_b,
        observation_query=observation_query or None,
    )

    if render_markdown and "error" not in plan:
        plan = {**plan, "markdown": render_plan_markdown(plan)}

    return plan
