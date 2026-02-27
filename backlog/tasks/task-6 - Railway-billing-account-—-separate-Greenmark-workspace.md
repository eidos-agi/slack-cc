---
id: TASK-6
title: Railway billing account — separate Greenmark workspace
status: Done
assignee:
  - '@Alex Kaye'
  - '@Daniel'
created_date: '2026-02-26 08:43'
updated_date: '2026-02-27 01:46'
labels:
  - infra
  - billing
  - railway
dependencies: []
references:
  - 'https://www.loom.com/share/78e0d8acd84d4423811845e20d57b9df'
  - reference/railway-walkthrough.srt
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Decision from Feb 19 call: Greenmark needs their own Railway billing account, separate from AIC. Daniel sent Alex the workspace creation link (https://railway.com/new/workspace) on Feb 20 via Teams. $20/mo pro plan, per-org billing. No confirmation Alex created it. Need to follow up.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Greenmark Railway account created (it@greenmarkwaste.com) — DONE
- [ ] #2 Alex Kaye added to Railway workspace with billing access
- [x] #3 Pro plan ($20/mo) activated with Greenmark payment method
- [x] #4 Daniel added as member with deploy permissions
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Feb 27: **Railway account created.** Greenmark IT (it@greenmarkwaste.com) signed up for Railway on Feb 26, agreed to Fair Use and Privacy policies. Welcome email received. Account exists — next step is upgrading to Pro plan ($20/mo) and either: (a) creating projects directly in this workspace, or (b) transferring existing projects from AIC workspace.

**Transfer research (Feb 27):** Railway supports project transfer between workspaces. Requirements: both workspaces need active Hobby or Pro plan, must be project Admin. Process: Settings → Transfer Project, or add user as member → Transfer Ownership (24hr acceptance window). Gotchas: env vars/secrets transfer not explicitly confirmed in docs, domains may need re-config, GitHub repo connections may need re-auth. Recommendation: do transfer on a call with Alex to verify everything lands. Developer feedback says transfer UX is clunky for non-technical users.

Feb 27: Next action — Daniel invites Alex Kaye to the Greenmark Railway workspace so Alex can add a payment method and upgrade to Pro. Alex owns the billing relationship.

Feb 27: **DONE.** Railway Pro plan active. 2 projects running: greenmark-toolkit (1 service) and greenmark-waste-solutions (3 services). All production, all online.

Feb 27: Loom walkthrough recorded — covers Railway login, 2FA, project management, GitHub connection, Pro plan billing. Next step: invite Alex (accounting) to manage billing. https://www.loom.com/share/78e0d8acd84d4423811845e20d57b9df
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Greenmark Railway workspace is live on Pro plan. Two projects deployed and running:\n- **greenmark-toolkit** — 1/1 service online (production)\n- **greenmark-waste-solutions** — 3/3 services online (production)\n\nGreenmark IT (it@greenmarkwaste.com) created the account Feb 26. Pro plan activated with Greenmark billing. Fully separate from AIC infrastructure as decided on the Feb 19 call. Transfer research documented in implementation notes in case projects need to move between workspaces in the future.
<!-- SECTION:FINAL_SUMMARY:END -->
