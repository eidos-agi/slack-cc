---
id: TASK-0022
title: Delete old sage_bronze migration from cerebro-migrations
status: To Do
created: '2026-04-10'
priority: high
milestone: 'M-02: Sage Bronze Reality-Aligned'
tags:
  - sage
  - bronze
  - cleanup
dependencies:
  - 'M-02: Dump warp-speed SQLite schema for all bronze_sage_intacct_* tables'
acceptance-criteria:
  - Old migration file deleted
  - No references to the old schema in cerebro-migrations
  - Rebuild branch created
---
The March migration at supabase/migrations/20260308000100_sage_bronze.sql is a hand-written hypothesis. Delete it. It will be replaced by a new migration derived from actual observed warp-speed schema. Commit deletion as part of the rebuild branch.
