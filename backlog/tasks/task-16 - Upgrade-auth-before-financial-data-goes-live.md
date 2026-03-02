---
id: TASK-16
title: Upgrade auth before financial data goes live
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:40'
updated_date: '2026-03-02 09:15'
labels:
  - mvp
  - security
  - cerebro
milestone: MVP
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The stop-gap auth is one shared password among 8 people. The moment real Sage financial data is on screen, that's a security exposure. One person leaves and the password should rotate but probably won't.

**Strategy (approved Mar 2 by Daniel):** Supabase Auth with a phased path to Microsoft SSO as the sole login method.

- **Phase 1:** Supabase Auth with email/password + TOTP 2FA. Replaces shared password with individual accounts and audit trail. Minimal lift (~2 days).
- **Phase 2:** Add Microsoft/Azure AD (Entra ID) as an OAuth provider, restricted to the `greenmarkwaste.com` tenant only. Greenmark already has M365 — no new identity provider needed.
- **Phase 3 (lockdown):** Disable email/password login in Supabase. Microsoft SSO becomes the only way into Cerebro. Offboarding from M365 = automatic lockout from Cerebro.

This keeps Greenmark fully separate from AIC (no Jetta SSO), uses infrastructure they already pay for (Microsoft 365), and gives IT (Michael) control over who can access financial data via their existing Microsoft account management.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Individual user accounts replace shared password (Phase 1)
- [ ] #2 TOTP 2FA enabled for all accounts (Phase 1)
- [ ] #3 Access log showing who logged in and when (Phase 1)
- [ ] #4 Microsoft/Azure AD OAuth registered as single-tenant for greenmarkwaste.com (Phase 2)
- [ ] #5 Email/password login disabled — Microsoft SSO is sole auth method (Phase 3)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Feb 27: **Second opinion (Gemini 2.5 Pro)** — Strong consensus: Supabase Auth. Already using Supabase for warehouse — zero new infrastructure. Email/password + TOTP 2FA via `@supabase/ssr`. Audit trail: trigger on `auth.sign_in` → `auth_events` table. Jetta SSO rejected (violates 'Greenmark fully separate from AIC'). NextAuth rejected (over-engineered middleman). Roll-your-own rejected ('cardinal sin' with financial data). Phase 1 (1-2 days): login page, middleware, logout. Phase 2 (1 day): TOTP + audit table.

Mar 2: **Daniel decision** — Approved Supabase Auth BUT only if Microsoft SSO can be bolted on later as the sole auth method. Confirmed: Supabase supports Azure AD as single-tenant OAuth provider (restrict to `greenmarkwaste.com` Entra ID only). Email/password can be disabled once Microsoft OAuth is proven. This means Phase 1 (email/password) is a stepping stone, not the end state. Phase 3 end state = Microsoft SSO only. Ref: [Supabase Azure OAuth docs](https://supabase.com/docs/guides/auth/social-login/auth-azure), [Supabase SAML SSO docs](https://supabase.com/docs/guides/auth/enterprise-sso/auth-sso-saml).
<!-- SECTION:NOTES:END -->
