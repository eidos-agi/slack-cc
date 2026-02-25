# /land — Cockpit Park Sequence

## When to Use
End of every session. Last thing you run before closing.

## What It Does
Captures the session outcome, writes a bookmark for next session, updates state, and exits cleanly.

## Invocation Modes

- **`/land`** — Interactive. Asks one question, waits for response.
- **`/land <debrief>`** — Scripted. Uses the provided text as the debrief, skips asking.
- **`/land clean`** — Silent. Infers everything from git log and session context. No question.

## Execution Steps

### 1. Gather Session State

**A. Git state** — run `git status --porcelain`, `git log --oneline -1`, `git diff --stat`
- Current branch (reuse from session context if available)
- Dirty files (list them)
- Last commit hash + message
- Diff summary

**B. Read state.json** — get current counters and watermarks

### 2. Get Debrief

**If arguments were provided:** Use them as the debrief. Skip to step 3.

**If "clean" was provided:** Infer summary from git log and dirty files. Skip to step 3.

**Otherwise:** Ask the user (inline, not a separate tool):

```
Landing checklist:
- What did we accomplish?
- What's next?
- Any blockers?
- Confidence: high / medium / low?

(Answer all at once, or just say "clean" and I'll infer from context.)
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

Output with ASCII art:

```
    __                __
   / /___ _____  ___/ /
  / / __ `/ __ \/ __  /
 / / /_/ / / / / /_/ /
/_/\__,_/_/ /_/\__,_/

 COCKPIT   <cockpit name>
 STATE     <lifecycle_state>
 SUMMARY   <1-line summary>
 NEXT      <top priority for next session>

 Bookmark written. Safe to close.
```

## Rules
- Maximum 2 tool calls for the landing itself (bookmark write + state update). Keep it fast.
- Only ONE question to the user. Don't interrogate.
- If the user says "just land", "clean", or gives a terse response, infer what you can from the session context and fill in the bookmark.
- If the user doesn't respond to the question (e.g., they just want to close), write the bookmark with what you know from the session. Use `confidence.level: "low"` and note "Auto-inferred from session context" in the summary.
- Always write the bookmark. Even a low-confidence bookmark is better than nothing.
- Keep the confirmation to 5-6 lines. The user is leaving.
- lifecycle_state:
  - `done` — session goal was completed
  - `paused` — work in progress, stopping by choice
  - `blocked` — can't continue without external input
