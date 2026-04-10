---
id: TASK-0044
title: Stress-test data-daemon at 1M+ row scale with synthetic load
status: To Do
created: '2026-04-10'
priority: high
milestone: 'M-03: Sage Connector Live'
tags:
  - sage
  - data-daemon
  - scale
  - validation
  - insurance
dependencies:
  - 'M-02: Deploy new sage_bronze migration to staging Supabase'
acceptance-criteria:
  - Synthetic fixture generated with 1M+ rows across 3-4 tables mimicking Sage shapes
  - data-daemon successfully extracts, loads, and refreshes through the full medallion
  on the fixture
  - No memory errors, no timeouts, no job queue deadlocks
  - Row counts reconcile end-to-end (bronze == silver == gold aggregates where applicable)
  - Existing HubSpot pipeline continues to run successfully in parallel (no resource
  contention)
  - Full run completes in <30 minutes (sanity check for real Sage load)
  - Any scaling bottlenecks identified and documented before Sage work begins
  - 'Stress test cleanup: synthetic schema dropped, no orphan data left in staging'
---
Before writing the real Sage connector, validate that data-daemon can actually handle Sage-scale data. Current HubSpot load is ~650 records. Sage is ~2.5M (with GL_ENTRIES at 1.3M alone). That's a 4,000x jump. Unknown whether data-daemon's executor, job queue, row_hash computation, batch upsert, MERGE refresh, or materialized view refresh can survive the volume. Generate a synthetic SQLite fixture with ~1M rows across 3-4 tables mimicking Sage shapes (account codes, departments, locations, large numeric columns). Wire it to the existing SQLiteConnector. Target a non-production Supabase schema (e.g., stress_test_bronze). Run full pipeline: extract → bronze upsert → silver refresh → gold refresh → smoke tests. Watch for: memory blowup in the executor, lock contention on the job queue, timeout on MERGE operations, batch size overflow, watermark tracking drift, HubSpot pipeline broken by resource contention. If it fails, we learn with synthetic data before burning a real Sage extraction and before Alex's credentials get rate-limited by a broken retry loop. If it succeeds, we have confidence that the real Sage load will work at volume. Either outcome is cheap insurance.
