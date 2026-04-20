---
id: TASK-0070
title: Add valid-JWT integration test to cerebro-mcp
status: To Do
created: '2026-04-19'
priority: medium
milestone: MS-0011
tags:
  - cerebro-mcp
  - testing
  - auth
definition-of-done:
  - Test creates a valid Supabase JWT (service account)
  - Test calls at least one tool (about) and verifies JSON response
  - Test verifies RLS scoping (user only sees their data)
  - Runs in CI
---
40/40 tests pass but all auth tests are rejection tests. No automated test proves a valid Supabase JWT can call a tool and get real data back. Need a test service account + JWT for CI.
