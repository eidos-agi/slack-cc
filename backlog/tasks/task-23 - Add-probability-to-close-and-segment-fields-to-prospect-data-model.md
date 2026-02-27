---
id: TASK-23
title: Add probability-to-close and segment fields to prospect data model
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
  - cerebro/lib/mock-prospects.ts
  - infra/vendors/hubspot/api-data-model.md
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the ProspectCompany mock data schema with fields that will exist in real HubSpot data and enable richer analysis:

- `probability` — maps to HubSpot's `hs_deal_stage_probability` (0-100). Useful for weighted pipeline calculations.
- `segment` — e.g., "Municipal", "Commercial", "HOA" (may overlap with existing `type` field, evaluate if separate or merge)
- `productLine` — if Greenmark tracks service type on deals (roll-off, front-load, residential carts)

Keep as separate keys (not baked into strings) so JSON is analysis-ready. Update mock data with realistic probability values per deal stage.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ProspectCompany type includes probability field (number 0-100)
- [ ] #2 Mock data has realistic probability values per deal stage
- [ ] #3 JSON output includes new fields
- [ ] #4 Sparkline or filter support for probability (optional)
<!-- AC:END -->
