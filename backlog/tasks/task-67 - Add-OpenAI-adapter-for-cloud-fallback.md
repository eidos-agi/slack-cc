---
id: TASK-67
title: Add OpenAI adapter for cloud fallback
status: To Do
assignee: []
created_date: '2026-02-27 08:35'
labels:
  - backend
  - models
  - adapter
milestone: m-1
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create src/models/openai_adapter.py implementing BaseModelAdapter. Uses OpenAI API as a cloud backend for extract/classify/summarize tasks. Enables fallback when local Phi-3 is overloaded or for higher-quality output. Adapter pattern means zero route changes — just register and configure priority.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 OpenAIAdapter implements BaseModelAdapter
- [ ] #2 Configurable via OPENAI_API_KEY env var
- [ ] #3 Can be registered alongside local Phi-3
- [ ] #4 Routes work without changes
<!-- AC:END -->
