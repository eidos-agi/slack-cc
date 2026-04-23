---
id: '0002'
title: Drift audit pattern already proven in forge-forge and gold security
status: open
evidence: VERIFIED
sources: 1
created: '2026-04-23'
---

## Claim

Two drift audit patterns exist: (1) forge-forge's forge-audit skill runs 20-30 compliance checks against the Forge Standard, (2) ADR-2026-14 defines audit.check_gold_security() with 6 automated checks (RLS enabled, FORCE RLS, policy exists, entity column, no service_role grant, no anon/public grant). Both run as continuous checks, not one-time assessments. cerebro-ciso should adopt this pattern — automated drift detection that runs on every session or CI cycle.

## Supporting Evidence

> **Evidence: [VERIFIED]** — forge-forge/.claude/skills/forge-audit.md, infra/decisions/ADR-2026-14-gold-drift-audit.md, infra/plans/IMPL-001-medallion-security.md, retrieved 2026-04-23

## Caveats

None identified yet.
