#!/usr/bin/env bash
# ensure-release.sh — Audit all repos against their tier classification.
#
# Usage:
#   ./tools/ensure-release.sh              # dry run — show drift
#   ./tools/ensure-release.sh --apply      # fix gaps via bootstrap-repo.sh
#
# Reads tier classification from tier-map.sh.
# Reports what each repo SHOULD have vs what it DOES have.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/tier-map.sh"

REPOS_DIR="${REPOS_DIR:-/home/dev/repos}"
DRY_RUN=true
[[ "${1:-}" == "--apply" ]] && DRY_RUN=false

# ── Expected artifacts per tier ──────────────────────────────────

# Returns space-separated list of artifact labels
artifacts_for_tier() {
    local tier="$1"
    case "$tier" in
        1) echo "ci guard-main PR-tmpl CODEOWNERS dependabot hook" ;;
        2) echo "ci guard-main PR-tmpl dependabot hook" ;;
        3) echo "hook" ;;
    esac
}

# Check if a single artifact exists for a repo
check_artifact() {
    local repo="$1" artifact="$2"
    case "$artifact" in
        ci)          [[ -f "$repo/.github/workflows/ci.yml" ]] ;;
        guard-main)  [[ -f "$repo/.github/workflows/guard-main.yml" ]] ;;
        PR-tmpl)     [[ -f "$repo/.github/pull_request_template.md" ]] ;;
        CODEOWNERS)  [[ -f "$repo/.github/CODEOWNERS" ]] ;;
        dependabot)  [[ -f "$repo/.github/dependabot.yml" ]] ;;
        hook)        [[ -f "$repo/.git/hooks/pre-push" ]] && grep -q "ensure-flow hook" "$repo/.git/hooks/pre-push" 2>/dev/null ;;
        *)           return 1 ;;
    esac
}

# ── Main audit ───────────────────────────────────────────────────

echo "ensure-release.sh: auditing ${#TIER_MAP[@]} repos across 3 tiers"
[[ "$DRY_RUN" == true ]] && echo "  MODE: dry run (use --apply to fix gaps)"
echo

total=0
compliant=0
drifted=0
not_cloned=0
repos_to_fix=()

for tier in 1 2 3; do
    echo "── T${tier} ${TIER_NAMES[$tier]} ──────────────────────────────────────────"

    # Collect repos at this tier, sorted
    tier_repos=()
    while IFS= read -r name; do
        tier_repos+=("$name")
    done < <(for name in "${!TIER_MAP[@]}"; do
        [[ "${TIER_MAP[$name]}" -eq "$tier" ]] && echo "$name"
    done | sort)

    expected="$(artifacts_for_tier "$tier")"

    for name in "${tier_repos[@]}"; do
        total=$((total + 1))
        repo="$REPOS_DIR/$name"

        if [[ ! -d "$repo/.git" ]]; then
            printf "  %-28s %s\n" "$name" "[NOT CLONED]"
            not_cloned=$((not_cloned + 1))
            continue
        fi

        # Check each expected artifact
        present=()
        missing=()
        for artifact in $expected; do
            if check_artifact "$repo" "$artifact"; then
                present+=("$artifact")
            else
                missing+=("$artifact")
            fi
        done

        # Format output
        artifact_line=""
        for artifact in $expected; do
            found=false
            for p in "${present[@]}"; do
                [[ "$p" == "$artifact" ]] && found=true && break
            done
            if [[ "$found" == true ]]; then
                artifact_line+=" $artifact"
            else
                artifact_line+=" [$artifact]"
            fi
        done

        if [[ ${#missing[@]} -eq 0 ]]; then
            printf "  %-28s %s  ✓\n" "$name" "$artifact_line"
            compliant=$((compliant + 1))
        else
            printf "  %-28s %s\n" "$name" "$artifact_line"
            printf "  %-28s DRIFT: missing %s\n" "" "${missing[*]}"
            drifted=$((drifted + 1))
            repos_to_fix+=("$name")
        fi
    done
    echo
done

# ── Report ───────────────────────────────────────────────────────

echo "─── RELEASE PRACTICES REPORT ──────────────────────────"
echo "  Repos audited:      $total"
echo "  Fully compliant:    $compliant"
echo "  Drift detected:     $drifted"
echo "  Not cloned:         $not_cloned"
if [[ "$DRY_RUN" == true ]]; then
    echo "  Mode:               DRY RUN — nothing changed"
else
    echo "  Mode:               APPLYING fixes..."
fi
echo "────────────────────────────────────────────────────────"

# ── Apply fixes ──────────────────────────────────────────────────

if [[ "$DRY_RUN" == false && ${#repos_to_fix[@]} -gt 0 ]]; then
    echo
    for name in "${repos_to_fix[@]}"; do
        echo "── Bootstrapping $name ──"
        "$SCRIPT_DIR/bootstrap-repo.sh" "$REPOS_DIR/$name"
        echo
    done

    echo "Done. Re-run without --apply to verify zero drift."
fi
