# Auth Upgrade — Engineering Checklist

References: [TASK-16](../../backlog/tasks/task-16%20-%20Upgrade-auth-before-financial-data-goes-live.md)

## Phase 1: Individual Accounts (Supabase Auth)

**Goal:** Replace shared password with per-user email/password + TOTP 2FA.

### Setup

- [ ] Enable Supabase Auth on greenmark-cerebro project
- [ ] Configure email templates (invite, password reset, magic link)
- [ ] Enable TOTP 2FA in Supabase Auth settings
- [ ] Enable password strength checker (minimum: medium level)
- [ ] Review default Supabase Auth settings (email confirmations on, session duration)
- [ ] Invite all 8 users via `inviteUserByEmail()` — do NOT create accounts with temp passwords

### Cerebro Code Changes

- [ ] Add Supabase Auth client to Next.js app
- [ ] Build login page (email/password form)
- [ ] Build 2FA enrollment flow (QR code + backup codes)
- [ ] Add auth middleware — protect all routes, enforce `aal2` (block users who skip TOTP)
- [ ] Add session management: short-lived access tokens (15–60 min), 30-min idle timeout
- [ ] Ensure `service_role` key is ONLY used server-side (API routes, SSR) — never in client bundle
- [ ] Add logout button to dashboard header

### Access Control

- [ ] Create `user_roles` table (admin, viewer)
- [ ] Enable Row Level Security (RLS) on ALL tables containing financial data
- [ ] Write RLS policies that check user role before allowing SELECT/INSERT/UPDATE
- [ ] Wire role checks to sensitive pages (financial data)
- [ ] Build access log: successful logins, failed attempts, password resets, MFA failures
- [ ] Plan audit log retention — export `auth.logs` periodically if Supabase plan has limited retention

### Rollout

- [ ] Remove shared password from environment
- [ ] Send invite emails to all 8 users (via `inviteUserByEmail()`)
- [ ] Verify all users can log in with 2FA
- [ ] Confirm audit log captures login events + failed attempts

### TASK-16 Acceptance Criteria (Phase 1)

- [ ] #1 Individual user accounts replace shared password
- [ ] #2 TOTP 2FA enabled for all accounts
- [ ] #3 Access log showing who logged in and when

---

## Phase 2: Add Microsoft SSO

**Goal:** Add Azure AD OAuth as login option. Email/password still available as fallback.

### Prerequisites

- [ ] Michael registers Azure AD app in greenmarkwaste.com Entra ID
  - Redirect URI: `https://<cerebro-domain>/api/auth/callback`
  - Permissions: `openid`, `profile`, `email`
- [ ] Client ID + secret stored in Knox (not in code)
- [ ] Supabase Auth configured with Azure AD provider

### Cerebro Code Changes

- [ ] Add "Sign in with Microsoft" button to login page
- [ ] Configure Supabase Azure AD provider with client ID/secret
- [ ] Restrict to `greenmarkwaste.com` tenant (no personal Microsoft accounts)
- [ ] Map Azure AD email to existing Supabase user accounts
- [ ] Test SSO flow end-to-end with a real Microsoft account

### TASK-16 Acceptance Criteria (Phase 2)

- [ ] #4 Microsoft/Azure AD OAuth registered

---

## Phase 3: Microsoft Only

**Goal:** Disable email/password. Microsoft SSO is the only login method.

### Prerequisites

- [ ] All 8 users confirmed working via Microsoft SSO
- [ ] Break-glass admin account created (see below)

### Break-Glass Procedure

- [ ] Create emergency admin account on a **non-greenmarkwaste.com domain** (e.g. `cerebro-breakglass@<other-domain>`)
- [ ] Generate long random password, store offline (physical safe accessible by 2+ trusted people)
- [ ] Enable TOTP on break-glass account, store backup codes offline with password
- [ ] Document procedure: when to use, who has access, how to verify it works
- [ ] Test break-glass login before disabling email/password

> **Why a different domain?** If Azure AD has an outage, all `@greenmarkwaste.com` accounts are locked out — including a break-glass account on that tenant. The emergency account must be independent.

### Changes

- [ ] Disable email/password provider in Supabase Auth (except break-glass account)
- [ ] Remove email/password form from login page
- [ ] Update login page: "Sign in with Microsoft" only
- [ ] Verify offboarding works: disable M365 account = locked out of Cerebro

### TASK-16 Acceptance Criteria (Phase 3)

- [ ] #5 Email/password login disabled

---

## Dependencies

| Dependency | Phase | Owner | Status |
|-----------|-------|-------|--------|
| Sage financial data going live | Phase 1 deadline | Daniel | In progress |
| Azure AD app registration | Phase 2 blocker | Michael | Not started |
| All users on Microsoft SSO | Phase 3 prerequisite | All users | Not started |
