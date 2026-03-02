---
id: TASK-61
title: Code review fixes — 9 issues resolved
status: Done
assignee: []
created_date: '2026-02-27 08:33'
labels:
  - security
  - bugfix
milestone: m-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Automated code review found 4 critical + 5 important issues. All fixed:\n\n1. CRITICAL: resp.content outside async-with block in transcribe → captured before client closes\n2. CRITICAL: tmp_path assignment order → assign before write for cleanup on failure\n3. CRITICAL: Dashboard auth logic gap → require auth when any credentials configured\n4. CRITICAL: Path traversal in prompt_template → os.path.basename + realpath validation\n5. IMPORTANT: Blocking CPU inference on event loop → asyncio.to_thread for all generate() calls\n6. IMPORTANT: Duplicate migrations table → removed from SQL, kept in Python bootstrap only\n7. IMPORTANT: Job memory leak → TTL-based pruning on poll\n8. IMPORTANT: No input size limits → max_length on all text fields\n9. IMPORTANT: Timing side-channel in auth → hmac.compare_digest
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
All 9 review findings fixed and committed. 9/9 tests passing after changes.
<!-- SECTION:FINAL_SUMMARY:END -->
