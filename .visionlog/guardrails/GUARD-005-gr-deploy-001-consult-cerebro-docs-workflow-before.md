---
id: "GUARD-005"
type: "guardrail"
title: "GR-DEPLOY-001 \u2014 Consult cerebro-docs workflow before any deploy operation"
status: "active"
date: "2026-04-20"
---

Before merging a PR to data-daemon, applying a migration, or deploying any service, MUST call cerebro-docs.workflow() to load the deployment procedure.

Specifically:
- data-daemon: workflow('deploy_data_daemon')
- cerebro-migrations: workflow('apply_migration')
- cerebro: workflow('ship_to_staging') or workflow('promote_to_production')

Origin: Session 34 — spent hours debugging because deploy goes to production (not develop), Docker cache trap on env var changes, migration tracking broken by raw psql.
