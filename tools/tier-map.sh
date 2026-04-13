#!/usr/bin/env bash
# tier-map.sh — Single source of truth for repo tier classification.
#
# Sourced by bootstrap-repo.sh and ensure-release.sh.
# When a repo changes tier, edit it HERE and re-run ensure-release.sh --apply.
#
# Tiers:
#   T1 Production  — CI, deploy, PR template, CODEOWNERS, dependabot (human review), branch protection, pre-push
#   T2 Supporting   — CI, PR template, dependabot (auto-merge patches), pre-push
#   T3 Reference    — pre-push hook only

declare -A TIER_MAP=(
    # T1 — Production: real users see these, outages page people
    [cerebro]=1
    [cerebro-migrations]=1
    [data-daemon]=1

    # T2 — Supporting: internal tools, QA, analytics
    [cerebro-qa]=2
    [cerebro-warp-speed]=2
    [cerebro-warp-speed-excel]=2
    [cerebro-ai-services]=2
    [cerebro-bot-farm]=2

    # T3 — Reference: docs, config, research
    [infra]=3
    [greenmark-cockpit]=3
    [cerebro-mcp]=3
    [cerebro-vault]=3
    [cerebro-excel]=3
)

declare -a TIER_NAMES
TIER_NAMES[1]="Production"
TIER_NAMES[2]="Supporting"
TIER_NAMES[3]="Reference"
