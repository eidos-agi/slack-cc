# /touch-and-go — Mid-Flight Checkpoint

## When to Use
Mid-session. When you want to save state without ending the session. After a milestone, before a risky change, or when you've been flying for a while.

## What It Does
Commits, pushes, writes a checkpoint bookmark, updates devlog — then keeps going. The cockpit stays open. You stay in the air.

## How It's Different from /land
- `/land` = park the plane, close the cockpit, walk away
- `/touch-and-go` = touch the runway, save state, take off again

The bookmark written by touch-and-go has `lifecycle_state: "flying"` — it's a snapshot, not a farewell.

## Invocation Modes

- **`/touch-and-go`** — Auto checkpoint. Infer summary from recent work.
- **`/touch-and-go <note>`** — Checkpoint with a note.

## Execution Steps

### 1. Gather State (parallel)

- `git status --porcelain`
- `git log --oneline -3`
- `git branch --show-current`
- Read `state.json`

### 2. Commit & Push

If dirty:
1. Stage relevant files (skip secrets)
2. Commit with descriptive message
3. Push

If clean: skip.

### 3. Write Checkpoint Bookmark

Write to `~/.claude/bookmarks/<project-name>-<date>-bookmark.json`:

Same schema as `/land` bookmark but with:
```json
{
  "lifecycle_state": "flying",
  "context": {
    "summary": "<what we've done so far>",
    "goal": "<what we're still working toward>",
    "current_step": "<what we're doing right now>"
  }
}
```

### 4. Update State

- Set `watermarks.last_touch_and_go` to current ISO timestamp
- Increment `counters.touch_and_gos` by 1 (create if missing)

### 5. Confirm

Short output — pilot is still working, don't interrupt flow:

```
  TOUCH AND GO — <branch> — <N> files committed, pushed
  <one-line summary of what was saved>
  Continuing...
```

That's it. Three lines max. Get back to work.

## Context Compaction

Touch-and-go is the natural compaction point. After persisting state:

1. **Devlog captures the narrative** — decisions, findings, bugs, learnings are written down
2. **Git captures the code** — diffs are committed, tool results are superseded
3. **Bookmark captures the position** — what we're doing, what's next
4. **Memory captures the durable knowledge** — preferences, patterns, project context

Once those four stores are written, the conversation tokens holding that same information are redundant. The system's automatic context compression can safely reclaim them because the important bits are persisted outside the conversation.

**After touch-and-go, tell the pilot:**
```
  Context saved to 4 stores (git, bookmark, devlog, memory).
  Conversation context is safe to compact — all state is persisted.
```

This is why touch-and-go matters for long sessions. Without it, the context window fills with stale reads and old tool results. With it, you periodically flush to durable storage and let the context breathe.

**If the session is getting long (>50 tool calls without a checkpoint), proactively suggest touch-and-go.** Not /land — touch-and-go. The pilot stays in the air, but the context gets relief.

## Rules

- **Fast and silent.** This is a save point, not a ceremony. Minimize output.
- **Never ask questions.** Infer everything. The pilot is in flow.
- **Always push.** The point is durability. If push fails, warn but continue.
- **Always write the bookmark.** Even if commit fails.
- **Don't suggest /land.** The pilot called touch-and-go because they're not done.
- **Don't run /can-i-close.** That's for when you're actually stopping.
- **Encourage compaction.** After persisting, note that context is safe to compress.
