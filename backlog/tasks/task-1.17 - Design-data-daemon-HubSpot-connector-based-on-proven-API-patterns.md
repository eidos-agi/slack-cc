---
id: TASK-1.17
title: Design data-daemon HubSpot connector based on proven API patterns
status: To Do
assignee:
  - '@Daniel'
created_date: '2026-02-24 22:40'
labels:
  - hubspot
  - data-daemon
  - architecture
dependencies: []
references:
  - data-daemon-testing/hubspot-testing/EXPLORATION.md
  - 'https://github.com/greenmark-waste-solutions/data-daemon'
  - >-
    https://github.com/greenmark-waste-solutions/infra/blob/main/vendor-status.md
parent_task_id: TASK-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design the data-daemon connector for HubSpot CRM using the API patterns proven during test account exploration (TASK-1.3).

**Proven extraction patterns:**
- List + paginate: `GET /crm/v3/objects/{type}?limit=100&after={cursor}`
- Batch read by ID: `POST /crm/v3/objects/{type}/batch/read` (up to 100/call)
- Search with filters: `POST /crm/v3/objects/{type}/search` (date range for incremental)
- Inline associations: `?associations=calls,meetings,tasks`
- Property discovery: `GET /crm/v3/properties/{type}` (dynamic schema detection)

**Bronze tables to implement (from infra vendor research):**
1. `hubspot_contacts` — 369 properties, batch read + search
2. `hubspot_companies` — 245 properties, batch read + search
3. `hubspot_deals` — 199 properties, batch read + search
4. `hubspot_owners` — simple list endpoint
5. `hubspot_calls` — engagement data, `hs_*` properties
6. `hubspot_meetings` — engagement data, `hs_*` properties
7. `hubspot_tasks` — engagement data, `hs_*` properties
8. `hubspot_associations` — cross-object links

**Auth approach:** Bearer token from `accessToken` in hubspot.config.yml. Token expires ~30min, needs refresh via `npx hs auth` or PAK exchange.

**Key design decisions needed:**
- Full extract vs incremental (search API supports `lastmodifieddate` filter)
- Property handling: fetch all vs curated list
- Association strategy: inline vs separate calls
- Token refresh automation
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 YAML connector config for HubSpot following data-daemon conventions
- [ ] #2 Extraction strategy documented for each bronze table
- [ ] #3 Token refresh mechanism designed
- [ ] #4 Incremental extraction approach using search API date filters
- [ ] #5 Mapped against existing data-daemon connector patterns (Sage, etc.)
<!-- AC:END -->
