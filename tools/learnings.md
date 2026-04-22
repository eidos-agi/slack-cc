# slack-cc Learnings

Accumulated knowledge from doctor runs and debugging sessions. Read this FIRST before diagnosing anything.

## 2026-04-21 — Channel listener requires --dangerously flag

**Symptom:** Bot reacts with 👀, `deliver.ok` fires in logs, but no `<channel>` tag appears in Claude session.
**Root cause:** `--channels plugin:slack-cc@eidos-agi` does NOT register the channel listener for private marketplace plugins. Only Anthropic-approved plugins get `--channels`. Private plugins MUST use `--dangerously-load-development-channels plugin:slack-cc@eidos-agi`.
**Fix:** Updated start-with-slack.sh to use `--dangerously-load-development-channels`.
**Prevention:** Always check Claude Code debug log for "Channel notifications skipped" and "not on the approved channels allowlist" after any launch.

## 2026-04-21 — Marketplace plugins need auto-install deps

**Symptom:** Plugin installs from marketplace but server fails to start silently.
**Root cause:** `claude plugin install` clones the repo but does NOT run `npm install`. No node_modules = server.ts can't import anything.
**Fix:** Changed package.json `start` script to `npm install --silent && tsx server.ts`. Changed .mcp.json to use `npm start --prefix ${CLAUDE_PLUGIN_ROOT}` instead of raw `npx tsx`.
**Prevention:** The Telegram plugin uses `bun install && bun server.ts` — same pattern. Any marketplace plugin with npm deps needs this.

## 2026-04-21 — Tool prefix for marketplace plugins is mcp__plugin_<name>_<server>__

**Symptom:** `--allowedTools "mcp__slack-cc__reply"` doesn't match. Tools still prompt.
**Root cause:** Claude Code names marketplace plugin tools as `mcp__plugin_<pluginName>_<serverName>__<toolName>`. For slack-cc with server name slack-cc, it's `mcp__plugin_slack-cc_slack-cc__reply`.
**Fix:** Updated --allowedTools in start script and settings.local.json.
**Prevention:** Check the `deferred tools` list in system reminders — it shows the exact tool names Claude Code assigned.

## 2026-04-21 — Five names must match for a plugin to work

**Symptom:** Various mismatches cause silent failures.
**Root cause:** These five must be identical:
1. `.claude-plugin/plugin.json` → `name`
2. `.claude-plugin/plugin.json` → `channels[0].server`
3. `.mcp.json` → server key name
4. `server.ts` → `new Server({ name: '...' })`
5. Skill SKILL.md → `/<name>:access`, `/<name>:configure`

If any diverge, Claude Code may load the MCP server but not register the channel, or skills may not map correctly.
**Prevention:** `tools/preflight.sh` checks all five. Run after any rename.

## 2026-04-21 — Process count false positive in debug tool

**Symptom:** `slack_debug_check` reports "DUAL-START: 3 processes" when only one bridge is running.
**Root cause:** `npm start` spawns `sh -c` → `tsx` → `node`. The debug tool greps for `tsx.*server.ts` and counts all three. They're one process chain, not three competing instances.
**Fix:** Known false positive. True dual-start only happens when processes come from DIFFERENT install paths (e.g., workspace .mcp.json + marketplace plugin both starting server.ts).
**Prevention:** Check the `command` field in process list — if all point to the same install path, it's one instance.

## 2026-04-21 — Socket Mode debug test gives invalid_auth while bridge is connected

**Symptom:** `slack_debug_socket_mode` returns `invalid_auth` even though the bridge is working.
**Root cause:** The debug tool calls `apps.connections.open` to test the app token. But Socket Mode only allows ONE connection per token. The running bridge already holds it. The debug tool's test fails because the slot is taken — not because the token is bad.
**Prevention:** If the bridge's own `status` tool shows `socketMode: "connected"`, ignore the debug tool's `invalid_auth`. Only trust `socket_mode` results when the bridge is NOT running.

## 2026-04-21 — Removing workspace .mcp.json "slack" entry is required for marketplace

**Symptom:** Two server instances compete for Socket Mode. Or: workspace server gets the channel listener but marketplace plugin doesn't.
**Root cause:** If workspace `.mcp.json` has a "slack" (or "slack-cc") entry AND the marketplace plugin is installed, both start a server.ts instance.
**Fix:** Remove the workspace `.mcp.json` entry. Let the marketplace plugin be the only server. Keep `slack-cc-debug` in workspace .mcp.json (it's a separate server).
**Prevention:** After switching to marketplace, grep workspace .mcp.json for any slack server entries and remove them.
