---
title: Project Board (#1)
tags: [project-board, milestones, sub-issues, ceremony, create-work, kanban, roadmap]
---

# Project Board — Cerebro Engineering

**URL:** https://github.com/orgs/greenmark-waste-solutions/projects/1
**Project Number:** 1
**Project ID:** PVT_kwDOD49Jk84BRMz-

## What it is

The central engineering board across all 13 Greenmark repos. One Kanban, one Roadmap, one place to see everything Daniel needs to know.

## Structure

```
Project Board
  |-- Milestones (parent issues, e.g. "M-04: Sage Medallion Complete")
  |     |-- Sub-issues (tasks, e.g. "Wire sage_gold.refresh_all()")
  |     |     |-- PRs that close sub-issues (e.g. "Closes #28")
  |     |-- Progress bar (fills as sub-issues close)
  |
  |-- Standalone issues (bugs, one-offs not tied to a milestone)
  |-- Open PRs (visible with CI status inline)
```

## Views

- **Table** — default, shows everything with status and repo columns
- **Board** — Kanban: Todo / In Progress / Done
- **Roadmap** — Gantt timeline using Start Date and Target Date fields

## Status fields

| Status | Option ID | When |
|--------|-----------|------|
| Todo | f75ad846 | Issue created, work not started |
| In Progress | 47fc9ee4 | Someone is actively working on it |
| Done | 98236657 | Issue closed, PR merged |

## How work gets on the board

1. `create_work(title, repo)` creates an issue and adds it to the board
2. `open_pr(repo, branch, closes=N)` ensures the linked issue is on the board
3. Merging the PR closes the issue, which updates milestone progress

## Relationship to ike.md

ike.md tracks tasks locally (TASK-0032, MS-0004). The board tracks issues on GitHub. These are parallel systems that should stay in sync:

- An ike task should have a corresponding board issue
- Closing an ike task should correspond to closing the board issue
- ike milestones (MS-0004) correspond to board milestone parent issues

The builder reads ike for "what should I work on?" and uses cerebro-github to make that work visible on the board.
