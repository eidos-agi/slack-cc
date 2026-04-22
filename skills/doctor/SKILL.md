---
name: doctor
description: Self-diagnose, fix, and learn from Slack bridge issues. Run when something's wrong, after changes, or before asking Daniel to restart. Fixes what it can, records what it learns.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - mcp__slack-cc-debug__slack_debug_check
  - mcp__slack-cc-debug__slack_debug_channel_reg
  - mcp__slack-cc-debug__slack_debug_bot_process
  - mcp__slack-cc-debug__slack_debug_socket_mode
  - mcp__slack-cc-debug__slack_debug_send_test
  - mcp__slack-cc-debug__slack_debug_roundtrip
  - mcp__slack-cc-debug__slack_debug_scope_diff
  - mcp__slack-cc-debug__slack_debug_logs
---

# /slack-cc:doctor

Self-diagnose, fix, and learn from Slack bridge issues. This is the agent's primary tool for maintaining the bridge — not Daniel's.

## When to Run

- After any code change to the plugin
- Before asking Daniel to restart
- When inbound or outbound stops working
- After a rename, refactor, or version bump
- Proactively after `npm test` passes but before declaring "done"

## Instructions

### Phase 1: Read learnings first

Read `tools/learnings.md` in the plugin repo. This file contains lessons from previous doctor runs — patterns that broke before, fixes that worked, gotchas to check. **Do not skip this.** Past learnings prevent repeat mistakes.

### Phase 2: Run diagnostics

Run these debug tools and collect results:
1. `slack_debug_check` — full health check
2. `slack_debug_channel_reg` — channel listener registration
3. `slack_debug_bot_process` — process state
4. `slack_debug_socket_mode` — Socket Mode liveness

Also run independently:
5. `tools/preflight.sh` — structural validation (names, versions, consistency)
6. `npm test` from the plugin repo — all 120+ tests pass?
7. `claude plugin validate` — manifest valid?

### Phase 3: Diagnose

Compare results against known patterns from learnings.md. Common issues:

**"Eyeballs but no `<channel>` tag"**
- Channel listener not registered. Check debug log for "Channel notifications skipped"
- Cause is ALWAYS the launch flag. Must use `--dangerously-load-development-channels plugin:slack-cc@eidos-agi`
- The `--channels` flag does NOT work for private marketplace plugins
- If the debug log says "not on the approved channels allowlist" — this is why

**"No eyeballs"**
- Socket Mode not connected. Check app token (xapp-) validity
- Or: server didn't start. Check if node_modules exist in install path
- Or: stale process holding Socket Mode slot

**"Tools prompt for approval"**
- `--allowedTools` flag has wrong prefix
- Claude Code tool prefix for marketplace plugins is: `mcp__plugin_<pluginName>_<serverName>__`
- Check by looking at deferred tool names in system reminders

**"Name mismatch"**
- plugin.json `name`, plugin.json `channels[].server`, .mcp.json server key, and server.ts `Server({ name: })` must ALL match
- Skill prefix `/<name>:` must match plugin name
- Any rename must hit ALL of these

**"Process count looks wrong"**
- `npm start` spawns: sh → npm → tsx → node. That's 3-4 processes for ONE instance
- Only flag as dual-start if processes come from DIFFERENT install paths

### Phase 4: Fix

Fix everything you can without a restart:
- File edits (names, configs, versions)
- npm install if deps missing
- Kill stale processes
- Update marketplace if version mismatch

Things that REQUIRE a restart (tell Daniel):
- Changes to plugin.json, .mcp.json, or server.ts
- Channel listener registration changes
- Marketplace plugin reinstall

### Phase 5: Verify

After fixes, re-run the diagnostics that failed. Confirm they pass now. If they don't, diagnose again — don't declare victory.

### Phase 6: Learn

Append to `tools/learnings.md`:
- Date
- What was wrong
- What fixed it (or what couldn't be fixed)
- What to check next time to catch this earlier

Format:
```
## YYYY-MM-DD — <short title>
**Symptom:** ...
**Root cause:** ...
**Fix:** ...
**Prevention:** Check X before Y next time.
```

### Phase 7: Report

Tell Daniel:
- What was wrong
- What you fixed
- Whether a restart is needed
- The exact launch command if restart is needed

Do NOT present option menus. Do NOT ask "what should I do?" Fix it or explain why you can't.
