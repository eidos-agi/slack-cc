---
name: weekly-update
description: "Generate comprehensive weekly intelligence report across all Greenmark repos. Use when Daniel says 'weekly update', 'weekly report', 'what happened this week', or '/weekly-update'. Collects commits, backlog changes, communications, cross-references everything, reconciles the backlog, interviews Daniel about ambiguities, and produces a report with no cracks."
---

# Weekly Update — Comprehensive Intelligence Report

Generate a full-spectrum weekly report covering all Greenmark Waste Solutions engineering activity. This goes beyond commit summaries — it cross-references, reconciles, interviews, and surfaces gaps.

## Audience

| Person | Role | Cares About |
|--------|------|-------------|
| Michael Nguyen | President | Outcomes, blockers, vendor progress, timeline |
| Alex Kaye | CFO | Spend implications, vendor access, Sage connection |
| Robert Heath | GM | Fleet/ops impacts, field system changes |
| William Holloway | AIC COO | Strategic progress, resource utilization |
| Collin Bird | AIC MD | ROI, milestone delivery, risk |
| Daniel Shanklin | Dir. Tech | Everything — technical depth + exec summary |

Write for Michael/Alex level (plain English, outcomes not implementation). Daniel reads the raw data anyway.

## Repos to Cover

**Dynamically discover all repos.** Do NOT use a hardcoded list. Repos get added over time.

### Discovery Method (use BOTH, reconcile)

**1. Local repos** — scan the workspace:
```bash
REPOS_DIR=~/repos-greenmark-waste-solutions
for dir in "$REPOS_DIR"/*/ "$REPOS_DIR"/.*/; do
    [ -d "$dir/.git" ] || continue
    basename "$dir"
done
```

**2. GitHub org repos** — check for any not cloned locally:
```bash
gh repo list greenmark-waste-solutions --limit 50 --json name,isPrivate,updatedAt \
    --jq '.[] | .name'
```

If a repo exists on GitHub but not locally, clone it. If a local directory has no remote, flag it as stale/orphaned.

### Before collecting, fetch all remotes:
```bash
for dir in "$REPOS_DIR"/*/ "$REPOS_DIR"/.*/; do
    [ -d "$dir/.git" ] || continue
    git -C "$dir" fetch --quiet 2>/dev/null &
done
wait
```

## Architecture — Subagent Pipeline

This skill uses **subagents (Task tool)** to avoid burning through the main agent's context. Each subagent works in isolation, writes a structured intermediate report, and the main agent synthesizes at the end.

### Pipeline Overview

```
Stage 1: Setup (main agent)
    ↓
Stage 2: Data Collection (main agent — git commands, lightweight)
    ↓
Stage 3: Analysis (PARALLEL subagents — one per domain)
    ├── Subagent A: Per-repo commit analysis (one per active repo)
    ├── Subagent B: Backlog & task analysis
    └── Subagent C: Communications & stakeholder scan
    ↓
Stage 4: Cross-reference & Reconcile (main agent — reads subagent outputs)
    ↓
Stage 5: Interview Daniel (main agent — interactive)
    ↓
Stage 6: Fixes Report (main agent — captures interview answers)
    ↓
Stage 7: Final Synthesis (main agent — writes report incorporating fixes)
```

## Execution — 7 Stages

### Stage 1: Setup & Date Range

Default: Monday through Sunday of the current week.
If Daniel specifies a date or range, use that.

```bash
DOW=$(date +%u)
SINCE=$(date -j -v-$((DOW-1))d "+%Y-%m-%d")
UNTIL=$(date -j -v+$((7-DOW))d "+%Y-%m-%d")
```

Also read the previous week's report from `~/repos-greenmark-waste-solutions/weekly-updates/reports/` for trend comparison.

### Stage 2: Data Collection (Main Agent)

Lightweight — just git commands to gather raw data. Do this in the main agent since it's fast and low-context.

