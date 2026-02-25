---
id: TASK-1.3
title: Explore HubSpot data via CLI
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 21:35'
updated_date: '2026-02-24 22:39'
labels:
  - hubspot
  - data-integration
dependencies:
  - TASK-1.2
  - TASK-1.9
references:
  - >-
    https://github.com/greenmark-waste-solutions/infra/blob/main/vendor-status.md
parent_task_id: TASK-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once the CLI is authenticated, explore what real data exists in Greenmark's HubSpot account. Map out available objects (contacts, companies, deals, tickets, custom objects) and their record counts. This feeds into the data-daemon connector design — we need to know what's actually in HubSpot before building extraction pipelines. Compare what we find against the 13 bronze tables proposed in the infra vendor research.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 List of HubSpot objects available in Greenmark account with record counts
- [ ] #2 Comparison against proposed bronze tables from infra vendor research
- [ ] #3 Sample data pulled for at least contacts, companies, and deals
- [ ] #4 Notes on data quality, completeness, and any surprises
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: BLOCKED — current PAK only has developer scopes. Cannot read CRM objects, custom objects, or HubDB. Need either admin to expand PAK scopes or a Private App created with CRM read access. Blocked on task-1.6 or task-1.7.

2026-02-24: Unblocked — test account created with Enterprise tier. Authenticate CLI against test account (ID 245316113), populate sample data, then explore. No longer blocked on production CRM scopes.

2026-02-24: CLI exploration complete. Key finding: HubSpot CLI is CMS/dev-tooling only — no commands for standard CRM objects (contacts, companies, deals, tickets). Custom objects and HubDB work via CLI. All CRM data access requires REST API with PAK as bearer token. Created TASK-1.9 (build skill), TASK-1.10 (seed data), TASK-1.11 (capability map). Test account has full Enterprise scopes and zero scope errors.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## Exploration Complete

Comprehensive exploration of HubSpot test account (245316113) via REST API.

### What We Mapped
- **36 scopes** verified via OAuth introspection (21 read, 11 write, 4 other)
- **Object access**: contacts/companies/deals/owners readable; tickets/products/emails denied
- **Property groups**: contacts=369 props (14 groups), companies=245 (12 groups), deals=199 (9 groups)
- **Engagement objects**: calls/meetings/tasks all readable with full `hs_*` properties
- **Associations**: v3 and v4 endpoints work; inline associations via query param work
- **API patterns proven**: list, single, search, batch read, properties, schemas, owners

### Key Discoveries
1. Standard CRM writes NOT in PAK — only custom objects writable
2. Deal stages use `externalOptions: true` — pipeline endpoint needs Private App auth
3. Email content redacted without `sales-email-read` scope
4. Batch read and search APIs confirmed working for data-daemon extraction
5. Legacy engagements endpoint reveals EMAIL engagement not visible in v3 emails endpoint

### Artifacts
- `EXPLORATION.md` — full findings document
- `scripts/hs-api.sh` — REST API wrapper (9 commands)
- `scripts/explore-helpers.py` — analysis helpers
- `scripts/show-filled.py` / `show-all-filled.py` — property filters
<!-- SECTION:FINAL_SUMMARY:END -->
