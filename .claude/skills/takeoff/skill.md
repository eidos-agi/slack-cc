# /takeoff — Cockpit Boot Sequence

## When to Use
Start of every session. This is the first thing you run.

## What It Does
Shows the ASCII art header, status bar, and drift detection. Composes `/pre-flight` (as a subagent) to produce the full situational briefing. Then generates persistent artifacts — `takeoff.md` and `cockpit.html` — so the briefing lives beyond the terminal. Waits for orders.

## Execution Steps

### 1. Gather Core State (cheap, in main context)

**A. state.json** — from the cockpit root
- Get `cockpit.name` (for the ASCII art header)
- Get `theme` (for HTML generation)
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

### 4. Generate takeoff.md

Write a markdown file at the cockpit root: `takeoff.md`

This is the persistent, git-friendly version of the takeoff briefing. It should contain everything shown in the terminal — status bar, drift alerts, resume context, and the full four-part briefing — in clean markdown.

Format:

```markdown
# <Cockpit Name> — Takeoff

**Session** #N &nbsp;|&nbsp; **Branch** `main` &nbsp;|&nbsp; **Working tree** clean &nbsp;|&nbsp; **Last landing** never / 2h ago / etc.

> **Resume:** <bookmark summary, if any>

> **Drift:** <drift details, if any>

---

## Where We Were

<briefing content — full paragraphs, not abbreviated>

## Where We Are

<briefing content>

## Where We're Going

1. <priority — with WHY it matters>
2. <priority>
3. <priority>

## Blockers

<blocker details with who, what, how long>

---

*Generated <ISO timestamp> by /takeoff*
```

**The markdown version can be MORE detailed than the terminal output.** The terminal is for quick orientation. The markdown is the full briefing document. Add context, connections between items, and implications that would be too verbose for the terminal.

### 5. Generate cockpit.html

Read the HTML template at `.claude/skills/takeoff/cockpit-template.html`.

Replace all `{{PLACEHOLDER}}` tokens with actual values:

| Placeholder | Source |
|---|---|
| `{{COCKPIT_NAME}}` | `state.json → cockpit.name` |
| `{{PRIMARY}}` | `state.json → theme.primary` |
| `{{DANGER}}` | `state.json → theme.danger` |
| `{{WARNING}}` | `state.json → theme.warning` |
| `{{BG}}` | `state.json → theme.bg` |
| `{{SURFACE}}` | `state.json → theme.surface` |
| `{{TEXT}}` | `state.json → theme.text` |
| `{{MUTED}}` | `state.json → theme.muted` |
| `{{SESSION_NUMBER}}` | `counters.sessions + 1` |
| `{{BRANCH}}` | Current git branch |
| `{{DIRTY_CLASS}}` | `clean` or `dirty` (CSS class) |
| `{{DIRTY_VALUE}}` | `Clean` or `N files modified` |
| `{{LAST_CLASS}}` | `never` if null, else empty |
| `{{LAST_LANDING}}` | Human-readable time since last land |
| `{{DRIFT_SECTION}}` | Full `<div class="drift">` block, or empty string if no drift |
| `{{RESUME_SECTION}}` | Full `<div class="resume">` block, or empty string if no bookmark |
| `{{WHERE_WE_WERE}}` | Briefing content wrapped in `<p>` tags |
| `{{WHERE_WE_ARE}}` | Briefing content wrapped in `<p>` tags |
| `{{WHERE_WERE_GOING}}` | Briefing content as `<ol><li>` items |
| `{{BLOCKERS}}` | Briefing content wrapped in `<p>` tags |
| `{{TIMESTAMP}}` | Human-readable date/time (e.g., "Feb 25, 2026 at 4:15 PM") |

Write the result to `cockpit.html` at the cockpit root.

**Content in the HTML should match takeoff.md** — same level of detail, same structure. The HTML is just the styled presentation layer.

After writing, output:
```
  COCKPIT   takeoff.md + cockpit.html written → open cockpit.html in browser
```

### 6. Update State

Write to `state.json`:
- Set `watermarks.last_takeoff` to current ISO timestamp
- Increment `counters.sessions` by 1
- Increment `counters.takeoffs` by 1

### 7. STOP

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
- If `theme` is missing from state.json, use these defaults: primary `#3fb950`, danger `#f85149`, warning `#d29922`, bg `#0d1117`, surface `#161b22`, text `#e6edf3`, muted `#8b949e`.
- `takeoff.md` and `cockpit.html` are overwritten on every takeoff. They always reflect the current session's starting position.
- Both files should be committed to git (they're useful artifacts, not build output).
