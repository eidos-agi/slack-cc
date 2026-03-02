---
id: TASK-73
title: Update cerebro-ai-services Railway env vars for Greenmark Supabase
status: To Do
assignee: []
created_date: '2026-02-27 20:34'
labels:
  - infra
  - cerebro-ai-services
  - supabase-migration
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
cerebro-ai-services currently has SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY pointing to the old AIC Supabase instance (zbscgmkkictwxoridyui). Update Railway env vars to point to the new Greenmark-owned Supabase project (greenmark-cerebro, wwmcgtyngnziepeynccz.supabase.co, account: it@greenmarkwaste.com). Verify ai_usage_log table exists in the new instance and service can write to it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Railway env vars updated to new Supabase URL and service role key
- [ ] #2 ai_usage_log table exists in new Supabase (public schema)
- [ ] #3 Service can write usage logs to new instance
- [ ] #4 /health endpoint returns healthy after restart
<!-- AC:END -->
