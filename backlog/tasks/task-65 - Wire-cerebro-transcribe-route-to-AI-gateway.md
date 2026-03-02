---
id: TASK-65
title: Wire cerebro transcribe route to AI gateway
status: To Do
assignee: []
created_date: '2026-02-27 08:35'
labels:
  - integration
  - cerebro
milestone: m-1
dependencies:
  - TASK-62
  - TASK-64
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In the cerebro repo, update app/api/feedback/transcribe/route.ts: replace 501 stub with real gateway calls. Flow: POST /v1/transcribe → poll until complete → POST /v1/extract with extract_feedback template → return pre-filled fields. Add AI_SERVICES_URL and AI_SERVICES_API_KEY env vars to cerebro Railway service. Re-enable recording flow in app/dashboard/feedback/record/page.tsx.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 cerebro transcribe route calls AI gateway instead of returning 501
- [ ] #2 Polling loop waits for transcription completion
- [ ] #3 Extracted fields pre-fill the feedback form
- [ ] #4 Recording flow re-enabled in frontend
- [ ] #5 AI_SERVICES_URL and AI_SERVICES_API_KEY env vars set on cerebro
<!-- AC:END -->
