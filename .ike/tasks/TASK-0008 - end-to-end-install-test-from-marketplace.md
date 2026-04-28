---
id: TASK-0008
title: End-to-end install test from marketplace
status: Done
created: '2026-04-21'
priority: high
milestone: MS-0002
dependencies:
  - TASK-0007
definition-of-done:
  - claude plugin install slack-cc@eidos-agi succeeds
  - claude --channels plugin:slack-cc@eidos-agi launches with channel listener
  - Inbound and outbound Slack messages work
updated: '2026-04-22'
---
Marketplace install → channel listener → inbound delivery confirmed. Chronicle page shipped to staging under StepProof governance (3 completed runs).
