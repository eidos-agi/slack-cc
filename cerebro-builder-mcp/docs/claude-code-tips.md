---
title: Claude Code Tips & Patterns
tags: [tips, patterns, prompting, CLAUDE.md, debugging, git, workflow, boris, thariq, parallel]
source: https://github.com/shanraisshan/claude-code-best-practice
review_by: 2026-07-01
---

# Claude Code Tips & Patterns

Hard-won wisdom from Anthropic engineers (Boris Cherny, Thariq, Cat Wu) and the community. Curated for builders.

## Prompting

- **Be specific about what you want.** "Fix the bug" < "The login form submits twice when clicking fast. Add debounce to the submit handler in `src/auth/LoginForm.tsx`."
- **Give Claude a way to verify.** End prompts with "verify by running the tests" or "check the build passes." Verification loops catch errors before you see them.
- **Use Opus with thinking for everything complex.** The thinking budget is where the real reasoning happens.

## CLAUDE.md

- **Keep it under 200 lines per file.** It's always in context — bloat costs tokens every turn.
- **Put commands to run (test, lint, build) at the top.** Claude uses these to verify its own work.
- **Use ancestor/descendant loading strategically.** Root = repo-wide rules. Subdirectory = component-specific. Siblings never load.
- **CLAUDE.local.md (gitignored) for personal preferences.** Team conventions in CLAUDE.md, your editor quirks in CLAUDE.local.md.
- **Don't duplicate what's in the code.** CLAUDE.md is for conventions and context the code doesn't express.
- **Update it when Claude does something wrong.** Every correction is a future instruction.
- **Global `~/.claude/CLAUDE.md`** for cross-project conventions (commit style, PR format, etc.)

## Parallel Execution

- **Run 5 Claudes in parallel** on different tasks. Use `claude.ai/code` for even more parallelism.
- **Git worktrees for parallel agents.** `isolation: worktree` gives each agent its own branch — no conflicts.
- **`/batch` for fan-out.** Apply the same operation across multiple files.
- **Programmatic Tool Calling (PTC):** Claude writes Python that orchestrates multiple tool calls in one inference pass. Only stdout enters context. 10 tools programmatically = 1/10th the tokens of 10 direct calls.

## Subagent Patterns

- **Use `Explore` (haiku, read-only) for fast search** instead of spawning general-purpose subagents.
- **`maxTurns` prevents runaway agents.** Always set it for autonomous work.
- **Subagents can't call other subagents via bash.** Must use `Agent()` tool.
- **`memory: project`** for subagents that need to learn across sessions.
- **Brief agents like a colleague who just walked in.** They have no context from the parent conversation.

## Skills & Commands

- **`disable-model-invocation: true`** for anything destructive (deploy, delete, force-push).
- **Skills are cheaper than agents** — no separate context window. Use skills when isolation isn't needed.
- **Descriptions are always in context.** Keep them concise. Full skill content loads on-demand only.
- **Compose small skills into larger workflows.** Skills can invoke other skills.
- **`context: fork`** turns a skill into an agent — isolated context, bounded work.
- **Hooks > skills for automated responses.** PostToolUse hooks fire automatically after every tool call. Use for formatting, linting, notifications.

## Workflow Patterns

- **Plan mode before code mode.** Use `shift+tab` or `/plan` to think before writing. Plan mode is read-only — can't accidentally change anything.
- **`/compact` at ~50% context usage.** Manual compaction beats hitting the wall.
- **`/btw` for side queries.** Ask a question without derailing the main task.
- **Fork sessions to explore.** `--fork-session` branches a conversation without losing the original.
- **`/loop` for recurring checks.** Poll CI, watch logs, retry until green.
- **`/schedule` for cron agents.** Automated nightly builds, weekly reports.

## Git & PRs

- **Squash merge by default.** 266 contributions/day productivity with squash merging (Boris's team).
- **PR size matters.** p50=118 lines, p90=498 lines, p99=2978 lines. Keep PRs small.
- **Pre-approve git commands** in permissions: `Bash(git *)` eliminates friction.
- **`--from-pr` to resume work** on an existing PR.
- **`/rewind` to undo mistakes.** Rolls back to a previous checkpoint.

## Debugging

- **Give Claude the error, not your interpretation.** Paste the full stack trace.
- **Claude can fix its own bugs.** When tests fail, let it read the error and iterate.
- **Use `/doctor` when things feel broken.** Checks MCP servers, permissions, config.
- **`Esc-Esc` to interrupt and redirect.** Don't wait for a bad approach to finish.
- **Check the build after every change.** Tell Claude to verify by running tests/lint/typecheck.

## MCP Design

- **Limit to 4-5 MCP servers.** More = more context bloat from tool definitions.
- **Context7 for library docs.** Always prefer it over web search for framework/API questions.
- **`.mcp.json` for team-shared servers.** Committed to git, auto-discovered.
- **`enableAllProjectMcpServers: true`** to stop permission prompts for project MCPs.

## Model Selection

- **Opus for complex reasoning.** Architecture, debugging, multi-file refactors.
- **Sonnet for routine work.** Standard code changes, test writing, simple features.
- **Haiku for search and exploration.** Read-only agents, codebase exploration, quick lookups.
- **`/effort` to dial reasoning depth.** `low` for simple, `max` for hard problems.
