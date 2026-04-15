---
id: TASK-0052
title: Wire verifier into builder adjourn ceremony
status: To Do
created: '2026-04-13'
priority: medium
milestone: 'M-08: cerebro-verifier — Learning QA System'
tags:
  - verifier
  - builder
  - ceremony
dependencies:
  - Build verifier learnings system
acceptance-criteria:
  - Adjourn ceremony includes verification status when UI tasks were done
  - Builder can call verification_report() to get latest results
  - which_forge routes 'verify dashboard' to cerebro-verifier
---
The builder's adjourn ceremony should check verification status when UI tasks were completed in the session. Not a synchronous gate — the builder reads the latest verification report and includes it in the adjourn record.
