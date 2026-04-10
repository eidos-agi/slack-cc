---
id: TASK-0021
title: Dump warp-speed SQLite schema for all bronze_sage_intacct_* tables
status: To Do
created: '2026-04-10'
priority: high
milestone: 'M-02: Sage Bronze Reality-Aligned'
tags:
  - sage
  - bronze
  - observation
acceptance-criteria:
  - Schema dumped for all 7 bronze_sage_intacct_* tables
  - 10 sample rows captured per table
  - Observations written to a reference doc (not lost after session)
  - Any surprising quirks flagged (date formats, string-encoded numbers, JSON nesting)
---
Connect to cerebro-warp-speed-excel/cerebro.db. Run .schema for each bronze_sage_intacct_* table. Sample 10 rows from each to see actual field types, nesting, date formats, JSON-encoded columns. Write the output to a reference file in the rebuild branch so the bronze DDL can be derived from observation, not hypothesis.
