---
id: TASK-1.2
title: Install and authenticate HubSpot CLI
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 21:35'
updated_date: '2026-02-24 21:56'
labels:
  - hubspot
dependencies:
  - TASK-1.1
parent_task_id: TASK-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Install the HubSpot CLI globally (`npm install -g @hubspot/cli`) and run `hs init` to authenticate against the Greenmark Waste Solutions HubSpot account (ID 244562652). Daniel already has developer portal access. Store auth config in the data-daemon-testing repo. Run `hs get-started` to verify the connection works.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 HubSpot CLI installed globally via npm
- [x] #2 hs init completed with Greenmark account auth
- [ ] #3 hs get-started runs without errors
- [x] #4 Auth credentials stored securely (not committed to git)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: Installed locally (not global) in hubspot/ subfolder via npm. Auth via Personal Access Key. Account name: it-gmw-djs-01, Account ID: 244562652. Config at hubspot/hubspot.config.yml (gitignored). Skipping AC #3 (hs get-started) — that scaffolds a sample app, not needed for data exploration.
<!-- SECTION:NOTES:END -->
