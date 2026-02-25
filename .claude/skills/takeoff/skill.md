# /takeoff — Cockpit Boot Sequence

## When to Use
Start of every session. This is the first thing you run.

## What It Does
Pre-flight check in 3 cheap reads, then a concise briefing. No questions asked — just show the state and wait for orders.

## Execution Steps

### 1. Read State (3 parallel reads, all local)

**A. state.json** — from the cockpit root
- Get `watermarks.last_land` (when was the last session?)
- Get `counters.sessions` (how many sessions total?)
- If `last_land` is null, this is the first session ever — say so

**B. Latest bookmark** — scan `~/.claude/bookmarks/` for the most recently modified `*-bookmark.json` whose `project.path` matches the current working directory
- If found: read it for `lifecycle_state`, `context.summary`, `next_actions`, `blockers`, `confidence`
- If not found: note "No previous bookmark for this cockpit"

**C. Git state** — run `git status --porcelain` and `git branch --show-current` and `git log --oneline -3`
- Current branch
- Dirty files count
- Last 3 commits (for orientation)

### 2. Detect Drift

Compare current git state to bookmark's `workspace_state`:
- **Branch changed?** Flag it: `DRIFT: Branch changed from X to Y`
- **New commits since bookmark?** Flag it: `DRIFT: N new commits since last session`
- **Dirty files that weren't dirty before?** Flag it: `DRIFT: N files modified outside session`
- **Clean when bookmark said dirty?** Note: `Files from last session were committed`

### 3. Output Briefing

Output ONE concise block. Format:

```
TAKEOFF: <cockpit name> | Branch: <branch> | Session #<N+1>
Last session: <bookmark summary or "first session"> | <time ago>
State: <lifecycle_state or "fresh"> | Dirty: <yes/no> (<N> files)
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
- Maximum 3 file reads + 2 git commands. Keep it fast.
- Never ask questions during takeoff. Just show state.
- If the previous session was `lifecycle_state: done`, just note "Previous session completed" and move on.
- If the previous session was `lifecycle_state: blocked`, highlight the blocker prominently.
- Keep the briefing to 5-8 lines max. The user is here to work, not read.
- If no bookmark exists and no state.json exists, this is a fresh cockpit — say "First flight. Cockpit initialized." and create state.json.
