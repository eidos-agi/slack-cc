---
id: TASK-55
title: 'FastAPI core: config, auth, DB pool, migrations'
status: Done
assignee: []
created_date: '2026-02-27 08:22'
updated_date: '2026-02-27 08:29'
labels:
  - backend
  - core
milestone: m-1
dependencies:
  - TASK-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build src/config.py (env vars), src/auth.py (Bearer token → app name), src/db/connection.py (psycopg2 pool), src/db/migrate.py (migration runner), src/db/usage.py (log to ai.usage_log), src/main.py (FastAPI app with lifespan, /health). Migration 001 creates ai schema + usage_log table + materialized view.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Auth middleware validates Bearer tokens and maps to app names
- [ ] #2 DB pool connects to Supabase
- [ ] #3 Migration creates ai.usage_log table
- [ ] #4 GET /health returns model status JSON
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Built config.py (env vars + Railway pricing), auth.py (Bearer token → app name mapping + dashboard access), db/connection.py (psycopg2 ThreadedConnectionPool), db/migrate.py (SQL migration runner), db/usage.py (log_usage + analytics queries), main.py (FastAPI lifespan loading models + DB). Migration 001 creates ai schema, usage_log table, materialized view.
<!-- SECTION:FINAL_SUMMARY:END -->
