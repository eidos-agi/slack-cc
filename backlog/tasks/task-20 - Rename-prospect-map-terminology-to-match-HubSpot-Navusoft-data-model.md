---
id: TASK-20
title: Rename prospect map terminology to match HubSpot/Navusoft data model
status: To Do
assignee: []
created_date: '2026-02-27 00:27'
labels:
  - cerebro
  - prospect-map
  - data-model
milestone: Cerebro — Prospect Map
dependencies: []
references:
  - infra/vendors/hubspot/api-data-model.md
  - infra/vendors/navusoft/api-data-model.md
  - cerebro/lib/mock-prospects.ts
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Align all labels, types, and field names in the prospect map with actual vendor terminology discovered during HubSpot API exploration and Navusoft data model research.

Renames:
- "Record Type" (customer/lead/prospect) → **Lifecycle Stage** (HubSpot's term)
- "Opportunity Stage" → **Deal Stage** (HubSpot calls deals, not opportunities)
- "Annual Value" → **Deal Amount** (maps to `deal.amount`)
- "Accounts" back to **Companies** (HubSpot's term, not Salesforce "Accounts")
- "Owner" stays (both systems use this)

Affects: `lib/mock-prospects.ts` types + constants, `map/page.tsx` labels, `map-filters.tsx` filter labels, `prospect-map.tsx` tooltip text, detail panel labels.

Post-close terminology bridge: HubSpot Company → wins Deal → becomes Navusoft Customer with Sites and Service Agreements.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All UI labels match HubSpot terminology (Companies, Deal Stage, Lifecycle Stage, Deal Amount)
- [ ] #2 TypeScript types renamed (OpportunityStage → DealStage, RecordType → LifecycleStage)
- [ ] #3 Filter pill labels updated
- [ ] #4 Detail panel labels updated
- [ ] #5 JSON output field names updated
- [ ] #6 Build passes clean
<!-- AC:END -->
