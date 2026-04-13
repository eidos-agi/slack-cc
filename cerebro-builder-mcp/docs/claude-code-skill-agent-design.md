---
title: Skill & Agent Design
tags: [skill, agent, subagent, command, frontmatter, design, orchestration, worktree]
source: https://github.com/shanraisshan/claude-code-best-practice
review_by: 2026-07-01
---

# Skill & Agent Design

When to use commands vs skills vs subagents. Frontmatter fields. Design patterns.

## Command → Agent → Skill (orchestration pattern)

```
Command:  User-initiated entry point (/slash-command)
Agent:    Autonomous worker in isolated context window
Skill:    Reusable procedure, no separate context window
```

- Commands orchestrate agents. Agents do autonomous work with preloaded skills.
- **Never use agents for simple tasks** — skills are cheaper (no separate context window).
- **Subagents cannot invoke other subagents via bash.** Must use the `Agent()` tool.

## When to use each

| Use | When |
|-----|------|
| **Skill** | Reusable procedure, no isolation needed, stays in parent context |
| **Command** | User-facing entry point, needs `/slash` invocation |
| **Subagent** | Needs isolation, parallel work, different model, or bounded turns |

## Skill / Command Frontmatter (13 fields)

| Field | Type | What |
|-------|------|------|
| `name` | string | Display name and `/slash` identifier |
| `description` | string | What it does — shown in autocomplete, used for auto-discovery |
| `argument-hint` | string | Hint during autocomplete (e.g., `[issue-number]`) |
| `disable-model-invocation` | bool | Require explicit `/skill-name` — use for dangerous operations |
| `user-invocable` | bool | Set `false` to hide from `/` menu (background knowledge only) |
| `paths` | glob | Limit activation to specific file paths |
| `allowed-tools` | string | Tools allowed without permission prompts |
| `model` | string | Model override (`haiku`, `sonnet`, `opus`) |
| `effort` | string | Effort level (`low`, `medium`, `high`, `max`) |
| `context` | string | `fork` to run in isolated subagent context |
| `agent` | string | Subagent type when `context: fork` |
| `shell` | string | `bash` (default) or `powershell` |
| `hooks` | object | Lifecycle hooks scoped to this skill |

### Skill description budget
Descriptions (up to 15K chars total across all skills) are always in context. Full content loads only when invoked. Keep descriptions tight.

### Skill auto-discovery in monorepos
Nested `.claude/skills/` directories are discovered on-demand when working with files in those directories.

## Subagent Frontmatter (16 fields)

Everything skills have, plus:

| Field | Type | What |
|-------|------|------|
| `tools` | list | Allowlist of tools. Supports `Agent(agent_type)` syntax |
| `disallowedTools` | list | Tools to deny |
| `permissionMode` | string | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | int | Bound autonomous work — prevents runaway agents |
| `skills` | list | Skills to preload into agent context at startup |
| `mcpServers` | list | MCP servers available to this subagent |
| `memory` | string | Persistent memory: `user`, `project`, or `local` |
| `background` | bool | Run as background task |
| `isolation` | string | `worktree` for temporary git worktree (parallel git work) |
| `initialPrompt` | string | Auto-submitted as first user turn |
| `color` | string | Display color in task list |

### Built-in agents

| Agent | Model | Tools | Use for |
|-------|-------|-------|---------|
| `general-purpose` | inherit | All | Research, code search, autonomous work |
| `Explore` | haiku | Read-only | Fast codebase search (cheapest option) |
| `Plan` | inherit | Read-only | Pre-planning research |
| `claude-code-guide` | haiku | Glob, Grep, Read, WebFetch, WebSearch | Claude Code feature questions |

## 9 Skill Types (Thariq's taxonomy)

| Type | Example | When |
|------|---------|------|
| **Library/API Reference** | Fetch docs for a framework | Using unfamiliar library |
| **Product Verification** | Screenshot + check UI | After frontend changes |
| **Data Fetching** | Query DB, call API | Need external state |
| **Business Process** | PR workflow, deploy checklist | Repeated ceremony |
| **Code Scaffolding** | Generate boilerplate | New component/module |
| **Code Quality** | Lint, type check, review | Before merge |
| **CI/CD** | Build, test, deploy | Ship pipeline |
| **Runbooks** | Incident response steps | Production issues |
| **Infrastructure Ops** | Provision, configure | Environment setup |

## Design contracts

- **Descriptions are always loaded.** Full content loads on-demand. Write descriptions that tell the agent WHEN to use the skill, not HOW.
- **Use `disable-model-invocation: true`** for destructive skills (deploy, delete, reset).
- **Use `maxTurns`** on subagents to prevent runaway work.
- **Use `isolation: worktree`** when agents need to do parallel git work.
- **Use `model: haiku`** for exploration/search agents — 10x cheaper, fast enough.
- **Compose skills**: skills can invoke other skills. Build small, compose large.
