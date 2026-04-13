#!/usr/bin/env bash
# pre-bash-branch-guard.sh — Claude Code PreToolUse hook for Bash tool calls.
#
# Blocks `gh pr merge ... --delete-branch` commands when the HEAD of the PR
# is `main`, `master`, or `develop`. Prevents Claude from accidentally
# deleting a long-lived branch (the cerebro develop deletion bug).
#
# Claude hook protocol:
#   - Tool input is on stdin as JSON
#   - Exit 0 = allow the tool call
#   - Exit 2 = block the tool call and show the stderr output to the user
#   - Exit !=0,2 = non-blocking error (logged but call proceeds)
#
# This hook complements tools/gh-guard.sh which does the same check at the
# shell level (when Daniel runs gh directly). The Claude hook catches the
# failure when I (Claude) run the command via the Bash tool.
#
# Escape hatch:
#   If the user sets GH_SKIP_BRANCH_GUARD=1 in their shell, the Bash tool
#   will inherit it and this hook will detect and allow.

set -euo pipefail

# Read the tool input JSON from stdin
input="$(cat)"

# Extract the bash command being run
cmd="$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null || echo "")"

# Not a Bash call with a command → allow
[[ -z "$cmd" ]] && exit 0

# Fast path: only intercept if it contains `gh pr merge` AND `--delete-branch`
if ! echo "$cmd" | grep -qE '\bgh\s+pr\s+merge\b'; then
    exit 0
fi
if ! echo "$cmd" | grep -qE '(\s--delete-branch\b|\s-d\b)'; then
    exit 0
fi

# Respect escape hatch
if echo "$cmd" | grep -qE 'GH_SKIP_BRANCH_GUARD=1'; then
    exit 0
fi

# Extract the PR reference. Walk args looking for the first non-flag value
# after `gh pr merge`.
pr_ref=""
# Use awk to tokenize while handling multi-word commands
tokens=()
# shellcheck disable=SC2162
while IFS= read -r tok; do
    tokens+=("$tok")
done < <(echo "$cmd" | tr ' ' '\n')

# Find `merge` in tokens, then scan for positional arg
found_merge=false
i=0
while [[ $i -lt ${#tokens[@]} ]]; do
    tok="${tokens[$i]}"
    if [[ "$tok" == "merge" && "$found_merge" == false ]]; then
        found_merge=true
        i=$((i + 1))
        continue
    fi
    if [[ "$found_merge" == true ]]; then
        case "$tok" in
            --delete-branch|-d|--merge|--squash|--rebase|--auto|--admin) ;;
            --body|--body-file|--subject|--match-head-commit|-m|-s|-r) i=$((i + 1)) ;;  # skip arg value
            -*) ;;
            "") ;;
            *)
                pr_ref="$tok"
                break
                ;;
        esac
    fi
    i=$((i + 1))
done

# If no PR ref, we can't determine HEAD → block (fail safe)
if [[ -z "$pr_ref" ]]; then
    cat >&2 << EOF

  🚫 branch-guard (Claude hook): cannot determine PR from command.

  Command:
    $cmd

  The '--delete-branch' flag is dangerous on long-lived branches. This hook
  could not identify which PR is being merged, so it's blocking to be safe.

  If you want to proceed anyway (e.g., the PR reference is in a variable),
  prefix with GH_SKIP_BRANCH_GUARD=1:

    GH_SKIP_BRANCH_GUARD=1 $cmd

EOF
    exit 2
fi

# Look up the HEAD branch of the PR
# Find the --repo flag if present so we query the right repo
repo_flag=""
for ((j=0; j<${#tokens[@]}; j++)); do
    if [[ "${tokens[$j]}" == "--repo" && $((j+1)) -lt ${#tokens[@]} ]]; then
        repo_flag="--repo ${tokens[$((j+1))]}"
        break
    fi
done

head_ref=""
# shellcheck disable=SC2086
if head_ref="$(gh pr view "$pr_ref" $repo_flag --json headRefName --jq '.headRefName' 2>/dev/null)"; then
    :
else
    cat >&2 << EOF

  🚫 branch-guard (Claude hook): cannot determine HEAD branch of PR '$pr_ref'.

  Command:
    $cmd

  This could be: offline, auth expired, PR doesn't exist, or wrong repo.
  Blocking to be safe — the '--delete-branch' flag deletes the HEAD of
  the PR, which is dangerous on long-lived branches.

  If you're sure the HEAD is a feature branch (not main/master/develop):

    GH_SKIP_BRANCH_GUARD=1 $cmd

EOF
    exit 2
fi

case "$head_ref" in
    main|master|develop)
        cat >&2 << EOF

  🚫 branch-guard (Claude hook): BLOCKED.

  Command:
    $cmd

  The HEAD branch of PR '$pr_ref' is '$head_ref'. Using '--delete-branch'
  would DELETE '$head_ref' from the remote. This is almost certainly not
  what you want — long-lived branches should never be deleted on merge.

  To fix: drop the '--delete-branch' flag and try again:

    $(echo "$cmd" | sed -E 's/\s*(--delete-branch|-d)\b//g')

  To override (if you're intentionally decommissioning '$head_ref'):

    GH_SKIP_BRANCH_GUARD=1 $cmd

EOF
        exit 2
        ;;
    *)
        # Feature branch — allow
        exit 0
        ;;
esac
