#!/usr/bin/env bash
# tier-map.sh — Legacy tier classification. Being retired (ADR-2026-03).
#
# NEW SOURCE OF TRUTH: each repo's `.github/settings.yml` `repository.topics`
# field (tier-t1 / tier-t2 / tier-t3). Reconciled by the Probot/Settings
# GitHub App. See ADR-2026-03.
#
# This file stays until every repo has its own settings.yml. When a repo
# migrates, its entry is removed from this map on the same commit that
# adds settings.yml to the target repo (rhea rule: retirement mandatory
# on same commit as the new source of truth lands).
#
# Migration status:
#   greenmark-cockpit  — settings.yml present (2026-04-16); intentionally not
#                         in TIER_MAP since cockpit is where tier-map.sh lives
#   cerebro             — settings.yml shipping in cerebro PR #66 (2026-04-16);
#                         removed from TIER_MAP here on the same commit
#   all others          — still sourced from this file
#
# Tiers (still authoritative for unmigrated repos):
#   T1 Production  — CI, deploy, PR template, CODEOWNERS, dependabot (human review), branch protection, pre-push
#   T2 Supporting   — CI, PR template, dependabot (auto-merge patches), pre-push
#   T3 Reference    — pre-push hook only

declare -A TIER_MAP=(
    # T1 — Production: real users see these, outages page people
    # cerebro retired to its own .github/settings.yml (2026-04-16, ADR-2026-03)
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
