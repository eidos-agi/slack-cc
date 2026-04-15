---
id: TASK-0050
title: Build verifier learnings system
status: To Do
created: '2026-04-13'
priority: high
milestone: 'M-08: cerebro-verifier — Learning QA System'
tags:
  - verifier
  - learning
  - implementation
dependencies:
  - Design the learning layer — how exploration crystallizes into regression checks
acceptance-criteria:
  - Learnings persist across verification runs
  - Exploration findings can crystallize into regression checks
  - Regression checks taper after N consecutive passes
  - Verifier consults learnings before attempting extraction
  - New pages or changes trigger exploratory mode
---
Implement the learning layer in cerebro-verifier. Verifier records what it discovers about pages (selectors, timing, values, auth flow), crystallizes findings into regression checks, and consults learnings before each run. verifier_learnings.json or equivalent.
