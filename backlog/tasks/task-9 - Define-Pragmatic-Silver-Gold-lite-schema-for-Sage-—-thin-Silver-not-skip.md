---
id: TASK-9
title: 'Define Pragmatic Silver + Gold-lite schema for Sage — thin Silver, not skip'
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:38'
updated_date: '2026-02-27 00:44'
labels:
  - mvp
  - architecture
  - data-daemon
milestone: MVP
dependencies: []
references:
  - infra/decisions/ADR-2026-01.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Originally proposed skipping Silver entirely for MVP. After second opinion, the recommendation is **Pragmatic Silver** — a thin 1:1 cleaning layer that adds ~1 day but prevents painful retrofitting when vendors 3-6 arrive.

**Pragmatic Silver approach:**
- Bronze: raw Sage data lands as-is (JSONB)
- Silver: 1:1 mapped tables with cleaning — cast types, rename columns to snake_case, filter junk, add `greenmark_entity_id` column (entity resolution lives here)
- Gold-lite: `gold.monthly_financials` with revenue, expenses, net by entity by month — pure aggregation from Silver

**Flow:**
```
bronze.sage_raw → (clean + entity tag) → silver.sage_transactions
silver.sage_transactions → (aggregate) → gold.monthly_financials
```

This is the shortest path to Michael seeing real numbers while maintaining architectural integrity. Gold becomes pure aggregation, Silver handles all cleaning and entity tagging.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 gold.monthly_financials table defined with revenue, expenses, net by entity by month
- [ ] #2 Bronze → Gold-lite transformation works with real Sage data (not synthetic)
- [ ] #3 At least one Cerebro chart wired to this table showing real numbers
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Feb 27: **Second opinion (Gemini 2.5 Pro)** — Don't skip Silver. Do 'Pragmatic Silver' instead. Skipping makes Gold-lite transformations monolithic, brittle, non-reusable. Thin Silver adds ~1 day but saves weeks of refactoring when vendors 3-6 arrive. 'Retrofitting Silver later' = foundational surgery, not a feature add. Entity resolution naturally lives in Silver (add `greenmark_entity_id`). Gold becomes pure aggregation: `SUM(amount) GROUP BY month, entity`.
<!-- SECTION:NOTES:END -->
