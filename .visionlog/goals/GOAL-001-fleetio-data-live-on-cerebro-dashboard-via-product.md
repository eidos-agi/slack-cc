---
id: "GOAL-001"
type: "goal"
title: "Fleetio data live on Cerebro dashboard via production pipeline"
status: "in_progress"
date: "2026-04-20"
depends_on: []
unlocks: []
backlog_tag: "fleetio-prod"
---

End state: Robert opens Cerebro on Monday morning and sees his fleet data — vehicles, maintenance costs, fuel efficiency, inspections — rendered from live Fleetio data flowing through the production system (data-daemon → Supabase bronze → silver/gold views → PostgREST → dashboard).

NOT from ad-hoc scripts. NOT from SQLite. NOT from Excel. Through the system.

Current state: FleetioConnector deployed to production. Trigger endpoint works. Jobs enqueue. But insert logic has a bug — jobs complete without error but most tables have 0 rows. Vehicles (53 rows) works. Others don't.

Remaining:
1. Debug and fix the FleetioConnector insert bug
2. Verify all 17 bronze tables populated through data-daemon
3. Create silver/gold materialized views (cerebro-migrations PR)
4. Wire Maintenance + Operations dashboard pages to fleetio_gold
5. Add client-side telemetry (page view events)
6. Ship to production, verify with cerebro-verifier
