---
id: TASK-79
title: Transfer Supabase org ownership to it@greenmarkwaste.com
status: To Do
assignee:
  - Daniel
created_date: '2026-02-28 02:11'
labels:
  - infra
  - ownership
  - greenmark-billing
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The "Greenmark Waste" Supabase org is currently owned by Daniel's account. Transfer ownership to `it@greenmarkwaste.com` so Greenmark owns their own database infrastructure.

Steps:
1. Invite `it@greenmarkwaste.com` to the Greenmark Waste org as Owner
2. Michael accepts and creates a Supabase account with that email (may already exist per memory notes)
3. Transfer org ownership
4. When org upgrades to Pro, set billing email to `accounting@greenmarkwaste.com`
5. Daniel remains as a team member

Current state: Greenmark Waste org (bbyinuakpppggpupiguo) on Free Plan, 2 projects (greenmark-cerebro, greenmark-cerebro-test). Account is it@greenmarkwaste.com per memory notes — verify if ownership is already correct.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 it@greenmarkwaste.com is org owner on Supabase
- [ ] #2 Daniel retains team member access
- [ ] #3 Billing email set to accounting@greenmarkwaste.com when upgraded to paid plan
<!-- AC:END -->
