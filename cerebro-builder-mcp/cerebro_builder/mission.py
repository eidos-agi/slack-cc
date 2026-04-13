"""Mission contract — reads live state from ike.md, keeps guardrails local.

The mayor doesn't track milestones or tasks — ike does that.
The mayor holds the mission statement, guardrails, and judgment about
whether proposed work is aligned. It reads ike to know what's current.
"""

import subprocess
import json


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
    {
        "rule": "Work not on the project board doesn't exist",
        "source": "Session 22 retrospective, Daniel directive",
        "test": "Did I create_work() before writing code? Is the issue on Project #1? Will the PR close it?",
    },
]

# ── Ike integration ─────────────────────────────────────────
# The builder reads ike's state to know what's current.

IKE_PROJECT_PATH = "/home/dev/repos/greenmark-cockpit"


def _read_ike_milestones() -> list[dict]:
    """Parse ike milestone files to get current state."""
    import glob
    import re

    milestones = []
    pattern = f"{IKE_PROJECT_PATH}/.ike/milestones/MS-*.md"
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path) as f:
                content = f.read()

            # Parse frontmatter
            ms = {"path": path, "tasks": []}
            for line in content.split("\n"):
                if line.startswith("title:"):
                    ms["title"] = line.split(":", 1)[1].strip().strip('"')
                elif line.startswith("status:"):
                    ms["status"] = line.split(":", 1)[1].strip().strip('"')
                elif line.startswith("id:") or "MS-" in line.split(":")[0] if ":" in line else False:
                    pass

            # Extract ID from filename
            fname = path.rsplit("/", 1)[-1]
            match = re.search(r"MS-(\d+)", fname)
            if match:
                ms["id"] = f"MS-{match.group(1).zfill(4)}"

            milestones.append(ms)
        except Exception:
            continue

    return milestones


def _read_ike_tasks(status: str | None = None) -> list[dict]:
    """Parse ike task files."""
    import glob
    import re

    tasks = []
    # Active tasks
    for folder in ["tasks", "completed"]:
        pattern = f"{IKE_PROJECT_PATH}/.ike/{folder}/TASK-*.md"
        for path in sorted(glob.glob(pattern)):
            try:
                with open(path) as f:
                    content = f.read()

                task = {"path": path, "in_completed": folder == "completed"}
                in_frontmatter = False
                in_dod = False
                dod_items = []

                for line in content.split("\n"):
                    if line.strip() == "---":
                        in_frontmatter = not in_frontmatter
                        continue
                    if in_frontmatter:
                        if line.startswith("title:"):
                            task["title"] = line.split(":", 1)[1].strip().strip('"')
                        elif line.startswith("status:"):
                            task["status"] = line.split(":", 1)[1].strip().strip('"')
                        elif line.startswith("priority:"):
                            task["priority"] = line.split(":", 1)[1].strip().strip('"')
                        elif line.startswith("milestone:"):
                            task["milestone"] = line.split(":", 1)[1].strip().strip('"')
                    if "definition_of_done:" in line or "## Definition of Done" in line:
                        in_dod = True
                        continue
                    if in_dod and line.strip().startswith("- "):
                        dod_items.append(line.strip()[2:].strip('"'))
                    elif in_dod and not line.strip().startswith("- ") and line.strip() and not line.strip().startswith("#"):
                        in_dod = False

                task["definition_of_done"] = dod_items

                fname = path.rsplit("/", 1)[-1]
                match = re.search(r"TASK-(\d+)", fname)
                if match:
                    task["id"] = f"TASK-{match.group(1).zfill(4)}"

                if status is None or task.get("status", "").lower() == status.lower():
                    tasks.append(task)
            except Exception:
                continue

    return tasks


def get_current_milestone() -> dict | None:
    """Get the first non-done milestone from ike."""
    milestones = _read_ike_milestones()
    for ms in milestones:
        status = ms.get("status", "").lower()
        if status not in ("done", "closed", "completed"):
            return ms
    return None


