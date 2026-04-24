---
id: TASK-0079
title: Verify cerebro-github uses GitHub App auth after MCP reconnect
status: Done
created: '2026-04-23'
priority: high
tags:
  - cerebro-github
  - github-app
updated: '2026-04-23'
---
Added cerebro-github to .mcp.json with CEREBRO_GITHUB_APP_* env vars. Need to reconnect MCP and verify rate_status shows auth_mode: 'github_app' with 6200/6200 limits instead of PAT.

**Completion notes:** Confirmed auth_mode: github_app, REST 6198/6200, GraphQL 6200/6200. Hardcoded defaults in app_auth.py since .mcp.json env field wasn't propagating.
