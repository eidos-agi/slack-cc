---
title: 'Approach B: Staging branch pattern — develop branch deploys to develop env,
  main deploys to production'
verdict: provisional
---

## What It Is

Change the deploy mapping: push to develop → deploy to develop Railway environment. Push to main → deploy to production Railway environment. This matches the conventional staging/production branch model and aligns with cerebro's existing pattern.

Wiring:
- deploy.yml: push to develop → railway up --environment develop
- deploy-prod.yml: push to main → railway up --environment production
- Ship ceremony: merge feature → develop (stages). Verify on staging. Promote develop → main (ships to production, Rhea gate).
- develop DATABASE_URL → izmuckuepryqneebwwol
- production DATABASE_URL → wwmcgtyngnziepeynccz

Pros: Matches cerebro-web-builder's ship_to_staging/promote_to_production pattern. Code is verified on staging before production. Conventional, easy to reason about.
Cons: Requires changing existing deploy.yml and GitHub Actions variables. Main branch needs protection rules (already has them per tier system).

## Validation Checklist

- [ ] Claim 1: Y — cerebro already uses this pattern (develop=staging, main=production). data-daemon is T1 with branch protection on main.

## Scoring
## Scores

| Criterion | Score |
|-----------|-------|
| C1 | 10/10 |
| C2 | 10/10 |
| C3 | 7/10 |
| C4 | 9/10 |
| C5 | 7/10 |
| **Total** | **43** |

**Notes:** Mirrors cerebro exactly. develop→staging, main→production. Rhea recommended. Requires changing deploy.yml and adding deploy-prod.yml. Precondition: prove dev Supabase extraction works.
