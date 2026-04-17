"""Builder ceremony — convene and adjourn.

The mayor calls sessions to order and closes them with minutes.
Not the cockpit /takeoff and /land — those are for the pilot.
This is for the builder's own coherence.

Convene: roll call before the mayor starts directing work.
Adjourn: minutes recorded, gavel down.

Session log: cerebro-builder-mcp/sessions/ — one JSON per session.
Persists across context clears. The builder's institutional memory.
"""

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .mission import get_current_milestone, get_next_tasks, _read_ike_tasks, MISSION, GUARDRAILS

SESSIONS_DIR = Path(__file__).parent.parent / "sessions"
LEARNINGS_PATH = Path(__file__).parent.parent / "learnings.json"
PERSONAS_DIR = Path(__file__).parent.parent / "personas"


def _session_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _latest_session() -> dict | None:
    """Read the most recent session log."""
    if not SESSIONS_DIR.exists():
        return None
    files = sorted(SESSIONS_DIR.glob("*.json"), reverse=True)
    if not files:
        return None
    try:
        with open(files[0]) as f:
            return json.load(f)
    except Exception:
        return None


def _load_session_history(last_n: int = 5) -> list[dict]:
    """Load the last N completed sessions (those with adjourned_at)."""
    if not SESSIONS_DIR.exists():
        return []
    files = sorted(SESSIONS_DIR.glob("*.json"), reverse=True)
    sessions = []
    for f in files[:last_n + 2]:
        try:
            with open(f) as fh:
                s = json.load(fh)
            if s.get("adjourned_at"):
                sessions.append(s)
            if len(sessions) >= last_n:
                break
        except Exception:
            continue
    return sessions


