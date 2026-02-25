---
name: weekly-update
description: "Generate comprehensive weekly intelligence report across all Greenmark repos. Use when Daniel says 'weekly update', 'weekly report', 'what happened this week', or '/weekly-update'. Collects commits, backlog changes, communications, cross-references everything, reconciles the backlog, and produces a report with no cracks."
---

# Weekly Update — Comprehensive Intelligence Report

Generate a full-spectrum weekly report covering all Greenmark Waste Solutions engineering activity. This goes beyond commit summaries — it cross-references, reconciles, and surfaces gaps.

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

If a repo exists on GitHub but not locally, note it in the report under "Repo Inventory Issues" and clone it:
```bash
cd ~/repos-greenmark-waste-solutions
git clone git@github.com:greenmark-waste-solutions/<repo>.git
```

If a local directory exists but has no remote (like `planning/`), note it as a stale/orphaned directory.

### Before collecting commits, fetch all remotes:
```bash
for dir in "$REPOS_DIR"/*/ "$REPOS_DIR"/.*/; do
    [ -d "$dir/.git" ] || continue
    git -C "$dir" fetch --quiet 2>/dev/null &
done
wait
```

Skip repos with zero commits that week. Always include `greenmark-planning` if backlog changed.

## Execution — 7 Stages

### Stage 1: Determine Date Range

Default: Monday through Sunday of the current week.
If Daniel specifies a date or range, use that.

```bash
# Calculate current week boundaries
DOW=$(date +%u)
SINCE=$(date -j -v-$((DOW-1))d "+%Y-%m-%d")
UNTIL=$(date -j -v+$((7-DOW))d "+%Y-%m-%d")
```

### Stage 2: Collect Commits (All Repos)

For each repo directory, collect commits in the date range:

```bash
REPOS_DIR=~/repos-greenmark-waste-solutions
for repo in "$REPOS_DIR"/*/; do
    [ -d "$repo/.git" ] || continue
    name=$(basename "$repo")
    git -C "$repo" log --since="$SINCE" --until="$UNTIL" \
        --format="%h|%ai|%an|%s" --no-merges
done
```

For repos with significant commits (5+ or architecturally important), also collect:
```bash
git -C "$repo" log --since="$SINCE" --until="$UNTIL" --stat --no-merges
```

Count commits per repo. Note which repos had zero activity.

### Stage 3: Collect Backlog & Planning Changes

From `greenmark-planning`:

```bash
PLANNING=~/repos-greenmark-waste-solutions/greenmark-planning

# Backlog task changes this week
git -C "$PLANNING" log --since="$SINCE" --until="$UNTIL" \
    --format="%h %s" -- backlog/

# Specific files changed in backlog/
git -C "$PLANNING" diff $(git -C "$PLANNING" log --since="$SINCE" --format="%H" --reverse -- backlog/ | head -1)^..HEAD -- backlog/ --stat

# New/changed meetings
git -C "$PLANNING" log --since="$SINCE" --until="$UNTIL" \
    --format="%h %s" -- meetings/

# New/changed decisions
git -C "$PLANNING" log --since="$SINCE" --until="$UNTIL" \
    --format="%h %s" -- decisions/

# New notes
git -C "$PLANNING" log --since="$SINCE" --until="$UNTIL" \
    --format="%h %s" -- notes/

# Project checklist changes
git -C "$PLANNING" log --since="$SINCE" --until="$UNTIL" \
    --format="%h %s" -- projects/
```

Also read every task file in `backlog/tasks/` to get current status snapshot:
```bash
# Read all task files to build status snapshot
ls "$PLANNING/backlog/tasks/"
```

Use the Backlog MCP `task_search` and `task_list` to get the current state of all tasks.

### Stage 4: Collect Communications

Check for evidence of stakeholder communications this week:

- **Emails sent** — look in notes/ for mentions of "sent", "emailed", "replied"
- **Meetings held** — new folders in meetings/
- **Decisions made** — new/updated files in decisions/
- **Setup instructions sent** — check projects/ for stakeholder-facing docs updated this week

Build a communications log: who was contacted, about what, what response (if any).

### Stage 5: Cross-Reference & Deep Dive

This is the critical stage. For each significant commit or group of commits:

1. **Match to tasks** — Does this commit relate to a backlog task? Look for:
   - Task IDs in commit messages (e.g., "TASK-1.3")
   - File paths that match task descriptions
   - Themes that match task titles

2. **Find untracked work** — Commits that don't match any task. This is work that happened but isn't in the backlog. Flag it.

3. **Find stale tasks** — Tasks marked "In Progress" or "To Do" with NO commits this week across any repo. Are they truly blocked, or just forgotten?

4. **Check blocker status** — For each known blocker:
   - Is it still blocked? Check if the blocking condition changed.
   - Was any progress made toward unblocking?
   - Who needs to act?

5. **Dependency chain** — Which tasks are blocking others? Is the critical path healthy?

### Stage 6: Reconcile Backlog

Perform a full backlog health check:

| Check | What to Look For |
|-------|-----------------|
| **Zombie tasks** | "In Progress" for 2+ weeks with no recent commits or notes |
| **Orphan work** | Commits that don't correspond to any task |
| **Missing tasks** | Work areas with activity but no backlog coverage |
| **Stale To Do** | Tasks in "To Do" that should have started based on dependencies being met |
| **Done but unclosed** | Work clearly completed but task still open |
| **Dependency violations** | Tasks in progress whose dependencies aren't Done |
| **Priority drift** | Low-priority tasks getting work while High-priority tasks are idle |

Produce a reconciliation table with specific recommendations (close task X, create task for Y, update status of Z).

### Stage 7: Write the Report

Output location: `~/repos-greenmark-waste-solutions/weekly-updates/reports/YYYY-WNN.md`

Use this format:

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
```

## After Writing

1. Show Daniel a preview of the report
2. Ask if he wants to adjust anything before publishing
3. If approved, save to `~/repos-greenmark-waste-solutions/weekly-updates/reports/YYYY-WNN.md`
4. Optionally commit to the weekly-updates repo

## Comparing to Existing Pipeline

The `weekly-updates` repo has a `generate.sh` pipeline that does commit collection + AI summarization. This skill **supersedes** that pipeline by adding:
- Backlog awareness (task status tracking)
- Cross-referencing (commits ↔ tasks)
- Communications tracking
- Reconciliation
- Deeper per-commit research when needed

The existing `generate.sh` can still run independently for quick commit-only reports. This skill is the comprehensive version.

## Key Rules

- **No cracks** — every commit must be accounted for. Every task must be checked. Every blocker must have a path forward.
- **Cross-reference everything** — if a commit touches a file related to a task, link them.
- **Plain English for executives** — Michael and Alex are not engineers. Write for them.
- **Technical depth for Daniel** — include task IDs, commit hashes, file paths in the detail sections.
- **Flag gaps loudly** — untracked work, stale tasks, and reconciliation issues go in dedicated sections, not buried in prose.
- **Don't invent** — only report what the evidence shows. If something is ambiguous, say so.
- **Include last week's metrics** — read the previous week's report from `weekly-updates/reports/` to calculate trends.
- **Reconcile honestly** — if the backlog is messy, say so. The point is to fix it, not hide it.
