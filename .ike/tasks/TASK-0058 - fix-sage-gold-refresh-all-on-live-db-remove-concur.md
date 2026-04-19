---
id: TASK-0058
title: Fix sage_gold.refresh_all() on live DB — remove CONCURRENTLY
status: To Do
created: '2026-04-18'
priority: critical
tags:
  - sage
  - database
  - hotfix
definition-of-done:
  - Run sage_gold.refresh_all() CREATE OR REPLACE in Supabase SQL Editor (non-concurrent
  version)
  - Call sage_gold.refresh_all() and confirm it completes without disk errors
  - Verify entity_pnl has April 2026 data with revenue > 0
---
The migration file (20260413120000) has the correct non-concurrent version, but the live database still has the old CONCURRENTLY version. This causes "No space left on device" errors during refresh. Need to run CREATE OR REPLACE FUNCTION sage_gold.refresh_all() from the migration file against the live Supabase database. One SQL statement in the SQL Editor.
