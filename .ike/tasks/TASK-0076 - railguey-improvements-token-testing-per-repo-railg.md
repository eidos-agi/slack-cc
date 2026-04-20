---
id: TASK-0076
title: 'Railguey improvements: token testing + per-repo .railguey folder'
status: To Do
created: '2026-04-20'
priority: medium
tags:
  - railguey
  - tooling
---
Two features for the railguey MCP (eidos-agi/railguey repo):

1. Token test suite as a railguey tool (railguey_token_test):
   - Test each account's token against: introspection, variable read/write, deploy permission, service listing
   - Output pass/fail per capability
   - Consult this when deploys fail or tokens seem wrong

2. Per-repo .railguey folder:
   - When railguey touches a repo, create .railguey/ with:
     - topology.json: services, environments, domains, deploy pipelines
     - learnings.md: what worked, what broke, token quirks
     - .gitignore'd secrets, but topology and learnings are committed
   - Becomes the repo-level source of truth for Railway configuration
