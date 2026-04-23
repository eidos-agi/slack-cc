---
id: '0006'
title: REST vs GraphQL budget imbalance
status: open
evidence: CONFIRMED
sources: 1
created: '2026-04-23'
---

## Claim

REST budget barely touched (~25-769 used/hour) while GraphQL hits 0/5000 repeatedly. These are separate budgets on the same PAT. The consumer is doing pure GraphQL operations, not REST.

## Supporting Evidence

> **Evidence: [CONFIRMED]** — gh api /rate_limit and gh api graphql rateLimit query, session 33, retrieved 2026-04-23

## Caveats

None identified yet.
