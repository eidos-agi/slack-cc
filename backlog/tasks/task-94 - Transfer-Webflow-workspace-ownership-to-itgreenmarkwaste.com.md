---
id: TASK-94
title: Transfer Webflow workspace ownership to it@greenmarkwaste.com
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
Centralize the Webflow workspace for greenmarkwaste.com (and htdisposal.com if same workspace) under `it@greenmarkwaste.com` with billing to `accounting@greenmarkwaste.com`.

**Context:** Daniel has Webflow editor access (Task-46 complete, credentials in LastPass). Workspace ownership is unknown. This follows the same account ownership pattern as Tasks 78–81 (Railway, Supabase, GitHub transfers), per the policy Alex Kaye approved Feb 27, 2026.

**Steps:**
1. Identify the Webflow workspace owner (check LastPass or ask Michael)
2. Change workspace owner email to `it@greenmarkwaste.com`
3. Update billing to `accounting@greenmarkwaste.com`
4. Audit who else has access (editors, designers, agencies)
5. Document Webflow plan tier and monthly cost
6. Check if htdisposal.com uses the same workspace

**Note:** Webflow stays live until the Astro replacement is deployed and verified. Do not cancel the subscription until cutover is complete.

**Deliverable:** `it@greenmarkwaste.com` owns the Webflow workspace, billing centralized, access list documented, plan/cost documented.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 it@greenmarkwaste.com is the workspace owner on Webflow
- [ ] #2 billing set to accounting@greenmarkwaste.com
- [ ] #3 Full access list documented (all editors, designers, agencies)
- [ ] #4 Webflow plan tier and monthly cost documented
- [ ] #5 htdisposal.com workspace relationship documented
<!-- AC:END -->
