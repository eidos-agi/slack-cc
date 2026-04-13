#!/usr/bin/env bash
# gh-guard.sh — transparent wrapper around `gh` that blocks dangerous flag
# combinations on long-lived branches.
#
# What it blocks:
#   gh pr merge <anything> --delete-branch
# when the HEAD of the PR is `main`, `master`, or `develop`.
#
# Why: `--delete-branch` deletes the HEAD branch of the PR. When the HEAD
# is a long-lived branch (e.g. a `develop → main` PR), this wipes develop.
# It happened on cerebro once. Never again.
#
# How to install:
#   mkdir -p ~/.local/bin
#   ln -sf /home/dev/repos/greenmark-cockpit/tools/gh-guard.sh ~/.local/bin/gh
#   # Make sure ~/.local/bin comes before /usr/local/bin in your PATH:
#   #   export PATH="$HOME/.local/bin:$PATH"  # add to ~/.zshrc or ~/.bashrc
#
# Escape hatch:
#   GH_SKIP_BRANCH_GUARD=1 gh pr merge 42 --delete-branch
# The guard will log a warning to stderr and pass through unchanged.
#
# Fail-safe behavior:
#   If we cannot determine the HEAD of the PR (offline, auth expired,
#   nonexistent PR), the guard BLOCKS the command rather than passing
#   through. A blocked command prints the exact override to use.
#
# Debug:
#   GH_GUARD_DEBUG=1 gh pr merge 42 --delete-branch
# Prints parsing decisions to stderr.

set -euo pipefail

# Find the real gh binary (anything in PATH that isn't this script)
find_real_gh() {
    local this_script
    this_script="$(readlink -f "${BASH_SOURCE[0]}")"
    local IFS=:
    local dir
    for dir in $PATH; do
        local candidate="$dir/gh"
        [[ -x "$candidate" ]] || continue
        local resolved
        resolved="$(readlink -f "$candidate" 2>/dev/null || echo "$candidate")"
        [[ "$resolved" == "$this_script" ]] && continue
        echo "$candidate"
        return 0
    done
    return 1
}

REAL_GH="$(find_real_gh || true)"
if [[ -z "$REAL_GH" ]]; then
    echo "gh-guard: could not locate real gh binary in PATH" >&2
    exit 127
fi

debug() {
    [[ "${GH_GUARD_DEBUG:-}" == "1" ]] && echo "gh-guard: $*" >&2 || true
}

# Save original args for pass-through and error messages
ORIG_ARGS=("$@")

# Escape hatch: user explicitly opts out
if [[ "${GH_SKIP_BRANCH_GUARD:-}" == "1" ]]; then
    echo "gh-guard: SKIP_BRANCH_GUARD=1 — passing through without checks" >&2
    exec "$REAL_GH" "${ORIG_ARGS[@]}"
fi

# Only intercept `gh pr merge ...`. Everything else passes through.
if [[ "${1:-}" != "pr" || "${2:-}" != "merge" ]]; then
    exec "$REAL_GH" "${ORIG_ARGS[@]}"
fi

debug "intercepted: ${ORIG_ARGS[*]}"

# Scan args for --delete-branch. If absent, nothing to guard.
has_delete=false
for arg in "${ORIG_ARGS[@]}"; do
    if [[ "$arg" == "--delete-branch" || "$arg" == "-d" ]]; then
        has_delete=true
        break
    fi
done

if [[ "$has_delete" == false ]]; then
    debug "no --delete-branch flag, passing through"
    exec "$REAL_GH" "${ORIG_ARGS[@]}"
fi

debug "--delete-branch present, determining PR HEAD"

# Figure out which PR is being merged.
# `gh pr merge [<number> | <url> | <branch>] [flags]`
# If no positional arg, it uses the current branch.
pr_ref=""
# Walk args (a local copy) to find the first positional arg after `pr merge`
set -- "${ORIG_ARGS[@]:2}"  # skip `pr merge`
while [[ $# -gt 0 ]]; do
    case "$1" in
        --delete-branch|-d) shift ;;
        --merge|--squash|--rebase|--auto|--admin) shift ;;
        --body|--body-file|--subject|--match-head-commit|-m|-s|-r) shift 2 ;;
        -*) shift ;;
        *) pr_ref="$1"; shift ;;
    esac
done

debug "pr_ref='$pr_ref'"

# Resolve the HEAD branch of the PR.
# If no ref given, use current git branch (which gh would do).
head_ref=""
if [[ -z "$pr_ref" ]]; then
    # No positional arg → current branch is the head
    head_ref="$(git branch --show-current 2>/dev/null || true)"
    debug "no pr_ref, using current branch: $head_ref"
else
    # Ask gh what the HEAD branch of this PR is
    if head_ref="$("$REAL_GH" pr view "$pr_ref" --json headRefName --jq '.headRefName' 2>/dev/null)"; then
        debug "gh pr view returned head_ref='$head_ref'"
    else
        # Fail-safe: couldn't determine HEAD → BLOCK
        echo "" >&2
        echo "  gh-guard: BLOCKED — cannot determine HEAD branch of PR '$pr_ref'." >&2
        echo "  Possible causes: offline, auth expired, PR does not exist, or repo access issue." >&2
        echo "" >&2
        echo "  This guard fails SAFE: rather than passing through a potentially dangerous" >&2
        echo "  --delete-branch command, it blocks and asks you to verify." >&2
        echo "" >&2
        echo "  If you are sure the HEAD is not a long-lived branch, override with:" >&2
        echo "" >&2
        echo "    GH_SKIP_BRANCH_GUARD=1 gh ${ORIG_ARGS[*]}" >&2
        echo "" >&2
        exit 1
    fi
fi

# If HEAD is a long-lived branch, block --delete-branch
case "$head_ref" in
    main|master|develop)
        echo "" >&2
        echo "  gh-guard: BLOCKED — '--delete-branch' on a PR whose HEAD is '$head_ref'." >&2
        echo "" >&2
        echo "  This would DELETE the '$head_ref' branch from the remote, which is" >&2
        echo "  almost certainly not what you want. Long-lived branches should never" >&2
        echo "  be deleted on merge." >&2
        echo "" >&2
        echo "  If you are intentionally decommissioning '$head_ref', override with:" >&2
        echo "" >&2
        echo "    GH_SKIP_BRANCH_GUARD=1 gh ${ORIG_ARGS[*]}" >&2
        echo "" >&2
        echo "  Otherwise, drop the --delete-branch flag and try again." >&2
        echo "" >&2
        exit 1
        ;;
    *)
        debug "head_ref='$head_ref' is not a long-lived branch, passing through"
        exec "$REAL_GH" "${ORIG_ARGS[@]}"
        ;;
esac
