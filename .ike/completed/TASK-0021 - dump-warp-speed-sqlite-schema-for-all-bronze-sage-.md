---
id: TASK-0021
title: Dump warp-speed SQLite schema for all bronze_sage_intacct_* tables
status: Done
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
updated: '2026-04-10'
---
Connect to cerebro-warp-speed-excel/cerebro.db. Run .schema for each bronze_sage_intacct_* table. Sample 10 rows from each to see actual field types, nesting, date formats, JSON-encoded columns. Write the output to a reference file in the rebuild branch so the bronze DDL can be derived from observation, not hypothesis.

**Completion notes:** Dumped schema and sampled rows from all 7 bronze_sage_intacct_* tables. Key findings: warp-speed uses a minimal JSON-blob bronze (4 cols: _id, _extracted_at, _source_id, _raw_json). Field counts: glaccount 41, glbatch 63, glentry 69, apbill 94, arinvoice 204, vendor 275, customer 226. Row counts: glaccount 252, glbatch 583,902, glentry 1,383,516, apbill 3,056, arinvoice 4, vendor 418, customer 3. Entity resolution fields: MEGAENTITYID (E1001/E1005/E1008) + LOCATION (L0100/L0200/L0400). Date format MM/DD/YYYY. Debit/credit encoded via TRX_AMOUNT + TR_TYPE (1=debit, -1=credit), NOT separate columns. The old sage_bronze migration had it wrong — it guessed separate debit/credit columns that don't exist in Sage.
