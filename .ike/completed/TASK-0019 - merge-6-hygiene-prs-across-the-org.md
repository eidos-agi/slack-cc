---
id: TASK-0019
title: Merge 6 hygiene PRs across the org
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-01: Session 21 Cleanup'
tags:
  - cleanup
  - prs
acceptance-criteria:
  - All 6 PRs merged
  - intel.sh sweep shows 0 unpushed commits across affected repos
  - No CI failures on main after merge
updated: '2026-04-10'
---
Open PRs from Session 21: cerebro-qa#1 (CI + lint), cerebro-warp-speed#1 (CI + lint), cerebro-warp-speed-excel#1 (CI + ruff.toml + lint), cerebro-migrations#1 (gitignore), gmw-dot-com-astro#1 (gitignore), tech-deck#1 (gitignore). All green, all low-stakes. Merge before starting Sage rebuild.

**Completion notes:** All 6 hygiene PRs merged: cerebro-qa#1, cerebro-warp-speed#1, cerebro-warp-speed-excel#1, cerebro-migrations#1 (rebased to resolve conflict before merge), gmw-dot-com-astro#1 (already merged before this task started), tech-deck#1 (already merged). Branches deleted. CI green on all four Python repos that had workflows.
