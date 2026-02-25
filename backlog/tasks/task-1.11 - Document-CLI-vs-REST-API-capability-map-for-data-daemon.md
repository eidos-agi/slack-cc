---
id: TASK-1.11
title: Document CLI vs REST API capability map for data-daemon
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 22:17'
updated_date: '2026-02-25 07:44'
labels:
  - hubspot
  - data-integration
  - documentation
dependencies: []
references:
  - >-
    https://github.com/greenmark-waste-solutions/infra/blob/main/vendor-status.md
parent_task_id: TASK-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The HubSpot CLI (hs) is CMS/developer-focused and cannot query standard CRM objects. Document exactly what each tool can do so we know when to use CLI vs REST API in the data-daemon connector.\n\nCLI capabilities: custom object schemas, custom object instances, HubDB tables, CMS assets, projects, file manager.\nREST API needed for: contacts, companies, deals, tickets, pipelines, owners, engagements, lists, workflows.\n\nThis informs which extraction approach data-daemon should use for each of the 13 proposed bronze tables.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Matrix showing each HubSpot data type and whether CLI or REST API is needed
- [x] #2 Mapped against the 13 proposed bronze tables from infra vendor research
- [x] #3 Extraction approach recommended for each table
- [x] #4 Documented in data-daemon-testing repo or infra repo
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## CLI vs REST API Capability Map

Documented in EXPLORATION.md under 'API Pattern Verification'.

### HubSpot CLI (@hubspot/cli)
- **Purpose**: CMS/developer tooling only
- **Can do**: Custom objects (via `hs custom-object`), HubDB, CMS assets, serverless functions, projects
- **Cannot do**: Query standard CRM objects (contacts, companies, deals, tickets)
- **Auth**: PAK via `hubspot.config.yml`

### REST API (via hs-api.sh wrapper)
- **Purpose**: Full CRM data access
- **Can do**: List/get/search/batch-read for all CRM objects, properties, schemas, owners, associations
- **Auth**: Bearer token from `accessToken` in config (NOT the PAK directly — PAK is exchanged for short-lived token)
- **Token lifecycle**: ~30 min expiry, auto-refresh via `npx hs auth`

### Conclusion for data-daemon
REST API is the only viable path for CRM data extraction. CLI is irrelevant for data-daemon's needs. The `hs-api.sh` wrapper script proves all extraction patterns needed.
<!-- SECTION:FINAL_SUMMARY:END -->
