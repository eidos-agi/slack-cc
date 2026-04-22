# slack-eidos-debug

Full-stack diagnostic MCP for the slack-cc Slack bridge. Installed into a workspace (e.g., greenmark-cockpit) so the agent can diagnose Slack bridge issues from any session — even when the bridge plugin itself isn't loaded.

**Philosophy:** Diagnose, don't fix. The MCP tells the agent what's broken across all 7 layers. The agent fixes it with Edit/Bash/normal tools. No mutations, no side effects beyond read + test message.

## The 7 Layers

The Slack ↔ Claude Code bridge is a stack of independent systems. A failure at any layer breaks the connection. This MCP inspects all of them:

```
Layer 7 ─ Plugin Wiring
         Claude Code --plugin-dir + --dangerously-load-development-channels
         Is Claude Code even loading the plugin? Is the channel listener registered?

Layer 6 ─ MCP Config
         .mcp.json entries in plugin root + workspace
         Are the server entries correct? Do the paths exist?

Layer 5 ─ Server Integrity
         server.ts, node_modules, tsx, TypeScript compilation
         Can the server even start?

Layer 4 ─ Bot Process
         Is tsx server.ts running? PID, memory, uptime
         Is Socket Mode connected?

Layer 3 ─ Access Control
         access.json: dmPolicy, allowFrom, channels, pending pairings
         Will the gate allow this user/channel through?

Layer 2 ─ Slack API
         auth.test, OAuth scopes, bot identity, team membership
         Can the bot talk to Slack at all?

Layer 1 ─ Tokens
         .env file: SLACK_BOT_TOKEN (xoxb-), SLACK_APP_TOKEN (xapp-)
         Exist? Valid prefix? Correct permissions (0600)?
```

## Tools

| Tool | Layer | What it checks |
|------|-------|----------------|
| `slack_debug_check` | All 7 | Full sweep — runs every check, returns unified report with `healthy` boolean and `issues[]` |
| `slack_debug_slack_api` | 2 | Deep API probe: auth.test, scope verification, list channels bot is member of |
| `slack_debug_bot_process` | 4 | `ps aux` for tsx server.ts, Socket Mode processes, start script existence |
| `slack_debug_server` | 5 | server.ts exists, deps installed, tsx binary, TypeScript compiles, package.json, manifest |
| `slack_debug_mcp_config` | 6 | .mcp.json in plugin root + workspace, path validation, .claude-plugin dir, skills |
| `slack_debug_access` | 3 | Full access.json dump with analysis (empty allowlist, disabled DMs, etc.) |
| `slack_debug_logs` | 4 | Structured JSON logs from `~/.claude/debug/`, summarized by event type |
| `slack_debug_send_test` | 2 | Send a message via Slack API (bypasses bridge) — tests outbound path |
| `slack_debug_read_channel` | 2 | Read messages via Slack API (bypasses bridge) — tests inbound path |

## Installation

The debug MCP is installed in the **workspace** (not as a plugin). This is intentional — it needs to work even when the plugin isn't loaded.

### In greenmark-cockpit/.mcp.json

```json
{
  "mcpServers": {
    "slack-eidos-debug": {
      "type": "stdio",
      "command": "/home/dev/repos/slack-cc/node_modules/.bin/tsx",
      "args": ["/home/dev/repos/slack-cc/debug/server.ts"]
    }
  }
}
```

### Dependencies

Uses the same deps as the main server (installed at plugin root):

```bash
cd ~/repos/slack-cc
npm install
```

## Usage

From any cockpit session:

```
"debug the slack bridge"     → agent calls slack_debug_check
"why isn't slack working?"   → agent calls slack_debug_check, reads issues, fixes them
"check slack logs"           → agent calls slack_debug_logs
"test outbound to #general"  → agent calls slack_debug_send_test
```

The agent reads the diagnostic output and fixes issues itself using Edit (to fix .env, access.json) or Bash (to restart processes, npm install, etc.).

## Key Files

| File | Purpose | Location |
|------|---------|----------|
| `.env` | Bot + app tokens | `~/.claude/channels/slack/.env` |
| `access.json` | Gate config (users, channels, policy) | `~/.claude/channels/slack/access.json` |
| `server.ts` | Main bridge server | `~/repos/slack-cc/server.ts` |
| `debug/server.ts` | This diagnostic MCP | `~/repos/slack-cc/debug/server.ts` |
| `.mcp.json` | Plugin MCP registration | `~/repos/slack-cc/.mcp.json` |
| `start-with-slack.sh` | Launch script | `~/repos/greenmark-cockpit/start-with-slack.sh` |

## Common Failure Patterns

### "deliver.ok" but no messages in session
**Layer 7 failure.** The bridge delivered the notification over stdio, but Claude Code didn't register a channel listener.
- **Cause:** Started without `--dangerously-load-development-channels server:slack`
- **Cause:** Used `/resume` inside a session (may drop the listener)
- **Fix:** Exit and restart with the full flags

