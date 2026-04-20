---
id: TASK-0072
title: Refresh Railway API token for cerebro-vault
status: To Do
created: '2026-04-19'
priority: high
assignees:
  - Daniel
tags:
  - infra
  - cerebro-vault
  - railway
acceptance-criteria:
  - New Railway API token generated from Railway dashboard
  - RAILWAY_TOKEN env var updated in the sandbox environment
  - cerebro-vault.secret_list() returns 200
  - 'Fleetio credentials vaulted: FLEETIO_API_KEY and FLEETIO_ACCOUNT_TOKEN'
---
The Railway API token used by cerebro-vault has expired. The vault stores secrets as Railway service variables (prefixed SECRET_) via Railway's GraphQL API. The token in $RAILWAY_TOKEN returns "Not Authorized" on even a basic `me` query.

Blocked: cannot vault Fleetio API credentials (or any new secrets) until this is fixed.
