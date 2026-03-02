---
id: TASK-91
title: Deploy Astro site to production domain (greenmarkwaste.com)
status: To Do
assignee:
  - Daniel Shanklin
created_date: '2026-02-28 02:18'
labels:
  - seo
  - infra
  - dns
  - migration
milestone: SEO Phase 1
dependencies:
  - TASK-84
  - TASK-82
  - TASK-47
  - TASK-37
references:
  - projects/seo-improvement/greenmarkwaste.com/seo-eisenhower-matrix.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Astro site is live at gmw-dot-com-production.up.railway.app with a pending custom domain at gm2026.jettaintelligence.com. Eventually it needs to replace the Webflow site at greenmarkwaste.com.

Prerequisites:
- Interior pages built (TASK-84) — can't go live with 404s
- Canonical tags set (TASK-82)
- GA4 tracking in place (TASK-47)
- Identify who controls greenmarkwaste.com DNS (TASK-37)

Steps:
1. Confirm DNS registrar for greenmarkwaste.com
2. Add greenmarkwaste.com as custom domain on Railway service
3. Update DNS records (CNAME or A record)
4. Update canonical tags to point to greenmarkwaste.com
5. Set up 301 redirects for any URL changes
6. Submit updated sitemap to GSC
7. Monitor for crawl errors in GSC for 2 weeks post-migration
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 greenmarkwaste.com serves the Astro site (not Webflow)
- [ ] #2 All old Webflow URLs 301 redirect to Astro equivalents
- [ ] #3 SSL certificate active on greenmarkwaste.com
- [ ] #4 Google Search Console shows no new crawl errors post-migration
- [ ] #5 PageSpeed score maintained at 90+ after domain switch
<!-- AC:END -->
