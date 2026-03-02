# The Case for Account Centralization

## The Problem

Today, Greenmark Waste Solutions does not know who owns the accounts that control its primary web presence:

| Account | Controls | Current Owner | Risk |
|---------|----------|---------------|------|
| GoDaddy | greenmarkwaste.com domain registration | **Unknown** | Domain could be transferred, DNS changed, or allowed to expire by someone outside Greenmark's control |
| Webflow | greenmarkwaste.com hosting + content | **Unknown** | Site could be modified, taken down, or access revoked by someone outside Greenmark's control |

This is a **visibility gap** — not necessarily a problem today, but the kind of thing that becomes a problem at the worst possible moment.

## The Policy

On February 27, 2026, Alex Kaye (CFO) approved an account ownership policy for all vendor accounts:

- **Owner:** `it@greenmarkwaste.com` (shared IT credential)
- **Billing:** `accounting@greenmarkwaste.com`
- **Pattern:** One Greenmark-controlled login per vendor, not tied to any individual

This policy has already been applied to:
- **Railway** (Task-78) — complete
- **Supabase** (Task-79) — complete
- **GitHub** (Task-80) — complete
- **Ownership transfer emails** (Task-81) — complete

GoDaddy and Webflow are the remaining gaps.

## Why This Matters

### 1. Domain Control Is Business-Critical
If the GoDaddy account owner:
- Doesn't renew the domain → greenmarkwaste.com goes offline August 2026
- Changes DNS records → website points somewhere else
- Transfers the domain → Greenmark loses its web address

These aren't far-fetched — the most common cause is simply a lapsed credit card on an account nobody's monitoring. It's not about bad actors; it's about making sure someone at Greenmark has eyes on it.

### 2. Continuity If People Move On
If only one person (a designer, an agency, a former assistant) has admin access to the Webflow workspace:
- If they change jobs or become unavailable, Greenmark may not be able to make urgent changes
- Password recovery may require their personal email
- This isn't about trust — it's about making sure Greenmark always has a way in

Centralizing ownership under `it@greenmarkwaste.com` ensures continuity regardless of personnel changes.

### 3. Audit Trail
When accounts are owned by a shared IT credential:
- Access can be tracked and logged
- Permissions can be granted and revoked
- Billing is centralized and visible to accounting
- Password changes don't require contacting external parties

### 4. Bus-Factor Risk
If one person (Daniel, a designer, Michael's assistant) is the sole admin on an account:
- If they leave, access may be lost
- If they're unavailable in an emergency, no one can intervene
- Password recovery may require their personal email

A shared credential (`it@greenmarkwaste.com`) with passwords in LastPass means any authorized person can access any account.

## What We're Asking For

| Action | From Whom | Effort |
|--------|-----------|--------|
| Identify who owns the GoDaddy account | Michael | 5-minute lookup |
| Initiate GoDaddy transfer to `it@greenmarkwaste.com` | Current owner + Daniel | 15 minutes |
| Identify who owns the Webflow workspace | Michael or Daniel (LastPass) | 5-minute lookup |
| Initiate Webflow transfer to `it@greenmarkwaste.com` | Current owner + Daniel | 15 minutes |

Total effort from Michael: approximately **10 minutes of answering questions**.
Total effort from Daniel: approximately **1 hour of account transfers**.

## Precedent

This is the same process used for Railway, Supabase, and GitHub — all completed without issues. The pattern works:

1. Identify current owner
2. Add `it@greenmarkwaste.com` as admin
3. Transfer ownership
4. Update billing to `accounting@greenmarkwaste.com`
5. Document in cockpit

No vendor has ever objected to this process. It's standard IT hygiene.
