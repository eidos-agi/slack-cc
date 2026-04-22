---
id: "ADR-001"
type: "decision"
title: "Publish via private Eidos marketplace + official submission"
status: "accepted"
date: "2026-04-21"
source_research_id: "4fe8079d-ce2b-48c6-899d-7d4c0e7dec6b"
---

## Context

slack-eidos-cc is a two-way Slack channel plugin for Claude Code. Currently runs as a development plugin requiring `--plugin-dir` and `--dangerously-load-development-channels`. This creates friction (dual-start bugs, permission prompts, no portability).

## Decision

Dual-track distribution:

**Phase 1 (immediate):** Create an `eidos-agi/claude-plugins` marketplace repo. Publish slack-eidos-cc as the first plugin. Any Claude Code user can then:
```bash
claude plugin marketplace add eidos-agi/claude-plugins
claude plugin install slack-eidos@eidos-agi
claude --channels plugin:slack-eidos@eidos-agi
```

**Phase 2 (async):** Submit to anthropics/claude-plugins-official via clau.de/plugin-directory-submission. If accepted, the plugin becomes discoverable to all Claude Code users without adding a custom marketplace.

## Rationale

Scored 97/105 weighted — highest of 4 candidates. Key advantages:
- Ships today (private marketplace) while official review runs async
- Builds Eidos ecosystem distribution infra reusable for railguey, research.md, ike.md, visionlog, rhea
- Eliminates --dangerously flag and dual-start problem at the root
- Only cost: creating marketplace repo (~30 min one-time)

## Implementation Requirements

1. Fix plugin .mcp.json: add server entry with `${CLAUDE_PLUGIN_ROOT}`
2. Re-add `channels` to plugin.json (needed for marketplace, safe now that workspace .mcp.json won't duplicate)
3. Add YAML frontmatter to skill SKILL.md files
4. Add LICENSE file
5. Create eidos-agi/claude-plugins marketplace repo with marketplace.json
6. Validate with `claude plugin validate`
7. Test full install → configure → connect flow
8. Submit to official marketplace

## Consequences

- start-with-slack.sh becomes optional (marketplace install handles everything)
- workspace .mcp.json slack entry becomes unnecessary for marketplace users
- Plugin name must be `slack-eidos` (not `slack` — name taken by Slack's official read-only MCP)
