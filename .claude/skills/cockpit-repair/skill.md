# /cockpit-repair — Validate and Fix Cockpit State

## When to Use
When `/takeoff` reports corruption, when state.json seems wrong, or when bookmarks aren't loading properly. Also useful after a crash or unexpected session termination.

## What It Does
Validates all cockpit state files, reports issues, and offers to fix them.

## Execution Steps

### 1. Validate state.json

- Check if `state.json` exists in the cockpit root
- If missing: offer to create a fresh one from the template schema
- If exists: validate structure
  - Required keys: `cockpit`, `watermarks`, `counters`
  - Required cockpit fields: `name`, `version`
  - Required watermark fields: `last_takeoff`, `last_land`, `last_status_check`
  - Required counter fields: `sessions`, `takeoffs`, `landings`
  - Counters must be non-negative integers
  - Watermarks must be null or valid ISO 8601 timestamps
  - `custom` key should exist (even if empty `{}`)

Report:
```
state.json: OK | MISSING | CORRUPT (<issue>)
```

### 2. Validate Bookmarks

- Scan `~/.claude/bookmarks/` for `*-bookmark.json` files matching current project path
- For each matching bookmark:
  - Validate JSON parses correctly
  - Validate required fields: `schema_version`, `session_id`, `timestamp`, `lifecycle_state`, `project`
  - Check `lifecycle_state` is one of: `done`, `paused`, `blocked`, `auto-closed`
  - Check `timestamp` is valid ISO 8601
- Count: total bookmarks, valid, corrupted

Report:
```
Bookmarks: <N> found, <M> valid, <K> corrupted
Latest: <session_id> (<lifecycle_state>, <time ago>)
```

### 3. Validate Skills

- Check `.claude/skills/` directory exists
- List all skill folders
- For each: verify `skill.md` exists and is non-empty
- Flag any empty or missing skill.md files

Report:
```
Skills: <N> installed
- takeoff/     OK
- land/        OK
- cockpit-status/ OK
- <domain>/    OK | MISSING skill.md
```

### 4. Check for Orphaned State

- Look for `.pending-sync.json` in bookmarks dir — report if present
- Look for heartbeat files (`.heartbeat-*.json`) — report if present (may indicate crashed sessions)
- Check if state.json counters make sense (takeoffs >= landings, sessions >= takeoffs)

Report:
```
Pending sync: yes | no
Orphan heartbeats: <N> found
Counter sanity: OK | MISMATCH (takeoffs: N, landings: M)
```

### 5. Offer Fixes

For each issue found, offer a specific fix:

| Issue | Fix |
|-------|-----|
| state.json missing | Create from template schema |
| state.json corrupt | Rewrite with defaults, preserve `custom` if parseable |
| Bookmark corrupt | Delete the corrupted bookmark file |
| Skill missing skill.md | Flag for manual attention (don't auto-create) |
| Pending sync orphaned | Process it (devlog_add) or delete it |
| Counter mismatch | Reset counters to match bookmark history |

**Ask before applying any fix.** Show what will change.

### 6. Summary

```
COCKPIT REPAIR: <cockpit name>
State:     <OK | fixed N issues>
Bookmarks: <OK | removed N corrupted>
Skills:    <OK | N warnings>
Counters:  <OK | reset>
```

## Rules
- Never delete bookmarks without asking first.
- Never overwrite state.json custom fields without asking first.
- If everything is healthy, just say "All clear. Cockpit is healthy." and stop.
- This is a diagnostic tool, not a destructive one. Ask before every fix.
