---
id: TASK-0073
title: Debug FleetioConnector insert bug — jobs complete but 0 rows
status: In Progress
created: '2026-04-20'
priority: critical
tags:
  - fleetio
  - data-daemon
  - bug
visionlog_goal_id: GOAL-001
---
data-daemon FleetioConnector jobs complete without error but most tables have 0 rows in Supabase. Vehicles (53 rows) works. Others (contacts, work_orders, fuel_entries, etc.) complete with 0 rows.

Hypothesis: the connector's insert method may be committing to a different schema, using wrong column names, or the upsert pattern is deleting before inserting and the insert fails silently.

Debug approach:
1. Read the FleetioConnector source (src/connectors/fleetio_connector.py)
2. Compare insert logic between vehicles (works) and contacts (doesn't)
3. Check if there's a schema mismatch between what the connector writes and what fleetio_bronze expects
4. Fix, test locally, merge through ceremony
