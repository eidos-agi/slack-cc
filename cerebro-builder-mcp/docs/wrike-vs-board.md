---
title: Wrike vs Project Board
tags: [wrike, project-board, audience, michael, alex, daniel, stakeholders]
---

# Wrike vs Project Board

Two systems, two audiences, two levels of detail.

## Why two systems?

Michael asked to keep Wrike "super high-level" — just enough for the weekly accounting review, no jargon, no implementation detail. But the engineering work needs granularity: which PRs are open, which CI checks are failing, what blocks what, and when each milestone lands.

## The split

| | Project Board (#1) | Wrike |
|---|---|---|
| **Audience** | Daniel | Michael + Alex |
| **Detail** | Task-level: specific code changes, blockers, CI status | Executive: what's on track, what's blocked, when it ships |
| **Example** | "Fix WAL pressure on 584K row bronze loads" | "Sage data pipeline running" |
| **Updated by** | Agents via cerebro-github MCP | Daniel (human voice) or agent in Daniel's voice |
| **Views** | Kanban, Roadmap/Gantt, Table | Standard Wrike views |
| **Language** | Technical, precise | Business outcomes, no jargon |

## What goes where

**Board gets:** Every issue, every PR, every milestone sub-issue, CI status, blockers, technical details.

**Wrike gets:** "Sage data is flowing." "Dashboard shows real numbers." "Blocked on vendor credentials." Never: PR numbers, CI status, column names, error messages.

## Common mistakes

1. **Pushing detail up.** Putting "Fix executor JSONB column lookup" in Wrike. Michael doesn't need this.
2. **AI voice in Wrike.** Michael and Alex can tell. Write in Daniel's voice — casual, direct, human.
3. **Board out of date.** If the board says "In Progress" but the work is done, Daniel's view is wrong.
4. **Wrike too detailed.** Michael was cleaning up the Cerebro project in Wrike because it had too much engineering jargon.
