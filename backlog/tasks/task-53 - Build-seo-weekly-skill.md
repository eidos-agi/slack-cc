---
id: TASK-53
title: Build /seo-weekly skill
status: To Do
assignee:
  - Daniel Shanklin
created_date: '2026-02-27 06:39'
labels:
  - seo
  - skill
  - automation
milestone: m-0
dependencies:
  - TASK-51
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the /seo-weekly Claude Code skill for weekly SEO heartbeat reports. The skill should: report new GSC issues, identify top gainers/losers by clicks/impressions, flag high-impression/low-CTR queries (title/meta candidates), flag queries at position 8-20 (easy wins), detect CWV regressions. Output: concise weekly delta report committed to cockpit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Skill file exists at .claude/skills/seo-weekly/skill.md
- [ ] #2 Produces weekly delta report with gainers/losers
- [ ] #3 Flags easy-win queries (position 8-20)
- [ ] #4 Committed to cockpit on each run
<!-- AC:END -->
