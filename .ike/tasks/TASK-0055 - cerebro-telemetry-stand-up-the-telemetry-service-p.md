---
id: TASK-0055
title: cerebro-telemetry — stand up the telemetry service + Python client
status: In Progress
created: '2026-04-15'
priority: high
tags:
  - telemetry
  - infra
  - observability
definition-of-done:
  - Node server builds, type-checks, boots locally
  - 11/11 Python integration tests pass
  - GitHub repo exists, pushed
  - Deployed to Railway via railguey with persistent volume
  - INGEST_TOKEN set via Railway secrets
  - healthz returns 200 from the deployed URL
  - Python client emit() succeeds against deployed URL
  - Registered in cerebro-builder topology + greenmark-cockpit tier-map
updated: '2026-04-17'
---
Build a dedicated telemetry service (Node + Hono + better-sqlite3) that every Greenmark component writes to, with a persistent Railway volume + Litestream backup to R2. Single source of truth for "what happened" across MCP, dashboard, bot, data-daemon. Decouples observability from Supabase so a Supabase outage can still be debugged.

Architecture:
- One Railway service, one volume at /data, single Node process
- In-memory bounded queue (10k events) drained every 500ms in batched transactions
- Hono HTTP server: POST /ingest (shared token), GET /query (Supabase JWT or ingest token), POST /flush (test/ops), GET /healthz
- better-sqlite3 with WAL mode, prepared statements, atomic batch inserts
- Python client with background drain thread, emit()/query() API, 11 integration tests green against the real Node server
- Producers: cerebro-mcp, cerebro Next.js, cerebro-bot, data-daemon

Out of scope for v1: Litestream wiring (configured in yml, needs R2 creds), cerebro-mcp telemetry_query tool, JS/TS client.

Repo: github.com/greenmark-waste-solutions/cerebro-telemetry
Deploy target: Railway, via railguey MCP

**Session 29 landing log (2026-04-15):**

Shipped end-to-end in one pass:

1. **Service live on Railway** — `cerebro-telemetry` in greenmark-waste-solutions develop env at `cerebro-telemetry-develop.up.railway.app`
2. **Persistent volume attached** at `/data`, 50 GB, `READY`. Created via raw Railway GraphQL (`volumeCreate` mutation) — proved project-scoped tokens CAN do volume operations. `DB_PATH` flipped to `/data/telemetry.sqlite`, redeployed, sentinel event UUID `133fd2ac-7c62-4ec0-83cc-12519b3e9c77` survived a `railguey_restart` → persistence proven
3. **Python client 11/11 local + 32/32 live suite green** — named test cases, one-hypothesis-per-test
4. **GH Actions chain**: Deploy → E2E live suite, chained via `workflow_run`, both green against production URL
5. **cerebro-mcp wired to emit**: every tool handler + auth rejection sends structured events to `/ingest` via `ctx.waitUntil`. Proved end-to-end: 3 unauth POSTs → row_count delta = 3 → query by `source=cerebro-mcp kind=auth` returns all 3 events with correct reason + method attrs
6. **Litestream → R2 Dockerfile wiring**: entrypoint.sh gates replication on R2 env vars; activates automatically when `R2_ACCOUNT_ID / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY` are set. Today runs bare-node (same behavior as before the wiring).

**Also shipped as a side effect**:
- `eidos-agi/railguey` PR #3 (closes #2) — volume CRUD tools (`volume_create`, `volumes`, `volume_delete`, `volume_resize`). 186/186 railguey tests green. Closes the last Railway-infra gap in railguey.

**Still outstanding for full production promotion:**
- Create Cloudflare R2 bucket + API token (dashboard), set `R2_*` vars via `railguey_variable_set`, redeploy → Litestream auto-activates
- Register cerebro-telemetry in cerebro-builder topology (get_topology services list)
- Register in greenmark-cockpit tier-map as T2
- Bake for 48h in develop with real traffic (cerebro-mcp is now producing events)
- Then: promote to `production` Railway env with fresh INGEST_TOKEN + volume

**Status update 2026-04-17:**
- Service live on develop: healthz returns 200, 2,346 events ingested
- Settings.yml merged (ADR-2026-03 T2 compliant)
- Registered in builder topology
- Baking with real cerebro-mcp traffic since 2026-04-15

**Remaining for production promotion:**
- [ ] R2 bucket + API token for Litestream (needs Daniel in Cloudflare dashboard)
- [ ] Promote to production Railway env with fresh INGEST_TOKEN + volume
- [ ] Production healthz returns 200


**Session 32 progress (2026-04-18):**

Production environment partially provisioned:
- ✅ INGEST_TOKEN set (fresh token, different from develop)
- ✅ DB_PATH set to /data/telemetry.sqlite
- ✅ SUPABASE_URL set
- ✅ Volume created (50 GB at /data, ID: 1d434a67-c8cc-4b98-8e5c-8f3dae8202f8)
- ❌ Service has no source connected — needs Daniel to link GitHub repo in Railway dashboard
- ❌ No domain assigned yet

**Daniel action needed:** In Railway dashboard → production env → cerebro-telemetry service → Settings → Connect repo → select `greenmark-waste-solutions/cerebro-telemetry`. Once connected, Railway will auto-deploy. Then assign a public domain.

R2/Litestream still deferred — service works without it.
