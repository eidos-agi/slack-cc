---
id: '0005'
title: Marketplace plugins eliminate --dangerously flag
status: open
evidence: VERIFIED
sources: 1
created: '2026-04-21'
---

## Claim

Development plugins require --dangerously-load-development-channels. Marketplace plugins use --channels plugin:name@marketplace (no "dangerously"). This also eliminates the dual-start problem entirely — Claude Code manages the lifecycle, no --plugin-dir needed. The workspace .mcp.json hack becomes unnecessary.

## Supporting Evidence

> **Evidence: [VERIFIED]** — code.claude.com/docs/en/channels-reference, Telegram plugin loading path, retrieved 2026-04-21

## Caveats

None identified yet.
