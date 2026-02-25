# /pre-flight — Situational Awareness Scan

## When to Use
- Called automatically by `/takeoff` (composed)
- Can also be called independently mid-session for a status refresh

## What It Does
Scans the cockpit workspace and produces a four-part **strategic** briefing. This is not a data dump — it's a human-readable situation report that helps the pilot decide what to do next.

When called by `/takeoff`, this runs as a subagent (Explore type) to keep the main context lean. When called independently, it runs inline.

## Tone & Voice

**Write like a sharp chief of staff briefing an executive.** Not like a database query result.

- Use plain language, not task IDs or technical jargon
- Say what *happened*, not what the bookmark JSON says
- Say what *matters*, not what exists in the file system
- If you don't have enough context to say something meaningful, say that — don't pad with noise

## Execution Steps

### 1. Scan What Exists (skip what doesn't)

**A. Bookmark context** (passed from takeoff, or read fresh if called independently)
- Last session summary, next actions, blockers, lifecycle state

**B. Recent git commits** — look at the last 5-10 commit messages on the current branch
- These tell you what *actually happened* recently, even if the bookmark is sparse

**C. Backlog** (if `backlog/tasks/` exists)
- Scan for the big picture: what initiatives are active, what's blocked, what's waiting on people
- Do NOT list task IDs or subtask numbers — synthesize into plain English

**D. Projects** (if `projects/` exists)
- List active project folders
- For each: what's the status? Is it moving or stale?

**E. CLAUDE.md** — pull the "What's Active" and "What's Blocked" sections
- These are the human-written status lines — they're the most reliable signal

**F. state.json custom fields**
- Read `custom` key for domain-specific state
- Translate numbers into meaning (e.g., "6 vendors researched" → "6 of 15 vendor systems researched — under half")

### 2. Compose the Briefing

Output EXACTLY this format. Keep each section to 1-4 lines. Write like you're briefing a busy person.

```
WHERE WE WERE
  <What got done recently — in plain English. Synthesize from commits,
   bookmark, and project state. Focus on outcomes, not process.>
  <If first session: "First session — fresh start.">
  <If auto-closed with no bookmark context: "Last session ended without
   a debrief. Reconstructing from commits and project state.">

WHERE WE ARE
  <Big picture: what phase is the engagement/project in?>
  <What's moving? What's stalled? What's waiting on someone?>
  <Keep it strategic — the pilot can drill into details themselves.>

WHERE WE'RE GOING
  1. <Most impactful thing to do next — plain English, not a task ID>
  2. <Second priority>
  3. <Third priority>
  <These should be actionable session goals, not backlog items.>

BLOCKERS
  <Who owes us what? How long have they owed it?>
  <What can't move until something external happens?>
  <Or "None" if clear skies.>
```

### Quality Checklist (before returning)

Before you return the briefing, check:
- [ ] Does WHERE WE WERE describe *outcomes*, not "session auto-closed"?
- [ ] Does WHERE WE ARE give the *big picture*, not task counts?
- [ ] Does WHERE WE'RE GOING suggest *session goals*, not backlog subtask IDs?
- [ ] Would a non-technical stakeholder understand every line?
- [ ] Is every line earning its place? Delete anything that doesn't help the pilot decide what to do.

### 3. Return

If called as a subagent (by `/takeoff`): return the formatted briefing text.
If called independently: output the briefing directly to the user.

## Rules
- Read-only. Never modify files.
- **No task IDs in the briefing.** Say "expand HubSpot API access", not "TASK-1.12".
- **No jargon without context.** If you mention "PAK", say "private app key" or just "API credentials".
- Skip sections that have no data. Don't show empty sections.
- If the cockpit is bare (no backlog, no projects, no CLAUDE.md state sections), return: "Fresh cockpit. No projects or tasks tracked yet."
- Prioritize recency. The most recently touched work goes first.
- Flag staleness. Anything untouched for 7+ days gets a "(stale)" marker.
- Adapt to what exists. Every cockpit is different — work with whatever is there.
