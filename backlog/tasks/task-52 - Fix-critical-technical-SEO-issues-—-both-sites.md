---
id: TASK-52
title: Fix critical technical SEO issues — both sites
status: To Do
assignee:
  - Daniel Shanklin
created_date: '2026-02-27 06:39'
labels:
  - seo
  - technical
milestone: m-0
dependencies:
  - TASK-46
  - TASK-49
  - TASK-50
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After baseline audits, fix the highest-ROI technical blockers identified. Typical Webflow fixes: 301 redirects for 404s, eliminate redirect chains, repair sitemap/canonical conflicts, optimize images (size/format), remove heavy unused embeds/scripts, fix accidental noindex. Ship fixes in Webflow, document changes in cockpit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All critical 404s resolved with 301 redirects
- [ ] #2 No redirect chains remain
- [ ] #3 No accidental noindex on money pages
- [ ] #4 PageSpeed improved on key pages
- [ ] #5 Changes documented in cockpit
<!-- AC:END -->
