---
id: TASK-1.5
title: 'Resolve HubSpot login: it@ distribution list vs personal accounts'
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 21:36'
updated_date: '2026-02-25 07:44'
labels:
  - hubspot
  - admin
dependencies: []
references:
  - notes/2026-02-24_152936_1271.md
parent_task_id: TASK-1
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Daniel resolved the HubSpot login issue today. `it@greenmarkwaste.com` is a Microsoft 365 Distribution List (owned by Michael Nguyen, members: Michael + Daniel), not a user account. Google/Microsoft SSO won't work with it. Fix was using HubSpot's password-based auth. 2FA set up with authenticator app. Open question: should this distribution list be upgraded to a Shared Mailbox or M365 Group? That requires M365 admin access (Travis Franson or Michael Nguyen).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 HubSpot login working via password auth
- [x] #2 2FA configured with authenticator app
- [x] #3 Documented: it@greenmarkwaste.com is a distribution list, not a user account
<!-- AC:END -->
