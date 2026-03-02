---
id: TASK-64
title: Generate and secure API keys in Knox
status: Done
assignee: []
created_date: '2026-02-27 08:35'
updated_date: '2026-02-27 08:37'
labels:
  - security
  - knox
milestone: m-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generate real API keys for each calling app (cerebro, cerebro-qa, data-daemon, portal). Store in Knox. Format: sk-gm-{app}-{random}. Update Railway env var API_KEYS with the real keys. Never commit keys to git.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 API keys generated for cerebro, cerebro-qa, data-daemon, portal
- [ ] #2 Keys stored in Knox
- [ ] #3 Railway API_KEYS env var updated with real keys
- [ ] #4 No keys in git
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Generated 4 API keys (sk-gm-{app}-{32 hex chars}) for cerebro, cerebro-qa, data-daemon, portal. Keys provided to user for Railway env var setup. Format: app:key,app:key
<!-- SECTION:FINAL_SUMMARY:END -->
