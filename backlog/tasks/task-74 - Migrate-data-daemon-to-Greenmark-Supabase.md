---
id: TASK-74
title: Migrate data-daemon to Greenmark Supabase
status: To Do
assignee: []
created_date: '2026-02-27 20:34'
labels:
  - infra
  - data-daemon
  - supabase-migration
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
data-daemon's database connection needs to point to the new Greenmark-owned Supabase (greenmark-cerebro, wwmcgtyngnziepeynccz.supabase.co). Update Railway env vars and verify all bronze schema tables, job queue, and extraction pipeline work against the new instance. This may require running migrations on the new Supabase.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Railway env vars updated for data-daemon
- [ ] #2 Bronze schema tables exist in new Supabase
- [ ] #3 Job queue operational against new instance
- [ ] #4 At least one test extraction completes successfully
<!-- AC:END -->
