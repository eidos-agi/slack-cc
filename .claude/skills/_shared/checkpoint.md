# Checkpoint Steps — Shared by /touch-and-go and /land

These steps run in both skills. Touch-and-go runs them and keeps flying. Land runs them and parks.

## Save

### Gather State (parallel)
- `git status --porcelain`
- `git log --oneline -5`
- `git branch --show-current`
- Read `state.json`

### Commit & Push
If dirty:
1. Stage relevant files (skip secrets, .env, credentials)
2. Commit with descriptive message
3. Push

If clean: skip.

If commit fails (pre-commit hook): fix, retry once. If still fails, note as blocker.
If push fails: warn but continue.

## Sync Outward

Flush progress to external systems. This is where task management stays current:

- **ike.md** — Mark completed tasks done. Update in-progress tasks with notes. Create new tasks discovered during work.
- **GitHub issues** — Close issues that were fixed. Update issue comments with progress. Check for new CI failures on other repos.
- **Wrike** — If Greenmark Wrike tasks were touched, comment with progress (never create new tasks — only comment on existing ones per reference_wrike_structure.md).
- **StepProof** — If a run is active, verify current step status is accurate. If a run completed, note it.

Only sync what changed since the last checkpoint. Don't audit everything — just flush what's in your head.

## Scan Inbound

Quick glance at the instruments — are there signals you've been ignoring?

- **Slack** — Unread messages in connected channels (use `fetch_messages` if available)
- **GitHub** — PR reviews waiting, CI failures, dependabot PRs piling up
- **Wrike** — New comments from Michael/Alex/Robert

Don't act on these during touch-and-go. During land, note them in `next_actions` so the next session picks them up.

## Write Bookmark

Write to `~/.claude/bookmarks/<project-name>-<date>-bookmark.json` using the standard schema.

- Touch-and-go sets `lifecycle_state: "flying"`
- Land sets `lifecycle_state: "done" | "paused" | "blocked"`

## Update State

- Set `watermarks.last_touch_and_go` or `watermarks.last_land` to current ISO timestamp
- Increment the appropriate counter

## Context Compaction

After persisting state, the conversation tokens holding that same information are redundant:

1. **Git captures the code** — diffs committed, tool results superseded
2. **Bookmark captures the position** — what we're doing, what's next
3. **Devlog captures the narrative** — decisions, findings, learnings
4. **Memory captures the durable knowledge** — preferences, patterns, project context

Tell the pilot:
```
Context saved to 4 stores (git, bookmark, devlog, memory).
Conversation context is safe to compact — all state is persisted.
```
