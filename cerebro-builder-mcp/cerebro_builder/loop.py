"""Loop contract — what happens every iteration of autonomous execution.

The loop is the outer ceremony. Each iteration:
  1. Ask the mayor what's next (reads ike)
  2. Do the work
  3. Verify the work (run DoD checks, not just read them)
  4. Challenge the work (Rhea on code tasks)
  5. Advance state (ike task_complete)
  6. Report (what happened, what's next, any concerns)

The stupidity catcher: before advancing, every output gets checked
against concrete assertions. "Did the SQL actually return rows?"
"Does the migration file reference tables that exist?"
"Did the test actually test the thing it claims to test?"
"""


# ── Pre-advance checks ──────────────────────────────────
# These run BEFORE task_complete(). If any fail, the task stays open
# and the agent must fix the issue before advancing.

CHECK_PATTERNS = {
    "migration": {
        "applies_when": ["migration", "schema", "view", "table", "sql"],
        "checks": [
            "File exists in supabase/migrations/ with correct naming (YYYYMMDDHHMMSS_*.sql)",
            "SQL parses without syntax errors (run through psql --echo-errors or supabase db reset)",
            "References only schemas/tables that exist or are created in the same migration",
            "Includes RLS policy or explicit rls_disabled_in_public comment",
            "WHERE deleted_at IS NULL on all SELECT views (soft deletes)",
            "Entity column present with CHECK constraint where applicable",
        ],
        "rhea_required": True,
        "rhea_prompt": (
            "Review this SQL migration for correctness. Check: "
            "wrong table names, missing joins, incorrect column references, "
            "type mismatches, and any logic that doesn't match the bronze schema. "
            "The bronze tables store raw_data as JSONB — silver views must extract "
            "with correct JSON paths. Compare against warp-speed seed_gold_sage.py "
            "for the known-correct transformation logic."
        ),
    },
    "connector": {
        "applies_when": ["connector", "extraction", "pipeline", "api"],
        "checks": [
            "Tests pass (pytest -v on the connector module)",
            "Registered in CONNECTOR_REGISTRY",
            "Handles pagination (test with >1 page of results)",
            "Rate limiting implemented (don't hammer vendor APIs)",
            "Error handling covers 429, 500, timeout",
        ],
        "rhea_required": True,
        "rhea_prompt": (
            "Review this connector for correctness. Check: "
            "auth flow, pagination termination, error handling edge cases, "
            "and whether the data mapping matches the vendor's actual API response format."
        ),
    },
    "dashboard": {
        "applies_when": ["dashboard", "page", "component", "ui", "frontend"],
        "checks": [
            "Component renders without errors (no TypeScript/JSX errors)",
            "Data fetcher queries the correct gold tables",
            "Entity filter works (ntx vs hometown)",
            "Numbers format correctly (currency, percentages, dates)",
            "Loading and error states handled",
        ],
        "rhea_required": False,
    },
    "verification": {
        "applies_when": ["parity", "validation", "compare", "fixture", "test"],
        "checks": [
            "Golden fixtures are from a trusted source (warp-speed cerebro.db)",
            "Comparison logic handles rounding correctly",
            "Failure messages are specific (which entity, which month, expected vs actual)",
            "Script exits non-zero on any failure",
        ],
        "rhea_required": True,
        "rhea_prompt": (
            "Review this validation script. The biggest risk is false positives — "
            "the script says 'pass' when the numbers are actually wrong. "
            "Check: tolerance thresholds, data type coercions, whether all "
            "entities and periods are covered (not just the ones that happen to match)."
        ),
    },
}


def get_pre_advance_checks(task_title: str) -> dict:
    """Get the checks that must pass before a task can be completed.

    Returns the applicable check pattern and whether Rhea review is required.
    """
    title_lower = task_title.lower()

    matches = []
    for pattern_name, pattern in CHECK_PATTERNS.items():
        if any(kw in title_lower for kw in pattern["applies_when"]):
            matches.append({
                "pattern": pattern_name,
                "checks": pattern["checks"],
                "rhea_required": pattern["rhea_required"],
                "rhea_prompt": pattern.get("rhea_prompt", ""),
            })

    if not matches:
        # Default: basic checks
        matches.append({
            "pattern": "default",
            "checks": [
                "The work is actually done (not just started)",
                "Any new files are committed to git",
                "Tests pass if applicable",
            ],
            "rhea_required": False,
        })

    return {
        "task": task_title,
        "pre_advance_checks": matches,
        "any_rhea_required": any(m["rhea_required"] for m in matches),
        "instruction": (
            "Run every check. If any fail, fix the issue before calling task_complete(). "
            "If rhea_required is true, run mcp__rhea__rhea_challenge with the rhea_prompt "
            "and your work output before advancing."
        ),
    }


# ── Loop iteration contract ─────────────────────────────

LOOP_CONTRACT = {
    "steps": [
        {
            "step": 1,
            "name": "orient",
            "action": "cerebro-builder: whats_next()",
            "purpose": "Know what to work on. Don't assume — read ike.",
        },
        {
            "step": 2,
            "name": "check_alignment",
            "action": "cerebro-builder: check_mission(proposed_task)",
            "purpose": "Confirm the task is on the critical path. Catch drift early.",
        },
        {
            "step": 3,
            "name": "plan",
            "action": "Read the task's definition_of_done. Plan the work.",
            "purpose": "Know what done looks like before starting.",
        },
        {
            "step": 4,
            "name": "execute",
            "action": "Do the work. Use child MCPs as needed.",
            "purpose": "Write code, create PRs, run commands.",
        },
        {
            "step": 5,
            "name": "verify",
            "action": "Run pre-advance checks for the task type.",
            "purpose": "Catch dumb errors before they ship. SQL returns rows? Tests pass? Joins correct?",
        },
        {
            "step": 6,
            "name": "challenge",
            "action": "If rhea_required: run mcp__rhea__rhea_challenge on the output.",
            "purpose": "Adversarial review catches what self-review misses.",
        },
        {
            "step": 7,
            "name": "advance",
            "action": "ike-md: task_complete(). If milestone done: milestone_close().",
            "purpose": "State moves forward. Next iteration picks up where this one left off.",
        },
        {
            "step": 8,
            "name": "report",
            "action": "Log what happened, what's next, any concerns.",
            "purpose": "Context for the next iteration (or the human reviewing the loop).",
        },
    ],
    "abort_conditions": [
        "Pre-advance check fails and cannot be fixed in this iteration",
        "Rhea rejects the work with low confidence",
        "Task requires human input (credentials, approval, external system access)",
        "More than 3 consecutive failures on the same task",
        "Context window approaching limit — land cleanly instead of degrading",
    ],
    "stupidity_catchers": [
        "Never declare a migration done without running it against a real database",
        "Never declare a connector done without at least one real API call (or mock that matches real response shape)",
        "Never declare parity without comparing actual numbers (not just 'script ran')",
        "Never advance past a VERIFY step without showing the output",
        "If a task title says 'write X' and you didn't write X, you didn't do the task",
        "If the definition of done has 5 items and you did 3, the task is not done",
    ],
}
