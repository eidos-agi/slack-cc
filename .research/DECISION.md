# Decision

**Date:** 2026-04-20
**Status:** Decided
**ADR:** ADR-003 (data-daemon deploy topology) — this decision supersedes the current broken state

## Decision

Approach B: Staging branch pattern — develop deploys to develop Railway (staging), main deploys to production Railway. Each environment uses its own Supabase database.

## Rationale

Scored 43/50, highest of 3 candidates. Mirrors cerebro's proven pattern. Fixes the session 34 cross-environment contamination. Rhea debate confirmed with preconditions: (1) prove one extraction against dev Supabase first, (2) define concrete smoke test SQL, (3) add staleness check to Rhea gate, (4) verify schema parity between databases.
