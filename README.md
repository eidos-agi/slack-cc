# cc-channel-slack-eidos

Two-way Slack channel for Claude Code. Talk to your session from Slack. Approve tool calls from your phone.

## How it works

```
Slack (cloud)
  ↕  WebSocket (Socket Mode — outbound only, no public URL)
server.ts (local, spawned by Claude Code)
  ↕  stdio (MCP)
Claude Code session
```

No servers to deploy. No URLs to expose. Works behind firewalls, NAT, anywhere.

## Setup (5 minutes)

### 1. Create a Slack App

[api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**

**Socket Mode:** Settings → Socket Mode → Enable → Generate App-Level Token (`xapp-...`) with `connections:write` scope.

**Events:** Enable Events → Subscribe to:
- `message.im` — DMs
- `message.channels` — public channels
- `message.groups` — private channels
- `app_mention` — @mentions

**Bot Scopes** (OAuth & Permissions):
- `chat:write`, `channels:history`, `groups:history`, `im:history`
- `reactions:write`, `files:read`, `files:write`, `users:read`

**App Home:** Enable the Messages tab + "Allow users to send messages."

**Install** to your workspace → copy the Bot Token (`xoxb-...`).

### 2. Start Claude Code with the plugin

```bash
claude --plugin-dir ~/repos/cc-channel-slack-eidos \
       --dangerously-load-development-channels server:slack
```

### 3. Configure tokens

In the Claude Code session:
```
/slack-eidos:configure xoxb-your-bot-token xapp-your-app-token
```

Tokens are saved to `~/.claude/channels/slack/.env` with `0600` permissions. Never logged, never echoed.

### 4. Connect

**DM the bot** in Slack. First-time users get a pairing code. Run `/slack-eidos:access pair <code>` in the terminal to approve.

**Or** — if you're already paired — just **@mention the bot in any channel**. It auto-connects for the current session. No channel IDs to copy-paste.

## Connecting channels

There are two ways to connect a Slack channel:

**Session-scoped (automatic):** @mention the bot in any channel. If you're on the allowlist, the channel connects for THIS session. When the session ends, the connection dies. Next session, @mention again.

**Permanent:** Run in the terminal:
```
/slack-eidos:access channel C0AV895UKFS
```
This persists to `access.json` and survives session restarts.

## Tools

Claude gets four Slack tools:

| Tool | What it does |
|------|-------------|
| `reply` | Post a message (auto-chunks long text) |
| `react` | Add an emoji reaction |
| `edit_message` | Update a sent message |
| `fetch_messages` | Read channel/thread history |

## Permission relay

When Claude wants to run a tool that needs approval, the prompt shows up in Slack too. Reply `yes <id>` or `no <id>` from your phone. First answer (terminal or Slack) wins.

## Access control

```bash
/slack-eidos:access status                    # What's connected
/slack-eidos:access add U12345678             # Add a user
/slack-eidos:access remove U12345678          # Remove a user
/slack-eidos:access policy allowlist          # Only pre-approved users
/slack-eidos:access channel C12345678         # Permanently opt-in a channel
/slack-eidos:access channel remove C12345678  # Remove a channel
```

## FAQ

**The bot reacts with 👀 but messages don't appear in my session.**
Two known causes:

1. You started Claude Code without `--dangerously-load-development-channels server:slack`. The MCP server loads fine (tools work, bot reacts), but Claude Code never registered a channel listener — notifications fire into the void. Always include the flag when launching from the shell, including with `--resume`.

2. *(Tentatively confirmed — needs more testing)* You used `/resume` inside a running session to switch to a past conversation. This may drop the channel listener even though the MCP server keeps running. The bot still reacts, tools still work, but inbound delivery stops. If this happens, exit and start a fresh session with the full flags.

```bash
claude --plugin-dir ~/repos/cc-channel-slack-eidos --dangerously-load-development-channels server:slack
```

**I @mentioned the bot but nothing happened.**
You're not on the allowlist yet. DM the bot first to get a pairing code, then run `/slack-eidos:access pair <code>` in the terminal.

**The channel connected but messages stopped after I restarted.**
Session-scoped channels (from @mention auto-opt-in) die when the session ends. @mention the bot again, or make it permanent with `/slack-eidos:access channel <id>`.

## Security

- **Sender gating:** Every message hits the gate. Unknown senders are dropped before reaching Claude.
- **Session-scoped channels:** @mention auto-connects for the current session only. No permanent state from a single action.
- **Outbound gate:** Claude can only reply to channels/threads that delivered inbound.
- **Token lockdown:** `.env` is `0600`, never logged, never in tool results.
- **Bot filtering:** Bot messages dropped by default. Self-echoes detected via user ID.
- **Prompt hardening:** System instructions tell Claude to refuse access manipulation from Slack messages.

## State files

All state lives in `~/.claude/channels/slack/`:

| File | What |
|------|------|
| `.env` | Bot token + app token (0600) |
| `access.json` | Allowlist, channel opt-ins, pending pairings (0600) |

## Diagnostics

### Debug MCP (v0.4)

A dedicated diagnostic server lives in `debug/server.ts` with 12 tools for full-stack inspection. Register it as `slack-eidos-debug` in your workspace `.mcp.json`.

Key tools:
- `slack_debug_check` — Full health check across all 7 layers (tokens, permissions, API, channels, process, server, config). Detects dual-start, permission friction, and missing scopes.
- `slack_debug_channel_reg` — Verifies channel listener registration. Filters stale logs from previous sessions. Checks `--allowedTools` and detects duplicate bridge processes.
- `slack_debug_scope_diff` — Token scopes vs bridge requirements in one output.
- `slack_debug_roundtrip` — Send + read back test through Slack API.

See [docs/known-limitations.md](docs/known-limitations.md) for known issues and workarounds.

### From the terminal (status tool)

Claude can call the `status` tool anytime to see the server's internal state — log buffer, transport status, channels, access config. Just ask "check the slack bridge status" or call it directly.

### From Slack

Send `@Cerebro Development debug` (exact match) in any connected channel. The bot replies in-thread with full diagnostics.

### Structured logs

The server writes JSON logs to stderr. Every entry includes timestamp, uptime, transport state, and session channel count. Events:

| Event | What it means |
|-------|--------------|
| `boot.complete` | Server started — shows botUserId, channels, access config |
| `slack.inbound` | Slack event received |
| `dedup.dropped` | Duplicate event filtered |
| `gate.drop` | Message rejected (check `reason` field) |
| `gate.auto-opt-in` | Channel connected via @mention |
| `gate.pair` | Pairing code issued |
| `deliver.ok` | Notification sent to Claude Code |
| `deliver.fail` | Notification failed (check `error` field) |
| `command.*` | Bot command executed (help, debug, permission-reply) |

To see them live:
```bash
./start-with-slack.sh --debug
```

Full diagnostics guide: [DIAGNOSTICS.md](DIAGNOSTICS.md)

### Common gotcha

If you see `deliver.ok` in the logs but no `<channel>` tag appears in your session, the channel listener isn't registered. This happens when you start or resume without the `--dangerously-load-development-channels` flag. Use the startup script:

```bash
# From greenmark-cockpit root:
./start-with-slack.sh
```

## Development

```bash
# Install deps
npm install

# Run tests (108 tests across 23 suites)
npm test

# Dev mode (skip plugin allowlist)
claude --plugin-dir . --dangerously-load-development-channels server:slack

# With debug logs
claude --debug --plugin-dir . --dangerously-load-development-channels server:slack
```

## License

MIT
