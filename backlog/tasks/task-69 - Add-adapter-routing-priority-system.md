---
id: TASK-69
title: Add adapter routing / priority system
status: To Do
assignee: []
created_date: '2026-02-27 08:35'
labels:
  - backend
  - models
  - adapter
milestone: m-1
dependencies:
  - TASK-67
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend ModelRegistry to support multiple adapters per task with priority ordering and fallback. E.g., try local Phi-3 first, fall back to OpenAI if local is overloaded or errors. Config via env var: ADAPTER_PRIORITY=extract:phi3,openai;classify:phi3,openai
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Registry supports multiple adapters per task
- [ ] #2 Priority ordering configurable via env var
- [ ] #3 Automatic fallback on adapter error
- [ ] #4 Usage log records which adapter actually handled the request
<!-- AC:END -->
