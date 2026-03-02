---
id: TASK-66
title: 'End-to-end test: record video → transcribe → extract → form pre-filled'
status: To Do
assignee: []
created_date: '2026-02-27 08:35'
labels:
  - testing
  - integration
milestone: m-1
dependencies:
  - TASK-65
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Full integration test from the Cerebro frontend. Record a feedback video, verify it uploads to Supabase storage, triggers transcription via AI gateway, extracts structured fields, and pre-fills the feedback form. Check ai.usage_log for correct entries.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Video records and uploads from cerebro frontend
- [ ] #2 AI gateway transcribes the audio
- [ ] #3 Extract endpoint returns title/description/category/priority
- [ ] #4 Feedback form pre-fills with extracted data
- [ ] #5 ai.usage_log shows transcribe + extract entries for calling_app=cerebro
<!-- AC:END -->
