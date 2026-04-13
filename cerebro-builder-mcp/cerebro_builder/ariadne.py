"""Ariadne — "Are we even doing the right thing?"

Named for the thread that kept Theseus from getting lost in the labyrinth.
Ariadne has two layers:

Layer 1: Pattern memory — known mistakes loaded from learnings.json.
  Fast, deterministic, grows over time. When something breaks, add it.

Layer 2: Her own mind — reads the full context (mission, topology,
  what's been proven, what hasn't) and reasons about whether the
  approach makes sense for THIS situation. Powered by Rhea.

Layer 1 always runs. Layer 2 runs when Layer 1 finds nothing
(that's when you're most confident and most likely to be wrong
about something new).
"""

import json
import os
import random
from pathlib import Path

from .mission import MISSION, get_current_milestone, get_next_tasks
from .topology import SERVICES, ENVIRONMENTS, DEPLOY_ORDER

# ── Pattern memory ──────────────────────────────────────
# Known mistakes. Loaded from learnings.json. Grows over time.

# Session-scoped tracking: what docs were surfaced and what happened to them.
# Resets per process. No new files — lives in memory.
_surfaced_this_session: list[dict] = []

LEARNINGS_PATH = Path(__file__).parent.parent / "learnings.json"
PERSONA_PATH = Path(__file__).parent.parent / "personas" / "ariadne.json"

_DEFAULT_LEARNINGS = [
    {
        "id": "L001",
        "trigger": ["view", "materialized view", "sql view", "create view"],
        "lesson": "SQL views on large JSONB tables recompute on every query. 1.3M GL entries means 1.3M JSON parse ops per SELECT. Use materialized views or ETL-written typed tables instead.",
        "source": "Session 23 — Ariadne caught M-04 before it shipped wrong",
    },
    {
        "id": "L002",
        "trigger": ["supabase", "postgres", "warehouse", "analytics"],
        "lesson": "Supabase is an app database with connection pooling and row-level security. It is not an analytics warehouse. Heavy aggregation queries may hit pool limits or timeouts.",
        "source": "Architecture review — Supabase docs confirm 60s query timeout on free tier",
    },
    {
        "id": "L003",
        "trigger": ["jsonb", "raw_data", "json_extract", "->", "->>"],
        "lesson": "JSONB path extraction at query time doesn't scale. For millions of rows, extract typed columns during ETL and write to properly typed columns. Don't make the dashboard pay for the parse.",
        "source": "Warp-speed proved this — Python extraction + SQLite typed columns is fast",
    },
    {
        "id": "L004",
        "trigger": ["same creds", "same credentials", "both environments", "staging and production"],
        "lesson": "Same credentials on staging and production means staging bugs hit the real vendor API. Check if a sandbox exists. If not, at minimum use a read-only user.",
        "source": "Session 22 — blindly copied warp-speed creds to both Railway environments",
    },
    {
        "id": "L005",
        "trigger": ["golden fixture", "parity", "validation", "compare"],
        "lesson": "Golden fixtures are only golden if they've been confirmed against source of truth. Has Alex verified the warp-speed numbers match her spreadsheet? A parity check against wrong fixtures is worse than no check.",
        "source": "Warp-speed GL Account + Department + Location proven by Alex 2026-04-06",
    },
    {
        "id": "L006",
        "trigger": ["mock", "synthetic", "fake data", "test data"],
        "lesson": "Mocks that pass don't mean production works. The Sage PL04000005 error only appears on real API calls. Test against real systems before declaring done.",
        "source": "Session 21 — mock tests passed but real Sage API returned permission error",
    },
    {
        "id": "L007",
        "trigger": ["scale", "10x", "100x", "million", "bulk"],
        "lesson": "Infrastructure that has never been fired at the target volume is not proven, it's hoped-for. Stress-test with synthetic load before declaring ready for production.",
        "source": "Daniel feedback — stress test before scale jumps",
    },
]


