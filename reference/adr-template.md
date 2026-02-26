# ADR Template — Greenmark Waste Solutions

This is the standard format for Architecture Decision Records (ADRs) at Greenmark.

ADRs document significant technology, infrastructure, and operational decisions that affect how Greenmark builds, deploys, and operates its systems. They create a durable record of *why* decisions were made — not just *what* was decided.

## When to Write an ADR

- Adopting or dropping a major tool, vendor, or platform
- Choosing an architecture pattern that locks in a direction
- Accepting concentration risk on a single system
- Changing how teams work (workflows, access, processes)
- Any decision leadership or future engineers would ask "why did we do this?"

## Where ADRs Live

- **Template**: `greenmark-cockpit/reference/adr-template.md` (this file)
- **Records**: `infra/decisions/ADR-YYYY-NN.md` (one file per decision)
- **Index**: `infra/decisions.md` (lightweight log linking to full ADRs)

## Numbering

ADRs use the format `ADR-YYYY-NN` where YYYY is the year and NN is a sequential number within that year. Example: `ADR-2026-01`, `ADR-2026-02`.

---

## Template

Copy everything below this line into a new file at `infra/decisions/ADR-YYYY-NN.md`.

---

```markdown
# ADR-YYYY-NN: <Decision Title>

- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Date**: YYYY-MM-DD
- **Owner**: <Name / Role>
- **Related**: <Links to issues, docs, Slack threads, meetings>

## Context

- What problem are we solving or what situation prompted this decision?
- Who is affected (teams, systems, workflows)?
- Why is this architecturally or operationally significant right now?

## Decision

- Clear, single-sentence statement of the decision.
- 2-4 bullets clarifying scope and what is explicitly in or out.

## Rationale

- Key reasons this option wins over the alternatives.
- Assumptions we are making (e.g., vendor stability, scale, budget).

## Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A      |             |      |      |
| B      |             |      |      |
| C      |             |      |      |

## Consequences

- **Positive**: What becomes easier or better.
- **Negative**: Risks, costs, or lock-in we are accepting.
- **Neutral / Open**: What we are explicitly not deciding right now.

## Implementation & Ownership

- Who owns executing this decision.
- Key steps or milestones (1-3 bullets).
- How and when we will measure whether this was the right call.

## Review & Sunset

- **Review trigger**: <date-based or event-based>
- **Conditions to revisit**: <what would cause us to deprecate or supersede this ADR>
```
