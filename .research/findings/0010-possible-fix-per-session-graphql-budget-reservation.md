---
id: '0010'
title: 'Possible fix: per-session GraphQL budget reservation'
status: open
evidence: HYPOTHESIS
sources: 1
created: '2026-04-23'
---

## Claim

The rate governor in cerebro-github reads actual GitHub quota but cannot distinguish between sessions. A coordination mechanism — shared file lock, named pipe, or Redis counter — could let sessions reserve budget slices. Simpler alternative: separate PATs per project (greenmark vs eidos-agi) to isolate budgets.

## Supporting Evidence

> **Evidence: [HYPOTHESIS]** — Architecture analysis, session 33, retrieved 2026-04-23

## Caveats

None identified yet.
