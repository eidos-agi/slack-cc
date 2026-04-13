#!/usr/bin/env bash
# open-prs.sh — Show all open PRs across the Greenmark GitHub org.
#
# Usage:
#   ./tools/open-prs.sh           # list all open PRs
#   ./tools/open-prs.sh --checks  # include CI status for each PR
#
# Requires: gh CLI authenticated to greenmark-waste-solutions org.

set -euo pipefail

GH_ORG="greenmark-waste-solutions"
SHOW_CHECKS=false
[[ "${1:-}" == "--checks" ]] && SHOW_CHECKS=true

prs=$(gh search prs --owner "$GH_ORG" --state open \
    --json repository,number,title,url,updatedAt,author \
    --jq 'sort_by(.repository.name)' 2>&1)

count=$(echo "$prs" | jq 'length')

if [[ "$count" -eq 0 ]]; then
    echo "No open PRs across $GH_ORG."
    exit 0
fi

echo "Open PRs across $GH_ORG ($count total):"
echo

echo "$prs" | jq -r '.[] | "\(.repository.name)#\(.number)|\(.title)|\(.author.login)|\(.url)"' | \
while IFS='|' read -r repo_pr title author url; do
    printf "  %-35s %s\n" "$repo_pr" "$title"

    if [[ "$SHOW_CHECKS" == true ]]; then
        repo_name="${repo_pr%%#*}"
        pr_num="${repo_pr##*#}"
        checks=$(gh pr view "$pr_num" --repo "$GH_ORG/$repo_name" \
            --json statusCheckRollup \
            --jq '[.statusCheckRollup[] | if .conclusion == "SUCCESS" then "✓" elif .conclusion == "FAILURE" then "✗" elif .status == "IN_PROGRESS" then "…" else "?" end + " " + .name] | join("  ")' 2>/dev/null || echo "  (no checks)")
        echo "    $checks"
    fi
done

echo
echo "Merge: gh pr merge <N> --repo $GH_ORG/<repo> --squash --delete-branch"