def _write_session(session: dict):
    """Write a session log entry."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = SESSIONS_DIR / f"{session['id']}.json"
    with open(path, "w") as f:
        json.dump(session, f, indent=2)


# ── Convene Checklist ───────────────────────────────────

CONVENE_CHECKS = [
    {"id": "C-01", "check": "Ike state is current", "automated": True},
    {"id": "C-02", "check": "Learnings are loaded", "automated": True},
    {"id": "C-03", "check": "Personas are loaded", "automated": True},
    {"id": "C-04", "check": "Git is clean or changes are understood", "automated": True},
    {"id": "C-05", "check": "Current milestone is identified", "automated": True},
    {"id": "C-06", "check": "Last session's next_actions are accounted for", "automated": True},
    {"id": "C-07", "check": "Database state matches expectations", "automated": True},
    {"id": "C-08", "check": "No open PRs blocking the critical path", "automated": True},
    {"id": "C-09", "check": "Mission alignment — what are we here to do?", "automated": True},
    {"id": "C-10", "check": "What are you avoiding?", "automated": True},
    {"id": "C-11", "check": "Comfort-zone detection", "automated": True},
]

ADJOURN_CHECKS = [
    {"id": "A-01", "check": "All work is committed and pushed", "automated": True},
    {"id": "A-02", "check": "Ike state reflects what was accomplished", "automated": True},
    {"id": "A-03", "check": "Learnings from this session are saved", "automated": False,
     "note": "Did anything go wrong or almost go wrong?",
     "fix": "Call ariadne_learn() for each lesson."},
    {"id": "A-04", "check": "PRs are opened for completed work", "automated": False,
     "note": "Code committed but no PR = invisible work.",
     "fix": "Open PRs with Closes #N."},
    {"id": "A-05", "check": "Migration state is consistent", "automated": False,
     "note": "If applied manually, is it also in the PR?",
     "fix": "Ensure migration file matches what's on the database."},
    {"id": "A-06", "check": "Next actions are concrete", "automated": False,
     "note": "Can the next convene start without context?",
     "fix": "Write specific next_actions, not vague goals."},
    {"id": "A-07", "check": "Stakeholders updated if work is visible", "automated": False,
     "note": "Did we ship something Michael/Alex would see?",
     "fix": "Update Wrike in Daniel's voice."},
    {"id": "A-08", "check": "Personas updated if calibration changed", "automated": False,
     "note": "Did Rhea hedge? Did Ariadne miss? Did the mayor drift?",
     "fix": "Update the relevant persona JSON."},
]


CRITICAL_PATH_REPOS = ["cerebro", "cerebro-migrations", "data-daemon"]


def _check_database_state() -> dict:
    """C-07: Query sage_bronze row counts via psql."""
    db_url = os.environ.get("STAGING_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        return {"status": "skip", "detail": "No DATABASE_URL — cannot check sage_bronze"}

    query = (
        "SELECT table_name, n_live_tup AS row_count "
        "FROM pg_stat_user_tables "
        "WHERE schemaname = 'sage_bronze' "
        "ORDER BY table_name;"
    )
    try:
        r = subprocess.run(
            ["psql", db_url, "-t", "-A", "-F", ",", "-c", query],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return {"status": "warn", "detail": f"psql error: {r.stderr.strip()[:120]}"}

        rows = [line.strip() for line in r.stdout.strip().split("\n") if line.strip()]
        if not rows:
            return {"status": "warn", "detail": "sage_bronze: no tables found (empty or stats not updated)"}

        tables = {}
        total = 0
        for row in rows:
            parts = row.split(",", 1)
            if len(parts) == 2:
                tables[parts[0]] = int(parts[1])
                total += int(parts[1])

        return {
            "status": "pass",
            "detail": f"sage_bronze: {len(tables)} tables, {total:,} total rows",
            "tables": tables,
        }
    except subprocess.TimeoutExpired:
        return {"status": "warn", "detail": "psql timed out after 10s"}
    except Exception as e:
        return {"status": "warn", "detail": f"DB check failed: {str(e)[:100]}"}


def _check_mission_alignment() -> dict:
    """C-09: Surface mission, milestone progress, and guardrails.

    Forces the agent to see the end goal every single convene.
    Not a pass/fail — always 'pass' with the mission as detail,
    so the agent can't skip it or treat it as noise.
    """
    ms = get_current_milestone()
    tasks = get_next_tasks()
    done_count = len([t for t in _read_ike_tasks() if t.get("in_completed")])
    open_count = len(tasks)

    ms_title = ms.get("title", "unknown") if ms else "All milestones complete"

    return {
        "status": "pass",
        "detail": f"MISSION: {MISSION['statement']}",
        "milestone": ms_title,
        "progress": f"{done_count} done, {open_count} open",
        "north_star": MISSION["north_star"],
        "guardrail_tests": [g["test"] for g in GUARDRAILS],
        "directive": (
            "Every task this session must advance this mission. "
            "If the top whats_next task is infrastructure, ask: "
            "does it unblock the dashboard for Monday? If not, skip it."
        ),
    }


def _check_avoidance() -> dict:
    """C-10: Which hard tasks have you seen the most cycles without touching?

    Scans session history for tasks that appear in next_actions repeatedly
    but never show up in summaries as completed. These are the tasks the
    agent keeps deferring — name them so avoidance is visible.
    """
    sessions = _load_session_history(last_n=10)
    if len(sessions) < 2:
        return {"status": "pass", "detail": "Not enough history to detect avoidance"}

    # Count how many sessions each task appeared in next_actions
    task_mentions = {}  # task fragment → count of sessions mentioning it
    task_completed = set()  # task fragments that appeared in a summary as done

    for s in sessions:
        summary = (s.get("summary") or "").lower()
        next_actions = s.get("next_actions") or []

        for action in next_actions:
            # Normalize: extract TASK-NNNN if present, else use first 60 chars
            key = action.strip()[:60].lower()
            import re
            task_match = re.search(r"task-\d{4}", action, re.IGNORECASE)
            if task_match:
                key = task_match.group(0).lower()

            task_mentions[key] = task_mentions.get(key, 0) + 1

            # Check if this task was completed in any summary
            if key in summary or "done" in summary and key in summary:
                task_completed.add(key)

    # Find tasks mentioned 3+ times but never completed
    avoided = [
        {"task": k, "sessions_deferred": v}
        for k, v in sorted(task_mentions.items(), key=lambda x: -x[1])
        if v >= 3 and k not in task_completed
    ]

    if avoided:
        return {
            "status": "fail",
            "detail": f"AVOIDANCE DETECTED: {len(avoided)} task(s) deferred 3+ cycles without progress",
            "avoided_tasks": avoided[:5],
            "directive": (
                "You have been deferring these tasks. Before doing anything else: "
                "pick the hardest one, decompose it into what you CAN do right now, "
                "and make partial progress. Do not fall back to easy work."
            ),
        }

    # Check for tasks deferred 2 times (warning)
    warning = [k for k, v in task_mentions.items() if v >= 2 and k not in task_completed]
    if warning:
        return {
            "status": "warn",
            "detail": f"{len(warning)} task(s) deferred 2 cycles — approaching avoidance threshold",
            "watch_list": warning[:5],
        }

    return {"status": "pass", "detail": "No avoidance pattern detected"}


def _check_comfort_zone() -> dict:
    """C-11: Are you repeating the same type of work cycle after cycle?

    Classifies recent session summaries by work category and flags
    when 3+ consecutive sessions are the same category.
    Merging PRs is not the mission. Building is.
    """
    sessions = _load_session_history(last_n=5)
    if len(sessions) < 3:
        return {"status": "pass", "detail": "Not enough history for comfort-zone detection"}

    CATEGORIES = {
        "merge": ["merge", "dependabot", "bump", "pr #"],
        "ci": ["ci", "workflow", "pipeline", "github action"],
        "docs": ["readme", "docs", "documentation", "claude.md"],
        "governance": ["settings.yml", "adr", "tier", "codeowners"],
        "infrastructure": ["hook", "ceremony", "mcp server", "refactor"],
        "mission": ["sage", "dashboard", "financial", "revenue", "parity", "verify", "live badge"],
    }

    def classify(summary: str) -> str:
        s = summary.lower()
        scores = {}
        for cat, keywords in CATEGORIES.items():
            scores[cat] = sum(1 for kw in keywords if kw in s)
        if not any(scores.values()):
            return "unknown"
        return max(scores, key=scores.get)

    recent = [classify(s.get("summary") or "") for s in sessions[:5]]

    # Check for 3+ consecutive same category (most recent first)
    if len(recent) >= 3 and recent[0] == recent[1] == recent[2] and recent[0] != "mission":
        return {
            "status": "fail",
            "detail": f"COMFORT ZONE: Last 3 sessions were all '{recent[0]}' work",
            "recent_categories": recent,
            "directive": (
                f"You've done '{recent[0]}' work 3 sessions in a row. "
                "That's a comfort pattern. Switch to mission-critical work NOW. "
                "What's the hardest open task that advances the dashboard?"
            ),
        }

    # Check for 2 consecutive non-mission
    if len(recent) >= 2 and recent[0] == recent[1] and recent[0] != "mission":
        return {
            "status": "warn",
            "detail": f"2 consecutive '{recent[0]}' sessions — one more triggers comfort-zone block",
            "recent_categories": recent,
        }

    return {
        "status": "pass",
        "detail": f"Work variety OK: {recent[:3]}",
        "recent_categories": recent,
    }


def _check_blocking_prs() -> dict:
    """C-08: Check critical-path repos for open PRs via gh CLI."""
    try:
        blocking = []
        all_prs = []
        for repo in CRITICAL_PATH_REPOS:
            full_repo = f"greenmark-waste-solutions/{repo}"
            r = subprocess.run(
                ["gh", "pr", "list", "--repo", full_repo,
                 "--state", "open", "--json", "number,title,statusCheckRollup,url"],
                capture_output=True, text=True, timeout=15,
            )
            if r.returncode != 0:
                continue
            prs = json.loads(r.stdout) if r.stdout.strip() else []
            for pr in prs:
                checks = pr.get("statusCheckRollup", []) or []
                failing = [c for c in checks if c.get("conclusion") == "FAILURE"]
                pr_info = {
                    "repo": repo,
                    "number": pr["number"],
                    "title": pr["title"],
                    "url": pr.get("url", ""),
                    "ci_failing": len(failing) > 0,
                    "failures": [c.get("name", "?") for c in failing],
                }
                all_prs.append(pr_info)
                if failing:
                    blocking.append(pr_info)

        if blocking:
            return {
                "status": "warn",
                "detail": f"{len(blocking)} PR(s) with failing CI on critical-path repos",
                "blocking_prs": blocking,
                "all_critical_prs": all_prs,
            }
        return {
            "status": "pass",
            "detail": f"{len(all_prs)} open PR(s) on critical-path repos, all CI green",
            "all_critical_prs": all_prs,
        }
    except subprocess.TimeoutExpired:
        return {"status": "warn", "detail": "gh CLI timed out"}
    except Exception as e:
        return {"status": "warn", "detail": f"PR check failed: {str(e)[:100]}"}


def run_convene() -> dict:
    """The mayor calls the session to order."""
    results = []
    last_session = _latest_session()

    for check in CONVENE_CHECKS:
        result = {"id": check["id"], "check": check["check"], "automated": check["automated"]}

        if not check["automated"]:
            result["status"] = "manual"
            result["note"] = check.get("note", "")
            results.append(result)
            continue

        try:
            if check["id"] == "C-01":
                ms = get_current_milestone()
                tasks = get_next_tasks()
                result["status"] = "pass"
                result["detail"] = f"Milestone: {ms.get('title') if ms else 'all done'}, {len(tasks)} open tasks"

            elif check["id"] == "C-02":
                if LEARNINGS_PATH.exists():
                    with open(LEARNINGS_PATH) as f:
                        count = len(json.load(f))
                    result["status"] = "pass"
                    result["detail"] = f"{count} learnings"
                else:
                    result["status"] = "fail"
                    result["detail"] = "learnings.json missing"

            elif check["id"] == "C-03":
                expected = ["ariadne.json", "rhea.json", "mayor.json"]
                found = [f for f in expected if (PERSONAS_DIR / f).exists()]
                result["status"] = "pass" if len(found) == 3 else "fail"
                result["detail"] = f"{len(found)}/3 personas"

            elif check["id"] == "C-04":
                r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5,
                                   cwd="/home/dev/repos/greenmark-cockpit")
                dirty = len([l for l in r.stdout.strip().split("\n") if l.strip()])
                result["status"] = "pass" if dirty == 0 else "warn"
                result["detail"] = f"{dirty} dirty files" if dirty else "clean"

            elif check["id"] == "C-05":
                ms = get_current_milestone()
                result["status"] = "pass" if ms else "done"
                result["detail"] = ms.get("title") if ms else "All milestones complete"

            elif check["id"] == "C-06":
                if last_session and last_session.get("next_actions"):
                    carried = last_session["next_actions"]
                    result["status"] = "pass"
                    result["detail"] = f"{len(carried)} actions from last session"
                    result["last_session_actions"] = carried
                elif last_session:
                    result["status"] = "warn"
                    result["detail"] = "Last session had no next_actions"
                else:
                    result["status"] = "pass"
                    result["detail"] = "First session — no prior log"

            elif check["id"] == "C-07":
                result.update(_check_database_state())

            elif check["id"] == "C-08":
                result.update(_check_blocking_prs())

            elif check["id"] == "C-09":
                result.update(_check_mission_alignment())

            elif check["id"] == "C-10":
                result.update(_check_avoidance())

            elif check["id"] == "C-11":
                result.update(_check_comfort_zone())

            else:
                result["status"] = "skip"

        except Exception as e:
            result["status"] = "error"
            result["detail"] = str(e)[:100]

        results.append(result)

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")

    # Write convene record
    session_id = _session_id()
    session = {
        "id": session_id,
        "convened_at": datetime.now(timezone.utc).isoformat(),
        "adjourned_at": None,
        "milestone": get_current_milestone().get("title") if get_current_milestone() else None,
        "convene_results": results,
        "summary": None,
        "next_actions": None,
        "tasks_completed": [],
        "learnings_added": [],
    }
    _write_session(session)

    return {
        "phase": "convene",
        "session_id": session_id,
        "results": results,
        "passed": passed,
        "failed": failed,
        "ready": failed == 0,
        "last_session": {
            "id": last_session["id"],
            "summary": last_session.get("summary"),
            "next_actions": last_session.get("next_actions"),
        } if last_session else None,
        "message": (
            f"Session convened. {passed} checks passed."
            + (f" Last session: {last_session['id']}" if last_session else " First session.")
        ) if failed == 0 else f"Convene blocked. {failed} checks failed.",
        "docs": _count_docs(),
        "serendipity": _serendipity_stats(last_session) if last_session else None,
    }


def _serendipity_stats(session: dict) -> dict | None:
    """Summarize doc surfacing from last session for the convene report."""
    docs_surfaced = session.get("docs_surfaced", [])
    if not docs_surfaced:
        return None

    total = len(docs_surfaced)
    read = sum(1 for d in docs_surfaced if d.get("read"))
    graduated = sum(1 for d in docs_surfaced if d.get("graduated"))

    return {
        "last_session_docs_surfaced": total,
        "read": read,
        "graduated_to_learnings": graduated,
        "ignored": total - read,
    }


def _count_docs() -> dict:
    """Surface docs availability so the agent knows to use docs()."""
    from .docs import list_docs
    all_docs = list_docs()
    return {
        "count": len(all_docs),
        "titles": [d["title"] for d in all_docs],
        "hint": "Use docs('keyword') to search, docs('') for table of contents.",
    }


def run_adjourn(summary: str = "", next_actions: list[str] | None = None) -> dict:
    """The mayor closes the session. Minutes recorded."""
    results = []

    for check in ADJOURN_CHECKS:
        result = {"id": check["id"], "check": check["check"], "automated": check["automated"]}

        if not check["automated"]:
            result["status"] = "manual"
            result["note"] = check.get("note", "")
            result["fix"] = check.get("fix", "")
            results.append(result)
            continue

        try:
            if check["id"] == "A-01":
                r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5,
                                   cwd="/home/dev/repos/greenmark-cockpit")
                dirty = len([l for l in r.stdout.strip().split("\n") if l.strip()])
                result["status"] = "pass" if dirty == 0 else "fail"
                result["detail"] = f"{dirty} uncommitted files" if dirty else "clean"
                result["fix"] = "Commit and push before adjourning." if dirty else None

            elif check["id"] == "A-02":
                tasks = get_next_tasks()
                in_progress = [t for t in tasks if t.get("status", "").lower() in ("in progress", "in_progress")]
                result["status"] = "warn" if in_progress else "pass"
                result["detail"] = f"{len(in_progress)} tasks still in-progress" if in_progress else "all tasks at rest"

            else:
                result["status"] = "skip"

        except Exception as e:
            result["status"] = "error"
            result["detail"] = str(e)[:100]

        results.append(result)

    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    manual = sum(1 for r in results if r["status"] == "manual")

    # Update the session log with adjourn data
    last = _latest_session()
    if last and not last.get("adjourned_at"):
        last["adjourned_at"] = datetime.now(timezone.utc).isoformat()
        last["summary"] = summary or "No summary provided."
        last["next_actions"] = next_actions or []
        last["adjourn_results"] = results

        # Populate fields that always existed but were never filled
        from .ariadne import get_surfaced_docs, _load_learnings

        # What docs were surfaced and what happened to them
        last["docs_surfaced"] = get_surfaced_docs()

        # What learnings were added this session (diff convene count vs now)
        current_learnings = _load_learnings()
        convene_count = 0
        for cr in last.get("convene_results", []):
            if cr.get("id") == "C-02" and "detail" in cr:
                try:
                    convene_count = int(cr["detail"].split()[0])
                except (ValueError, IndexError):
                    pass
        if len(current_learnings) > convene_count:
            last["learnings_added"] = [
                {"id": l["id"], "lesson": l["lesson"][:80]}
                for l in current_learnings[convene_count:]
            ]

        _write_session(last)

    # Surface existing learnings so the agent can avoid duplicates
    from .ariadne import _load_learnings
    existing = _load_learnings()

    return {
        "phase": "adjourn",
        "results": results,
        "passed": passed,
        "failed": failed,
        "manual_checks": manual,
        "clear_to_adjourn": failed == 0,
        "message": (
            f"Session adjourned. {passed} passed, {manual} manual reminders."
            if failed == 0
            else f"Adjourn blocked. {failed} items need attention."
        ),
        "manual_reminders": [
            {"id": r["id"], "check": r["check"], "note": r.get("note", ""), "fix": r.get("fix", "")}
            for r in results if r["status"] == "manual"
        ],
        "reflect": {
            "existing_learnings": [
                {"id": l["id"], "lesson": l["lesson"]} for l in existing
            ],
            "instruction": (
                "You just lived through this session. If you learned something novel — "
                "something not already in the list above — call ariadne_learn(). If not, move on."
            ),
        },
        "minutes": {
            "summary": summary,
            "next_actions": next_actions,
        },
        "clear_context": True,
        "continuity": (
            "Session minutes are saved. Next convene() reads them. "
            "Clear context now — the builder doesn't need chat history. "
            "If you need prior context, read the session log or use claude-resume."
        ),
    }
