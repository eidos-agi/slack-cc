---
id: TASK-0047
title: Prove auth flow works end-to-end in browser
status: Done
created: '2026-04-13'
priority: high
milestone: 'M-08: cerebro-verifier — Learning QA System'
tags:
  - verifier
  - browser
  - auth
acceptance-criteria:
  - agent-browser logs into staging Cerebro
  - Session persists via --session-name
  - Dashboard page renders after auth (not login redirect)
  - Screenshot of authenticated Financial page captured
updated: '2026-04-17'
---
Use agent-browser to authenticate to staging Cerebro (site password + Supabase login + TOTP if needed). Prove the session persists across commands. This blocks everything else — if auth fails, the verifier can't see any pages.

**Completion notes:** Done — auth flow verified end-to-end in session 30 (2026-04-16). Claude connector → OAuth consent → Supabase login → TOTP → session → tools/list. Working in production.
