# Auth Upgrade — Cerebro Authentication

**Status:** Active
**Owner:** Daniel Shanklin
**Requested by:** Security review, Mar 2026 — [TASK-16](../../backlog/tasks/task-16%20-%20Upgrade-auth-before-financial-data-goes-live.md)
**Target:** Replace shared password with individual accounts + SSO before financial data goes live

## The Problem

Cerebro currently uses a single shared password across 8 users. With real Sage Intacct financial data going live, this is a security exposure — no audit trail, no way to revoke one person's access, no 2FA.

## Strategy: Three Phases

| Phase | What | Timeline | Effort |
|-------|------|----------|--------|
| **1. Individual Accounts** | Supabase Auth: email/password + TOTP 2FA per user | Before Sage goes live | ~2 days |
| **2. Add Microsoft SSO** | Azure AD OAuth alongside email/password | Within 30 days of Phase 1 | ~1 day |
| **3. Microsoft Only** | Disable email/password, SSO-only | Within 60 days of Phase 1 | ~0.5 day |

## Phase Details

### Phase 1 — Individual Accounts (Supabase Auth)

Each user gets their own email/password login with mandatory TOTP 2FA. Shared password is retired.

- **Who's affected:** All 8 current Cerebro users
- **What changes:** New login page, individual credentials, authenticator app required
- **What we get:** Audit trail (logins + failed attempts), per-user revocation, mandatory 2FA (AAL2 enforced), 30-min idle timeout, row-level security on financial data
- **Key implementation details:** Enforce `aal2` in middleware (not just offer 2FA), use `inviteUserByEmail()` (no temp passwords), enable RLS on all financial tables, `service_role` key server-side only

### Phase 2 — Add Microsoft Login

Greenmark already uses Microsoft 365. Adding "Sign in with Microsoft" as an option lets users authenticate with their existing work accounts.

- **Requires:** Azure AD app registration in the greenmarkwaste.com tenant
- **Who does it:** Michael (Entra ID admin) or Daniel with admin access
- **What users see:** "Sign in with Microsoft" button alongside email/password

### Phase 3 — Microsoft Only

Email/password login disabled. Microsoft SSO becomes the sole authentication method.

- **Why:** Single identity provider = automatic offboarding (disable M365 account = locked out of Cerebro)
- **Tenant restriction:** Only `greenmarkwaste.com` Microsoft accounts can log in
- **Break-glass:** Emergency admin account on a **non-greenmarkwaste.com domain**, stored offline in a physical safe. Independent of Azure AD — survives Microsoft outages.

## What We Need From Stakeholders

| Who | Action | Status |
|-----|--------|--------|
| Michael | Approve Phase 1 rollout plan | Pending |
| Michael | Register Azure AD app (Phase 2) or grant Daniel Entra ID access | Pending |
| Alex | Review security summary in [auth-upgrade-plan.html](auth-upgrade-plan.html) | Pending |

## Deliverables

- [checklist.md](checklist.md) — Engineering checklist with tasks per phase
- [auth-upgrade-plan.html](auth-upgrade-plan.html) — Print-ready plan for Michael + Alex review

## Blockers

- **Phase 1:** None — can proceed immediately after approval
- **Phase 2:** Needs Azure AD app registration (requires Entra ID admin)
- **Phase 3:** Blocked by Phase 2 completion + user adoption confirmation

## Change Log

| Date | Change | Details |
|------|--------|---------|
| Mar 2 | Project created | Three-phase strategy approved by Daniel. TASK-16 updated. |
| Mar 2 | PAL security review | Gemini 2.5 Pro reviewed plan. Added: AAL2 enforcement, password policy, RLS, audit log expansion, idle timeout, break-glass procedure, `service_role` key handling. |
