---
id: TASK-11
title: Define sync frequency strategy per vendor
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:39'
updated_date: '2026-02-27 00:44'
labels:
  - mvp
  - architecture
  - data-daemon
milestone: MVP
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The ADR is silent on how often data-daemon pulls. Different vendors need different frequencies: Sage financials can be daily batch, HubSpot pipeline needs near-real-time for sales team, fleet data is somewhere in between. Define and document the sync cadence for each P1 vendor, configure data-daemon scheduler accordingly, and set expectations with stakeholders about data freshness.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Sync frequency documented for Sage (P1) and HubSpot (P1)
- [ ] #2 data-daemon scheduler configured with correct cron intervals
- [ ] #3 Stakeholders informed of expected data freshness per source
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Feb 27: **Second opinion (Gemini 2.5 Pro)** — Tiered strategy, not one-size-fits-all. Sage: daily batch 2am. HubSpot: webhook + 15-min polling fallback (sales team needs near-real-time). Navusoft: daily batch end-of-day. Fleetio: webhook + hourly polling fallback. Paylocity: weekly batch (low volatility, high sensitivity). Build webhook support for HubSpot and Fleetio only. Webhooks enqueue jobs in Postgres queue; workers process like any other. Polling fallback = safety net for missed webhooks. Extend YAML config: `sync_strategy: 'webhook' | 'batch'` + `reconciliation_schedule`.
<!-- SECTION:NOTES:END -->
