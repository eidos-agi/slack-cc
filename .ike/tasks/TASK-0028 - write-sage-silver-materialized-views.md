---
id: TASK-0028
title: Write sage_silver materialized views
status: To Do
created: '2026-04-10'
priority: high
milestone: 'M-04: Sage Medallion Complete'
tags:
  - sage
  - silver
  - migration
dependencies:
  - 'M-03: Run first data-daemon Sage extraction against staging'
acceptance-criteria:
  - sage_silver schema created
  - Materialized view for each bronze table
  - L-code entity mapping applied (L0100/L0200 → ntx, L0400 → hometown)
  - Date fields parsed from MM/DD/YYYY to DATE type
  - Numeric fields cast with NULLIF guards
  - REFRESH MATERIALIZED VIEW CONCURRENTLY works on all views
  - Row count per silver view matches its bronze source
---
New migration in cerebro-migrations. Create sage_silver schema. For each sage_bronze table, create a materialized view that: (1) NULLIFs empty strings, (2) casts TEXT to proper types (NUMERIC, TIMESTAMPTZ, DATE), (3) parses MM/DD/YYYY dates to DATE, (4) applies the L-code → entity mapping to resolve_entity column, (5) carries _job_id for lineage. Follow the hubspot_silver.deals pattern from 20260309142701_silver_per_vendor.sql.
