# /cockpit-status — Instrument Panel

## When to Use
Anytime during a session. Shows what's active, what's blocked, and what needs attention.

## What It Does
Scans the cockpit workspace and produces a dashboard view. This is the "instruments" — a snapshot of everything in flight.

## Execution Steps

### 1. Gather Data (parallel)

**A. Git state**
- `git status --porcelain` — dirty files
- `git branch --show-current` — current branch
- `git log --oneline -5` — recent activity

**B. state.json** — watermarks and counters
- When was last takeoff/landing?
- How many sessions?

**C. Backlog scan** (if backlog/ exists)
- Count tasks by status (to do, in progress, done, blocked)
- Find the oldest open task
- Find any blocked tasks

**D. Project scan** (if projects/ exists)
- List active projects
- For each: check for checklist.md, count done/total items

**E. Tasks scan** (if tasks/ exists)
- Read the task register
- Group by owner/blocker
- Flag items older than 7 days without updates

### 2. Output Dashboard

Format as a clean, scannable dashboard:

```
COCKPIT STATUS: <cockpit name> | <timestamp>
Branch: <branch> | Dirty: <yes/no> | Sessions: <N>

ACTIVE WORKSTREAMS
| Workstream | Status | Progress | Owner | Age |
|------------|--------|----------|-------|-----|
| ...        | ...    | ...      | ...   | ... |

BLOCKED (needs external input)
- <item> — blocked on <who/what> — <age> days

WAITING ON
| Person | Item | Raised | Age | Follow-ups |
|--------|------|--------|-----|------------|
| ...    | ...  | ...    | ... | ...        |

STALE (no update in 7+ days)
- <item> — last touched <date>

RECENT ACTIVITY (last 5 commits)
- <hash> <message> (<time ago>)
```

### 3. Adapt to What Exists

Not every cockpit has every structure. Only show sections that have data:
- No `backlog/`? Skip the backlog section.
- No `projects/`? Skip the project scan.
- No `tasks/`? Skip the task register.
- Nothing blocked? Skip the BLOCKED section.
- Nothing stale? Skip the STALE section.

If the cockpit is minimal (just state.json and git), show:
```
COCKPIT STATUS: <name> | <timestamp>
Branch: <branch> | Dirty: <yes/no> | Sessions: <N>
Last takeoff: <time> | Last landing: <time>

No projects, tasks, or backlog found.
Use domain-specific skills to start tracking work.
```

## Rules
- This is read-only. Never modify files.
- Keep it scannable. Use tables for structured data, bullets for alerts.
- Flag anything over 7 days without an update as STALE.
- Flag anything with no owner as UNOWNED.
- Sort blocked items by age (oldest first — they need attention most).
- If the cockpit has a custom `status_sections` key in state.json, include those sections too (extensibility hook for domain-specific dashboards).
