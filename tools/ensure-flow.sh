#!/usr/bin/env bash
# ensure-flow.sh — audit and fix the feature → develop → main flow across
# deployable repos.
#
# Usage:
#   ./tools/ensure-flow.sh              # dry run, show what would change
#   ./tools/ensure-flow.sh --apply      # actually create branches and install hooks
#
# What it does for each repo in the allowlist:
#   1. Confirms `main` (or `master`) exists on remote
#   2. If `develop` doesn't exist: creates it from main/master and pushes
#   3. Warns if `develop` exists but is >10 commits behind main (auto-fix
#      would be destructive — Daniel decides)
#   4. Installs `.git/hooks/pre-push` that blocks direct pushes to main,
#      master, and develop (feature branches only)
#
# Why an allowlist:
#   Not every repo needs the three-layer flow. Deployed apps, database
#   state, and stakeholder-facing docs do. Simple tool/utility repos
#   don't. Hardcoding the list keeps the rule explicit — no marker file
#   convention to maintain.
#
# Relationship to tier-map.sh / ensure-release.sh:
#   ensure-release.sh (ADR-2026-02) handles artifact drift (CI, PR templates,
#   hooks, etc.) across ALL 13 repos. This script focuses specifically on the
#   develop-branch lifecycle: creating develop, checking staleness vs main.
#   The allowlist here is a SUBSET of tier-map.sh — only repos that use the
#   feature→develop→main flow, not T3 reference repos.
#   Pre-push hooks overlap: both scripts install the same hook. That's fine —
#   both are idempotent.
#
# Idempotent: safe to run multiple times. Prints one line per repo
# saying what was done or skipped.

set -euo pipefail

REPOS_DIR="${REPOS_DIR:-/home/dev/repos}"
DRY_RUN=true
[[ "${1:-}" == "--apply" ]] && DRY_RUN=false

# ── Allowlist ──────────────────────────────────────────────────────────
# Repos that require the feature → develop → main flow.
# To add a new repo: append it here and re-run with --apply.
ALLOWLIST=(
    cerebro                    # Next.js dashboard app (production site)
    cerebro-migrations         # database schema — staging + production
    cerebro-qa                 # QA dashboard
    cerebro-warp-speed         # legacy local-first agent (transitioning)
    cerebro-warp-speed-excel   # semantic layer + Excel oracle
    data-daemon                # extraction pipeline — deployed on Railway
    infra                      # vendor research + connection-specs (stakeholder-facing)
    greenmark-cockpit          # this repo — stakeholder-facing planning
)

# ── Helpers ────────────────────────────────────────────────────────────

GIT_IDENTITY_NAME="${GIT_IDENTITY_NAME:-Daniel Shanklin}"
GIT_IDENTITY_EMAIL="${GIT_IDENTITY_EMAIL:-daniel@boone.voyage}"

log() { echo "  [ensure-flow] $*"; }
info() { echo "  [INFO]  $*"; }
warn() { echo "  [WARN]  $*" >&2; }
err() { echo "  [ERR]   $*" >&2; }

find_primary_branch() {
    # Returns main, master, or empty
    local repo="$1"
    if git -C "$repo" show-ref --verify --quiet refs/remotes/origin/main; then
        echo "main"
    elif git -C "$repo" show-ref --verify --quiet refs/remotes/origin/master; then
        echo "master"
    else
        echo ""
    fi
}

branch_exists_remote() {
    local repo="$1"
    local branch="$2"
    git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$branch"
}

commits_behind() {
    # Returns number of commits that ahead_branch is behind behind_branch
    local repo="$1"
    local ahead_branch="$2"
    local behind_branch="$3"
    git -C "$repo" rev-list --count "origin/$ahead_branch..origin/$behind_branch" 2>/dev/null || echo "?"
}

install_pre_push_hook() {
    local repo="$1"
    local hook="$repo/.git/hooks/pre-push"

    if [[ -f "$hook" ]] && grep -q "ensure-flow hook" "$hook" 2>/dev/null; then
        return 0  # Already installed
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log "(dry run) would install pre-push hook at $hook"
        return 0
    fi

    cat > "$hook" << 'HOOK'
#!/usr/bin/env bash
# ensure-flow hook — blocks direct pushes to main, master, and develop.
# Feature branches only. Go through a PR.
#
# Installed by tools/ensure-flow.sh in greenmark-cockpit.

while read local_ref local_sha remote_ref remote_sha; do
    case "$remote_ref" in
        refs/heads/main|refs/heads/master|refs/heads/develop)
            branch="${remote_ref##refs/heads/}"
            echo ""
            echo "  BLOCKED: Direct push to $branch."
            echo "  Feature branches only. Open a PR."
            echo ""
            exit 1
            ;;
    esac
done

exit 0
HOOK
    chmod +x "$hook"
}

# ── Main loop ──────────────────────────────────────────────────────────

echo "ensure-flow.sh: auditing ${#ALLOWLIST[@]} deployable repos"
[[ "$DRY_RUN" == true ]] && echo "  MODE: dry run (use --apply to make changes)"
echo

fixed=0
warned=0
skipped=0
missing=0

for name in "${ALLOWLIST[@]}"; do
    repo="$REPOS_DIR/$name"

    if [[ ! -d "$repo/.git" ]]; then
        err "$name: not a git repo at $repo — skipping"
        missing=$((missing + 1))
        continue
    fi

    # Refresh remote refs
    git -C "$repo" fetch --quiet origin 2>/dev/null || {
        warn "$name: fetch failed, skipping"
        continue
    }

    primary="$(find_primary_branch "$repo")"
    if [[ -z "$primary" ]]; then
        err "$name: neither main nor master exists on origin — skipping"
        missing=$((missing + 1))
        continue
    fi

    # Check develop
    if ! branch_exists_remote "$repo" "develop"; then
        if [[ "$DRY_RUN" == true ]]; then
            log "$name: WOULD create develop from $primary"
        else
            log "$name: creating develop from $primary"
            git -C "$repo" push origin "origin/$primary:refs/heads/develop" 2>&1 | sed 's/^/         /'
        fi
        fixed=$((fixed + 1))
    else
        # develop exists — check if it's stale vs primary
        behind="$(commits_behind "$repo" develop "$primary")"
        if [[ "$behind" == "?" ]]; then
            warn "$name: could not compute develop staleness"
        elif [[ "$behind" -gt 10 ]]; then
            warn "$name: develop is $behind commits behind $primary. Not auto-fixing (would be destructive). Consider rebasing develop onto $primary manually."
            warned=$((warned + 1))
        else
            log "$name: develop exists, $behind commits behind $primary (OK)"
            skipped=$((skipped + 1))
        fi
    fi

    # Install pre-push hook
    install_pre_push_hook "$repo"
done

echo
echo "─── ENSURE-FLOW REPORT ─────────────────────────────────"
echo "  Fixed / would fix:    $fixed"
echo "  Warnings (stale):     $warned"
echo "  Already OK:           $skipped"
echo "  Missing / broken:     $missing"
[[ "$DRY_RUN" == true ]] && echo "  Mode:                 DRY RUN — nothing changed"
[[ "$DRY_RUN" == false ]] && echo "  Mode:                 APPLIED"
echo "────────────────────────────────────────────────────────"
