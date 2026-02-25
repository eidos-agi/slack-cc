# /land — Cockpit Park Sequence

## When to Use
End of every session. Last thing you run before closing.

## What It Does
Captures the session outcome, writes a bookmark for next session, updates state, and exits cleanly.

## Execution Steps

### 1. Gather Session State (parallel)

**A. Git state** — run `git status --porcelain`, `git branch --show-current`, `git log --oneline -1`
- Current branch
- Dirty files (list them)
- Last commit hash + message
- Run `git diff --stat` for a diff summary

**B. Read state.json** — get current counters and watermarks

### 2. Ask ONE Question

Ask the user (inline, not a separate tool):

```
Landing checklist:
- What did we accomplish?
- What's next?
- Any blockers?
- Confidence: high / medium / low?

(You can answer all at once or just the ones that matter.)
```

Wait for the user's response before proceeding.

### 3. Write Bookmark

Write to `~/.claude/bookmarks/<session-id>-bookmark.json`:

```json
{
  "schema_version": "1.1",
  "session_id": "<current session ID>",
  "timestamp": "<ISO 8601 UTC>",
  "lifecycle_state": "<done|paused|blocked>",
  "project": {
    "path": "<current working directory>",
    "git_branch": "<current branch>"
  },
  "context": {
    "summary": "<user's accomplishments, condensed to 1-2 sentences>",
    "goal": "<what we were trying to do>",
    "current_step": "<where we stopped>"
  },
  "workspace_state": {
    "dirty": <true|false>,
    "uncommitted_files": [<list of dirty files>],
    "last_commit": "<hash> <message>",
    "diff_summary": "<git diff --stat output>"
  },
  "next_actions": [
    "<action 1>",
    "<action 2>",
    "<action 3>"
  ],
  "blockers": [<blockers if lifecycle_state is "blocked">],
  "confidence": {
    "level": "<high|medium|low>",
    "risk_areas": [<any risks mentioned>]
  },
  "meta": {
    "created_by": "manual"
  }
}
```

### 4. Update State

Write to `state.json`:
- Set `watermarks.last_land` to current ISO timestamp
- Increment `counters.landings` by 1

### 5. Confirm Landing

Output:

```
LANDED: <cockpit name> | Branch: <branch> | State: <lifecycle_state>
Summary: <1-line summary>
Next: <top priority for next session>
Bookmark written. Safe to close.
```

## Rules
- Only ONE question to the user. Don't interrogate.
- If the user says "just land" or gives a terse response, infer what you can from the session context and fill in the bookmark.
- If the user doesn't respond to the question (e.g., they just want to close), write the bookmark with what you know from the session. Use `confidence.level: "low"` and note "Auto-inferred from session context" in the summary.
- Always write the bookmark. Even a low-confidence bookmark is better than nothing.
- Keep the confirmation to 3-4 lines. The user is leaving.
- lifecycle_state:
  - `done` — session goal was completed
  - `paused` — work in progress, stopping by choice
  - `blocked` — can't continue without external input
