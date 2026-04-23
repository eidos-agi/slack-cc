---
title: Cloudflare Worker MCP — remote, always-on
verdict: provisional
---

## What It Is

Remote MCP hosted on Cloudflare Workers (like cerebro-mcp). Always-on, could run scheduled checks via Cron Triggers. Advantage: runs without Daniel's machine, could feed results to the security map page automatically. Disadvantage: creates another hosted service to secure, adds Cloudflare cost (even if minimal), needs its own auth (Supabase service_role key stored in CF secrets), and the security scanning MCP itself becomes an attack surface. Also adds complexity to the MCP topology — currently 5 MCPs, this would be 6th remote service.

## Validation Checklist

- [ ] Claim 1: Y — Cron Triggers are a native CF Workers feature. cerebro-mcp already runs on CF.
- [x] Cloudflare Worker can run scheduled security checks via Cron Triggers without Daniel being in a session: Y — CF Cron Triggers are native. cerebro-mcp already runs on CF.
- [ ] Hosting a security scanner remotely does not create a net-negative security posture by adding attack surface: N — A remote service holding service_role key IS a new attack surface. If compromised, attacker gets full DB bypass. Net-negative for security posture of a security tool. Violates principle of least privilege.

## Scoring
## Scores

| Criterion | Score |
|-----------|-------|
| C1 | 5/10 |
| C2 | 1/10 |
| C3 | 5/10 |
| C4 | 3/10 |
| C5 | 2/10 |
| C6 | 5/10 |
| **Total** | **21** |

**Notes:** Claim 2 fails — service_role key on remote surface is self-defeating for a security tool.
