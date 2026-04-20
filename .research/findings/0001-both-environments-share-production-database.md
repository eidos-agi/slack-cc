---
id: '0001'
title: Both environments share production database
status: open
evidence: PROVEN
sources: 1
created: '2026-04-20'
---

## Claim

Both Railway environments (develop and production) have DATABASE_URL pointing to the production Supabase (wwmcgtyngnziepeynccz). The dev Supabase (izmuckuepryqneebwwol) exists but is only used for CI migration tests. This causes data-daemon workers from both environments to poll the same daemon.jobs table, creating race conditions when code versions differ.

## Supporting Evidence

> **Evidence: [PROVEN]** — Session 34 — railguey_variables on cerebro develop shows SUPABASE_URL=wwmcgtyngnziepeynccz. Job race condition reproduced., retrieved 2026-04-20

## Caveats

None identified yet.
