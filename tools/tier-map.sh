#!/usr/bin/env bash
# tier-map.sh — Legacy tier classification. Being retired (ADR-2026-03).
#
# NEW SOURCE OF TRUTH: each repo's `.github/settings.yml` `repository.topics`
# field (tier-t1 / tier-t2 / tier-t3). Reconciled by the Probot/Settings
# GitHub App. Validated on a cadence by `.github/workflows/settings-yml-audit.yml`.
# See ADR-2026-03 for the full contract.
#
# This file stays until every repo has its own settings.yml. When a repo
# migrates, its entry is removed from this map on the same commit that
# adds settings.yml to the target repo (rhea rule: retirement mandatory
# on same commit as the new source of truth lands).
#
# Migration status (2026-04-16, session 30):
#   Migrated (settings.yml present + PR open or merged):
#     greenmark-cockpit, cerebro, cerebro-mcp, cerebro-telemetry,
#     cerebro-migrations, cerebro-qa, cerebro-ai-services,
#     cerebro-bot-farm, cerebro-warp-speed, cerebro-warp-speed-excel,
#     cerebro-excel, infra
#   Deferred:
#     data-daemon — pre-commit hook runs full pytest; needs Daniel's
#     local env to land. Tracked as follow-up.
#   Stale entry removed:
#     cerebro-vault — not in the GitHub org, retired here too.
#
# When TIER_MAP is empty AND data-daemon is migrated, delete this file.

declare -A TIER_MAP=(
    # T1 — Production
    [data-daemon]=1          # pending: pre-commit hook blocks landing via CI env
)

declare -a TIER_NAMES
TIER_NAMES[1]="Production"
TIER_NAMES[2]="Supporting"
TIER_NAMES[3]="Reference"
