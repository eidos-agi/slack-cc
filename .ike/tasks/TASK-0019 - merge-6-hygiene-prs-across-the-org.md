---
id: TASK-0019
title: Merge 6 hygiene PRs across the org
status: To Do
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
---
Open PRs from Session 21: cerebro-qa#1 (CI + lint), cerebro-warp-speed#1 (CI + lint), cerebro-warp-speed-excel#1 (CI + ruff.toml + lint), cerebro-migrations#1 (gitignore), gmw-dot-com-astro#1 (gitignore), tech-deck#1 (gitignore). All green, all low-stakes. Merge before starting Sage rebuild.
