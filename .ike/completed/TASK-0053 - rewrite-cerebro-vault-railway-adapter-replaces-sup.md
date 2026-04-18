---
id: TASK-0053
title: Rewrite cerebro-vault — Railway adapter replaces Supabase Vault backend
status: Done
created: '2026-04-13'
priority: medium
milestone: 'M-08: cerebro-verifier — Learning QA System'
tags:
  - infra
  - ADR-2026-28
  - cerebro-vault
definition-of-done:
  - secret_get reads from Railway env vars via Railway API or railguey CLI
  - secret_set writes to Railway env vars (with service targeting)
  - secret_list returns Railway env vars (filtered to secrets, not infra vars)
  - secret_delete removes a Railway env var
  - Old Supabase Vault code removed
  - cerebro-vault repo updated, not archived — it's still the ceremony layer
  - '.mcp.json updated: no more SUPABASE_URL/VAULT_ACCESSOR_TOKEN env vars'
updated: '2026-04-17'
---
Per ADR-2026-28: keep the ceremony (secret_get/set/list/delete), swap the Supabase Vault RPC backend for a Railway env vars adapter. cerebro-vault becomes a thin wrapper around Railway's native secrets management.

**Completion notes:** Rewrite complete. Railway GraphQL API replaces Supabase Vault RPCs. Same 4 tools, SECRET_* prefix filters secrets from infra vars. Supabase dependency removed. .mcp.json updated. Local-only repo (no GitHub remote). Type checks and builds clean.
