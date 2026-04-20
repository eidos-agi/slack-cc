---
id: TASK-0074
title: 'ADR-004: Wire environment isolation for data-daemon'
status: To Do
created: '2026-04-20'
priority: critical
tags:
  - infra
  - data-daemon
  - ADR-004
acceptance-criteria:
  - develop data-daemon deploys to develop Railway on push to develop
  - production data-daemon deploys to production Railway on push to main
  - develop DATABASE_URL points to izmuckuepryqneebwwol
  - production DATABASE_URL points to wwmcgtyngnziepeynccz
  - One successful Fleetio extraction against dev Supabase proven
  - cerebro-docs workflow updated
visionlog_goal_id: GOAL-001
---
Implement the staging branch pattern per ADR-004 and research.md decision.

Subtasks:
1. Get dev Supabase password from Daniel
2. Set develop DATABASE_URL to dev Supabase
3. Apply fleetio_bronze + index fix migrations to dev database
4. Change deploy.yml: develop → develop Railway environment
5. Add deploy-prod.yml: main → production Railway environment
6. Prove one extraction against dev Supabase
7. Define smoke test SQL for staging verification
8. Update cerebro-docs deploy_data_daemon workflow with new topology
9. Remove CACHEBUST ARG from Dockerfile (no longer needed once deploys target correct env)
