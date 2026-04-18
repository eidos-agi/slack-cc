---
id: MS-0004
title: 'M-04: Sage Medallion Complete'
status: closed
created: '2026-04-10'
---
Write sage_silver materialized views (NULLIF cleanup, type casting, L-code entity mapping, _job_id lineage). Write sage_gold tables (revenue by period, P&L by entity, AR aging, GL balances). Write forge.refresh_sage_* MERGE functions following HubSpot's SECURITY DEFINER pattern with advisory locks.

**Closed:** Done since session 26 (2026-04-13). 7 silver materialized views, 3 gold views (entity_pnl, gl_summary, ap_aging), refresh_all() wired into data-daemon executor. Dec 2025 parity confirmed.
