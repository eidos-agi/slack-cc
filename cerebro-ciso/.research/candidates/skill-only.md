---
title: Skill-only — no MCP, cockpit skill + CI workflow
verdict: provisional
---

## What It Is

No new MCP. Instead: (1) a /security-audit cockpit skill in greenmark-cockpit that runs SQL queries and GitHub API checks inline, (2) a CI workflow (.github/workflows/security-drift.yml) that runs the same checks on schedule. Advantage: zero new infrastructure, zero new repos, uses existing session context. Disadvantage: no MCP tool reuse across sessions, drift checks only run when Daniel is in a session or CI fires, can't be composed with other MCPs (e.g., cerebro-builder can't call security checks during convene). Doesn't match Daniel's ask for 'its own repo that looks like AIC's CISO program.'

## Validation Checklist

- [ ] Claim 1: N — A skill runs inline in conversation context, can't be composed. CI workflow only catches drift on push events, not on-demand during sessions. MCP tools are callable by any agent at any time.
- [x] A cockpit skill + CI workflow provides equivalent security coverage to an MCP without the overhead of a new repo: N — skill can't be composed across MCPs, CI only on push events. Not equivalent.
- [ ] Other MCPs (cerebro-builder, cerebro-github) do not need to call security checks during their own workflows: N — cerebro-builder already calls check_mission and pre_advance_checks during convene. Adding security_sweep to that chain is natural. cerebro-github's health_check could also benefit from security posture data. Cross-MCP composability matters.

## Scoring
## Scores

| Criterion | Score |
|-----------|-------|
| C1 | 3/10 |
| C2 | 5/10 |
| C3 | 1/10 |
| C4 | 5/10 |
| C5 | 5/10 |
| C6 | 1/10 |
| **Total** | **20** |

**Notes:** Both claims fail. Not composable, doesn't match Daniel's ask. Cheapest but least capable.
