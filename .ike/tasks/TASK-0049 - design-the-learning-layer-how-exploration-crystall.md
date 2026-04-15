---
id: TASK-0049
title: Design the learning layer — how exploration crystallizes into regression checks
status: To Do
created: '2026-04-13'
priority: high
milestone: 'M-08: cerebro-verifier — Learning QA System'
tags:
  - verifier
  - learning
  - design
dependencies:
  - First dogfood run on staging Cerebro
acceptance-criteria:
  - Data model for verifier learnings defined
  - 'Crystallization rules: what makes a finding become a regression check'
  - 'Tapering rules: when does a check get deprioritized'
  - 'Re-exploration triggers: what causes the verifier to go wide again'
  - Integration point with builder's adjourn ceremony defined
---
The core design problem: how does an exploration finding become a regression check? How does a regression check taper when it passes consistently? How does the verifier know when to explore again? Model after human QA teams: explore → crystallize → regress → taper → explore again. Same violin model as builder knowledge.
