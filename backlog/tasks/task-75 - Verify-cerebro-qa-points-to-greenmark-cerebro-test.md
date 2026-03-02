---
id: TASK-75
title: Verify cerebro-qa points to greenmark-cerebro-test
status: To Do
assignee: []
created_date: '2026-02-27 20:34'
labels:
  - infra
  - cerebro-qa
  - supabase-migration
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Confirm cerebro-qa is wired to the greenmark-cerebro-test Supabase project (not prod and not old AIC instance). Check both local .env.local and Railway env vars. Verify QA dashboard loads and data quality checks run against the test instance.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 cerebro-qa Railway env vars point to greenmark-cerebro-test
- [ ] #2 QA dashboard loads without errors
- [ ] #3 Data quality checks execute against test instance
<!-- AC:END -->
