---
id: "GUARD-001"
type: "guardrail"
title: "GR-AUTH-001 \u2014 Email/password users must enroll TOTP"
status: "active"
date: "2026-04-15"
---

# GR-AUTH-001 — Email/password users must enroll TOTP

**Scripture. Not a preference. Not a default. A rule.**

## Rule

Any user authenticating to a Greenmark service with email + password MUST enroll a TOTP factor before accessing any authenticated route. This applies to every Greenmark-owned service that sits behind Supabase auth: `cerebro`, `cerebro-mcp`, `cerebro-qa`, `cerebro-telemetry` (when its query surface is exposed to non-service-token users), and anything new.

GitHub OAuth users are exempt — GitHub enforces its own 2FA upstream, and we trust that guarantee. `provider` values other than `"email"` skip this gate.

## Why

Password-only auth is the weakest factor we're willing to accept at all. TOTP is the minimum second factor we trust. Without it, a single credential compromise (reused password, phished, breached from somewhere else) is a full account takeover. TOTP moves that bar from "one credential" to "one credential AND physical control of a device with the seed" — meaningfully stronger at effectively zero UX cost after enrollment.

This matters especially because our authenticated routes serve live Sage financial data and executive P&L. The blast radius of a compromised account is not "annoying" — it's a real confidentiality incident for a real client.

## Enforcement — today

Implemented in `cerebro/middleware.ts`, the "MFA enforcement" block (search for `isEmailUser`). Checks the Supabase session's `app_metadata.provider`. If user is email-auth, calls `supabase.auth.mfa.getAuthenticatorAssuranceLevel()`. Three outcomes:

1. AAL check errors → redirect to `/verify-mfa` (fail closed)
2. User has TOTP factor but current session is AAL1 → redirect to `/verify-mfa`
3. User has no TOTP factor at all → redirect to `/setup-mfa`

Middleware-level enforcement means the rule applies to every route by default; only paths in `MFA_PATHS` (the setup/verify pages themselves) and `PUBLIC_PATHS` are exempt. Verified against real Supabase admin API 2026-04-15 — all existing dshanklin* accounts have 0 factors and all get redirected.

## Enforcement — what still needs to exist

- **MFA `?next=` preservation through redirects** — PR #60 on cerebro (merged to develop 2026-04-15). Without this, OAuth flows for users without TOTP get stranded after enrollment. Until this reaches main, the rule is enforced but the UX is broken for any non-GitHub user's first login. This is a gap in enforcement *quality*, not in the rule.
- **A secure admin-initiated password reset flow** — see GR-AUTH-002. Required so non-GitHub users who forget their password have any path back at all.

## When it is safe to break this rule

**Never.** Not for testing. Not for a visiting contractor. Not for "just this once." A guardrail that admits "just this once" exceptions is not a guardrail. If a real scenario makes this rule wrong, the correct move is to write a new guardrail that explicitly supersedes this one, not to quietly skip the check.

## Non-goals

- This does NOT mandate MFA for GitHub OAuth users. GitHub's own 2FA is the upstream factor, and adding a second TOTP layer on top of GitHub is UX cost with no security win.
- This does NOT mandate hardware keys (WebAuthn/passkeys). TOTP is the floor. Moving to passkeys as an upgrade is welcome but separate.
- This does NOT require MFA on service-to-service auth (the service role key used by cerebro's backend, the telemetry ingest token). Those are machine identities, not users.

## References

- `cerebro/middleware.ts` — enforcement code
- `cerebro/app/setup-mfa/page.tsx` — enrollment UI
- `cerebro/app/verify-mfa/page.tsx` — challenge UI
- `decisions/ADR-0001-auth-policy.md` in cerebro repo (to be written) — engineering rationale, trade-offs, edge cases
- GR-AUTH-002 (sibling) — admin-only password reset
