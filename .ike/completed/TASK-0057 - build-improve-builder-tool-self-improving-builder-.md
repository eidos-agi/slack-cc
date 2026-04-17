---
id: TASK-0057
title: Build improve_builder tool — self-improving builder ceremony
status: Done
created: '2026-04-17'
priority: high
tags:
  - cerebro-builder
  - governance
  - meta
definition-of-done:
  - improve_builder() tool exists in cerebro-builder server.py
  - Reads last 5 session logs from sessions/ directory
  - 'Identifies friction: ad-hoc patterns, repeated failures, missing tools'
  - Returns one concrete proposal (file, function, what it does)
  - Called during adjourn ceremony (not convene)
  - First real improvement proposed and verified
updated: '2026-04-17'
---
The builder should be able to identify its own gaps by reading session logs. Called at adjourn. Reads last N sessions, finds friction patterns (ad-hoc work, multiple attempts, missing tools), proposes one concrete fix per invocation. Optionally builds it right there.

**Completion notes:** Done. improve_builder() reads last 5 session logs, scans for 6 friction patterns, proposes one concrete fix. First finding: blocked-then-easy in 5/5 sessions → proposes decompose_blocker() as next build. Tested against real data.
