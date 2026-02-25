---
id: TASK-1.9
title: Build Claude Code skill for HubSpot data exploration
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 22:16'
updated_date: '2026-02-25 07:44'
labels:
  - hubspot
  - tooling
  - skill
dependencies: []
documentation:
  - >-
    https://developers.hubspot.com/docs/api-reference/crm-custom-objects-v3/guide
parent_task_id: TASK-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The HubSpot CLI doesn't support standard CRM object queries (contacts, companies, deals, tickets). Build a Claude Code skill in greenmark-planning that wraps HubSpot REST API calls so Claude can explore CRM data from the terminal. The skill should read the PAK from `hubspot.config.yml` (or env var) and make authenticated API calls via curl. Target the test account (245316113) for development, production (244562652) later.\n\nKey API endpoints to support:\n- GET /crm/v3/objects/{objectType} — list records\n- GET /crm/v3/objects/{objectType}/{id} — get single record\n- GET /crm/v3/schemas — list all object schemas (standard + custom)\n- GET /crm/v3/objects/{objectType}?count=true — record counts\n- POST /crm/v3/objects/{objectType}/search — filtered queries
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Skill can list all CRM object types and record counts
- [x] #2 Skill can fetch sample records for contacts, companies, deals
- [x] #3 Skill can query/search with filters
- [x] #4 Skill reads auth from hubspot.config.yml — no hardcoded tokens
- [x] #5 Works against test account; switchable to production
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: Built hs-api.sh wrapper in hubspot-testing/scripts/. Uses accessToken from hubspot.config.yml (not PAK directly — PAK doesn't work as bearer token). Commands working: counts, objects, object, properties, schemas, owners, search, associations. Pipelines endpoint returns 403 (needs app-level auth, not user PAK). Created hubspot-explore skill in greenmark-planning. AC #3 (search/filter) not yet tested with complex filters but the command works.

2026-02-25: AC #3 marked done — search API confirmed working with date filters and property filters during exploration.
<!-- SECTION:NOTES:END -->
