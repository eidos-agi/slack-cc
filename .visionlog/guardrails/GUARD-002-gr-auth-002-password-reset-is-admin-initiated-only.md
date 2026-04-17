---
id: "GUARD-002"
type: "guardrail"
title: "GR-AUTH-002 \u2014 Password reset is admin-initiated only"
status: "active"
date: "2026-04-15"
---

# GR-AUTH-002 — Password reset is admin-initiated only

**Scripture. Not a preference. Not a UX ask. A rule.**

## Rule

Cerebro does not offer self-service password recovery. There is no "Forgot password?" link on `/login`. Users who lose access to their password must contact the admin (Daniel) out of band, and the admin is the one who triggers the recovery action.

This applies to every Greenmark service that authenticates via Supabase: `cerebro`, `cerebro-mcp` (consent flow), `cerebro-qa`, future admin tools, anything new.

GitHub OAuth users don't need this at all — they recover their account via GitHub, and GitHub's recovery is out of our hands anyway.

## Why

Self-service password reset is a social engineering vector. The attack shape:

1. Attacker obtains user's email address (trivially — corporate emails are published)
2. Attacker clicks "Forgot password?" on the login page
3. Supabase emails a reset link to the user's inbox
4. If the attacker has any access to the inbox (phishing, credential stuffing on the email provider, corporate compromise, a forwarded rule), they reset the password
5. The attacker now owns the cerebro account

Admin gatekeeping is deliberate friction we accept in exchange for integrity of account recovery. The cost is: a user who forgets their password has to wait for Daniel. The benefit is: an attacker who compromises an inbox can't unilaterally reset a cerebro account without a real human-to-human interaction first.

This trade-off matters because our users are executives with live financial data access. The friction cost is low (few users, rare events). The integrity benefit is high (real confidentiality).

## Enforcement — today

- **No `Forgot password?` link in `/login/page.tsx`** — verified 2026-04-15 via grep, zero matches for `forgot|recover|reset` in the login page source
- **`/update-password` requires a valid recovery session** — the page calls `supabase.auth.updateUser({ password })` which fails without an authenticated session. Random navigation to `/update-password` without admin initiation does nothing.
- **`/auth/callback` handles recovery tokens as admin-initiated only** — the route file literally has the comment: "Password recovery links are admin-initiated only (via /api/admin/password-reset). We allow the recovery callback so admin-generated reset links work."
- **No public recovery API** — the route `/api/admin/password-reset` (exists in repo) is an admin-gated endpoint; there is no `/api/auth/recover` or similar unauthenticated trigger

## Enforcement — what still needs to exist

- **Supabase URL Configuration fix (non-code)** — Supabase currently sends recovery emails with the token in the URL fragment (`#access_token=...`, implicit flow) landing at `/login`, which cerebro's `/login` page does not parse. The PKCE flow `/auth/callback?code=...&type=recovery` is what the code is designed for. Fix in Supabase dashboard: Authentication → URL Configuration → Site URL + Redirect URLs, plus Email Templates → Reset Password template uses `{{ .ConfirmationURL }}`. Filed as an issue for the next admin operation.
- **A visible admin UI in cerebro to trigger resets** — today admin triggers are done via the Supabase dashboard. Long-term, a cerebro-internal admin panel calling `/api/admin/password-reset` would make the "admin-initiated" part of this rule easier to audit and live within our own code.

## When it is safe to break this rule

**Never.** Not for "users are complaining about friction." Not because "Supabase makes it easy." Not for a demo. If a real scenario makes this rule wrong, write a new guardrail that explicitly supersedes it.

Adding a "Forgot password?" link to `/login` is a direct violation. Any PR that does so should be closed with a reference to this guardrail.

## Non-goals

- This does NOT require admin-only *logins*. Users can log in themselves. The rule is about *password reset*, not *login*.
- This does NOT prohibit Supabase-side recovery emails entirely. The admin CAN trigger recovery emails from the Supabase dashboard — they just do it as an admin action, not in response to a user-facing button.
- This does NOT apply to service credentials, API keys, or machine auth. Those are managed out-of-band.

## References

- `cerebro/app/login/page.tsx` — verified: no forgot-password UI
- `cerebro/app/update-password/page.tsx` — the password-change page (admin-flow destination)
- `cerebro/app/auth/callback/route.ts` — recovery token exchange, PKCE
- `cerebro/app/api/admin/password-reset/route.ts` — admin-gated endpoint
- GR-AUTH-001 (sibling) — TOTP requirement
- `decisions/ADR-0001-auth-policy.md` in cerebro repo (to be written) — engineering rationale
