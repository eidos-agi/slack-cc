---
title: Operational Tooling vs Infrastructure Drift
tags: [drift, infrastructure, operational, guardrails, mission, critical-path]
---

# Operational Tooling vs Infrastructure Drift

Not all infrastructure work is drift. Some is on the critical path.

## The distinction

**Drift** — building tools that don't unblock the mission:
- "Let me add a CLI dashboard for job status"
- "Let me refactor the config module"
- Session 22 lost 8 hours to this pattern

**Operational tooling** — building what's needed to run the mission:
- POST /trigger endpoint (couldn't run the pipeline without it)
- Periodic commits (couldn't load 584K rows without it)
- Reconnect before load (couldn't survive PgBouncer without it)

## How to tell the difference

Ask: "If I don't build this, can the mission succeed today?"

- If no → it's operational. Build it.
- If yes → it's drift. Check with the guardrails.

## The guardrails should know this

The mission check asks "Is this on the M-01→M-07 critical path?" But operational tooling doesn't look like milestone work — it looks like infrastructure. The test should be: "Does this unblock something on the critical path?" not "Does this match a milestone keyword?"

Session 25 examples:
- Trigger endpoint: not in any milestone, but M-04 was dead without it
- Reconnect fix: not planned, but every load would fail without it
- Builder docs tool: actual drift (useful, but not critical path)
