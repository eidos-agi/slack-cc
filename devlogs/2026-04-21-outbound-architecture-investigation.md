# Outbound Architecture Investigation

**Date:** 2026-04-21
**Session:** 33
**Trigger:** Daniel noticed Slack bridge requires terminal permission approval for each reply, while Telegram plugin felt smoother. Questioned whether Telegram uses a different outbound transport.

## Investigation

### Hypothesis

The official Telegram channel plugin sends outbound messages through a native channel transport (not MCP tools), bypassing Claude Code's permission system entirely. If true, the Slack bridge should be refactored to match.

### Findings

**Hypothesis rejected.** Both plugins use the identical architecture.

#### Telegram Plugin (official)
- Source: `~/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/telegram/server.ts`
- Exposes `reply`, `react`, `edit_message`, `download_attachment` as MCP tools via `ListToolsRequestSchema`
- Claude calls `mcp__telegram__reply(chat_id, text)` — standard MCP tool invocation
- Instructions say: *"Anything you want them to see must go through the reply tool"*

#### Slack Bridge (slack-cc)
- Source: `/home/dev/repos/slack-cc/server.ts`
- Exposes `reply`, `react`, `edit_message`, `fetch_messages`, `status` as MCP tools
- Claude calls `mcp__slack__reply(chat_id, text)` — same pattern
- Instructions say: *"Anything you want them to see must go through the reply tool"*

#### Channel Protocol (all plugins)

| Method | Direction | Purpose |
|--------|-----------|---------|
| `notifications/claude/channel` | Server -> Claude Code | Push inbound messages as `<channel>` XML tags |
| `notifications/claude/channel/permission_request` | Claude Code -> Server | Forward tool-approval prompts to remote user |
| `notifications/claude/channel/permission` | Server -> Claude Code | Relay user's allow/deny verdict back |

There is no `notifications/claude/channel/reply` or native outbound content method. All outbound goes through MCP tool calls.

### Why Telegram Feels Smoother

The perceived difference is likely in **permission configuration**, not architecture:
1. Telegram plugin may auto-approve its tools via `--allowedTools` or plugin-level defaults
2. The Slack bridge's `mcp__slack__reply` is already in `settings.local.json` allow list — but may not be matching correctly at runtime

### Current Permission State

`/home/dev/repos/greenmark-cockpit/.claude/settings.local.json` includes:
```
"mcp__slack__reply"
```
in the `permissions.allow` array. This should auto-approve without prompting.

## Health Check (same session)

Full `slack_debug_check` returned **healthy: true, 0 issues** across all 7 layers:
- Tokens: present, 0600 perms
- Slack API: authenticated as U0AUE6PPXU2 on Aicholdings
- Access: allowlist with Daniel (U0ADVV3RKHN), channel C0AV895UKFS
- Bot process: running (PID 51094)
- Server: deps installed, plugin intact

## Functional Test

Three outbound replies sent successfully in-thread during this session. Inbound messages from Daniel received and processed correctly. Bridge is fully operational.

## Open Questions

- [ ] Is `settings.local.json` allow list actually being respected at runtime? Need to confirm next session whether `mcp__slack__reply` prompts or auto-approves.
- [ ] Compare how the Telegram plugin's marketplace install configures permissions vs manual `settings.local.json` entries.
- [ ] Consider whether `--allowedTools` CLI flag at launch is more reliable than file-based allow lists.
