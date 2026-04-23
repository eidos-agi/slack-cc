---
id: '0004'
title: 'AIC CISO pattern: local MCP, read-only audit, Daniel-only scope'
status: open
evidence: INFERRED
sources: 1
created: '2026-04-23'
---

## Claim

AIC's security approach uses local MCPs (not remote/hosted), read-only audit patterns (never auto-remediate), and operator-only access (not stakeholder-facing). This matches Greenmark's constraints: stakeholders default to 'no' on new tooling cost, there's no security team, and Daniel is the sole operator. A remote MCP would add hosting cost and create another surface to secure — contradicting the mission. Local Python MCP running against Supabase + GitHub APIs is the right architecture.

## Supporting Evidence

> **Evidence: [INFERRED]** — Pattern analysis of cerebro-builder-mcp, forge-forge audit patterns, software-approved.md policy, retrieved 2026-04-23

## Caveats

None identified yet.
