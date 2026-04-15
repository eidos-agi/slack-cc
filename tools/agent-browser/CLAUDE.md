# Agent Browser — Claude runtime instructions

**Read this before using `ab` from an AI agent.**

## The contract (what `ab` guarantees)

Per Daniel, session 29 (2026-04-15): `ab` means a **fully working and continuously tested agent-browser that uses Browserbase in the cloud and shares the URL with the user**. Every component of that contract is now in place:

| Property | How it's delivered |
|---|---|
| Fully working | `agent-browser 0.25.4` native binary + `-p browserbase` → verified end-to-end against real production URLs |
| Uses Browserbase in the cloud | The `ab` bash wrapper auto-injects `-p browserbase` when `BROWSERBASE_API_KEY` is set, so you never have to remember the flag |
| Shares URL with user | After every `ab open`, the wrapper prints `🔴 Live View: https://...` by querying the Browserbase REST API for the latest running session. Also: `ab live` reprints the URL for the current session without navigating |
| Continuously tested | `.github/workflows/ab-selftest.yml` runs `ab open` against `cerebro-telemetry-develop.up.railway.app/healthz` every 6 hours and emits a `source=ab kind=selftest` event to cerebro-telemetry. Regressions open a GitHub issue. |

## TL;DR

- `ab -p browserbase` **works** on this sandbox. Verified 2026-04-15. Earlier claims of silent fallback were wrong — `agent-browser 0.25.4 linux-arm64` creates real Browserbase sessions when `BROWSERBASE_API_KEY` + `BROWSERBASE_PROJECT_ID` are set in env.
- Our `ab` wrapper auto-injects `-p browserbase` when `BROWSERBASE_API_KEY` is present, so you can just type `ab open <url>`.
- Per-invocation mode: each `ab open <url>` creates a session, runs the command, releases. Each invocation is isolated.
- Persistent / interactive mode: create a keepAlive session via REST (see below), attach via `ab connect <connectUrl>`, run many commands against the same session. Default Browserbase session timeout is 300s — always set `"keepAlive": true, "timeout": 3600` for human-in-the-loop flows.

## Wrapper behavior (what our `ab` script does on top of upstream)

1. **Auto-provider:** if `BROWSERBASE_API_KEY` is in env and you did not pass `-p <provider>`, `ab` injects `-p browserbase` automatically.
2. **Live View URL on `open`:** after a successful `open`, the wrapper queries Browserbase's REST API for the newest running session and prints the fullscreen debugger URL so a human can watch.
3. **`ab live`:** standalone convenience command — prints the Live View URL for the current session without navigating. Useful after a prior `open` when you want to re-surface the link.
4. **Logging:** every invocation appends to `logs/YYYY-MM-DD.log`.
5. **Failure tolerance:** Live View lookup is best-effort; if Browserbase's API is slow or down, the core command still succeeds and exits cleanly.

## Per-invocation mode (the simple path)

For one-off scripted actions — smoke tests, CI health checks, nightly verification:

```bash
export BROWSERBASE_API_KEY="bb_live_ykBt2_UNkOT0yZoSYSSdx9eR4k8"
export BROWSERBASE_PROJECT_ID="2080dfe2-9805-4fc7-be2f-512dc5762e90"
./ab -p browserbase open https://cerebro-telemetry-develop.up.railway.app/healthz
./ab -p browserbase screenshot /tmp/out.png
```

Each `ab` invocation spins up a fresh session, runs the command, releases. Clean for CI. Not useful for human-in-the-loop flows.

## Persistent + Live View mode (for human-in-the-loop + multi-step flows)

Create a long-lived session via REST so you can share the Live View URL with a human and run multiple `ab` commands against it.

```bash
# 1. Create a session (returns a connectUrl)
curl -s -X POST "https://api.browserbase.com/v1/sessions" \
  -H "X-BB-API-Key: $BROWSERBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "2080dfe2-9805-4fc7-be2f-512dc5762e90",
    "keepAlive": true,
    "timeout": 3600,
    "browserSettings": {
      "context": {"id": "<context-id>", "persist": true}
    }
  }'
# IMPORTANT: default timeout is 300s (5 min) — nowhere near enough for a human
# to log in + complete MFA. Always pass "timeout": 3600 (1 hr) for interactive
# sessions. keepAlive:true only survives CDP disconnects; it does NOT extend
# the wall-clock timeout. Proven 2026-04-14 when session expired mid-login.

# 2. Parse the connectUrl from the JSON response
# 3. Attach via Playwright CDP
#    const browser = await playwright.chromium.connectOverCDP(connectUrl);

# 4. Drive the session. Context state persists when persist:true.

# 5. Release the session
curl -s -X POST "https://api.browserbase.com/v1/sessions/<id>" \
  -H "X-BB-API-Key: $BROWSERBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "REQUEST_RELEASE", "projectId": "..."}'
```

