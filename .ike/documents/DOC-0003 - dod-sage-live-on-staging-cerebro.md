---
id: DOC-0003
title: DOD — Sage Live on Staging Cerebro
created: '2026-04-10'
tags:
  - definition-of-done
  - sage
  - acceptance
---
# Definition of Done — Sage Live on Staging Cerebro

**Purpose:** Concrete, verifiable acceptance criteria. "Sage is live" means all of the following are true and provable. Not "it mostly works." Not "most tables have data." All of it, provably.

## Data Layer

- [ ] `sage_bronze` schema exists in staging Supabase
- [ ] Bronze tables populated from real Sage API (not SQLite fixture, not mock data): `gl_accounts`, `gl_batches`, `gl_entries`, `ap_bills`, `ar_invoices`, `vendors`, `customers`
- [ ] Row counts in staging bronze match warp-speed's SQLite within ±5% (accounting for timing drift)
- [ ] Every bronze table has `_job_id` populated on every row (lineage proof)
- [ ] Every bronze table has `row_hash` computed (change detection works)
- [ ] `daemon.watermark_state` has rows for every Sage table using incremental sync

## Silver Layer

- [ ] `sage_silver` schema exists
- [ ] Materialized views created for every bronze table
- [ ] L-code → entity mapping works: every row in `sage_silver.gl_entries` has `resolved_entity` IN ('ntx', 'hometown')
- [ ] Date fields correctly parsed from MM/DD/YYYY to DATE
- [ ] Numeric fields correctly cast with NULLIF guards (no string-to-numeric errors)
- [ ] `REFRESH MATERIALIZED VIEW CONCURRENTLY` succeeds on every silver view
- [ ] Silver row counts match bronze row counts (no data loss in transformation)

## Gold Layer

- [ ] `gold.sage_revenue_by_period` table exists, populated, RLS enabled
- [ ] `gold.sage_pnl_by_entity` table exists, populated, RLS enabled
- [ ] `gold.sage_ar_aging` table exists, populated, RLS enabled
- [ ] `gold.sage_gl_balances` table exists, populated, RLS enabled
- [ ] `forge.refresh_sage_*` functions exist for all four tables
- [ ] Each refresh function follows HubSpot pattern: SECURITY DEFINER, advisory lock, MERGE, soft delete, 50%-delete safeguard
- [ ] Refresh functions called in order by data-daemon executor after bronze + silver load
- [ ] All gold tables have `_last_job_id`, `_refreshed_at`, `deleted_at` columns populated correctly

## Data-Daemon Integration

- [ ] `data-daemon/services/sage-intacct.yaml` enabled with real REST/XML config (SQLite fixture path removed)
- [ ] `data-daemon/src/connectors/sage_intacct_connector.py` exists and passes `test_connection()`
- [ ] Scheduled cron triggers Sage extraction daily
- [ ] Post-sync smoke tests defined in sage-intacct.yaml and passing: `row_count > 0`, `not_null [source_id, entity]`, `freshness` within SLA
- [ ] Extraction logs visible in `daemon.jobs` and `daemon.job_logs`

## Excel Parity — The Hard Gate

- [ ] Validation script exists at `cerebro-migrations/validation/sage_excel_parity.py` (or equivalent location)
- [ ] Script queries each `gold.sage_*` table and compares to fixture extracted from warp-speed's workbook
- [ ] **Revenue by entity × month matches Excel to 2 decimal places, for every month, both entities**
- [ ] **LOB rollups match Alex's breakthrough (Entity + E1001 allocations = LOB total, $0.00 delta)**
- [ ] **AR aging buckets match Excel**
- [ ] **GL balance running totals match Excel**
- [ ] Script returns non-zero exit code on any mismatch. CI-runnable.
- [ ] **100% parity. Not 99.9%. Not "close enough." 100% to 2 decimal places.**

## Cerebro UI

- [ ] `cerebro/lib/data/financial.ts` (or existing equivalent) queries `gold.sage_*` via PostgREST
- [ ] Financial dashboard page renders real Sage numbers (not mock data, not placeholders)
- [ ] Executive Summary page shows real revenue by entity
- [ ] RLS enforced: querying without auth returns zero rows; querying with ntx auth returns only NTX data
- [ ] No JavaScript console errors in the browser for pages that touch Sage data
- [ ] Smoke test (`/api/health` returns 200, `/dashboard` redirects to /login) still passing after deploy

## Deployment

- [ ] Changes deployed via develop → PR → main pipeline (not direct push)
- [ ] CI checks passing on the PR: type check, lint, unit tests, build
- [ ] Post-deploy smoke tests passing on staging
- [ ] Migrations applied cleanly to staging Supabase (no manual intervention)
- [ ] `cerebro-migrations/status.md` (or equivalent) updated to reflect new migrations applied

## Stakeholder-Visible Proof

- [ ] Daniel can open `https://staging-cerebro-greenmark.jettaintelligence.com/dashboard/financial` and see real Sage revenue by entity
- [ ] Screenshot captured and saved to `/reference/stakeholders/` or similar
- [ ] Michael has been informed (email or Teams) that Sage is now live in staging and how to view it
- [ ] Alex has been informed that the Postgres numbers match his Excel workbook exactly

## Documentation

- [ ] `infra/vendors/sage-intacct/README.md` updated with `last_verified` date pointing to this deployment
- [ ] Session 22 bookmark (or whenever this ships) mentions Sage is live in staging
- [ ] `CLAUDE.md` "What's Active" section updated to reflect Sage as live

## Post-Ship (within 72 hours)

- [ ] Excel workbook's cron (warp-speed) downgraded to validation-only status per M-07
- [ ] Staging Sage runs successfully for 3 consecutive days without human intervention
- [ ] Row counts remain stable (no unexplained drops)
- [ ] Michael or Alex has viewed the dashboard at least once (confirmed via logs or ask)

## Explicit Non-Goals

- Sage is live in **staging**, not production. Production cutover is a separate milestone (M-08 if it happens).
- Not every Sage object has a gold metric. Only the four in this batch (revenue, P&L, AR aging, GL balances). Others come later.
- Excel workbook continues to exist as a deliverable for Alex. Retirement means it stops being infrastructure, not that it stops being a report.
- Navusoft, Fleetio, Paylocity, etc. are NOT in scope. They get their own milestones after Sage ships.
