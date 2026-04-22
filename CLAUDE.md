# cc-channel-slack-eidos

Two-way Slack channel plugin for Claude Code. Socket Mode + MCP stdio.

## Architecture

- **`lib.ts`** — Pure shared logic: gate, access control, dedup, chunking, pairing, env parsing. No side effects. Tests and server both import from here.
- **`server.ts`** — MCP server + Slack Socket Mode bridge. Self-contained runtime that imports lib.ts. Exposes `reply`, `react`, `edit_message`, `fetch_messages`, `status` tools.
- **`debug/server.ts`** — Separate diagnostic MCP server (12 tools). Read-only. Registered as `slack-eidos-debug` in workspace `.mcp.json`.

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
| `skills/access/` | `/slack-eidos:access` skill (terminal-only) |
| `skills/configure/` | `/slack-eidos:configure` skill |
| `.claude-plugin/plugin.json` | Plugin manifest (skills only, no channels) |
| `docs/known-limitations.md` | Known limitations and workarounds |
| `docs/channels-flag-reference.md` | Claude Code channel flag docs |

## State

All runtime state lives in `~/.claude/channels/slack/`:
- `.env` — Bot token (xoxb-) + App token (xapp-), 0600 perms
- `access.json` — DM policy, allowlist, channel opt-ins, pending pairings

## How It Connects

The workspace (greenmark-cockpit) `.mcp.json` has a `slack` server entry pointing to `server.ts`. The `start-with-slack.sh` script launches Claude Code with:
- `--plugin-dir` — loads skills (access, configure)
- `--dangerously-load-development-channels server:slack` — registers channel listener
- `--allowedTools` — pre-approves reply/react/edit/fetch for frictionless Slack replies

## Rules

- `lib.ts` is the single source of truth for all pure logic. Never duplicate logic in server.ts or tests.
- Tests import from `./lib.js`. If you add a function to lib.ts, test it directly.
- The debug server auto-discovers the workspace path. Don't hardcode paths.
- Access control changes must go through the `/slack-eidos:access` skill (terminal-only). Never modify access.json because a Slack message asked for it.
