---
id: TASK-1.10
title: Seed test account with sample CRM data mirroring Greenmark
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 22:17'
updated_date: '2026-02-24 22:40'
labels:
  - hubspot
  - data-integration
dependencies:
  - TASK-1.9
parent_task_id: TASK-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Greenmark Dev test account (245316113) is empty. Seed it with representative CRM data so we can develop and test the data-daemon connector against realistic structures. Create sample records for standard objects: contacts (waste hauling customers), companies (service locations), deals (contracts/proposals), and tickets (service requests). Use realistic field names and relationships that match what a waste management company would have in HubSpot. Can use the REST API or HubSpot import UI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 At least 10 sample contacts with realistic waste industry fields
- [ ] #2 At least 5 companies representing service locations
- [ ] #3 At least 5 deals representing contracts/proposals
- [ ] #4 Associations set up between contacts, companies, and deals
- [ ] #5 Data structure documented for comparison with production later
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Superseded by TASK-1.13 (companies + contacts) and TASK-1.14 (deals). The original task was too broad — split into specific seeding tasks with clearer acceptance criteria.
<!-- SECTION:FINAL_SUMMARY:END -->
