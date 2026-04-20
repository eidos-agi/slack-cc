---
title: 'Approach C: Develop env disabled — production only, CI tests against dev database'
verdict: provisional
---

## What It Is

Remove the develop Railway data-daemon service entirely. Only production runs. The dev Supabase is used exclusively by CI (migration tests, integration tests). Staging verification happens via the warp-speed Excel pipeline (SQLite) before shipping to production.

Wiring:
- deploy.yml: push to develop → railway up --environment production (unchanged)
- No develop data-daemon service on Railway
- CI tests run against izmuckuepryqneebwwol
- Production runs against wwmcgtyngnziepeynccz
- Warp-speed Excel serves as the staging validation layer

Pros: Simplest. No second deploy pipeline. No migration coordination. One environment to manage.
Cons: No staging data-daemon to test against. Connector bugs hit production directly. Testing limited to unit tests + warp-speed Excel.

## Validation Checklist

- [ ] Claim 1: Y — works today but provides no staging safety net for data pipeline changes

## Scoring
## Scores

| Criterion | Score |
|-----------|-------|
| C1 | 6/10 |
| C2 | 3/10 |
| C3 | 10/10 |
| C4 | 2/10 |
| C5 | 10/10 |
| **Total** | **31** |

**Notes:** Simplest but no staging safety net. Connector bugs hit production directly. Session 34 proved this is insufficient.
