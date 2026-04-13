---
id: TASK-0046
title: Integrate Rhea token-gate pattern into cerebro-github MCP
status: Done
created: '2026-04-11'
priority: P2
tags:
  - cerebro-github
  - rhea
  - architecture
dependencies:
  - cerebro-github MCP v0.1.0 (done)
  - Rhea MCP server (done, needs file context fix)
definition-of-done:
  - merge_pr() for T1→main returns rhea_required with context bundle instead of executing
  - New gate_production_merge() tool that accepts rhea_decision token
  - 'Token validation: hash of decision + timestamp + context'
  - 15+ tests covering gate flow, token validation, bypass rejection
  - Ledger entry documenting the pattern
updated: '2026-04-11'
---
Build the two-call handshake pattern for Rhea pre-flight challenges at production gates.

**Architecture (from Rhea debate session 22):**

Gate call → returns context snapshot + challenge prompt + `rhea_required: true`
Agent runs `mcp__rhea__rhea_challenge` with the context bundle
Execution call → requires `rhea_decision` token as input, errors without it

**Where gates fire:**
- T1 repo merge targeting main (promote to production)
- Milestone closure
- Credential provisioning across environments

**What the token contains:**
- Hash of (decision text + timestamp + challenge context)
- Internal integrity check, not a security boundary

**Key files to modify:**
- `cerebro-github/cerebro_github/ceremony.py` — split merge_pr into gate + execute
- `cerebro-github/cerebro_github/server.py` — new tool: `gate_production_merge`, modify `merge_pr` to validate token
- `cerebro-github/cerebro_github/topology.py` — context snapshot function for the bundle

**Doubter's valid concern:** Agent can fabricate a token without running Rhea. Acceptable for current threat model (protecting against carelessness, not deception). Revisit if team grows.

**Rhea's ruling:** Medium confidence — proceed with caution. Spec the token format before writing code.

**Completion notes:** Built and shipped in session 22. 19 tests passing. Token-gate pattern: merge_pr gates T1→main, requires Rhea challenge + decision token. Topology model added (environments, services, credentials, deploy order).
