# Known Limitations

## 1. `/resume` drops the channel listener

**Status:** Known limitation of Claude Code's channel plugin protocol
**Issue:** [#6](https://github.com/aic-holdings/cc-channel-slack-eidos/issues/6)

When you use `/resume` inside a running session to switch to a previous conversation, Claude Code may not re-register the channel listener. The MCP server stays running — tools work, the bot reacts with 👀 — but inbound `notifications/claude/channel` deliveries are silently dropped.

**How to detect:** Run `debug` in Slack. If transport shows connected but messages aren't appearing in your session, the listener is gone.

**Workaround:** Exit Claude Code entirely and restart:
```bash
./start-with-slack.sh
```

**Cannot fix in the bridge.** The channel listener registration is managed by Claude Code's runtime, not the MCP server.

## 2. Missing `channels:read` Slack scope

**Status:** Requires Slack app reconfiguration
**Issue:** [#4](https://github.com/aic-holdings/cc-channel-slack-eidos/issues/4)

The bot token is missing `channels:read`. The bot can read channel history (`channels:history`) but cannot list public channels. Diagnostics use a history-probe fallback to verify channel membership.

**Impact:** Cannot enumerate channels the bot belongs to. Limits future discovery features.

**Fix:** Add `channels:read` scope at api.slack.com → OAuth & Permissions, then reinstall to workspace.

## 3. Socket Mode: one poller per token

Telegram's Bot API has the same constraint. Only one process can consume events via `getUpdates` (Telegram) or Socket Mode (Slack) per token. If a stale process survives (e.g., Claude Code crashes without clean shutdown), the new session gets 409 Conflict.

The server handles this with a PID file (`~/.claude/channels/slack/bot.pid`) — on boot, it kills any stale holder. But if the PID was reused by an unrelated process, the kill is a false positive (harmless SIGTERM to a random process that ignores it).

## 4. Two-instance risk with `--plugin-dir`

**Status:** Fixed in v0.1.1
**Issue:** [#5](https://github.com/aic-holdings/cc-channel-slack-eidos/issues/5) (closed)

Previously, `--plugin-dir` started a second server instance (`plugin:slack-channel:slack`) alongside the workspace `.mcp.json` entry (`slack`). Both competed for Socket Mode. Fixed by removing the `channels` declaration from `plugin.json` — `--plugin-dir` now only loads skills.
