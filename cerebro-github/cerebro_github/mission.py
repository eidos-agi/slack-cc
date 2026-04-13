"""Mission contract — the bigger picture that every session serves.

This is the macro-ceremony. The tools enforce micro-ceremony (issue before PR).
This enforces strategic coherence (is this task advancing the mission?).

Read at takeoff. Checked before work starts. Verified at landing.
"""

from datetime import datetime

# ── The Mission ─────────────────────────────────────────────
# This is what Michael is paying for. Everything else is scaffolding.

MISSION = {
    "statement": (
        "Get real Sage financial data onto the Cerebro dashboard "
        "so Michael and Alex can see their business on Monday morning."
    ),
    "north_star": "Alex's Greenmark_Metrics spreadsheet — populated with real numbers, not mocks.",
    "client": "Michael D. Nguyen (President) and Alex Kaye (CFO)",
    "deadline_context": "Monday morning review — every week. If the dashboard is stale, we failed that week.",
}

# ── The Roadmap ─────────────────────────────────────────────
# Milestones in dependency order. Each one unlocks the next.

MILESTONES = [
    {"id": "M-01", "title": "Plan Sage rebuild", "status": "done", "date": "2026-04-09"},
    {"id": "M-02", "title": "sage_bronze schema on staging", "status": "done", "date": "2026-04-10"},
    {"id": "M-03", "title": "SageIntacctConnector + first extraction", "status": "done", "date": "2026-04-11",
     "note": "Connector merged. Creds set on Railway. Live extraction not yet tested."},
    {"id": "M-04", "title": "sage_silver + sage_gold views", "status": "next", "date": "",
     "note": "Materialized views: bronze → silver (typed) → gold (Alex's layout)."},
    {"id": "M-05", "title": "Excel parity validation", "status": "blocked_by_m04", "date": "",
     "note": "Compare pipeline gold against warp-speed Excel golden fixtures."},
    {"id": "M-06", "title": "Wire Financial dashboard to gold", "status": "blocked_by_m05", "date": "",
     "note": "Replace mock data. This is what Michael sees Monday."},
    {"id": "M-07", "title": "Downgrade warp-speed to validation-only", "status": "blocked_by_m06", "date": ""},
]

# ── Strategic Guardrails ────────────────────────────────────
# These prevent drift. Check before starting any work.

GUARDRAILS = [
    {
        "rule": "Sage pipeline is priority #1",
        "source": "Michael, 2026-04-06 call",
        "test": "Is this task on the M-01→M-07 critical path? If not, why am I doing it?",
    },
    {
        "rule": "Infrastructure is scaffolding, not the product",
        "source": "Session 22 retrospective",
        "test": "Am I building tools or shipping the thing the client sees?",
    },
    {
        "rule": "Wrike stays executive-level, GitHub has the detail",
        "source": "Michael, Wrike cleanup directive",
        "test": "If I'm updating Wrike, is it in Daniel's voice? If I'm in GitHub, is it actionable?",
    },
    {
        "rule": "No AI-generated content for stakeholders",
        "source": "Michael, 2026-04-06 call",
        "test": "Would Michael recognize this as Daniel writing, or as AI writing?",
    },
    {
        "rule": "Alex's spreadsheet is the north star",
        "source": "Michael, 2026-04-06 call",
        "test": "Does the output match Alex's Greenmark_Metrics format?",
    },
]


def mission_check(proposed_task: str) -> dict:
    """Check a proposed task against the mission and guardrails.

    If the task doesn't align with the current milestone, returns a
    Rhea challenge prompt — the agent MUST run adversarial reasoning
    before proceeding with off-mission work.

    Returns alignment assessment + rhea_required flag.
    """
    current = next((m for m in MILESTONES if m["status"] == "next"), None)
    done = [m for m in MILESTONES if m["status"] == "done"]

    if not current:
        return {
            "aligned": True,
            "mission": MISSION["statement"],
            "progress": f"{len(done)}/{len(MILESTONES)}",
            "note": "All milestones complete. Free to work on anything.",
        }

    # Simple heuristic: does the task mention the current milestone's keywords?
    task_lower = proposed_task.lower()
    milestone_keywords = current["title"].lower().split()
    alignment_signals = sum(1 for kw in milestone_keywords if kw in task_lower)

    # Also check if task mentions any milestone ID
    mentions_milestone = any(m["id"].lower() in task_lower for m in MILESTONES)

    # Check against guardrails
    is_infrastructure = any(
        kw in task_lower
        for kw in ["refactor", "ci", "hook", "ceremony", "mcp", "tool", "docs", "documentation", "readme"]
    )

    aligned = alignment_signals >= 2 or mentions_milestone
    drifting = is_infrastructure and not aligned

    result = {
        "aligned": aligned,
        "mission": MISSION["statement"],
        "north_star": MISSION["north_star"],
        "current_milestone": current,
        "progress": f"{len(done)}/{len(MILESTONES)}",
        "proposed_task": proposed_task,
    }

    if aligned:
        result["verdict"] = f"Aligned with {current['id']}: {current['title']}. Proceed."
        result["rhea_required"] = False
    elif drifting:
        result["verdict"] = (
            f"DRIFT DETECTED. '{proposed_task}' looks like infrastructure work, "
            f"not {current['id']}: {current['title']}. "
            f"Session 22 lost 8 hours to this pattern."
        )
        result["rhea_required"] = True
        result["rhea_challenge_prompt"] = (
            f"The agent wants to work on: '{proposed_task}'\n"
            f"The current milestone is {current['id']}: {current['title']}\n"
            f"The mission is: {MISSION['statement']}\n"
            f"The north star is: {MISSION['north_star']}\n\n"
            f"Session 22 spent 8 hours on infrastructure instead of the Sage pipeline. "
            f"Is this task justified, or is the agent drifting again? "
            f"If justified, what's the concrete dependency that makes this necessary before {current['id']}? "
            f"If not, what should the agent do instead?"
        )
        result["guardrail_violations"] = [
            g["test"] for g in GUARDRAILS
            if "infrastructure" in g["rule"].lower() or "priority" in g["rule"].lower()
        ]
    else:
        result["verdict"] = (
            f"Not clearly aligned with {current['id']}: {current['title']}. "
            f"Proceed if you can justify it, but check: is this blocking {current['id']}?"
        )
        result["rhea_required"] = False

    return result


def mission_status() -> dict:
    """Full mission status — for takeoff and landing."""
    current = next((m for m in MILESTONES if m["status"] == "next"), None)
    done = [m for m in MILESTONES if m["status"] == "done"]

    return {
        "mission": MISSION,
        "milestones": MILESTONES,
        "progress": f"{len(done)}/{len(MILESTONES)}",
        "current": current,
        "guardrails": GUARDRAILS,
        "drift_warning": (
            "Session 22 spent 8 hours on infrastructure while Sage pipeline sat untouched. "
            "Check the guardrails before starting work. Ask: is this M-04?"
        ),
    }
