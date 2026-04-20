---
id: '0004'
title: cerebro-migrations supports two linked Supabase projects
status: open
evidence: PROVEN
sources: 1
created: '2026-04-20'
---

## Claim

cerebro-migrations CLAUDE.md documents two Supabase instances: production (wwmcgtyngnziepeynccz) and test/dev (izmuckuepryqneebwwol). The Supabase CLI can link to either. npm run migrate applies to whichever is linked. The CI 'Fresh database' test already runs against a temporary database. Migrations can be applied to both instances independently.

## Supporting Evidence

> **Evidence: [PROVEN]** — cerebro-migrations/CLAUDE.md lines 22-26, CI workflow runs fresh database test, retrieved 2026-04-20

## Caveats

None identified yet.
