---
id: TASK-57
title: 'API routes: transcribe, extract, classify, summarize'
status: Done
assignee: []
created_date: '2026-02-27 08:22'
updated_date: '2026-02-27 08:29'
labels:
  - backend
  - api
milestone: m-1
dependencies:
  - TASK-3
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build src/routes/ with all 4 endpoints. Transcribe is async (202 + polling). Extract/classify/summarize are sync. All routes log usage to ai.usage_log. Prompt templates in prompts/ directory.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 POST /v1/transcribe returns 202 with job_id and poll_url
- [ ] #2 GET /v1/transcribe/{job_id} returns status and result
- [ ] #3 POST /v1/extract returns structured data from text
- [ ] #4 POST /v1/classify returns label + confidence
- [ ] #5 POST /v1/summarize returns summary text
- [ ] #6 All responses include model, tokens_in, tokens_out, latency_ms
- [ ] #7 All requests logged to ai.usage_log
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Built all 4 API routes: POST /v1/transcribe (async 202 + poll via in-memory job store), POST /v1/extract (sync, schema or template-based), POST /v1/classify (sync, returns label + confidence), POST /v1/summarize (sync, supports concise/detailed/bullet styles). All log usage. Prompt templates in prompts/. 4 auth tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
