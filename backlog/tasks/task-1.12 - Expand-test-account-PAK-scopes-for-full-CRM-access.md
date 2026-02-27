---
id: TASK-1.12
title: Expand test account PAK scopes for full CRM access
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 22:30'
updated_date: '2026-02-26 08:43'
labels:
  - hubspot
  - admin
dependencies: []
references:
  - data-daemon-testing/hubspot-testing/EXPLORATION.md
parent_task_id: TASK-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Expand test account PAK scopes to enable full CRM access. Current PAK has 36 scopes but is missing standard CRM writes and several read scopes.

**Missing scopes needed:**
- `crm.objects.contacts.write` — create/update contacts
- `crm.objects.companies.write` — create/update companies
- `crm.objects.deals.write` — create/update deals
- `tickets` — ticket access (read + write)
- `sales-email-read` — email content (currently redacted)
- `e-commerce` — products, line items, quotes

**How to do it:** Regenerate PAK from HubSpot test account Settings → Integrations → Private Apps / Personal Access Keys. Check the additional scope boxes.

**Note:** Pipeline endpoint (`/crm/v3/pipelines/`) requires Private App auth regardless — PAK scope expansion won't fix that. See TASK-1.7.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PAK regenerated with tickets, e-commerce, sales-email-read, feedback_submissions scopes
- [ ] #2 hs-api.sh counts returns data for tickets, products, line_items, quotes
- [ ] #3 emails endpoint accessible
- [ ] #4 Document which endpoints still need Private App auth
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: Scope audit complete. Current PAK has 35 scopes including crm.objects.contacts/companies/deals.read, crm.objects.custom.read/write, crm.schemas.custom.read/write, hubdb, files, cms.*, sandboxes.*. Missing: contacts.write, tickets, e-commerce (products/line_items/quotes), sales-email-read. Core CRM read works fine. Write for standard objects and tickets/products need scope expansion. This is just a PAK regeneration on the test account — Daniel controls it, no admin needed. Deprioritized since reads work for exploration.

2026-02-24: Scope audit complete. 36 scopes present. CRM reads work but CRM writes all denied. Need to regenerate PAK with write scopes checked to enable seeding via API.

2026-02-25: Promoted to high priority. This is the critical path — unblocks test data seeding (1.13/1.14/1.16) and is a 5-minute PAK regeneration Daniel controls. No dependency on Michael or anyone else. Clarified: production read-only directive does NOT apply to the sandbox.

2026-02-25: Daniel told Michael he wants one more day of testing to prove read-only PAK access works (can read CRM data but not edit). Safer choice for AI. Expansion deferred until read-only proof is complete. Future plan: separate read-write key project for CRM agent improvements.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Superseded: Daniel now has admin access to production HubSpot. Sandbox PAK scope expansion no longer needed — production Private App will have the required scopes.
<!-- SECTION:FINAL_SUMMARY:END -->
