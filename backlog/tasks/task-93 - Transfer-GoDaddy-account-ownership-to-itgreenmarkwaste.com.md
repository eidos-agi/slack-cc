---
id: TASK-93
title: Transfer GoDaddy account ownership to it@greenmarkwaste.com
status: To Do
assignee:
  - Daniel
  - Michael
created_date: '2026-03-02 22:22'
labels:
  - account-ownership
  - infrastructure
  - greenmarkwaste.com
dependencies:
  - TASK-92
references:
  - projects/new-website/account-transfer-checklist.md
  - projects/new-website/discovery-questions.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Centralize the GoDaddy registrar account for greenmarkwaste.com under `it@greenmarkwaste.com` with billing to `accounting@greenmarkwaste.com`.

**Context:** greenmarkwaste.com is registered at GoDaddy. Current account owner is unknown. Domain expires Aug 1, 2026. This follows the same account ownership pattern as Tasks 78–81 (Railway, Supabase, GitHub transfers), per the policy Alex Kaye approved Feb 27, 2026.

**Steps:**
1. Michael identifies who owns the GoDaddy account (email on file)
2. Add `it@greenmarkwaste.com` as delegate/admin
3. Transfer full account ownership to `it@greenmarkwaste.com`
4. Update billing to `accounting@greenmarkwaste.com`
5. Verify Daniel can manage DNS records
6. Verify domain auto-renewal is ON (expires Aug 2026)
7. Check if htdisposal.com is on the same account — include in transfer if so

**Deliverable:** Daniel has full admin access to GoDaddy, auto-renewal confirmed, billing centralized.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 it@greenmarkwaste.com is the account owner on GoDaddy
- [ ] #2 billing set to accounting@greenmarkwaste.com
- [ ] #3 Daniel can manage DNS records for greenmarkwaste.com
- [ ] #4 Domain auto-renewal confirmed ON (expires Aug 2026)
- [ ] #5 htdisposal.com ownership documented (same or separate account)
<!-- AC:END -->
