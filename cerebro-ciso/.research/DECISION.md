# Decision

**Date:** 2026-04-23
**Status:** Decided
**ADR:** ADR-2026-TBD (cerebro-ciso architecture)

## Decision

Local Python MCP — audit-only, 6 tools. Own repo (greenmark-waste-solutions/cerebro-ciso). FastMCP server modeled on cerebro-builder-mcp. Read-only, no remediation. Runs locally against Supabase + GitHub APIs.

## Rationale

Scored 29/30 — highest across all 6 criteria. All claims verified. Zero new attack surface (local only, no hosted service). Fully composable (cerebro-builder can call security_sweep during convene, cerebro-github can include posture in health_check). Proven implementation patterns (cerebro-data-engineer's run_sql for DB queries, forge-audit for drift checks, settings.yml validator already Python). Zero ongoing cost. Matches Daniel's explicit ask for dedicated security MCP in its own repo modeled on AIC CISO. Remote candidate failed its own security claim (service_role key on CF Worker = new attack surface for a security tool). Skill-only failed composability and didn't match the ask.
