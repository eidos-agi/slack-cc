---
id: TASK-1.17
title: Design data-daemon HubSpot connector based on proven API patterns
status: To Do
assignee:
  - '@Daniel'
created_date: '2026-02-24 22:40'
updated_date: '2026-02-27 00:44'
labels:
  - hubspot
  - data-daemon
  - architecture
dependencies:
  - TASK-1.6
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-25: Added formal dependencies on TASK-1.3 (exploration) and TASK-1.11 (capability map) — both Done, so this task is unblocked.

Feb 26: Now actionable. Daniel has admin access to production HubSpot. Security review in AM, then connector design proceeds with real schema knowledge.

Feb 27: **Second opinion (GPT-5.2)** — Four design decisions resolved: (1) Full vs incremental: incremental after first full load, `lastmodifieddate >= (last_sync - 5 min)` overlap window, weekly full resync as backstop. (2) Properties: store ALL in JSONB in bronze, auto-discover property names from HubSpot metadata endpoint — don't hand-maintain 300 names in YAML. (3) Associations: separate edge table `(from_type, from_id, to_type, to_id, association_type, fetched_at)`, refresh edges only for changed objects. (4) Token: PAK doesn't expire, focus on rate-limit handling (429 + exponential backoff), scope minimization, quarterly rotation. Also handle `archived` flag via periodic reconciliation.
<!-- SECTION:NOTES:END -->
