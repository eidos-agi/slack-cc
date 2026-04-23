---
title: Local Python MCP — audit-only, 6 tools
verdict: provisional
---

## What It Is

Local FastMCP Python server modeled on cerebro-builder-mcp. 6 MVP tools: (1) security_sweep — run all drift checks across RLS, RBAC, headers, settings.yml, secrets exposure; (2) rls_audit — query pg_tables + pg_policies, compare against expected policies; (3) rbac_audit — validate role definitions match code, check for privilege escalation paths; (4) repo_governance — check settings.yml compliance across all repos (tier contract); (5) secrets_scan — scan for exposed credentials in env vars, configs, logs; (6) posture_report — generate security posture summary feeding the security map. Read-only, no remediation. Runs against Supabase (service_role for pg_* queries) and GitHub API (settings.yml checks). No hosting cost, no new attack surface. Owns its own repo (greenmark-waste-solutions/cerebro-ciso).

## Validation Checklist

- [ ] Claim 1: Y — cerebro-data-engineer already does this with run_sql against Supabase via service_role. Same pattern.
- [x] FastMCP Python server can query Supabase pg_tables/pg_policies via service_role key without hosting infrastructure: Y — cerebro-data-engineer already does this via run_sql. Proven pattern.
- [ ] 6 audit tools can be built in a single session using existing SQL queries from the RLS audit and forge-audit patterns: Y — RLS audit SQL is proven (ran it this session), forge-audit checks are templated, settings.yml validator already exists in Python.

## Scoring
## Scores

| Criterion | Score |
|-----------|-------|
| C1 | 5/10 |
| C2 | 5/10 |
| C3 | 5/10 |
| C4 | 4/10 |
| C5 | 5/10 |
| C6 | 5/10 |
| **Total** | **29** |

**Notes:** All claims pass. Proven patterns, zero attack surface, full composability, matches ask.
