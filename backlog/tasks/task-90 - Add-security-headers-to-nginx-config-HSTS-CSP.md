---
id: TASK-90
title: 'Add security headers to nginx config (HSTS, CSP)'
status: To Do
assignee:
  - Daniel Shanklin
created_date: '2026-02-28 02:18'
labels:
  - seo
  - security
  - quick-win
milestone: SEO Phase 1
dependencies: []
references:
  - projects/seo-improvement/greenmarkwaste.com/seo-eisenhower-matrix.md
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The nginx.conf already has X-Frame-Options, X-Content-Type-Options, and Referrer-Policy. Missing: Strict-Transport-Security (HSTS) and Content-Security-Policy (CSP). PageSpeed Best Practices flags these.

Quick fix — add to nginx.conf:
- `add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;`
- Basic CSP header

Not a direct ranking factor but affects PageSpeed Best Practices score (currently 96) and enterprise buyer security scans.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 HSTS header present with max-age >= 31536000
- [ ] #2 CSP header present
- [ ] #3 PageSpeed Best Practices score improves
- [ ] #4 securityheaders.com scan shows A or A+ rating
<!-- AC:END -->
