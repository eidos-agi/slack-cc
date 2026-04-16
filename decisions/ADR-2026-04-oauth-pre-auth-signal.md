# ADR-2026-04 — On pre-auth pages, use URL signal, not server-side resolver

## Status

Accepted — 2026-04-16

## Context

When an external OAuth client (Claude Web, VS Code, a third-party MCP consumer) authorizes against Cerebro via Supabase OAuth Server, the browser is redirected to `cerebro/login?next=/oauth/consent?authorization_id=<id>`. The user signs in, lands on `/oauth/consent`, sees the requesting app's details, and clicks Allow.

The UX complaint (2026-04-16, Daniel): the login page looked identical whether the user came from Claude or landed on it directly. Users in the middle of a Claude-initiated OAuth flow saw a bare "Sign in" page with no acknowledgement of the OAuth context — indistinguishable from a phishing attempt replaying the Cerebro login form.

The obvious fix, modeled on Google / GitHub / Microsoft OAuth flows, is to render a frame on the login page showing who's asking ("Claude wants access to your Cerebro account"). **PR #68 shipped this — but it never actually rendered in production.**

## What went wrong in PR #68

The banner relied on a server-side resolver (`resolveOAuthContext`) that fetched client details from Supabase admin API at `/auth/v1/admin/oauth/authorizations/{id}`. **This endpoint does not exist.**

Supabase only exposes:
- `/auth/v1/oauth/authorizations/{id}` — requires a user session (JWT bearer), no service-role shortcut
- `/auth/v1/admin/oauth/clients` — lists registered clients, no authorization-by-id endpoint

The resolver pattern-matched from the one admin endpoint that did exist (`/admin/oauth/clients`) and assumed a sibling endpoint (`/admin/oauth/authorizations/{id}`) would exist. 236 unit tests mocked `fetch()` with the imagined response shape, so tests passed. A single real `curl` against the assumed endpoint would have returned 404 — that curl was never made.

In production, the resolver always returned `null`, the banner never rendered, and the login page continued to look phishing-adjacent — the exact problem the PR was supposed to fix.

## What we actually needed

The UX goal was *"user sees they're in an OAuth flow, not a normal sign-in."* That goal doesn't require knowing *which specific app* is asking. It only requires knowing *whether an OAuth flow is in progress*.

That signal is already free: the **presence of `?next=/oauth/consent?authorization_id=<valid-shape>` in the login URL**. Supabase OAuth Server is the only thing that constructs that URL. The `extractAuthorizationId` regex (already existed, kept) rejects attacker-crafted malformed ids. Its presence in the `next` param is a 100%-reliable "user is mid-OAuth" marker.

The *specific* requesting-app identity — logo, name, scopes, redirect_host — renders on `/oauth/consent` post-auth via the Supabase SDK's `supabase.auth.oauth.getAuthorizationDetails(id)` call. That path uses the user's session JWT, works correctly, and always has.

## Decision

**For pre-authentication surfaces (any page reachable by an unauthenticated browser), do not attempt to resolve authenticated Supabase state via admin APIs. Use only the signals already present in the URL, query params, headers, or middleware-set state.**

For the OAuth login banner specifically:

- `/login` server component checks `params.next?.includes("/oauth/consent")` — a boolean.
- If true, render a plain text hint: *"You're signing in to authorize an external application. You'll see exactly what it wants and can approve or cancel on the next screen."*
- No specific app name, no logo, no first-party/external distinction on this surface.
- `/oauth/consent` (post-auth) continues to render the specific app identity via the SDK — unchanged from its pre-#68 behavior.

## Broader rules this codifies

1. **Minimum signal before scaffolding.** When building toward a UX aspiration, list what's already present at the render moment (URL, session, headers). Ask: *"is the minimum of that information enough to materially improve the UX?"* If yes, ship that. Build fetch-layer scaffolding only when the minimum is genuinely insufficient.

2. **Mocked tests are not verification of external system shape.** Unit tests that mock `fetch` prove the code handles a specified response shape — they do not prove the endpoint exists, returns that shape, or behaves that way under real authorization. Every integration with an external system needs at minimum one real HTTP call during development to confirm the endpoint's existence and shape. `curl` is fine; it doesn't have to become a permanent integration test.

3. **Pre-auth surfaces don't get to call admin APIs for authenticated state.** The distinction is fundamental: pre-auth code has no way to prove who the user is, so it must not claim to render authenticated state. Service-role keys are not a substitute for a user session — they're a bypass for admin operations, and Supabase deliberately does not expose all authenticated endpoints via admin.

4. **Browser-drive UI changes on real systems before declaring done.** CLAUDE.md in this repo and in `cerebro/` already say this explicitly. The lesson from this incident: the rule is not about thoroughness, it's about catching this exact class of failure — feature-not-working while tests-pass.

## Consequences

**Accepted:**

- `/login` shows a generic "authorizing an external app" frame, not a specific client name. This is a step behind Google/GitHub's UX, but matches the data available pre-auth.
- If the community ever builds (or Supabase exposes) an admin authorizations endpoint, we can revisit and add a specific-client banner — as a fast-follow ADR, not reopening this one.
- First-party vs external distinction moves entirely to the consent page (where the client data is actually available via SDK).

**Positive side effects from the journey:**

The 5 rounds of durable-tests work on PR #68 caught real security bugs that are unrelated to the broken main feature and are retained:

- `lib/security/safe-next-path.ts` — consolidated three copies of the `next` gate; added defenses against URL-encoded backslash, URL-encoded CRLF injection, absolute-URL open-redirect, whitespace-trim edge cases. 56 tests.
- `lib/security/url.ts` — shared `isValidAuthorizationId` + `sanitiseHttpUrl`. 19 tests.
- `app/oauth/consent/actions.ts` — shape-check authorization_id before admin call; scheme-validate Supabase-returned `redirect_url` before `next/navigation redirect()`. 15 tests.
- `app/oauth/consent/page.tsx` — `parseScopes` dedup + 50-scope DoS cap; `redactUrl` safe placeholder for malformed/non-http URLs. 20 tests.
- `lib/rbac/permissions.ts` — `Object.hasOwn` guard on `pathToPage` (previously leaked `Function.prototype.toString`, `Object.prototype`, etc. for prototype-property names). 39 tests.

**Negative:**

- The cognitive / review cost of five rounds of commits built on an unverified foundation was real. If rule #2 had been applied on day one, the castle would have died in 30 seconds and the real security fixes would have landed as their own focused PR.

## Supersedes / Related

- PR #68 (merged, then partially superseded by PR #74)
- PR #74 (the simplification; 2,007 lines deleted, 88 added, verified end-to-end with a real Claude.ai connector flow on 2026-04-16)
- Test tool: `reference/oauth-ux-test-tool.md` — the persistent test DCR client + authorize-URL generator for future smoke checks
