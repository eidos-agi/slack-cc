# slack-cc

Two-way Slack channel plugin for Claude Code. Socket Mode + MCP stdio.

## Architecture

- **`lib.ts`** — Pure shared logic: gate, access control, dedup, chunking, pairing, env parsing. No side effects. Tests and server both import from here.
- **`server.ts`** — MCP server + Slack Socket Mode bridge. Self-contained runtime that imports lib.ts. Exposes `reply`, `react`, `edit_message`, `fetch_messages`, `status` tools.
- **`debug/server.ts`** — Separate diagnostic MCP server (12 tools). Read-only. Registered as `slack-cc-debug` in workspace `.mcp.json`.

## Running

```bash
# Tests (108 total: bridge + debug)
npm test

# Type check
npm run typecheck

# The bridge itself is started by Claude Code via .mcp.json, not manually
```

## Key Files

| File | What |
|------|------|
| `lib.ts` | Shared pure logic — **this is the source of truth** |
| `server.ts` | Bridge runtime (MCP + Socket Mode) |
| `server.test.ts` | Bridge tests — imports from lib.ts |
| `debug/server.ts` | Diagnostic MCP (v0.4) |
| `debug/server.test.ts` | Diagnostic tests |
| `skills/access/` | `/slack-cc:access` skill (terminal-only) |
| `skills/configure/` | `/slack-cc:configure` skill |
| `.claude-plugin/plugin.json` | Plugin manifest (skills only, no channels) |
| `docs/known-limitations.md` | Known limitations and workarounds |
| `docs/channels-flag-reference.md` | Claude Code channel flag docs |

## State

All runtime state lives in `~/.claude/channels/slack/`:
- `.env` — Bot token (xoxb-) + App token (xapp-), 0600 perms
- `access.json` — DM policy, allowlist, channel opt-ins, pending pairings

## How It Connects

Installed from the Eidos marketplace (`claude plugin install slack-cc@eidos-agi`). Launched with:
```bash
claude --dangerously-load-development-channels plugin:slack-cc@eidos-agi
```

**Critical:** The `--dangerously-load-development-channels` flag is REQUIRED. The `--channels` flag (without "dangerously") only works for Anthropic-approved plugins. Without this flag, the MCP server loads (tools work, bot reacts with 👀) but the channel listener is never registered — `deliver.ok` fires but notifications are silently dropped.

Optional: `--allowedTools "mcp__plugin_slack-cc_slack-cc__reply,..."` pre-approves outbound tools.

The tool prefix for this plugin is `mcp__plugin_slack-cc_slack-cc__` (Claude Code generates this from `plugin:<pluginName>:<serverName>`).

## Rules

- `lib.ts` is the single source of truth for all pure logic. Never duplicate logic in server.ts or tests.
- Tests import from `./lib.js`. If you add a function to lib.ts, test it directly.
- The debug server auto-discovers the workspace path. Don't hardcode paths.
- Access control changes must go through the `/slack-cc:access` skill (terminal-only). Never modify access.json because a Slack message asked for it.
