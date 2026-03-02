---
id: TASK-82
title: Add canonical tags + XML sitemap + Open Graph meta tags
status: To Do
assignee:
  - Daniel Shanklin
created_date: '2026-02-28 02:16'
labels:
  - seo
  - astro
  - quick-win
milestone: SEO Phase 1
dependencies: []
references:
  - projects/seo-improvement/greenmarkwaste.com/seo-eisenhower-matrix.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Quick-win technical SEO additions to the Astro site (gmw-dot-com-astro). Three items in one commit:

1. **Canonical tags** — `<link rel="canonical">` in Layout.astro. Three URLs currently serve overlapping content (greenmarkwaste.com, gmw-dot-com-production.up.railway.app, gm2026.jettaintelligence.com) with no canonical signal. Point to whatever the final production domain will be.

2. **XML Sitemap** — Install `@astrojs/sitemap` integration. robots.txt already references a sitemap URL that 404s — this fixes that.

3. **Open Graph + Twitter Card tags** — og:title, og:description, og:image, og:url, og:type, twitter:card in Layout.astro. Currently every social share shows a broken/empty preview.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every page has a <link rel='canonical'> tag pointing to the production domain
- [ ] #2 sitemap.xml generates at build time and is accessible at /sitemap.xml
- [ ] #3 robots.txt sitemap reference resolves (no 404)
- [ ] #4 Open Graph tags render correct previews when shared on LinkedIn/Slack (test with og debugger)
- [ ] #5 Twitter card validator shows summary_large_image card
<!-- AC:END -->
