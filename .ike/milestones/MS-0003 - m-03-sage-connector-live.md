---
id: MS-0003
title: 'M-03: Sage Connector Live'
status: closed
created: '2026-04-10'
---
Write SageIntacctConnector in data-daemon by hand, pattern-matching hubspot_connector.py. Copy XML session/pagination logic from warp-speed's proven downloader. Enable sage-intacct in data-daemon/services/sage-intacct.yaml with the real REST/XML config. First real extraction lands in sage_bronze.

**Closed:** SageIntacctConnector merged with 15 tests. Creds set on both Railway environments.
