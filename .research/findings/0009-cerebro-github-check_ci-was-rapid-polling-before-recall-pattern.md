---
id: 0009
title: cerebro-github check_ci was rapid-polling before recall pattern
status: open
evidence: CONFIRMED
sources: 1
created: '2026-04-23'
---

## Claim

Before the recall pattern fix (this session), check_ci fired ~15 rapid GraphQL calls per PR CI check. 4 PRs = ~60 calls. Each checks query returns ~20 check run nodes, costing ~20+ points each. This alone could burn 1000-1200 points. The recall pattern (2 calls instead of 15) is deployed in code but MCP servers loaded pre-fix still use the old behavior.

## Supporting Evidence

> **Evidence: [CONFIRMED]** — Session 33 pre-compaction: user said 'that fucking check ci is broken', observed 15+ rapid polls per PR, retrieved 2026-04-23

## Caveats

None identified yet.
