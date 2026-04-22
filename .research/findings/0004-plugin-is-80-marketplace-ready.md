---
id: '0004'
title: Plugin is 80% marketplace-ready
status: open
evidence: VERIFIED
sources: 1
created: '2026-04-21'
---

## Claim

The plugin has the core structure (plugin.json, skills, server.ts, tests, CI). Remaining gaps: (1) .mcp.json needs server entry with ${CLAUDE_PLUGIN_ROOT}, (2) skills need YAML frontmatter, (3) no LICENSE file, (4) channels declaration removed from plugin.json during dual-start fix — needs to be re-added for marketplace mode. These are all small fixes.

## Supporting Evidence

> **Evidence: [VERIFIED]** — claude plugin validate output, comparison with Telegram plugin structure, retrieved 2026-04-21

## Caveats

None identified yet.