**Collect commits per repo:**
```bash
REPOS_DIR=~/repos-greenmark-waste-solutions
for repo in "$REPOS_DIR"/*/ "$REPOS_DIR"/.*/; do
    [ -d "$repo/.git" ] || continue
    name=$(basename "$repo")
    git -C "$repo" log --since="$SINCE" --until="$UNTIL" \
        --format="%h|%ai|%an|%s" --no-merges
done
```

**Also check for uncommitted work** (this is important — it catches work-in-progress that hasn't been committed):
```bash
for repo in "$REPOS_DIR"/*/ "$REPOS_DIR"/.*/; do
    [ -d "$repo/.git" ] || continue
    name=$(basename "$repo")
    changes=$(git -C "$repo" status --short | wc -l | tr -d ' ')
    [ "$changes" -gt 0 ] && echo "$name: $changes uncommitted files"
done
```

**Collect planning folder changes:**
```bash
PLANNING=~/repos-greenmark-waste-solutions/greenmark-planning
git -C "$PLANNING" log --since="$SINCE" --until="$UNTIL" --format="%h %s" -- backlog/ meetings/ decisions/ notes/ projects/
```

Save all raw data as context for the subagents.

### Stage 3: Parallel Subagent Analysis

Launch these subagents **in parallel** using the Task tool. Each subagent gets the relevant raw data and writes a structured analysis.

#### Subagent A: Per-Repo Commit Analysis (one per active repo)

For each repo with commits this week, launch a subagent:

```
Task tool:
  subagent_type: "haiku" or "general-purpose"
  prompt: "Analyze the following commits for repo {name}.
           Commits: {commit list with stats}
           Produce a structured summary:
           1. What changed (2-5 bullets, plain English)
           2. Key files touched and why they matter
           3. Contributors
           4. Impact assessment (active dev / maintenance / dormant)
           5. Any task IDs referenced in commit messages
           6. Any ambiguities or things that seem incomplete"
```

#### Subagent B: Backlog & Task Analysis

One subagent reads ALL task files and produces:

```
Task tool:
  subagent_type: "general-purpose"
  prompt: "Read all task files in {backlog/tasks/} and the Backlog MCP.
           Produce:
           1. Status snapshot (count by status)
           2. Tasks completed this week (check updated dates)
           3. Tasks started this week
           4. New tasks created this week
           5. Dependency chain analysis — is the critical path healthy?
           6. Zombie check — any In Progress tasks with no recent notes?
           7. Stale check — any To Do tasks whose dependencies are all Done?
           8. Priority drift — any Low tasks getting work while High tasks idle?
           9. Specific reconciliation recommendations"
```

#### Subagent C: Communications & Stakeholder Scan

One subagent scans notes/, meetings/, decisions/, and project files:

```
Task tool:
  subagent_type: "general-purpose"
  prompt: "Scan these locations for stakeholder communications this week:
           - notes/ files (look for mentions of sent, emailed, replied, called)
           - meetings/ folders (new meetings held)
           - decisions/ (new or updated decisions)
           - projects/ (stakeholder-facing docs updated)
           Produce a communications log:
           1. Who was contacted, about what, via what channel
           2. Who responded and what they said
           3. Who is still waiting for a response
           4. Any commitments made with deadlines
           5. Draft emails or setup guides that exist but haven't been sent"
```

### Stage 4: Cross-Reference & Reconcile (Main Agent)

Read all subagent outputs. This stage runs in the main agent because it needs to correlate across domains.

1. **Match commits to tasks** — Do commits reference task IDs? Do file paths match task descriptions?
2. **Find untracked work** — Commits that don't match any task. Flag for backlog creation.
3. **Find stale tasks** — Tasks with no commits this week. Flag for review.
4. **Check blockers** — For each known blocker, has anything changed? Who needs to act?
5. **Reconciliation table** — Combine task analysis with commit analysis to find gaps.

Write a **draft findings document** (not the final report) summarizing:
- Everything that happened (from subagents)
- Cross-reference results
- Reconciliation issues found
- **Ambiguities and questions** — things that don't add up, seem incomplete, or need human context

### Stage 5: Interview Daniel

**This is the quality gate.** Present the draft findings to Daniel and ask about every ambiguity. Do NOT proceed to the final report until this stage is complete.

Use `AskUserQuestion` or direct conversation to cover:

**Categories of questions to ask:**

1. **Ambiguities** — "Commit X mentions Y but there's no task for it. Was this planned work or ad-hoc?"
2. **Missing context** — "TASK-1.7 has no commits this week. Is it blocked, deferred, or just not started?"
3. **Communications gaps** — "The setup email for Michael is drafted but not sent. Should we mark this as 'pending send' or 'deferred'?"
4. **Blocker updates** — "Alex said Sage credentials would come Monday. Did that happen? Should we escalate?"
5. **Priority corrections** — "The reconciliation found X is low priority but got work. Is that intentional?"
6. **Things to add** — "Is there anything that happened this week that isn't captured in any repo? Meetings, calls, decisions made verbally?"
7. **Things to remove or correct** — "The subagent flagged X as a concern. Is that actually fine?"
8. **Next week priorities** — "What should the 'What's Next' section say? What are YOUR priorities?"

**Format the interview as a numbered list.** Present all questions at once so Daniel can answer efficiently. If answers raise follow-up questions, ask those too.

### Stage 6: Fixes Report

Capture Daniel's answers into a fixes report saved alongside the weekly update:

Output: `~/repos-greenmark-waste-solutions/weekly-updates/reports/YYYY-WNN-fixes.md`

```markdown
# W{NN} Fixes Report

*Interview date: {date}*

## Ambiguities Resolved
| # | Question | Answer | Action Taken |
|---|----------|--------|--------------|
| 1 | {question} | {Daniel's answer} | {Updated report / created task / corrected status} |

## Corrections Made
- {What was wrong} → {What was fixed}

## Context Added
- {What Daniel provided that wasn't in any repo}

## Backlog Updates Applied
- {Task status changes, new tasks created, tasks closed based on interview}
```

**Apply the fixes** — update backlog tasks, create new tasks, correct statuses, add notes. Do this BEFORE writing the final report so the backlog is clean.

### Stage 7: Final Synthesis (Main Agent)

NOW write the final report, incorporating all fixes from the interview.

Output: `~/repos-greenmark-waste-solutions/weekly-updates/reports/YYYY-WNN.md`

```markdown
# Weekly Intelligence Report — {Week Label}

*Generated: {date}*
*Period: {Mon date} – {Sun date}*
*Repos: {active} active / {total} total*
*Commits: {count} | Tasks touched: {count} | Blockers: {count}*

## Executive Summary

3-5 bullets covering the most important things that happened.
Written for Michael/Alex. Plain English. Outcomes, not implementation.

## Progress by Project

### {Project/Workstream Name}
What happened, what it means, what's next.
Reference specific tasks (TASK-X.Y) and commits.

(Group by logical project, not by repo. A project may span multiple repos.)

## Backlog Status

| Status | Count | Change |
|--------|-------|--------|
| Done | X | +Y this week |
| In Progress | X | |
| To Do | X | +Y new |
| Blocked | X | |

### Tasks Completed This Week
- TASK-X.Y: {title} — {one-line summary of what was delivered}

### Tasks Started This Week
- TASK-X.Y: {title} — {current status}

### New Tasks Created
- TASK-X.Y: {title} — {why it was created}

## Communications Log

| Date | Who | Channel | Topic | Status |
|------|-----|---------|-------|--------|
| {date} | {person} | Email/Meeting/etc | {topic} | Sent/Replied/Waiting |

## Blockers & Risks

| Blocker | Owner | Since | Impact | Path to Unblock |
|---------|-------|-------|--------|-----------------|
| {description} | {who} | {date} | {what it blocks} | {what needs to happen} |

## Cross-Reference Audit

### Untracked Work (commits without tasks)
- {repo}: {commit description} — **Recommend:** {create task / link to existing}

### Stale Tasks (no activity this week)
- TASK-X.Y: {title} — last activity {date}. **Recommend:** {update/close/deprioritize}

## Backlog Reconciliation

| Issue | Task | Recommendation |
|-------|------|----------------|
| {zombie/orphan/stale/etc} | {task ID} | {specific action} |

## What's Next

Prioritized list of what should happen next week, based on:
1. Critical path tasks
2. Unblocked items
3. Upcoming deadlines or stakeholder commitments
(Informed by Daniel's interview answers from Stage 5)

## Metrics

| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
| Total commits | X | Y | ↑/↓/→ |
| Active repos | X | Y | |
| Tasks completed | X | Y | |
| Tasks created | X | Y | |
| Open blockers | X | Y | |

---
*Generated by /weekly-update skill from greenmark-planning.*
*Sources: GitHub commits, Backlog.md tasks, project files, meeting notes.*
*Quality gate: Interview with Daniel on {date} — see YYYY-WNN-fixes.md*
```

## After Writing

1. Show Daniel the final report for approval
2. If approved, save all three files:
   - `reports/YYYY-WNN.md` (the report)
   - `reports/YYYY-WNN-fixes.md` (the interview record)
   - `reports/YYYY-WNN-notebooklm.md` (podcast/audio source — see below)
3. Commit all three to the weekly-updates repo
4. Push to remote

### Stage 8: NotebookLM Podcast Source

**Always produce this as the final step.** This file is NOT a script — it's a raw data document with front-matter instructions that NotebookLM uses to generate an audio overview (podcast-style recording).

Output: `~/repos-greenmark-waste-solutions/weekly-updates/reports/YYYY-WNN-notebooklm.md`

**Structure:**

1. **Front-matter instructions** — Tell NotebookLM how to structure the ~3 minute audio:
   - Where we were (30s) — starting position entering this week
   - Where we are now (60s) — what happened, outcomes not implementation
   - Where we're going (45s) — near-term roadmap
   - Blockers and who can fix them (30s) — names and actions
   - How we're tracking this (15s) — GitHub now, Wrike/Cerebro later
   - Tone: conversational, plain English, small company leadership audience

2. **Full context section** — Everything NotebookLM needs to draw from:
   - Company background (who Greenmark is, what Project Cerebro is, the 2+2+2 strategy)
   - Where we were (pull from last week's report)
   - Where we are now (pull from this week's report — full detail, don't shorten)
   - Where we're going (from interview Stage 5, question 12)
   - Blockers table with owners, timelines, impact
   - Communications log
   - Metrics comparison (this week vs last week)
   - Vendor system overview for context
   - Any thematic emphasis (e.g., safety-first approach, stakeholder engagement)

**Key rules for NotebookLM file:**
- Do NOT shorten the content — the goal is maximum context for the AI to draw from
- Do NOT write a script — write raw data with instructions. NotebookLM generates the audio.
- DO include last week's context so the "where we were" section is grounded
- DO emphasize the narrative arc (blocked → unblocked → what's next)
- DO include the note about task tracking moving to Wrike/Cerebro in future

## Key Rules

- **No cracks** — every commit must be accounted for. Every task must be checked. Every blocker must have a path forward.
- **Subagents for research, main agent for synthesis** — don't burn context reading every task file in the main conversation.
- **Interview BEFORE final report** — the report should never contain ambiguities that could have been resolved by asking Daniel.
- **Cross-reference everything** — if a commit touches a file related to a task, link them.
- **Plain English for executives** — Michael and Alex are not engineers. Write for them.
- **Technical depth for Daniel** — include task IDs, commit hashes, file paths in the detail sections.
- **Flag gaps loudly** — untracked work, stale tasks, and reconciliation issues go in dedicated sections, not buried in prose.
- **Don't invent** — only report what the evidence shows. If something is ambiguous, ask Daniel in Stage 5 rather than guessing.
- **Include last week's metrics** — read the previous week's report for trends.
- **Reconcile honestly** — if the backlog is messy, say so. The point is to fix it, not hide it.
- **The fixes report is permanent record** — it captures institutional knowledge that only exists in Daniel's head. This is the "no cracks" guarantee.
