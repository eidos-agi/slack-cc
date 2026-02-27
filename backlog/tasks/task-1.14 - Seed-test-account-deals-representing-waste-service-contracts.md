---
id: TASK-1.14
title: 'Seed test account: deals representing waste service contracts'
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
Create sample deals in the Greenmark Dev test account representing waste management service contracts. Include different deal stages, amounts, and service types typical for a waste hauler:\n\n- New commercial dumpster service (monthly recurring)\n- Construction rolloff rental (project-based)\n- Municipal contract bid (large, long cycle)\n- Residential route expansion\n- Recycling program add-on\n\nAssociate deals to companies and contacts. Set realistic pipeline stages, amounts, and close dates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 At least 5 deals across different service types
- [ ] #2 Deals associated to companies and contacts
- [ ] #3 Multiple pipeline stages represented (new, qualified, proposal, won, lost)
- [ ] #4 Realistic amounts for waste management contracts
- [ ] #5 At least one closed-won and one closed-lost deal
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-25: Added dependency on TASK-1.12 (PAK scope expansion). Can't create deals via API without write scopes. Alternative: seed via HubSpot UI.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Superseded: Production HubSpot has real deal data. Sandbox seeding no longer needed.
<!-- SECTION:FINAL_SUMMARY:END -->
