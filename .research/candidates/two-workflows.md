---
title: 'Approach A: Two deploy workflows, two DATABASE_URLs, shared migration repo'
verdict: provisional
---

## What It Is

Add a second GitHub Actions workflow (deploy-develop.yml) that triggers on push to develop and deploys to the develop Railway environment. Each environment gets its own DATABASE_URL pointing to its own Supabase. Migrations are applied to both databases via cerebro-migrations with environment-specific Supabase CLI linking. No code changes to data-daemon — environment isolation is purely infrastructure configuration.

Wiring:
- deploy.yml: push to develop → railway up --environment production (existing)
- deploy-develop.yml: push to develop → railway up --environment develop (new)
- develop DATABASE_URL → izmuckuepryqneebwwol
- production DATABASE_URL → wwmcgtyngnziepeynccz
- cerebro-migrations: npm run migrate:staging and npm run migrate:prod scripts
- railguey: already has develop/production accounts

Pros: No code changes. Uses existing tools. Both environments always have latest code.
Cons: Both environments deploy on every push (more Railway build minutes). Migrations must be applied twice.

## Validation Checklist

- [ ] Claim 1: Y — both deploy workflows can target different Railway environments via separate RAILWAY_ENVIRONMENT vars

## Scoring
## Scores

| Criterion | Score |
|-----------|-------|
| C1 | 9/10 |
| C2 | 5/10 |
| C3 | 6/10 |
| C4 | 8/10 |
| C5 | 4/10 |
| **Total** | **32** |

**Notes:** Safe but wasteful. Both environments deploy on every push. Doesn't match cerebro's branch model. Double build minutes.
