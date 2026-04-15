---
id: TASK-0047
title: Prove auth flow works end-to-end in browser
status: To Do
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
---
Use agent-browser to authenticate to staging Cerebro (site password + Supabase login + TOTP if needed). Prove the session persists across commands. This blocks everything else — if auth fails, the verifier can't see any pages.
