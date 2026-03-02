---
id: TASK-83
title: Add structured data / JSON-LD schema to Astro site
status: To Do
assignee:
  - Daniel Shanklin
created_date: '2026-02-28 02:16'
labels:
  - seo
  - astro
  - schema
milestone: SEO Phase 1
dependencies: []
references:
  - projects/seo-improvement/greenmarkwaste.com/seo-eisenhower-matrix.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add JSON-LD structured data to the Astro homepage and eventually all pages. This is the single highest-impact SERP change — enables rich snippets (business hours, service catalog, star ratings, FAQ dropdowns).

Schema types needed:
- **LocalBusiness** (or WasteManagementService subtype) — NAP, geo coordinates, opening hours, service area, logo
- **Organization** — logo, social profiles, sameAs links
- **Service** — one per service type (roll-off, commercial, portable restrooms, mini dumpsters)
- **FAQPage** — on any page with FAQ content (28 questions exist from Webflow)

Counterfactual: Competitors with schema get rich snippets — expandable FAQs, star ratings, business hours directly in search results. Higher CTR on the same ranking position. We show up as a plain blue link.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 LocalBusiness JSON-LD on homepage with correct NAP, hours, geo coords
- [ ] #2 Google Rich Results Test passes for LocalBusiness
- [ ] #3 Service schema for each of the 4 service types
- [ ] #4 FAQPage schema on FAQ page (once built)
- [ ] #5 Schema Markup Validator shows no errors
<!-- AC:END -->
