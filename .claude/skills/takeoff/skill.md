# /takeoff — Cockpit Boot Sequence

## When to Use
Start of every session. This is the first thing you run.

## What It Does
Pre-flight check in 2 cheap reads (git state is already in context), then a concise briefing. No questions asked — just show the state and wait for orders.

## Execution Steps

### 1. Read State (2 reads + context reuse)

**A. state.json** — from the cockpit root
- Get `watermarks.last_land` (when was the last session?)
- Get `counters.sessions` (how many sessions total?)
- If `last_land` is null, this is the first session ever — say so

**B. Latest bookmark** — scan `~/.claude/bookmarks/` for the most recently modified `*-bookmark.json` whose `project.path` matches the current working directory
- If found: read it for `lifecycle_state`, `context.summary`, `next_actions`, `blockers`, `confidence`
- If not found: note "No previous bookmark for this cockpit"

**C. Git state** — use the `gitStatus` block injected at session start
- Current branch, dirty files, recent commits are **already in context**
- **Do NOT re-run** `git status`, `git branch`, or `git log` — they're already there
- Only run git commands if `gitStatus` is missing from context (fallback)

### 2. Detect Drift

Compare current git state to bookmark's `workspace_state`:
- **Branch changed?** Flag it: `DRIFT: Branch changed from X to Y`
- **New commits since bookmark?** Flag it: `DRIFT: N new commits since last session`
- **Dirty files that weren't dirty before?** Flag it: `DRIFT: N files modified outside session`
- **Clean when bookmark said dirty?** Note: `Files from last session were committed`

### 3. Output Briefing

Output ONE concise block with two-line ASCII art header:

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

**Then the status block:**
```
  BRANCH    <branch>          DIRTY  <yes (N) | clean>
  SESSION   #<N+1>            LAST   <time since last land>
```

**Block letter reference** — use this character set for generating the cockpit name:
```
█ ═ ╗ ╔ ╚ ╝ ║ ╠ ╣ ╦ ╩ ╬ ▀ ▄
```
Match the exact same visual weight and style as the TAKEOFF text above. Each letter should be 6-7 chars wide and 6 lines tall.

If there's a bookmark summary:
```
 RESUME    <bookmark summary>
```

If there are next_actions from the bookmark:
```
Next actions:
1. <action>
2. <action>
3. <action>
```

If there are blockers:
```
BLOCKED: <blocker description>
```

If drift was detected:
```
DRIFT: <what changed>
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
- Maximum 2 file reads. Reuse gitStatus from session context. Keep it fast.
- Never re-fetch git state that's already in session context.
- Never ask questions during takeoff. Just show state.
- If the previous session was `lifecycle_state: done`, just note "Previous session completed" and move on.
- If the previous session was `lifecycle_state: blocked`, highlight the blocker prominently.
- Keep the briefing to 5-10 lines max. The user is here to work, not read.
- If no bookmark exists and no state.json exists, this is a fresh cockpit — say "First flight. Cockpit initialized." and create state.json.
- If bookmark file is corrupted or unreadable, note "Bookmark corrupted — starting fresh" and continue without it.
