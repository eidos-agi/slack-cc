"""Session planning — six-phase template with gates and kill criteria.

Codifies the framework derived from session 29's failure modes:
  Phase 0 — Pre-flight (contracts, bookmark, env, health)
  Phase 1 — Observation (verify assumptions with real data)
  Phase 2 — Build A (one scoped deliverable)
  Phase 3 — Build B (one scoped deliverable, parallel-shippable with A)
  Phase 4 — Integrate + deploy (single atomic deploy + live verify)
  Phase 5 — Document + land (trilogy capture, /land, bookmark)

The mayor does not execute. plan_session returns a structured plan for
the agent to follow. The agent is responsible for honoring phase gates,
kill criteria, and end-of-phase checkpoints. Enforcement is by nudge,
not by block — future phase_gate and checkpoint tools will surface drift,
not prevent it.

Scope discipline: plan_session takes ONE scope statement and ONE budget.
If the caller can't name one thing, the plan refuses. Multi-goal sessions
are session 29, not session 30.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ── Phase templates ────────────────────────────────────────────────

@dataclass(frozen=True)
class PhaseTemplate:
    """Template for one phase. Concrete plans bind specific steps + gates."""
    name: str
    goal: str
    default_budget_minutes: int
    hard_cap_minutes: int
    required_inputs: tuple[str, ...]
    required_output: str
    default_kill_criterion: str


PHASE_0_PREFLIGHT = PhaseTemplate(
    name="0-preflight",
    goal="Load contracts, verify services, confirm scope",
    default_budget_minutes=15,
    hard_cap_minutes=25,
    required_inputs=("scope statement", "budget in hours"),
    required_output="confirmed scope + services healthy + credentials loaded",
    default_kill_criterion="any blocking service unhealthy or credentials missing",
)

PHASE_1_OBSERVATION = PhaseTemplate(
    name="1-observation",
    goal="Verify the assumption driving this session against real data before writing code",
    default_budget_minutes=30,
    hard_cap_minutes=45,
    required_inputs=("scope statement",),
    required_output="findings document in .research/ with actual numbers, not hypotheses",
    default_kill_criterion="observation exceeds 45 min or fails to produce 3+ concrete findings",
)

PHASE_2_BUILD_A = PhaseTemplate(
    name="2-build-a",
    goal="Ship scoped deliverable A — one thing, tested, committed locally",
    default_budget_minutes=60,
    hard_cap_minutes=90,
    required_inputs=("Phase 1 findings",),
    required_output="local commit with passing type-check + test suite",
    default_kill_criterion="tests failing after 90 min — revert this phase only",
)

PHASE_3_BUILD_B = PhaseTemplate(
    name="3-build-b",
    goal="Ship scoped deliverable B — second thing, tested, committed locally",
    default_budget_minutes=45,
    hard_cap_minutes=60,
    required_inputs=("Phase 2 complete or killed",),
    required_output="local commit with passing type-check + test suite",
    default_kill_criterion="tests failing after 60 min — revert this phase only, ship Phase 2 alone",
)

PHASE_4_DEPLOY = PhaseTemplate(
    name="4-deploy",
    goal="Ship Phases 2 + 3 as one atomic deploy and verify live",
    default_budget_minutes=30,
    hard_cap_minutes=45,
    required_inputs=("Phase 2 and/or Phase 3 commits",),
    required_output="live /healthz 200 + verification event visible in telemetry",
    default_kill_criterion="deploy fails twice — revert to previous, file issue, end with partial work",
)

PHASE_5_LAND = PhaseTemplate(
    name="5-land",
    goal="Capture work in the trilogy and land cleanly",
    default_budget_minutes=30,
    hard_cap_minutes=45,
    required_inputs=("Phase 4 deploy green OR explicit partial-work note",),
    required_output="bookmark written, working trees clean on T1 repos, /land completed",
    default_kill_criterion="never — /land is non-negotiable; if exhausted, land minimal",
)

PHASES_IN_ORDER = (
    PHASE_0_PREFLIGHT,
    PHASE_1_OBSERVATION,
    PHASE_2_BUILD_A,
    PHASE_3_BUILD_B,
    PHASE_4_DEPLOY,
    PHASE_5_LAND,
)


# ── Core planning function ────────────────────────────────────────

def plan_session(
    scope: str,
    budget_hours: float = 4.0,
    build_a: Optional[dict] = None,
    build_b: Optional[dict] = None,
    observation_query: Optional[str] = None,
) -> dict:
    """Produce a 6-phase session plan bound to a specific scope + budget.

    Args:
        scope: One-sentence statement of what this session delivers. Refusal
               condition: if scope contains " and " linking two goals, the
               plan includes a warning — multi-goal sessions are the failure
               mode this template exists to prevent.
        budget_hours: Total time budget. The template defaults sum to ~3.5h;
               budgets below 3h get scaled phase budgets, budgets above 5h
               get a warning that this is beyond single-session shipping size.
        build_a: Optional dict with keys `goal`, `steps`, `gate`, `kill`,
               `artifact` to override Phase 2 defaults with session-specific
               content.
        build_b: Same for Phase 3.
        observation_query: Optional SQL or command string to run in Phase 1.
               Captured verbatim in the plan so there's no ambiguity.

    Returns:
        A structured plan ready for the agent to execute. The caller is
        expected to write this plan to ike.md as a task with phases as
        subtasks, then check off phases as they complete.
    """
    scope = scope.strip()
    warnings: list[str] = []

    if not scope:
        return {
            "error": "scope is required — the session must deliver one named thing",
            "hint": "call plan_session(scope='ship query_gold + error emitter', budget_hours=4)",
        }

    # Multi-goal detection — the framework's whole point is single-scope sessions.
    if " and " in scope.lower() and scope.lower().count(" and ") > 1:
        warnings.append(
            f"scope contains multiple 'and' clauses — is this really one session? "
            f"session 29 failure mode was multi-goal drift."
        )
    if len(scope.split()) > 20:
        warnings.append("scope sentence is long — consider tightening it")

    if budget_hours < 3:
        warnings.append(
            f"budget {budget_hours}h is below the 3.5h template floor — "
            f"phase budgets will be scaled down proportionally"
        )
    if budget_hours > 5:
        warnings.append(
            f"budget {budget_hours}h exceeds the 5h session ceiling — "
            f"consider splitting scope into two sessions"
        )

    scale = budget_hours * 60 / sum(p.default_budget_minutes for p in PHASES_IN_ORDER)

    phases: list[dict] = []
    for i, template in enumerate(PHASES_IN_ORDER):
        budget = max(10, int(template.default_budget_minutes * scale))
        cap = max(budget + 5, int(template.hard_cap_minutes * scale))

        phase_dict = {
            "index": i,
            "name": template.name,
            "goal": template.goal,
            "budget_minutes": budget,
            "hard_cap_minutes": cap,
            "required_output": template.required_output,
            "default_kill_criterion": template.default_kill_criterion,
        }

        # Phase-specific content injection
        if template.name == "1-observation" and observation_query:
            phase_dict["observation_query"] = observation_query
        if template.name == "2-build-a" and build_a:
            phase_dict["goal"] = build_a.get("goal", template.goal)
            for key in ("steps", "gate", "kill", "artifact"):
                if key in build_a:
                    phase_dict[key] = build_a[key]
        if template.name == "3-build-b" and build_b:
            phase_dict["goal"] = build_b.get("goal", template.goal)
            for key in ("steps", "gate", "kill", "artifact"):
                if key in build_b:
                    phase_dict[key] = build_b[key]

        phases.append(phase_dict)

    total_budget_minutes = sum(p["budget_minutes"] for p in phases)
    total_cap_minutes = sum(p["hard_cap_minutes"] for p in phases)

    return {
        "scope": scope,
        "budget_hours": budget_hours,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "phases": phases,
        "total_budget_minutes": total_budget_minutes,
        "total_hard_cap_minutes": total_cap_minutes,
        "out_of_scope_reminder": (
            "Name 2-3 tempting adjacent threads we are NOT doing this session. "
            "Post them in the session log before Phase 1."
        ),
        "discipline_reminders": [
            "Phases are sequential — no parallel work across phases.",
            "Every phase ends with a commit (local for 2-3, pushed in 4-5).",
            "Kill criteria are real — Phase 2 running long does NOT eat Phase 3's budget.",
            "Observation before construction — Phase 1 is first, always.",
            "Phase 5 /land is non-negotiable.",
        ],
        "warnings": warnings,
    }


def render_plan_markdown(plan: dict) -> str:
    """Render a plan dict as an ike.md-friendly markdown task body.

    The agent is expected to write this to .ike/sessions/YYYY-MM-DD.md
    as the body of a session task, with phases as checkbox sub-items.
    """
    if "error" in plan:
        return f"ERROR: {plan['error']}\n\nHINT: {plan.get('hint', '')}"

    lines: list[str] = [
        f"# Session plan — {plan['generated_at']}",
        "",
        f"**Scope:** {plan['scope']}",
        f"**Budget:** {plan['budget_hours']}h "
        f"(~{plan['total_budget_minutes']}m budget, ~{plan['total_hard_cap_minutes']}m hard cap)",
        "",
    ]

    if plan.get("warnings"):
        lines.append("## Warnings")
        for w in plan["warnings"]:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    lines.append("## Disciplines")
    for d in plan["discipline_reminders"]:
        lines.append(f"- {d}")
    lines.append("")

    lines.append("## Out of scope (fill before Phase 1)")
    lines.append(f"_{plan['out_of_scope_reminder']}_")
    lines.append("- [ ] _TODO: name tempting thread 1 we are NOT doing_")
    lines.append("- [ ] _TODO: name tempting thread 2 we are NOT doing_")
    lines.append("- [ ] _TODO: name tempting thread 3 we are NOT doing_")
    lines.append("")

    lines.append("## Phases")
    lines.append("")
    for p in plan["phases"]:
        lines.append(f"### Phase {p['index']} — {p['name']}")
        lines.append(
            f"**Budget:** {p['budget_minutes']}m "
            f"(hard cap {p['hard_cap_minutes']}m)"
        )
        lines.append("")
        lines.append(f"- **Goal:** {p['goal']}")
        lines.append(f"- **Required output:** {p['required_output']}")
        lines.append(f"- **Kill criterion:** {p.get('kill', p['default_kill_criterion'])}")
        if "observation_query" in p:
            lines.append("- **Observation query:**")
            lines.append("  ```")
            for ql in p["observation_query"].splitlines():
                lines.append(f"  {ql}")
            lines.append("  ```")
        if "steps" in p:
            lines.append("- **Steps:**")
            for s in p["steps"]:
                lines.append(f"  - [ ] {s}")
        if "gate" in p:
            lines.append(f"- **Gate to advance:** {p['gate']}")
        if "artifact" in p:
            lines.append(f"- **Artifact:** {p['artifact']}")
        lines.append("")

    return "\n".join(lines)