def get_next_tasks() -> list[dict]:
    """Get the highest-priority open tasks from ike."""
    tasks = _read_ike_tasks()
    open_tasks = [
        t for t in tasks
        if t.get("status", "").lower() in ("to do", "in progress", "in_progress")
        and not t.get("in_completed")
    ]
    # Sort by priority
    priority_order = {"p0": 0, "p1": 1, "high": 1, "p2": 2, "medium": 2, "p3": 3, "low": 3}
    open_tasks.sort(key=lambda t: priority_order.get(t.get("priority", "medium").lower(), 2))
    return open_tasks


# ── Mission check ───────────────────────────────────────────


def mission_check(proposed_task: str) -> dict:
    """Check alignment against ike's current milestone and guardrails."""
    current_ms = get_current_milestone()
    next_tasks = get_next_tasks()

    if not current_ms:
        return {
            "aligned": True,
            "mission": MISSION["statement"],
            "note": "All milestones complete. Free to work on anything.",
        }

    task_lower = proposed_task.lower()
    ms_title = current_ms.get("title", "").lower()

    # Check alignment with current milestone
    ms_keywords = ms_title.split()
    alignment_signals = sum(1 for kw in ms_keywords if len(kw) > 2 and kw in task_lower)

    # Check if matches any open task title
    matches_task = any(
        proposed_task.lower() in t.get("title", "").lower()
        or t.get("title", "").lower() in proposed_task.lower()
        for t in next_tasks[:5]
    )

    is_infrastructure = any(
        kw in task_lower
        for kw in ["refactor", "ci", "hook", "ceremony", "mcp", "tool", "docs", "documentation", "readme"]
    )

    aligned = alignment_signals >= 2 or matches_task
    drifting = is_infrastructure and not aligned

    result = {
        "mission": MISSION["statement"],
        "north_star": MISSION["north_star"],
        "current_milestone": current_ms.get("title"),
        "next_tasks": [t.get("title") for t in next_tasks[:5]],
        "proposed_task": proposed_task,
    }

    if aligned:
        result["aligned"] = True
        result["verdict"] = f"Aligned with {current_ms.get('title', 'current milestone')}. Proceed."
        result["rhea_required"] = False
    elif drifting:
        result["aligned"] = False
        result["verdict"] = (
            f"DRIFT DETECTED. '{proposed_task}' looks like infrastructure work, "
            f"not '{current_ms.get('title')}'. Session 22 lost 8 hours to this pattern."
        )
        result["rhea_required"] = True
        result["rhea_challenge_prompt"] = (
            f"The agent wants to work on: '{proposed_task}'\n"
            f"The current milestone is: {current_ms.get('title')}\n"
            f"The mission is: {MISSION['statement']}\n"
            f"The next ike tasks are: {[t.get('title') for t in next_tasks[:3]]}\n\n"
            f"Is this justified, or is the agent drifting?"
        )
    else:
        result["aligned"] = None
        result["verdict"] = (
            f"Not clearly aligned with '{current_ms.get('title')}'. "
            f"Proceed if justified."
        )
        result["rhea_required"] = False

    return result


def mission_status() -> dict:
    """Full mission status from ike."""
    milestones = _read_ike_milestones()
    next_tasks = get_next_tasks()
    current = get_current_milestone()

    done = [m for m in milestones if m.get("status", "").lower() in ("done", "closed", "completed")]

    return {
        "mission": MISSION,
        "milestones": [{"id": m.get("id"), "title": m.get("title"), "status": m.get("status")} for m in milestones],
        "progress": f"{len(done)}/{len(milestones)}",
        "current": current,
        "next_tasks": [{"id": t.get("id"), "title": t.get("title"), "status": t.get("status")} for t in next_tasks[:5]],
        "guardrails": GUARDRAILS,
    }
