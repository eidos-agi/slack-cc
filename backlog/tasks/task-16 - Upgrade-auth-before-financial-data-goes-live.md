---
id: TASK-16
title: Upgrade auth before financial data goes live
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:40'
updated_date: '2026-02-27 00:43'
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
The stop-gap auth is one shared password among 8 people. The moment real Sage financial data is on screen, that's a security exposure. One person leaves and the password should rotate but probably won't. Before MVP launch with real data, upgrade to Supabase Auth with individual accounts and TOTP 2FA, or at minimum implement per-user passwords with forced rotation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Individual user accounts replace shared password
- [ ] #2 Password rotation or 2FA enabled
- [ ] #3 Access log showing who logged in and when
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Feb 27: **Second opinion (Gemini 2.5 Pro)** — Strong consensus: Supabase Auth. Already using Supabase for warehouse — zero new infrastructure. Email/password + TOTP 2FA via `@supabase/ssr`. Audit trail: trigger on `auth.sign_in` → `auth_events` table. Jetta SSO rejected (violates 'Greenmark fully separate from AIC'). NextAuth rejected (over-engineered middleman). Roll-your-own rejected ('cardinal sin' with financial data). Phase 1 (1-2 days): login page, middleware, logout. Phase 2 (1 day): TOTP + audit table.
<!-- SECTION:NOTES:END -->
