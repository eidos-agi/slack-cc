---
id: "GUARD-006"
type: "guardrail"
title: "GR-ENV-001 \u2014 Develop and production are isolated environments with separate databases"
status: "active"
date: "2026-04-20"
---

Develop data-daemon connects to the dev Supabase (izmuckuepryqneebwwol). Production data-daemon connects to the production Supabase (wwmcgtyngnziepeynccz). NEVER cross-wire them.

Each environment has its own:
- DATABASE_URL pointing to its own Supabase instance
- Job queue (daemon.jobs table in its own database)
- Workers that only process jobs from their own database
- Migrations applied independently

Violations:
- Setting develop's DATABASE_URL to production → workers steal production jobs
- Running ad-hoc scripts against production database from develop context
- Deleting infrastructure instead of fixing the configuration

Origin: Session 34 — set develop's DATABASE_URL to production Supabase, causing develop workers to grab and fail Fleetio extraction jobs before production workers could process them. Spent hours debugging what looked like a connector bug but was an environment isolation failure.
