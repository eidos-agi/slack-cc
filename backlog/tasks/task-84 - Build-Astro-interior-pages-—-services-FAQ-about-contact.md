---
id: TASK-84
title: 'Build Astro interior pages — services, FAQ, about, contact'
status: To Do
assignee:
  - Daniel Shanklin
created_date: '2026-02-28 02:17'
labels:
  - seo
  - astro
  - content
milestone: SEO Phase 1
dependencies: []
references:
  - projects/seo-improvement/greenmarkwaste.com/seo-eisenhower-matrix.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Astro site only has a homepage. All nav/footer links go to 404s. Port Webflow content to Astro pages. This unblocks all content-based SEO improvements (internal linking, service-specific schema, FAQ schema, service area pages).

Pages needed (content exists in Webflow export at /tmp/gmw-webflow/):
- /roll-off-dumpsters — service page with sizing guide, pricing info, FAQs
- /commercial-dumpsters — service page with pickup schedules, container sizes
- /portable-restrooms — service page with event/jobsite options
- /mini-dumpsters — service page with residential use cases
- /faqs — 28 questions across 5 categories (biggest FAQ schema opportunity)
- /about-us — company story, team, testimonials
- /contact-us — form, map, phone, address
- /request-services — service request form

Counterfactual: Google can't rank pages that don't exist. A competitor with dedicated service pages ranks for those keywords. We literally cannot compete on any non-brand query without pages.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 8 pages render with correct content from Webflow export
- [ ] #2 No broken internal links (all nav/footer links resolve)
- [ ] #3 Each page has unique title tag and meta description
- [ ] #4 FAQ page has accordion/expandable format for the 28 questions
- [ ] #5 All pages pass Lighthouse accessibility 100
<!-- AC:END -->
