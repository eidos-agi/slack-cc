---
id: TASK-71
title: Wire data-daemon to AI gateway for ETL enrichment
status: To Do
assignee: []
created_date: '2026-02-27 08:35'
labels:
  - integration
  - data-daemon
milestone: m-1
dependencies:
  - TASK-62
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add AI gateway calls to data-daemon for text classification and summarization during ETL. Use cases: auto-classify HubSpot tickets, summarize long Navusoft notes, extract structured data from unstructured vendor fields. Add AI_SERVICES_URL and AI_SERVICES_API_KEY to data-daemon env.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 data-daemon can call /v1/classify and /v1/extract
- [ ] #2 Usage logged with calling_app=data-daemon
- [ ] #3 AI enrichment runs as part of ETL silver layer
<!-- AC:END -->
