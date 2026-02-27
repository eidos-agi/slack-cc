---
id: TASK-38
title: Identify registrar and host for htdisposal.com
status: To Do
assignee: []
created_date: '2026-02-27 00:53'
updated_date: '2026-02-27 00:53'
labels:
  - infra
  - dns
  - hometown
dependencies: []
references:
  - 'https://github.com/greenmark-waste-solutions/infra'
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Determine who the domain registrar and web host are for htdisposal.com (Hometown Disposal / Indiana entity website). Need to know:
- Domain registrar (GoDaddy, Namecheap, Cloudflare, etc.)
- DNS provider (may differ from registrar)
- Web host / where the site is served from (Webflow confirmed, but verify)
- Who has login credentials for registrar and DNS
- Domain expiration date
- Any email hosting tied to the domain (MX records)

This matters for SEO work (TASK-4), DNS changes, and ensuring Greenmark controls their own infrastructure.

**Output**: Document findings in the infra repo (e.g., infra/dns/htdisposal.com.md or similar).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Domain registrar identified for htdisposal.com
- [ ] #2 DNS provider identified
- [ ] #3 Web host confirmed (Webflow or other)
- [ ] #4 Credential holder identified (who can log in to manage DNS)
- [ ] #5 Domain expiration date documented
<!-- AC:END -->
