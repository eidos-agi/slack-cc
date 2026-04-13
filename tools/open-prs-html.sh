#!/usr/bin/env bash
# open-prs-html.sh — Generate a local HTML dashboard of all open PRs.
#
# Usage:
#   ./tools/open-prs-html.sh              # writes pr-dashboard.html and opens it
#   ./tools/open-prs-html.sh --no-open    # writes file only
#
# Auto-refreshable: just re-run the script to update the page.

set -euo pipefail

GH_ORG="greenmark-waste-solutions"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$SCRIPT_DIR/../pr-dashboard.html"
OPEN_BROWSER=true
[[ "${1:-}" == "--no-open" ]] && OPEN_BROWSER=false

# Fetch all open PRs
prs_json=$(gh search prs --owner "$GH_ORG" --state open \
    --json repository,number,title,url,updatedAt,author,labels \
    --jq 'sort_by(.repository.name)' 2>&1)

count=$(echo "$prs_json" | jq 'length')

# Fetch CI status for each PR
pr_rows=""
while IFS= read -r line; do
    repo_name=$(echo "$line" | jq -r '.repository.name')
    pr_num=$(echo "$line" | jq -r '.number')
    title=$(echo "$line" | jq -r '.title')
    url=$(echo "$line" | jq -r '.url')
    author=$(echo "$line" | jq -r '.author.login')
    updated=$(echo "$line" | jq -r '.updatedAt')

    # Get CI checks
    checks_json=$(gh pr view "$pr_num" --repo "$GH_ORG/$repo_name" \
        --json statusCheckRollup \
        --jq '[.statusCheckRollup[] | {name: .name, status: .status, conclusion: .conclusion}]' 2>/dev/null || echo "[]")

    # Build check badges HTML
    check_badges=""
    all_pass=true
    any_fail=false
    while IFS= read -r check; do
        name=$(echo "$check" | jq -r '.name')
        conclusion=$(echo "$check" | jq -r '.conclusion')
        status=$(echo "$check" | jq -r '.status')

        if [[ "$conclusion" == "SUCCESS" ]]; then
            check_badges+="<span class=\"badge pass\">$name</span> "
        elif [[ "$conclusion" == "FAILURE" ]]; then
            check_badges+="<span class=\"badge fail\">$name</span> "
            all_pass=false
            any_fail=true
        elif [[ "$status" == "IN_PROGRESS" ]]; then
            check_badges+="<span class=\"badge running\">$name</span> "
            all_pass=false
        elif [[ "$conclusion" == "SKIPPED" ]]; then
            check_badges+="<span class=\"badge skip\">$name</span> "
        else
            check_badges+="<span class=\"badge unknown\">$name</span> "
            all_pass=false
        fi
    done < <(echo "$checks_json" | jq -c '.[]')

    if [[ -z "$check_badges" ]]; then
        check_badges="<span class=\"badge unknown\">no checks</span>"
        all_pass=false
    fi

    # Row status class
    if [[ "$any_fail" == true ]]; then
        row_class="row-fail"
    elif [[ "$all_pass" == true ]]; then
        row_class="row-pass"
    else
        row_class="row-pending"
    fi

    # Human-readable time
    updated_human=$(date -d "$updated" '+%b %d, %I:%M %p' 2>/dev/null || echo "$updated")

    pr_rows+="<tr class=\"$row_class\">
        <td><strong>$repo_name</strong></td>
        <td><a href=\"$url\" target=\"_blank\">#$pr_num</a></td>
        <td><a href=\"$url\" target=\"_blank\">$title</a></td>
        <td>$author</td>
        <td class=\"checks\">$check_badges</td>
        <td class=\"updated\">$updated_human</td>
    </tr>"
done < <(echo "$prs_json" | jq -c '.[]')

generated=$(date '+%b %d, %Y at %I:%M %p')

cat > "$OUT" << HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Greenmark — Open PRs</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: #0d1117; color: #e6edf3; padding: 2rem;
  }
  h1 { color: #3fb950; margin-bottom: 0.25rem; font-size: 1.5rem; }
  .subtitle { color: #8b949e; margin-bottom: 1.5rem; font-size: 0.9rem; }
  table { width: 100%; border-collapse: collapse; }
  th {
    text-align: left; padding: 0.6rem 0.8rem;
    background: #161b22; color: #8b949e; font-size: 0.8rem;
    text-transform: uppercase; letter-spacing: 0.05em;
    border-bottom: 1px solid #30363d;
  }
  td {
    padding: 0.6rem 0.8rem; border-bottom: 1px solid #21262d;
    font-size: 0.9rem; vertical-align: top;
  }
  tr:hover { background: #161b22; }
  a { color: #58a6ff; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .badge {
    display: inline-block; padding: 2px 8px; border-radius: 12px;
    font-size: 0.75rem; margin: 2px 2px; white-space: nowrap;
  }
  .badge.pass { background: #1a3a2a; color: #3fb950; }
  .badge.fail { background: #3d1a1a; color: #f85149; }
  .badge.running { background: #2d2a1a; color: #d29922; }
  .badge.skip { background: #1a1a2d; color: #8b949e; }
  .badge.unknown { background: #1a1a2d; color: #8b949e; }
  .checks { max-width: 400px; }
  .updated { color: #8b949e; white-space: nowrap; }
  .row-pass td:first-child { border-left: 3px solid #3fb950; }
  .row-fail td:first-child { border-left: 3px solid #f85149; }
  .row-pending td:first-child { border-left: 3px solid #d29922; }
  .footer { margin-top: 1.5rem; color: #8b949e; font-size: 0.8rem; }
  .merge-cmd {
    background: #161b22; padding: 0.8rem 1rem; border-radius: 6px;
    margin-top: 1rem; font-family: monospace; font-size: 0.85rem;
    color: #e6edf3; border: 1px solid #30363d;
  }
  .summary {
    display: flex; gap: 2rem; margin-bottom: 1.5rem;
  }
  .stat { text-align: center; }
  .stat-value { font-size: 2rem; font-weight: bold; }
  .stat-label { font-size: 0.8rem; color: #8b949e; }
  .stat-value.green { color: #3fb950; }
  .stat-value.red { color: #f85149; }
  .stat-value.yellow { color: #d29922; }
</style>
</head>
<body>
<h1>Greenmark — Open Pull Requests</h1>
<p class="subtitle">$count open across $GH_ORG · Generated $generated</p>

<table>
<thead>
<tr>
  <th>Repo</th>
  <th>PR</th>
  <th>Title</th>
  <th>Author</th>
  <th>CI Checks</th>
  <th>Updated</th>
</tr>
</thead>
<tbody>
$pr_rows
</tbody>
</table>

<div class="merge-cmd">
  <strong>Merge all passing:</strong><br>
  gh pr merge &lt;N&gt; --repo $GH_ORG/&lt;repo&gt; --squash --delete-branch
</div>

<p class="footer">
  Re-run <code>./tools/open-prs-html.sh</code> to refresh.
  This file is local-only and not committed to git.
</p>
</body>
</html>
HTMLEOF

echo "Written: $OUT ($count PRs)"

if [[ "$OPEN_BROWSER" == true ]]; then
    if command -v xdg-open &>/dev/null; then
        xdg-open "$OUT" 2>/dev/null &
    elif command -v open &>/dev/null; then
        open "$OUT"
    else
        echo "Open in browser: file://$OUT"
    fi
fi
