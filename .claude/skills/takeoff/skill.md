# /takeoff — Cockpit Boot Sequence

## When to Use
Start of every session. This is the first thing you run.

## What It Does
Shows the ASCII art header, status bar, and drift detection. Then composes `/pre-flight` (as a subagent) to produce the full situational briefing. Waits for orders.

## Execution Steps

### 1. Gather Core State (cheap, in main context)

**A. state.json** — from the cockpit root
- Get `cockpit.name` (for the ASCII art header)
- Get `watermarks.last_land` (when was the last session?)
- Get `counters.sessions` (how many sessions total?)
- If `last_land` is null, this is the first session ever

**B. Latest bookmark** — scan `~/.claude/bookmarks/` for the most recently modified `*-bookmark.json` whose `project.path` matches the current working directory
- If found: read it for `lifecycle_state`, `context.summary`, `next_actions`, `blockers`, `confidence`
- If not found: note "No previous bookmark for this cockpit"

**C. Git state** — use the `gitStatus` block injected at session start
- Current branch, dirty files, recent commits are **already in context**
- **Do NOT re-run** `git status`, `git branch`, or `git log` — they're already there

### 2. Output ASCII Art Header

**Line 1: Cockpit name** — Generate the `cockpit.name` from state.json as bold Unicode block letters (same style as TAKEOFF below). This is dynamic per cockpit.

**Line 2: TAKEOFF** — Always this exact text:

```
  ████████╗ █████╗ ██╗  ██╗███████╗ ██████╗ ███████╗███████╗
  ╚══██╔══╝██╔══██╗██║ ██╔╝██╔════╝██╔═══██╗██╔════╝██╔════╝
     ██║   ███████║█████╔╝ █████╗  ██║   ██║█████╗  █████╗
     ██║   ██╔══██║██╔═██╗ ██╔══╝  ██║   ██║██╔══╝  ██╔══╝
     ██║   ██║  ██║██║  ██╗███████╗╚██████╔╝██║     ██║
     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝
```

**Block letter reference** — use this character set for generating the cockpit name:
```
█ ═ ╗ ╔ ╚ ╝ ║ ╠ ╣ ╦ ╩ ╬ ▀ ▄
```
Match the exact same visual weight and style as the TAKEOFF text above. Each letter should be 6-7 chars wide and 6 lines tall.

**Then the status bar:**
```
  BRANCH    <branch>          DIRTY  <yes (N) | clean>
  SESSION   #<N+1>            LAST   <time since last land>
```

If drift was detected (compare git state to bookmark's `workspace_state`):
```
  DRIFT     <branch changed / N new commits / N files modified outside session>
```

### 3. Compose /pre-flight

Launch the `/pre-flight` skill as a **subagent** (Task tool, `subagent_type: "Explore"`) to scan the workspace and produce the four-part briefing.

Pass the subagent:
- The current working directory
- Bookmark context (summary, next_actions, blockers, lifecycle_state)
- Instructions to read the `/pre-flight` skill at `.claude/skills/pre-flight/skill.md` and follow it

**Output the subagent's result directly below the status bar.**

The result should be the four-part briefing:
```
WHERE WE WERE
  ...

WHERE WE ARE
  ...

WHERE WE'RE GOING
  1. ...
  2. ...
  3. ...

BLOCKERS
  ...
```

### 4. Update State

Write to `state.json`:
- Set `watermarks.last_takeoff` to current ISO timestamp
- Increment `counters.sessions` by 1
- Increment `counters.takeoffs` by 1

### 5. STOP

Do NOT proceed with any work. Output:

```
Ready for orders.
```

And wait for the user to tell you what to do.

## Rules
- Reuse gitStatus from session context. Never re-fetch what's already there.
- The subagent (pre-flight) does the heavy scanning. Main context stays lean.
- Never ask questions during takeoff. Just show state.
- If no bookmark exists and no state.json exists, this is a fresh cockpit — say "First flight. Cockpit initialized." and create state.json. Still run pre-flight.
- If bookmark file is corrupted or unreadable, note "Bookmark corrupted — starting fresh" and continue.
