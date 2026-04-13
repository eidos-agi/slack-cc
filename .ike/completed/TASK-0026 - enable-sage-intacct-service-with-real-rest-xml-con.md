---
id: TASK-0026
title: Enable sage-intacct service with real REST/XML config
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-03: Sage Connector Live'
tags:
  - sage
  - data-daemon
  - service-config
dependencies:
  - 'M-03: Write SageIntacctConnector in data-daemon by hand'
acceptance-criteria:
  - services/sage-intacct.yaml has REST/XML config, no SQLite fixture
  - All 7 tables defined
  - Incremental sync configured for GLENTRY and GLBATCH with watermark column
  - Tests defined (row_count, not_null, freshness)
  - Credentials reference env vars, not hardcoded
updated: '2026-04-13'
---
Update data-daemon/services/sage-intacct.yaml. Remove SQLite fixture source (type: sqlite, path: ${FIXTURE_DIR}/sage_intacct.db). Replace with type: sage_intacct (or type: rest_api if supported) with credentials from env: SAGE_SENDER_ID, SAGE_SENDER_PASSWORD, SAGE_COMPANY_ID, SAGE_USER_ID, SAGE_USER_PASSWORD. Define tables matching bronze schema. Set sync_mode (full for small, incremental for GLENTRY/GLBATCH with watermark). Add smoke tests (row_count, not_null, freshness).

**Completion notes:** SageIntacctConnector registered as sage-intacct in CONNECTOR_REGISTRY. Creds set on Railway.
