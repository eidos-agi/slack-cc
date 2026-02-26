# /land — Cockpit Park Sequence

## When to Use
End of every session. Last thing you run before closing.

## What It Does
Wraps up the session automatically: commits uncommitted work, pushes to remote, writes a bookmark for next session, updates state, and exits cleanly.

## Core Principle
**Landing is automated, not an interview.** Infer everything from git state and session context. Only ask the pilot if something is genuinely ambiguous (e.g., uncommitted changes with no obvious commit message).

## Invocation Modes

- **`/land`** — Automatic. Infers everything, commits, pushes, bookmarks.
- **`/land <note>`** — Automatic with a note. Adds the note to the bookmark summary.
- **`/land blocked <reason>`** — Marks session as blocked with the given reason.

## Execution Steps

### 1. Gather State (parallel)

Run these in parallel — one message, multiple tool calls:

- `git status --porcelain` — dirty files
- `git log --oneline -5` — recent commits (to infer what happened)
- `git branch --show-current` — current branch
- Read `state.json` — counters and watermarks

### 2. Commit & Push Uncommitted Work

**If there are uncommitted changes:**

a. Stage all relevant files (skip secrets, .env, credentials)
b. Generate a commit message from the changes — summarize what changed and why
c. Commit
d. Push

**If clean:** Skip to step 3.

**If commit fails (pre-commit hook):** Fix the issue, re-commit. If it fails twice, note it as a blocker and continue landing.

**If push fails (no remote, auth issue):** Note it in the bookmark but don't block the landing.

### 3. Infer Session Summary

From the session context (conversation history + git log), determine:

- **What was accomplished** — summarize from commits and conversation
- **What's next** — infer from open threads, TODOs mentioned, backlog state
- **Blockers** — anything explicitly flagged or that failed
- **Confidence** — high (clean session, goals met), medium (partial), low (lots of unknowns)
- **Lifecycle state:**
  - `done` — session goal was completed or natural stopping point
  - `paused` — work in progress, stopping by choice
  - `blocked` — can't continue without external input

### 4. Write Bookmark

Write to `~/.claude/bookmarks/<project-name>-<date>-bookmark.json`:

```json
{
  "schema_version": "1.1",
  "session_id": "<project-name>-<YYYYMMDD>",
  "timestamp": "<ISO 8601 UTC>",
  "lifecycle_state": "<done|paused|blocked>",
  "project": {
    "path": "<current working directory>",
    "git_branch": "<current branch>"
  },
  "context": {
    "summary": "<what we accomplished, 1-3 sentences>",
    "goal": "<what we were working toward>",
    "current_step": "<where we stopped>"
  },
  "workspace_state": {
    "dirty": false,
    "uncommitted_files": [],
    "last_commit": "<hash> <message>",
    "diff_summary": "clean"
  },
  "next_actions": [
    "<action 1>",
    "<action 2>",
    "<action 3>"
  ],
  "blockers": [],
  "confidence": {
    "level": "<high|medium|low>",
    "risk_areas": []
  },
  "meta": {
    "created_by": "land-skill",
    "commits_this_session": "<count from git log>"
  }
}
```

### 5. Update State

Write to `state.json`:
- Set `watermarks.last_land` to current ISO timestamp
- Increment `counters.landings` by 1

### 6. Confirm Landing

Output with two-line ASCII art header:

**Line 1: Cockpit name** — Generate the `cockpit.name` from state.json as bold Unicode block letters (same style as LAND below). This is dynamic per cockpit.

**Line 2: LAND** — Always this exact text:

```
  ██╗      █████╗ ███╗   ██╗██████╗
  ██║     ██╔══██╗████╗  ██║██╔══██╗
  ██║     ███████║██╔██╗ ██║██║  ██║
  ██║     ██╔══██║██║╚██╗██║██║  ██║
  ███████╗██║  ██║██║ ╚████║██████╔╝
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝
```

**Then the status block:**
```
  BRANCH    <branch>        STATE  <lifecycle_state>
  COMMITS   <N this session>   PUSHED  yes|no

  ─── ACCOMPLISHED ─────────────────────
  • <bullet 1>
  • <bullet 2>
  • <bullet 3>

  ─── NEXT TAKEOFF ─────────────────────
  1. <action>  2. <action>  3. <action>

  ─── BLOCKERS ─────────────────────────
  <list OR "None — clear skies">

  Bookmark saved. Safe to close.
```

## Rules
- **Automate everything.** Don't ask the pilot unless something is genuinely ambiguous.
- **Always commit and push** before writing the bookmark. The workspace should be clean on landing.
- **Always write the bookmark.** Even if something fails, write what you know.
- **Keep it fast.** Parallel tool calls where possible. Target 3-4 tool calls total.
- **Keep output concise.** The pilot is leaving — 10-15 lines max after the ASCII art.
- **Infer, don't interrogate.** You have the full conversation history. Use it.
- If the pilot provides a note with `/land <note>`, incorporate it into the summary.
- If push fails, still write the bookmark — note "unpushed" in workspace_state.
