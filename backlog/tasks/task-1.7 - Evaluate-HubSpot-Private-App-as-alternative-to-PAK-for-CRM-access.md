---
id: TASK-1.7
title: Evaluate HubSpot Private App as alternative to PAK for CRM access
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 21:58'
updated_date: '2026-02-26 08:41'
labels:
  - hubspot
  - architecture
dependencies: []
references:
  - notes/2026-02-24_155759_0399.md
parent_task_id: TASK-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
With admin access to production, Private App is the confirmed approach (proven in sandbox). PAK vs Private App evaluation is moot — Private App gives granular scope control.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Determined whether Daniel can create a Private App with current permissions
- [ ] #2 Documented: Private App scopes available vs PAK scopes available
- [ ] #3 Decision: PAK expansion vs Private App for data-daemon integration
- [ ] #4 If Private App chosen: app created and tested with CRM read access
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: Confirmed pipeline endpoint explicitly rejects user-level tokens. Deal stage names cannot be resolved without pipeline access. Private App is the only path to pipeline data.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Resolved: Private App is the approach. Admin access granted Feb 25, sandbox validation complete. No further evaluation needed.
<!-- SECTION:FINAL_SUMMARY:END -->
