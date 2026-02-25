# /pre-flight — Situational Awareness Scan

## When to Use
- Called automatically by `/takeoff` (composed)
- Can also be called independently mid-session for a status refresh

## What It Does
Scans the cockpit workspace and produces a four-part situational briefing: where we were, where we are, where we're going, and what's blocking us.

When called by `/takeoff`, this runs as a subagent (Explore type) to keep the main context lean. When called independently, it runs inline.

## Execution Steps

### 1. Scan What Exists (skip what doesn't)

**A. Bookmark context** (passed from takeoff, or read fresh if called independently)
- Last session summary, next actions, blockers, lifecycle state

**B. Backlog** (if `backlog/tasks/` exists)
- Count tasks by status: to do, in progress, done, blocked
- Find the most urgent in-progress task
- Find any blocked tasks with blocker details

**C. Projects** (if `projects/` exists)
- List active project folders
- For each: check for checklist.md, count done/total items
- Identify the most active project (most recent changes)

**D. Task register** (if `tasks/README.md` exists)
- Scan for waiting-on items grouped by person
- Flag items older than 7 days
- Count follow-ups per item

**E. CLAUDE.md** — pull structured state sections
- Look for: "Active Research", "Current State", "What's Active", "What's Blocked", "Active Workstreams"
- Extract key status lines (not the whole section — just the headlines)

**F. state.json custom fields**
- Read `custom` key for domain-specific state (e.g., study status, vendor counts, email watermarks)
- Surface anything that looks like active work or a tracked metric

### 2. Compose the Briefing

Output EXACTLY this format. Keep each section to 1-5 lines. Be concise — headlines, not paragraphs.

```
WHERE WE WERE
  <What the last session accomplished. Pull from bookmark summary.>
  <If first session: "First session — no prior context.">
  <If auto-closed: "Previous session auto-closed without landing.">

WHERE WE ARE
  <Active workstreams with status>
  <Task counts: N in progress, N blocked, N waiting on others>
  <Domain-specific metrics from state.json custom fields>
  <Key facts from CLAUDE.md active sections>

WHERE WE'RE GOING
  1. <Top priority — from bookmark next_actions or most urgent task>
  2. <Second priority>
  3. <Third priority>

BLOCKERS
  <Blocked items: what's stuck, who/what is blocking, how long>
  <Or "None" if nothing is blocked>
```

### 3. Return

If called as a subagent (by `/takeoff`): return the formatted briefing text.
If called independently: output the briefing directly to the user.

## Rules
- Read-only. Never modify files.
- Skip sections that have no data. Don't show empty "WHERE WE ARE" with "No projects found."
- If the cockpit is bare (no backlog, no projects, no tasks, no CLAUDE.md state sections), return: "Fresh cockpit. No projects or tasks tracked yet."
- Prioritize recency. The most recently touched work goes first.
- Flag staleness. Anything untouched for 7+ days gets a "(stale)" marker.
- Keep it scannable. Bullets and short lines, not paragraphs.
- Adapt to what exists. Every cockpit is different — some have backlogs, some have projects, some have both, some have neither. Work with whatever is there.
