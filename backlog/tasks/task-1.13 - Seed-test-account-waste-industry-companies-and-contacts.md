---
id: TASK-1.13
title: 'Seed test account: waste industry companies and contacts'
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 22:30'
updated_date: '2026-02-26 08:43'
labels:
  - hubspot
  - data-integration
  - testing
dependencies:
  - TASK-1.12
parent_task_id: TASK-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Seed test account with waste industry companies and contacts matching Greenmark's real customer profile.

**Companies to create:**
- Waste hauling customers (commercial, municipal)
- Locations/sites (multi-site customers)
- Vendor/partner companies

**Contacts to create:**
- Site managers, billing contacts, operations staff
- Use realistic names, job titles, lifecycle stages
- Associate contacts to companies

**Blocked by:** TASK-1.12 (need write scopes) OR can be done manually via HubSpot UI.

**Alternative:** Seed via HubSpot UI import (CSV upload) — bypasses scope requirement entirely.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 At least 5 companies across different waste industry customer types
- [ ] #2 At least 10 contacts with realistic names, roles, and emails
- [ ] #3 Contacts associated to companies
- [ ] #4 Lifecycle stages set (lead, customer, opportunity)
- [ ] #5 Data documented in EXPLORATION.md
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: API writes confirmed denied. Two paths: expand PAK scopes, or use UI CSV import.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Superseded: Production HubSpot has real Greenmark data. Sandbox seeding no longer needed.
<!-- SECTION:FINAL_SUMMARY:END -->
