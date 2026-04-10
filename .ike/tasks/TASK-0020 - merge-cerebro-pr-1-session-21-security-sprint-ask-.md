---
id: TASK-0020
title: 'Merge cerebro PR #1 — Session 21 security sprint + Ask Cerebro Phase 1'
status: To Do
created: '2026-04-10'
priority: high
milestone: 'M-01: Session 21 Cleanup'
tags:
  - cleanup
  - cerebro
  - ask-cerebro
dependencies:
  - 'M-01: Merge 6 hygiene PRs across the org'
acceptance-criteria:
  - 'CI passing on PR #1'
  - Reviewed (or self-reviewed with intent)
  - Merged to main
  - Production deploy succeeds
  - Post-deploy smoke tests green
  - Ask Cerebro chat visible on production cerebro dashboard
---
The big PR: RLS security sprint (all 7 rls_disabled_in_public errors), ADR-2026-29 schema placement, Ask Cerebro Phase 1 (real Agent SDK chat replaces canned /ask), branch guard, CI pipeline, post-deploy smoke tests. CI is green after the auth gate fix. Ready to merge. This is what makes the real AI chat live on production cerebro.
