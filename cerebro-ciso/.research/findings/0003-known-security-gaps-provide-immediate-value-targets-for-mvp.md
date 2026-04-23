---
id: '0003'
title: Known security gaps provide immediate value targets for MVP
status: open
evidence: VERIFIED
sources: 1
created: '2026-04-23'
---

## Claim

Current known gaps: (1) tenants/entities tables have RLS enabled but zero policies (deny-all, safe only because service_role bypasses), (2) no URL validation on transcribe AI endpoint, (3) CRLF injection possible in invite emails, (4) Unicode homograph/zero-width confusables accepted in entity slugs/emails, (5) rate limiting only in middleware (no per-user), (6) Microsoft Entra ID + Azure Key Vault adopted (ADR-2026-25) but not yet implemented. An MVP cerebro-ciso that catches these in automated sweeps immediately proves value.

## Supporting Evidence

> **Evidence: [VERIFIED]** — RLS audit 2026-04-23 (pg_policies query), cerebro/security/ test expectations, ADR-2026-25, retrieved 2026-04-23

## Caveats

None identified yet.
