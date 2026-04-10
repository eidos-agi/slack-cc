---
id: DOC-0001
title: 'PLAN — Sage End-to-End: From Discovery to Production'
created: '2026-04-10'
tags:
  - plan
  - sage
  - master
---
# Sage End-to-End — Master Plan

**Created:** 2026-04-10
**Owner:** Daniel Shanklin
**Status:** Active

## Context

Sage Intacct is Greenmark's financial system of record. The discovery work has already happened in `cerebro-warp-speed-excel` — 2.5M real records extracted, entity mapping confirmed by Alex Kaye, gold metrics proven to the penny against the Excel workbook. Excel was the **discovery instrument**. Now we rebuild directly into the cloud pipeline, following the HubSpot medallion pattern already proven in staging Cerebro.

## Philosophy

1. **Running code is truth.** The validated Excel workbook and the 2.5M rows in warp-speed's SQLite database are the ground truth for Sage. Any document that contradicts them is wrong by definition.
2. **Don't bridge. Rebuild.** The Excel pipeline proved how Sage data works. That epistemic output is what we keep. The pipeline itself is research scaffolding, not infrastructure.
3. **Follow HubSpot exactly.** The medallion pattern for HubSpot (bronze → silver → gold, with `forge.refresh_*` MERGE functions, advisory locks, RLS, per-vendor schemas) is proven in production. Sage wears HubSpot's clothes.
4. **Validate behaviorally.** The Excel workbook becomes the golden oracle. Every Postgres gold metric must match its Excel counterpart to 2 decimal places. No cell-level disagreement is acceptable. See VALIDATION doc.

## Phases

### M-01: Session 21 Cleanup
Ship the essay, archive the stale Sage spec with a pointer README, merge the 7 open PRs across the org. Start Phase 0 from a clean state.

### M-02: Sage Bronze Reality-Aligned
Delete the March `sage_bronze` migration (hand-written hypothesis). Dump warp-speed's actual SQLite schema. Observe real rows. Write a new Postgres bronze DDL derived from observation, not guess. Deploy to staging Supabase.

### M-03: Sage Connector Live
Write `SageIntacctConnector` in data-daemon by hand, pattern-matching `hubspot_connector.py`. Copy the XML session/pagination logic from warp-speed's proven downloader. Enable `sage-intacct` in `data-daemon/services/sage-intacct.yaml` with the real REST/XML config. First real extraction lands in `sage_bronze`.

### M-04: Sage Medallion Complete
Write `sage_silver` materialized views (cleanup, type casting, entity mapping, `_job_id` lineage). Write `sage_gold` tables (revenue by period, P&L by entity, AR aging, GL balances). Write `forge.refresh_sage_*` MERGE functions following HubSpot's SECURITY DEFINER pattern with advisory locks.

### M-05: Excel Parity Proven
Export warp-speed's gold tables as golden fixtures. Write a validation script that compares every Postgres gold metric to its Excel counterpart. Fix until 100% parity. This is the refactor-forge discipline applied to a pipeline rebuild.

### M-06: Sage Live on Staging Cerebro
Update `cerebro/lib/data/financial.ts` (or create it) to query `gold.sage_*`. Update the Financial and Executive Summary dashboards. Remove mock fallbacks. Ship via develop → PR → main. Michael's staging dashboard shows real Sage numbers.

### M-07: Excel Retired as Infrastructure
warp-speed keeps its identity as a validation oracle and Alex-deliverable. Its cron becomes a daily validation run, not a production feed. All downstream consumption flows through Postgres gold.

## Related Documents

- **ARCH — Medallion Pattern for Sage (HubSpot as Template)** — technical reference, SQL patterns to copy
- **DOD — Sage Live on Staging Cerebro** — concrete acceptance criteria
- **VALIDATION — Excel Workbook as Golden Oracle** — the golden fixture discipline applied to pipelines

## What This Unlocks

Once Sage is live end-to-end with validated parity, it becomes the template for every subsequent vendor. Navusoft, Fleetio, Paylocity — each is roughly a week of work following this same pattern. Within 4–6 weeks of Sage shipping, Cerebro stops being a research project and becomes the thing Michael and Alex actually use on Monday mornings. That is the trajectory-A moment.

## Scope Discipline

This plan does NOT include:
- Extending `elt-forge` with a Postgres target (overbuilt — single-vendor rebuild doesn't need a reusable generator)
- Porting the Agent SDK backend from Python to TypeScript (different project, tracked as TASK-0016)
- Building new gold metrics beyond what Excel already proves (scope creep — ship what's validated, not what's aspirational)

If any of those become valuable, they get separate plans with separate milestones. Do not let them leak into this one.
