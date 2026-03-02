---
id: TASK-59
title: Deploy to Railway + wire up cerebro
status: To Do
assignee: []
created_date: '2026-02-27 08:22'
labels:
  - deploy
  - integration
milestone: m-1
dependencies:
  - TASK-4
  - TASK-5
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create GitHub repo, push, deploy to Railway in greenmark-waste-solutions project. Run migration against Supabase. Update cerebro's transcribe route to call the gateway. Add AI_SERVICES_URL and AI_SERVICES_API_KEY env vars to cerebro.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Railway service deploys successfully
- [ ] #2 GET /health returns healthy with both models loaded
- [ ] #3 cerebro calls gateway for transcription
- [ ] #4 ai.usage_log receives entries from cerebro
- [ ] #5 End-to-end: record video → transcribe → extract → form pre-filled
<!-- AC:END -->
