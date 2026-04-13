---
title: Claude Code Architecture
tags: [claude-code, settings, permissions, CLAUDE.md, hierarchy, configuration, sandbox, env-vars]
source: https://github.com/shanraisshan/claude-code-best-practice
review_by: 2026-07-01
---

# Claude Code Architecture

How the machine works. Settings, permissions, CLAUDE.md loading, MCP scopes, environment variables.

## Settings Hierarchy (5 levels, highest wins)

```
1. Managed (enterprise admin)     ← always wins
2. CLI flags (--model, --tools)   ← per-invocation
3. .claude/settings.local.json    ← personal, gitignored
4. .claude/settings.json          ← project, committed
5. ~/.claude/settings.json        ← user-global
```

- Array settings (like `permissions.allow`) **concatenate** across scopes — they don't replace.
- `deny` rules **always win** regardless of which level sets them.

## Permission Rules

Syntax: `ToolName(pattern)` or `mcp__server__tool`

```
Bash(npm run *)        — allow npm scripts
Bash(git *)            — allow git commands
Edit(src/**)           — allow edits in src/
Read(.env)             — allow reading .env
mcp__cerebro-builder__ — allow all builder tools
```

Evaluation order: **deny first → ask → allow**. First match wins.

### Permission Modes (8)

| Mode | Behavior |
|------|----------|
| `default` | Prompt for everything not explicitly allowed |
| `acceptEdits` | Auto-approve file edits, prompt for bash/MCP |
| `auto` | Auto-approve everything except deny list |
| `dontAsk` | Never prompt — skip disallowed tools silently |
| `bypassPermissions` | No prompts at all (dangerous) |
| `plan` | Read-only — no edits, no bash, no MCP writes |

## CLAUDE.md Loading Mechanics

Two loading mechanisms — direction matters:

### Ancestor Loading (UP) — at startup
Walks **upward** from cwd to filesystem root. Loads every CLAUDE.md it finds. Always happens at startup.

### Descendant Loading (DOWN) — lazy
Subdirectory CLAUDE.md files load **only when Claude reads files in that directory**. Not at startup.

### What never loads
**Sibling directories.** If you're in `src/`, the CLAUDE.md in `tests/` never loads unless Claude touches a file there.

### Global CLAUDE.md
`~/.claude/CLAUDE.md` applies to ALL sessions across all projects.

### Practical implications
- Root CLAUDE.md: shared conventions, repo-wide rules
- Component CLAUDE.md: component-specific instructions (lazy-loaded)
- `.claude/CLAUDE.local.md`: personal preferences (gitignored)
- Keep each file **under 200 lines** — it's always in context

## MCP Server Scopes (3 levels)

```
Subagent frontmatter  ← highest priority, scoped to one agent
.mcp.json (repo root) ← project-level, committed, team-shared
~/.claude.json         ← user-global, personal
```

- Server types: `stdio` (local process) or `http` (remote URL)
- Env var expansion: `${MCP_API_TOKEN}` in config
- `enableAllProjectMcpServers: true` in settings auto-approves project MCP servers
- Tool permission syntax: `mcp__<server>__<tool>`

## Environment Variables (key ones)

| Var | What |
|-----|------|
| `ANTHROPIC_API_KEY` | API key |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Cap output tokens |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | No telemetry |
| `CLAUDE_CODE_EFFORT_LEVEL` | low/medium/high/max |
| `CLAUDE_CODE_TMPDIR` | Custom temp directory |
| `DISABLE_AUTOUPDATER` | Prevent auto-updates |
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | Extra CLAUDE.md locations |

170+ env vars available via the `env` key in settings.json — see source repo for full list.

## Sandbox

Controls filesystem and network access when enabled:

- `sandbox.filesystem.readDenyGlobs` / `readAllowGlobs`
- `sandbox.filesystem.writeDenyGlobs` / `writeAllowGlobs`
- `sandbox.network.domainAllowList` — restrict outbound HTTP