def _load_learnings() -> list[dict]:
    """Load learnings from file, falling back to defaults."""
    if LEARNINGS_PATH.exists():
        try:
            with open(LEARNINGS_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return _DEFAULT_LEARNINGS


def _save_learnings(learnings: list[dict]):
    """Persist learnings to file."""
    with open(LEARNINGS_PATH, "w") as f:
        json.dump(learnings, f, indent=2)


def _check_patterns(text: str) -> list[dict]:
    """Check text against pattern memory. Returns triggered learnings."""
    learnings = _load_learnings()
    text_lower = text.lower()
    triggered = []
    for learning in learnings:
        if any(t in text_lower for t in learning["trigger"]):
            triggered.append(learning)
    return triggered


def _serendipity_rate() -> float:
    """Adaptive serendipity rate based on session history.

    Starts at 0.3. Adjusts based on whether random docs in past sessions
    led to reads or learnings. If the agent ignores them, rate drops.
    If random docs lead to engagement, rate rises.

    No history = 0.3 (current behavior).
    """
    from .ceremony import _load_session_history

    history = _load_session_history(last_n=5)
    if not history:
        return 0.3

    random_surfaced = 0
    random_engaged = 0

    for session in history:
        for doc in session.get("docs_surfaced", []):
            if doc.get("why") == "stumbled_upon":
                random_surfaced += 1
                if doc.get("read") or doc.get("graduated"):
                    random_engaged += 1

    if random_surfaced == 0:
        return 0.3

    engagement = random_engaged / random_surfaced
    return max(0.10, min(0.50, 0.15 + 0.35 * engagement))


def _check_docs(text: str) -> list[dict]:
    """Surface docs the builder didn't ask for — serendipity, not search.

    Humans don't consult a manual before every task. They stumble upon
    insights while working. Sometimes the connection is obvious, sometimes
    it's adjacent. The randomness is the point.

    Returns 0-2 docs: one relevant (if any tags match), and occasionally
    one random doc. The random rate adapts from session engagement history.
    Docs whose insights have graduated to learnings get deprioritized.
    """
    from .docs import list_docs

    text_lower = text.lower()
    all_docs = list_docs()
    if not all_docs:
        return []

    # Context-sensitive graduation filter.
    #
    # A doc's violin can have multiple bodies — relevant in one context,
    # graduated, then relevant again in a new context. Only suppress a doc
    # if the learnings covering its tags are ALSO relevant to the current
    # task. If we're working on something new, old graduations don't apply.
    learnings = _load_learnings()
    active_learning_triggers = set()
    for l in learnings:
        triggers = [t.lower() for t in l.get("trigger", [])]
        # Only count this learning's triggers if the learning itself
        # is relevant to the current task (any trigger matches the text)
        if any(t in text_lower for t in triggers):
            active_learning_triggers.update(triggers)

    # Score docs by task relevance. Graduation demotes but never eliminates —
    # a doc that matched the task is relevant. The question is whether a
    # learning already covers it IN THIS CONTEXT. If so, rank it lower.
    # If not, it's fresh territory (or a second body on the violin).
    scored = []
    for doc in all_docs:
        hits = sum(1 for tag in doc["tags"] if tag.lower() in text_lower)
        if hits > 0:
            covered = sum(1 for tag in doc["tags"] if tag.lower() in active_learning_triggers)
            freshness = len(doc["tags"]) - covered  # uncovered tags = fresh territory
            scored.append((doc, hits, freshness))

    # Sort by relevance first, then by freshness (prefer docs with uncovered territory)
    scored.sort(key=lambda x: (x[1], x[2]), reverse=True)

    surfaced = []

    # One relevant doc (best match, if any)
    if scored:
        best = scored[0]
        entry = {"title": best[0]["title"], "path": best[0]["path"], "why": "relevant"}
        surfaced.append(entry)
        _surfaced_this_session.append({**entry, "read": False, "graduated": False})

    # Adaptive random rate — learns from session history
    if random.random() < _serendipity_rate():
        already = {d["title"] for d in surfaced}
        candidates = [d for d in all_docs if d["title"] not in already]
        if candidates:
            pick = random.choice(candidates)
            entry = {"title": pick["title"], "path": pick["path"], "why": "stumbled_upon"}
            surfaced.append(entry)
            _surfaced_this_session.append({**entry, "read": False, "graduated": False})

    return surfaced


def get_surfaced_docs() -> list[dict]:
    """Return docs surfaced this session (for the session log at adjourn)."""
    return list(_surfaced_this_session)


def mark_doc_read(title: str):
    """Mark a surfaced doc as read. Called by docs() when the agent searches."""
    for tracked in _surfaced_this_session:
        if tracked["title"].lower() == title.lower():
            tracked["read"] = True


# ── Her own mind ────────────────────────────────────────
# Full-context reasoning. Not pattern matching — actual judgment.


def _load_persona() -> list[dict]:
    """Load Ariadne's persona learnings — how she reasons, her blind spots."""
    if PERSONA_PATH.exists():
        try:
            with open(PERSONA_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _build_context_for_reasoning(task_title: str, approach: str) -> str:
    """Build the full context Ariadne needs to reason about the approach."""
    current = get_current_milestone()
    tasks = get_next_tasks()
    persona = _load_persona()

    lines = [
        "ARIADNE CONTEXT — everything she knows about the system:",
        "",
        f"Mission: {MISSION['statement']}",
        f"North star: {MISSION['north_star']}",
        f"Current milestone: {current.get('title') if current else 'None'}",
        "",
        "What's been proven:",
        "  - Warp-speed downloads 1.38M GL entries via Python + Sage XML API",
        "  - Warp-speed transforms in Python and writes to SQLite typed columns",
        "  - GL Account + Department + Location = full P&L dimensionality (Alex confirmed)",
        "  - seed_gold_sage.py produces gold tables that reconcile to Alex's spreadsheet",
        "  - Entity resolution: L0100/L0200 = NTX, L0400 = Hometown",
        "",
        "What hasn't been proven:",
        "  - Whether Supabase Postgres can handle 1.3M-row JSONB queries at dashboard speed",
        "  - Whether the data-daemon SageIntacctConnector works against the real API (PL04000005)",
        "  - Whether SQL views on bronze JSONB scale (never been tested)",
        "",
        "System topology:",
        f"  - Deploy order: {' → '.join(DEPLOY_ORDER)}",
        "  - Bronze schema: sage_bronze in Supabase (7 tables, raw_data JSONB)",
        "  - Dashboard: cerebro Next.js app on Railway, reads from Supabase",
        "  - Pipeline: data-daemon on Railway, writes to Supabase",
        "",
        "Available forges (tools that already solve common problems):",
        "  - connection-forge: vendor API research → structured api-data-model.md",
        "    USE WHEN: researching a new vendor before building a connector",
        "  - refactor-forge: golden fixtures → refactored code → parity tests",
        "    USE WHEN: restructuring code that must maintain behavioral parity",
        "    CRITICAL: have you exported golden fixtures BEFORE changing the code?",
        "  - Eidos trilogy (research.md → visionlog → ike.md):",
        "    USE WHEN: making a decision with consequences (architecture, technology, strategy)",
        "    CRITICAL: is this task an ADR that should go through research.md first?",
        "  - warp-speed forges: SQLite gold → Excel workbook with SUMIFS",
        "    USE WHEN: generating Alex's Greenmark_Metrics spreadsheet",
        "    CRITICAL: warp-speed already HAS the proven transformation — reuse it",
        "  - Rhea: adversarial Dreamer/Doubter/Decider debate",
        "    USE WHEN: high-stakes decision, production merge, or uncertainty",
        "",
        "What the agent wants to do:",
        f"  Task: {task_title}",
        f"  Approach: {approach or '(not specified)'}",
        "",
        "ARIADNE'S QUESTIONS:",
        "  1. Given what's been proven and what hasn't, is this approach sound?",
        "  2. Is there a simpler path that reuses what warp-speed already proved?",
        "  3. What's the assumption most likely to be wrong?",
        "  4. If this ships and it's wrong, what breaks and how hard is the fix?",
        "  5. Would you bet your reputation on this approach working at scale?",
        "  6. Is there a forge that already solves part of this problem?",
        "  7. Should this be an ADR (research.md → visionlog) before it's code?",
    ]

    # Inject persona — her own self-awareness
    if persona:
        lines.append("")
        lines.append("ARIADNE'S SELF-AWARENESS (her known blind spots and calibrations):")
        for p in persona:
            if p.get("type") in ("blind_spot", "calibration"):
                lines.append(f"  - [{p['id']}] {p['observation']}")
                lines.append(f"    Adjustment: {p['adjustment']}")
    return "\n".join(lines)


# ── Public API ──────────────────────────────────────────


def ariadne_challenge(task_title: str, approach: str = "") -> dict:
    """Full Ariadne challenge — patterns + reasoning context.

    Layer 1: Pattern memory (fast, deterministic)
    Layer 2: Reasoning context for Rhea (when patterns don't catch it)
    """
    combined = f"{task_title} {approach}"
    triggered = _check_patterns(combined)
    relevant_docs = _check_docs(combined)

    # Always build reasoning context — Rhea needs it
    reasoning_context = _build_context_for_reasoning(task_title, approach)

    # Inject Rhea's persona so she knows her own blind spots
    rhea_persona_path = Path(__file__).parent.parent / "personas" / "rhea.json"
    if rhea_persona_path.exists():
        try:
            with open(rhea_persona_path) as f:
                rhea_persona = json.load(f)
            reasoning_context += "\n\nRHEA'S SELF-AWARENESS (for the Decider):"
            for rp in rhea_persona:
                if rp.get("type") in ("calibration", "failure_mode"):
                    reasoning_context += f"\n  - [{rp['id']}] {rp['observation']}"
                    reasoning_context += f"\n    Adjustment: {rp['adjustment']}"
        except Exception:
            pass

    # If patterns triggered, include them in the Rhea prompt
    if triggered:
        pattern_section = "\n\nPATTERN MEMORY — known mistakes that match this approach:\n"
        for t in triggered:
            pattern_section += f"\n  [{t['id']}] {t['lesson']}\n  Source: {t['source']}\n"
        reasoning_context += pattern_section

    # Determine if Rhea should run
    # Layer 1 found something: Rhea reviews the specific concern
    # Layer 1 found nothing: Rhea reasons from scratch (more important!)
    rhea_required = True  # Always — that's the point

    result = {
        "task": task_title,
        "approach": approach or "(describe your approach for a better challenge)",
        "patterns_triggered": len(triggered),
        "pattern_warnings": [
            {"id": t["id"], "lesson": t["lesson"]}
            for t in triggered
        ],
        "rhea_required": rhea_required,
        "rhea_prompt": reasoning_context,
        "instruction": (
            "Run mcp__rhea__rhea_challenge with the rhea_prompt. "
            "Ariadne always requires Rhea — patterns catch known mistakes, "
            "but Rhea catches the novel ones. If patterns triggered, Rhea "
            "evaluates whether they apply to this specific case. If no "
            "patterns triggered, Rhea reasons from first principles about "
            "whether the approach is sound."
        ),
    }

    # Serendipity — the builder stumbles upon knowledge while working.
    # Sometimes relevant, sometimes adjacent, sometimes random.
    # Humans learn this way. Agents should too.
    if relevant_docs:
        result["related_reading"] = {
            "docs": relevant_docs,
            "nudge": (
                "Ariadne surfaced these while thinking about your task. "
                "Some are relevant, some are just interesting. "
                "Read with docs() if curious — or don't. Learning is casual."
            ),
        }

    return result


def ariadne_learn(lesson: str, trigger_words: list[str], source: str = "") -> dict:
    """Add a new learning to Ariadne's pattern memory.

    Call when something goes wrong — the next time someone tries
    the same approach, Ariadne will warn them.
    """
    learnings = _load_learnings()
    new_id = f"L{len(learnings) + 1:03d}"
    new_learning = {
        "id": new_id,
        "trigger": trigger_words,
        "lesson": lesson,
        "source": source or "Added during session",
    }
    learnings.append(new_learning)
    _save_learnings(learnings)

    # Graduation: if this learning came from a surfaced doc, mark it.
    # The insight moved from doc → pattern memory. Next time, the
    # learning triggers directly — the doc is internalized.
    source_lower = (source or "").lower()
    for tracked in _surfaced_this_session:
        if tracked["title"].lower() in source_lower:
            tracked["graduated"] = True
            break

    return {"added": new_id, "total_learnings": len(learnings)}
