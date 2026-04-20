---
id: TASK-0060
title: 'Page status registry: slug → status, vendor, progress steps'
status: In Progress
created: '2026-04-19'
priority: medium
milestone: MS-0009
tags:
  - cerebro
  - config
definition-of-done:
  - Registry file exists with all 32 pages
  - Sidebar reads from registry for badge state
  - Adding a new page or changing status = one file edit
updated: '2026-04-19'
---
Central config mapping every page to: status (live/preview/tool), vendor system, blocking reason, and progress steps array [{label, done}]. Sidebar and overlay both read from this. Single file edit to promote a page from preview to live.
