---
id: TASK-35
title: Infrastructure map — vendor/provider cards below the diagram
status: Done
completed_date: '2026-02-27'
assignee: []
created_date: '2026-02-27 00:31'
labels:
  - cerebro
  - infrastructure
  - feature
dependencies: []
references:
  - cerebro/app/dashboard/infrastructure/page.tsx
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a row of cards below the React Flow infrastructure map that highlight the infrastructure service providers powering the stack. These are the platforms and tools Greenmark relies on — not the vendor data sources shown as nodes in the map, but the infra layer underneath (e.g., Railway for hosting, Supabase for the warehouse, GitHub for repos, Cloudflare for DNS, etc.).

Each card should show:
- Provider name and logo
- What it does for Greenmark (1-line role description)
- Current status or tier (e.g., "Pro plan", "Free tier")
- Link to the provider's dashboard or docs

This gives the team visibility into the infrastructure foundation — who runs what, and where to go when something needs attention.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Cards appear below the React Flow diagram on /dashboard/infrastructure
- [ ] #2 Each card shows provider name, role, status/tier, and link
- [ ] #3 Covers key infra providers (Railway, Supabase, GitHub, Cloudflare, etc.)
- [ ] #4 Cards are responsive and match Cerebro's card styling
<!-- AC:END -->
