# /touch-and-go — Land, Compact, Take Back Off

## When to Use
Mid-session. After a milestone, before a risky change, or when context is getting heavy.

## What It Does
Runs the full `/land` sequence (save, sync, scan, bookmark) — then stays in the air. Context compacts. The cockpit stays open.

## How It's Different from /land
- `/land` = park the plane, close the cockpit, walk away
- `/touch-and-go` = land, save everything, take off again

The only differences:
1. Bookmark gets `lifecycle_state: "flying"` instead of `"done"`
2. Output is 5 lines instead of the full ASCII debrief
3. The session continues

## Execution

### 1-5. Run the /land checkpoint steps

Follow every step in `_shared/checkpoint.md`:
1. **Save** — gather state, commit, push
2. **Sync outward** — update ike tasks, close issues, comment Wrike, check StepProof
3. **Scan inbound** — glance at Slack, GitHub PRs/CI, Wrike
4. **Write bookmark** — with `lifecycle_state: "flying"`
5. **Update state** — set `watermarks.last_touch_and_go`, increment counter

### 6. Confirm

```
  TOUCH AND GO — <branch> — <N> files committed, pushed
  <one-line summary of what was saved>
  Synced: <N> tasks updated, <N> issues closed
  Inbound: <anything urgent, or "clear">
  Context saved. Safe to compact. Continuing...
```

Five lines max. Get back to work.

## Context Compaction

Touch-and-go is the natural compaction point. After persisting to 4 stores (git, bookmark, devlog, memory), the conversation tokens are redundant. The system's automatic context compression can safely reclaim them.

**If the session is getting long (>50 tool calls without a checkpoint), proactively suggest touch-and-go.** Not /land — touch-and-go. The pilot stays in the air, but the context gets relief.

## Rules

- **Fast and silent.** This is a save point, not a ceremony. Minimize output.
- **Never ask questions.** Infer everything. The pilot is in flow.
- **Always push.** The point is durability.
- **Always write the bookmark.** Even if commit fails.
- **Don't suggest /land.** The pilot called touch-and-go because they're not done.
- **Encourage compaction.** After persisting, note that context is safe to compress.