## Credentials

| What | Where |
|------|-------|
| `BROWSERBASE_API_KEY` | `bb_live_ykBt2_UNkOT0yZoSYSSdx9eR4k8` (Daniel's — also in Railway secrets for cerebro production) |
| Browserbase project ID (Greenmark) | `2080dfe2-9805-4fc7-be2f-512dc5762e90` |

## Persistent auth contexts

Browserbase supports persistent browser contexts so cookies/localStorage/sessionStorage survive across sessions. Create once via manual login, reuse forever.

| Context ID | Purpose | Auth state captured |
|------------|---------|---------------------|
| `870a8efe-dfd9-4ee3-aab8-c1843e9d8d74` | `cerebro` | Signed into `cerebro.greenmark.jettaintelligence.com` production dashboard. Session 28 2026-04-13. |

### Creating a new context

1. Create a fresh Browserbase session via API **with `persist: true`** and no context ID (Browserbase assigns one)
2. Get the Live View URL from the session response — this is a web UI where you can interact with the browser
3. Share the Live View URL with Daniel; he logs in manually (including MFA)
4. The session's `contextId` in the response is now the persisted context — save it here in the table
5. Future sessions use that context ID, pre-authenticated

## Decision tree

| Goal | Best tool |
|------|-----------|
| Verify a public URL returns the right status + body | `curl` — skip browser entirely |
| Query a vendor's log/data system | Check for a Management API first (Supabase has PATs, Railway has tokens, Cloudflare has API tokens). Prefer APIs over scraping. |
| Log into a vendor dashboard requiring creds + MFA | Browserbase session via API + Live View for manual MFA + save context for reuse |
| Scrape data from a post-login page | Browserbase session attached via Playwright CDP, then navigate + extract |
| Anything the `ab` CLI is designed for but needs a real browser | **Don't use `ab -p browserbase` — use Browserbase API directly** per section above |

## Supabase-specific: logs access

Supabase's dashboard Auth Logs are NOT exposed via service role PostgREST (the `auth` schema is hidden by default).

Three real paths to Supabase auth logs:
1. **Supabase Management API** with a Personal Access Token (PAT, `sbp_...`) — programmatic, repeatable. Generate at `https://supabase.com/dashboard/account/tokens`
2. **Manual dashboard screenshot** — fastest one-off
3. **Create a Postgres view** in the `public` schema that selects from `auth.audit_log_entries` — persistent but requires a migration

For OAuth Server events specifically, `/auth/v1/admin/audit` returns empty (endpoint exists but OAuth events don't flow through it in the current Supabase OAuth Server version). Use the dashboard UI or the Management API.

## Failure modes I hit and resolved (2026-04-14)

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ab -p browserbase` returns success but no session appears in Browserbase | Silent fallback to local Chromium. Proven via direct Browserbase API listing showing zero sessions after `ab` claimed success | Use Browserbase REST API directly; don't trust the CLI provider flag |
| `TLS handshake failure (alert 40)` curling `*.workers.dev` | Sandbox TLS fingerprint being flagged by Cloudflare | Eventually passed through on retry; intermittent. For reliable access, use Browserbase |
| `PGRST106 Invalid schema: auth` | PostgREST doesn't expose `auth` schema | Either create a view in `public` or use Supabase Management API |
| `ab close --all` leaves the CLI unable to start new sessions | Daemon file cleanup issue | Restart the shell session; start sessions with fresh `--session-name` |

## What to update here going forward

- When you verify `ab -p browserbase` works (someone fixes the upstream issue), delete the "Known-broken" section
- When you capture a new auth context via Browserbase, add it to the context table with the exact URLs it's authenticated for
- When you hit a new failure mode, document symptom → cause → fix
- When API keys rotate, update them here AND remove old values from anywhere they leaked

## Related

- `learnings.md` — older notes from before this overhaul (keep for history; this file supersedes)
- `node_modules/agent-browser/README.md` — upstream `ab` CLI reference (useful for commands that DO work — snapshot, click, fill, etc.)