### Bot reacts with eyes but nothing happens
**Layer 7 failure.** Same as above — the MCP server is running (tools work, bot reacts) but the channel listener isn't registered.

### "gate.drop" in logs
**Layer 3 failure.** The access gate rejected the message. Check the `reason` field:
- `channel-not-opted-in` → channel not in access.json and no @mention auto-opt-in
- `dm-not-allowlisted` → user not in allowFrom and dmPolicy is "allowlist"
- `bot-message` / `self-echo` → expected, the gate filters these

### "not_in_channel" error
**Layer 2 failure.** Bot isn't a member of the channel.
- **Fix:** `/invite @BotName` in the Slack channel, or `conversations.join`

### "invalid_auth" error
**Layer 1 failure.** Bot token is wrong or revoked.
- **Fix:** Regenerate at api.slack.com/apps → OAuth & Permissions, then write to .env

### Server won't start
**Layer 5 failure.** Check: node_modules present? tsx binary exists? TypeScript compiles?
- **Fix:** `cd ~/repos/slack-cc && npm install`

## Architecture

```
                    ┌─────────────────────────────────┐
                    │        Claude Code Session       │
                    │                                  │
                    │  ┌──────────┐  ┌──────────────┐ │
                    │  │ debug/   │  │ server.ts    │ │
                    │  │ server.ts│  │ (bridge)     │ │
                    │  │ (MCP)    │  │ (MCP+plugin) │ │
                    │  └────┬─────┘  └──────┬───────┘ │
                    │       │ stdio         │ stdio    │
                    └───────┼───────────────┼──────────┘
                            │               │
                   reads state      WebSocket (Socket Mode)
                   + Slack API              │
                            │               │
              ┌─────────────┼───────────────┼──────────┐
              │  ~/.claude/channels/slack/   │          │
              │  ├── .env (tokens)          │          │
              │  └── access.json (gate)     │          │
              └─────────────────────────────┼──────────┘
                                            │
                                    ┌───────┴────────┐
                                    │   Slack API    │
                                    │  (api.slack.com)│
                                    └────────────────┘
```

The debug MCP and the bridge server are **independent processes**. The debug MCP reads the same state files and talks to the same Slack API, but it doesn't go through the bridge. This means it works even when the bridge is completely broken.

## Claude Code Channels — Reference

This MCP diagnoses the [Claude Code channels system](https://docs.anthropic.com/en/docs/claude-code/channels). Key concepts:

- **Channels** are bidirectional communication pipes between Claude Code and external services (Slack, Discord, etc.)
- **Plugin channels** are loaded via `--plugin-dir` + `--dangerously-load-development-channels`
- The MCP server declares `claude/channel` capability and sends `notifications/claude/channel` for inbound messages
- Claude Code surfaces these as `<channel>` tags in the conversation
- Permission relay uses `notifications/claude/channel/permission_request` and `notifications/claude/channel/permission`

### Claude Code channel documentation
- [Channels overview](https://docs.anthropic.com/en/docs/claude-code/channels) — how channels work, plugin vs. marketplace
- [Channel plugins](https://docs.anthropic.com/en/docs/claude-code/channel-plugins) — building channel plugins, MCP capabilities
- [Slack channel plugin](https://github.com/anthropics/claude-code-plugins/tree/main/slack-channel) — Anthropic's reference implementation

### Prior art
- [claude-code-plugins/slack-channel](https://github.com/anthropics/claude-code-plugins/tree/main/slack-channel) — Anthropic's official Slack channel plugin (marketplace). Our slack-cc is a clean-room rewrite with Socket Mode, access control, and permission relay.
- [claude-code-slack-channel](https://github.com/anthropics/claude-code-slack-channel) — Earlier reference. Was the upstream before slack-cc replaced it.
- [slack-mcp-server](https://github.com/slackapi/slack-mcp-server) — Slack's official MCP server (different purpose: gives Claude Slack tools, not a channel bridge)
- [bolt-js-starter-agent](https://github.com/slack-samples/bolt-js-starter-agent) — Slack's starter for Claude Agent SDK bots (what cerebro-slack-bot is based on — a standalone bot, not a Claude Code channel)

## Differences from the main server

| Aspect | server.ts (bridge) | debug/server.ts (this) |
|--------|--------------------|------------------------|
| Purpose | Bidirectional Slack ↔ Claude Code channel | Diagnose why the bridge isn't working |
| Runs as | Plugin (--plugin-dir) | Workspace MCP (always available) |
| Mutates state | Yes (access.json, reactions, messages) | No (reads only, except test messages) |
| Socket Mode | Yes (persistent WebSocket) | No (one-shot API calls) |
| Channel capability | Yes (claude/channel) | No |
| When to use | Normal operation | When things are broken |
