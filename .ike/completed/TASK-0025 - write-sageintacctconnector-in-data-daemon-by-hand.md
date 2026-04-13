---
id: TASK-0025
title: Write SageIntacctConnector in data-daemon by hand
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-03: Sage Connector Live'
tags:
  - sage
  - connector
  - data-daemon
dependencies:
  - 'M-03: Stress-test data-daemon at 1M+ row scale with synthetic load'
acceptance-criteria:
  - SageIntacctConnector class exists inheriting BaseConnector
  - test_connection() returns True against real Sage API
  - extract() returns ExtractionResult with rows and watermark
  - Pagination works — tested against GLENTRY (1.3M rows)
  - Unit tests pass for connector logic (mocked XML responses)
updated: '2026-04-13'
---
New file: data-daemon/src/connectors/sage_intacct_connector.py. Inherit from BaseConnector. Copy structure from hubspot_connector.py. Copy XML session/pagination logic from warp-speed pipeline/downloaders/sage-intacct.py. Implement test_connection() (get_session), extract(watermark) (readByQuery + readMore pagination), get_row_count(). Handle 100ms rate limit, 6-hour session timeout, retry on 401.

**Completion notes:** Merged in session 22. SageIntacctConnector with 15 tests, PR #17.
