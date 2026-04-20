---
id: '0002'
title: GitHub Actions deploys data-daemon to production only
status: open
evidence: PROVEN
sources: 1
created: '2026-04-20'
---

## Claim

deploy.yml runs `railway up --environment production` on push to develop. RAILWAY_ENVIRONMENT=production is set as a GitHub Actions variable. There is no automated deploy pipeline for the develop Railway environment. Develop runs whatever was last manually pushed via `railway up`.

## Supporting Evidence

> **Evidence: [PROVEN]** — Session 34 — gh api repos/greenmark-waste-solutions/data-daemon/actions/variables shows RAILWAY_ENVIRONMENT: production, retrieved 2026-04-20

## Caveats

None identified yet.
