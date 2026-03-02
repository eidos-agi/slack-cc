---
id: TASK-56
title: 'Model adapter layer: registry, whisper, phi3'
status: Done
assignee: []
created_date: '2026-02-27 08:22'
updated_date: '2026-02-27 08:29'
labels:
  - backend
  - models
milestone: m-1
dependencies:
  - TASK-2
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build src/models/ with BaseModelAdapter ABC, WhisperAdapter (faster-whisper), Phi3Adapter (llama-cpp-python), and ModelRegistry. Adapter pattern allows future backends (OpenAI, Anthropic, etc.) without changing route code. Models loaded at startup via lifespan.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 BaseModelAdapter ABC defines interface for all adapters
- [ ] #2 WhisperAdapter wraps faster-whisper with transcribe method
- [ ] #3 Phi3Adapter wraps llama-cpp-python with generate method
- [ ] #4 ModelRegistry loads/health-checks all adapters at startup
- [ ] #5 Adding a new backend requires only a new adapter class
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented adapter pattern: BaseModelAdapter ABC in registry.py with name/model_id/tasks/load/health interface. WhisperAdapter wraps faster-whisper. Phi3Adapter wraps llama-cpp-python. ModelRegistry maps task types → adapters, loads at startup. Adding a new backend = one new adapter file + one register call. 5 unit tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
