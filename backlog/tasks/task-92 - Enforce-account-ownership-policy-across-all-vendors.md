---
id: TASK-92
title: Enforce account ownership policy across all vendors
status: To Do
assignee:
  - Daniel
created_date: '2026-02-28 05:46'
labels:
  - infra
  - ownership
  - governance
  - greenmark-billing
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Policy:** Every vendor and infrastructure account should be owned by `it@greenmarkwaste.com` with `accounting@greenmarkwaste.com` receiving bills. Daniel gets admin/developer access, never owns the account.

**Why:** Greenmark must own their own infrastructure. If AIC engagement ends, nothing breaks — credentials, billing, and admin access all stay with Greenmark.

## Accounts to verify/transfer

### Infrastructure (TASK-78/79/80 cover these)
- [ ] Railway — transfer from Daniel → it@
- [ ] Supabase — verify it@ already owns
- [ ] GitHub — add Michael as Owner

### Vendor accounts (enforce when credentials are provisioned)
- [ ] Sage Intacct API — Alex (akaye@) owns credentials, OK (finance owner)
- [ ] HubSpot — ensure it@ or Lannis owns the private app token
- [ ] Fleetio — ensure it@ or Robert owns the API key
- [ ] Navusoft — ensure it@ owns when API access granted
- [ ] Paylocity — ensure it@ or Alex owns OAuth app
- [ ] 3rd Eye — TBD (no vendor contact yet)
- [ ] Webflow — ensure it@ owns editor access for both sites

### Exceptions (documented, not violations)
- Sage Intacct: Alex (CFO) owns credentials directly — appropriate for financial system
- Individual vendor logins (Robert for Fleetio, Lannis for HubSpot) are OK when that person is the business owner of the system
- AIC-owned tools (Wrike, internal) stay under AIC

### Rule
When provisioning ANY new vendor credential: owner = it@greenmarkwaste.com unless there's a documented business reason for an exception.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Ownership policy documented in infra repo
- [ ] #2 Every provisioned account follows the policy or has a documented exception
- [ ] #3 accounting@greenmarkwaste.com receives bills on all paid accounts
<!-- AC:END -->
