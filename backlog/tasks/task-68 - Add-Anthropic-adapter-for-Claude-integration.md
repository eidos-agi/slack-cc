---
id: TASK-68
title: Add Anthropic adapter for Claude integration
status: To Do
assignee: []
created_date: '2026-02-27 08:35'
labels:
  - backend
  - models
  - adapter
milestone: m-1
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create src/models/anthropic_adapter.py implementing BaseModelAdapter. Uses Anthropic API for higher-quality extraction/classification/summarization. Adapter pattern — register and go.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AnthropicAdapter implements BaseModelAdapter
- [ ] #2 Configurable via ANTHROPIC_API_KEY env var
- [ ] #3 Routes work without changes
<!-- AC:END -->
