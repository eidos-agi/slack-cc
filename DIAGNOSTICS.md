# Diagnostics Guide

cc-channel-slack-eidos writes structured JSON logs to stderr. Claude Code captures these in `~/.claude/debug/<session-id>.txt`. Every log entry includes a timestamp, uptime, transport status, and session channel count.

## Reading the logs

```bash
# Live tail during a session (find the session ID from claude --debug)
tail -f ~/.claude/debug/<session-id>.txt | grep cc-slack

# Or parse the JSON
tail -f ~/.claude/debug/<session-id>.txt | grep '"event":' | jq .
```

## Log events

### Boot

| Event | Meaning |
|-------|---------|
| `boot.complete` | Server started. Shows botUserId, dmPolicy, permanent channels, pending pairings. If botUserId is "unknown", self-echo filtering is disabled. |

### Inbound flow

| Event | Meaning |
|-------|---------|
| `slack.inbound` | Slack event received. Shows channel, user, ts, first 80 chars of text. |
| `dedup.dropped` | Duplicate event (same channel+ts seen within 60s). Expected for message + app_mention on same event. |
| `gate.drop` | Message rejected. Check `reason` field: `self-echo`, `bot-message`, `subtype:*`, `no-user`, `dm-disabled`, `dm-not-allowlisted`, `channel-not-opted-in`, `channel-user-not-allowed`, `mention-required`. |
| `gate.auto-opt-in` | Allowlisted user @mentioned bot in new channel. Session-scoped opt-in created. |
| `gate.pair` | Unknown DM user in pairing mode. Code issued. |
| `deliver.start` | Gate passed, building notification payload. |
| `deliver.ok` | `mcp.notification()` completed. If messages still don't appear in the session, the channel listener isn't registered (see Troubleshooting). |
| `deliver.fail` | `mcp.notification()` threw an error. Check `error` field. |

### Commands

| Event | Meaning |
|-------|---------|
| `command.help` | User sent "help" — help text served. |
| `command.debug` | User sent "debug" — diagnostics dumped to Slack. |
| `command.permission-reply` | User sent "yes/no <id>" — verdict forwarded to Claude Code. |

## Troubleshooting

### "deliver.ok" but no `<channel>` tag in session

The notification fired successfully over stdio but Claude Code isn't surfacing it. This means the **channel listener isn't registered**.

**Cause:** You started or resumed the session without `--dangerously-load-development-channels server:slack`. The MCP server loads (tools work), but Claude Code never set up a listener for `notifications/claude/channel`.

**Fix:** Exit and start fresh:
```bash
claude --plugin-dir ~/repos/cc-channel-slack-eidos --dangerously-load-development-channels server:slack
```

**Also suspected:** Using `/resume` inside a running session may drop the channel listener even if the original session had it. If messages stop after a `/resume`, exit and restart.

### "gate.drop" with reason "channel-not-opted-in"

The channel isn't connected. Either:
- @mention the bot (session-scoped, requires being on allowlist)
- Run `/slack-channel:access channel <id>` in the terminal (permanent)

### "gate.drop" with reason "dm-not-allowlisted"

User isn't on the allowlist and DM policy is `allowlist`. Either:
- Change policy to `pairing`: `/slack-channel:access policy pairing`
- Add the user: `/slack-channel:access add <user_id>`

### No logs at all

The MCP server isn't running. Check:
1. Did you pass `--plugin-dir ~/repos/cc-channel-slack-eidos`?
2. Are deps installed? `cd ~/repos/cc-channel-slack-eidos && npm install`
3. Does the server start? `timeout 5 ./node_modules/.bin/tsx server.ts 2>&1`

### "deliver.fail" with transport error

The MCP stdio connection broke. This usually means Claude Code crashed or the session ended while the bot was still running. Restart.

## Using "debug" from Slack

Send `@Cerebro Development debug` (exact match, nothing else) in any connected channel. The bot replies in-thread with:

- MCP transport status
- Bot user ID
- Uptime
- Session channels (ephemeral)
- Permanent channels (access.json)
- DM policy and allowlist
- Recent delivered threads
- Dedup cache and pending permissions count
- The `/resume` warning

This is the fastest way to diagnose from your phone without terminal access.
