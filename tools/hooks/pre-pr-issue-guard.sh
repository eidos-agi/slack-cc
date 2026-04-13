#!/usr/bin/env bash
# pre-pr-issue-guard.sh — Claude Code PreToolUse hook for Bash tool calls.
#
# Blocks `gh pr create` commands that don't include "closes #" or "fixes #"
# in the --body flag. Forces every PR to reference an issue.
#
# Claude hook protocol:
#   - Tool input is on stdin as JSON
#   - Exit 0 = allow the tool call
#   - Exit 2 = block the tool call and show the stderr output to the user
#   - Exit !=0,2 = non-blocking error (logged but call proceeds)
#
# Installed in ~/.claude/settings.json as a PreToolUse hook on Bash.
# Companion to pre-bash-branch-guard.sh (which blocks dangerous merges).

set -euo pipefail

input="$(cat)"

cmd="$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null || echo "")"

[[ -z "$cmd" ]] && exit 0

# Only intercept commands that START with gh pr create (not commit messages mentioning it)
# Strip heredoc/quoted content first — we only care about the actual command
cmd_first_line="$(echo "$cmd" | head -1)"
if ! echo "$cmd_first_line" | grep -qE '^\s*(GH_\w+=\S+\s+)?gh\s+pr\s+create\b'; then
    # Also check for piped/chained commands where gh pr create is a standalone command
    if ! echo "$cmd" | grep -qE '(^|&&|\|\||;)\s*gh\s+pr\s+create\b'; then
        exit 0
    fi
fi

# Check if --body contains "closes #" or "fixes #" (case insensitive)
body=""
# Extract --body value: could be --body "..." or --body '...' or via heredoc
if echo "$cmd" | grep -qiE '(closes|fixes|resolves)\s+#[0-9]+'; then
    exit 0
fi

# Also allow if the body is passed via a variable (can't inspect at this level)
# and allow --body-file which we can't read
if echo "$cmd" | grep -qE '\-\-body-file'; then
    exit 0
fi

cat >&2 << 'EOF'

  🚫 issue-guard (Claude hook): BLOCKED.

  Every PR must reference an issue. Include "Closes #N" in the --body.

  The process:
    1. Create an issue first (or find an existing one)
    2. Add it as a sub-issue of the relevant milestone
    3. Add it to the GitHub Project
    4. THEN create the PR with "Closes #N" in the body

  This ensures the project board shows linked PRs, sub-issue progress
  fills automatically, and merged PRs auto-close their issues.

  If this is truly a PR with no associated issue (rare), create the
  issue first — even chore/infra work gets an issue.

EOF
exit 2
