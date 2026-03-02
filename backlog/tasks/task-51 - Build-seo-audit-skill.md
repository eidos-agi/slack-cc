---
id: TASK-51
title: Build /seo-audit skill
status: To Do
assignee:
  - Daniel Shanklin
created_date: '2026-02-27 06:38'
labels:
  - seo
  - skill
  - automation
milestone: m-0
dependencies:
  - TASK-49
  - TASK-50
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the /seo-audit Claude Code skill that automates baseline SEO audits. The skill should: fetch GSC coverage/errors + top queries/pages, run PageSpeed Insights for key templates, crawl sitemap URLs + check HTTP status/canonicals/meta robots/titles/H1, identify duplicate titles/meta and missing H1, produce a structured Markdown audit report. Uses free APIs only: GSC API, PageSpeed Insights API, sitemap parsing, HTML checks. Build AFTER doing the first manual audits so the skill encodes lessons learned.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Skill file exists at .claude/skills/seo-audit/skill.md
- [ ] #2 Skill produces structured Markdown audit report
- [ ] #3 Uses only free APIs (GSC, PageSpeed Insights, sitemap parsing)
- [ ] #4 Tested against both domains
<!-- AC:END -->
