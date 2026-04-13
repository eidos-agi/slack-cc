---
title: Information Hierarchy
tags: [github, project-board, wrike, hierarchy, audience, visibility]
---

# Information Hierarchy

Three layers, most detail to least. Each filters for its audience.

```
GitHub repos         Everything (code, commits, CI, PRs, discussions)
  |-- Project Board  Curated (issues, milestones, progress bars, status)
       |-- Wrike     Distilled (business outcomes, no jargon)
```

## GitHub repos (13 repos)

**Audience:** Engineers (Daniel + agents)
**Detail:** Everything. Code diffs, commit messages, CI logs, PR discussions.
**Who writes here:** Agents via cerebro-github MCP.

This is where the work lives. Every line of code, every test, every deployment log.

## Project Board (#1, "Cerebro Engineering")

**URL:** https://github.com/orgs/greenmark-waste-solutions/projects/1
**Audience:** Daniel (engineering oversight across all repos)
**Detail:** Issues, milestones (as parent issues with sub-issues), status fields, progress bars, Roadmap/Gantt view.
**Who writes here:** cerebro-github create_work() and open_pr() add items automatically.

The board is Daniel's single pane of glass. He shouldn't have to open 13 repos to know what's happening. The board aggregates issues and PRs from all repos into one Kanban/Roadmap view.

Milestones on the board are parent issues (e.g., "M-04: Sage Medallion Complete"). Each task is a sub-issue. Closing a sub-issue fills the parent's progress bar. This is how Daniel sees "M-04 is 60% done" without reading commit logs.

## Wrike

**Audience:** Michael (President) + Alex (CFO)
**Detail:** Business outcomes only. "Sage data flowing to dashboard, targeting Monday." No PR numbers, no CI status, no technical jargon.
**Who writes here:** Daniel (human) or agent in Daniel's voice.

Michael asked to keep Wrike "super high-level" — just enough for the weekly accounting review. He was cleaning up the Cerebro project in Wrike because it had too much engineering detail.

## Rules

1. **Detail flows down, never up.** Michael doesn't need "Fix WAL pressure on 584K row loads." He needs "Data pipeline running."
2. **Every layer must be current.** If the board shows M-04 in progress but Wrike says "waiting on credentials," someone is wrong.
3. **Work not on the board doesn't exist.** If there's no issue, Daniel can't see it. create_work() before writing code.
4. **Wrike updates are in Daniel's voice.** AI-generated content triggers Greenmark stakeholders. They can tell.
