#!/usr/bin/env bash
# pre-bash-ceremony-guard.sh — Claude Code PreToolUse hook for Bash tool calls.
#
# Blocks raw `gh issue create` and `gh pr create` commands. Forces the agent
# to use cerebro-github MCP tools (create_work / open_pr) instead, which
# handle project-board linkage, milestone wiring, and audit trail.
#
# Read-only gh commands (pr view, pr checks, pr list, issue list, issue view,
# run list, run view, run watch, etc.) are allowed — only mutation commands
# that bypass the ceremony are blocked.
#
# Why: the agent optimizes for "works first try" and falls back to raw CLI
# when MCP tools error. The hook makes the fallback path fail loudly so the
# agent debugs the MCP tool instead of bypassing it.
#
# Claude hook protocol:
#   - Tool input is on stdin as JSON
#   - Exit 0 = allow the tool call
#   - Exit 2 = block the tool call and show the stderr output to the user
#   - Exit !=0,2 = non-blocking error (logged but call proceeds)
#
# Installed in ~/.claude/settings.json as a PreToolUse hook on Bash.

set -euo pipefail

input="$(cat)"

cmd="$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null || echo "")"

[[ -z "$cmd" ]] && exit 0

# Check for `gh issue create` (bypass of cerebro-github create_work)
if echo "$cmd" | grep -qE '(^|&&|\|\||;)\s*(GH_\w+=\S+\s+)?gh\s+issue\s+create\b'; then
    echo "  🚫 ceremony-guard (Claude hook): BLOCKED." >&2
    echo "" >&2
    echo "  gh issue create is blocked. Use cerebro-github instead:" >&2
    echo "" >&2
    echo "    mcp__cerebro-github__create_work(" >&2
    echo "      title=\"...\", repo=\"...\", body=\"...\"" >&2
    echo "    )" >&2
    echo "" >&2
    echo "  create_work handles:" >&2
    echo "    - Project board linkage (Project #1)" >&2
    echo "    - Milestone wiring (sub-issue of milestone)" >&2
    echo "    - Status tracking (todo / in_progress)" >&2
    echo "" >&2
    echo "  If create_work errors, DEBUG THE ERROR — don't fall back to gh." >&2
    echo "  The error is information, not permission to bypass." >&2
    exit 2
fi

# Check for `gh pr create` (bypass of cerebro-github open_pr)
if echo "$cmd" | grep -qE '(^|&&|\|\||;)\s*(GH_\w+=\S+\s+)?gh\s+pr\s+create\b'; then
    echo "  🚫 ceremony-guard (Claude hook): BLOCKED." >&2
    echo "" >&2
    echo "  gh pr create is blocked. Use cerebro-github instead:" >&2
    echo "" >&2
    echo "    mcp__cerebro-github__open_pr(" >&2
    echo "      repo=\"...\", branch=\"...\", closes=N" >&2
    echo "    )" >&2
    echo "" >&2
    echo "  open_pr handles:" >&2
    echo "    - Closes #N linkage" >&2
    echo "    - Project board sync" >&2
    echo "    - Issue existence verification" >&2
    echo "" >&2
    echo "  If open_pr errors, DEBUG THE ERROR — don't fall back to gh." >&2
    exit 2
fi

# All other gh commands (read-only, merge, etc.) are allowed
exit 0
