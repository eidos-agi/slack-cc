---
id: '0005'
title: Docker cache trap requires deploy workflow changes
status: open
evidence: PROVEN
sources: 1
created: '2026-04-20'
---

## Claim

Railway's Docker builder caches the COPY layer aggressively. Setting env vars triggers a redeploy from cached layers, not from fresh source. The deploy.yml workflow needs workflow_dispatch trigger (added in session 34) and should pass --no-cache or a build arg to force fresh builds. Additionally, a second deploy workflow targeting the develop environment is needed.

## Supporting Evidence

> **Evidence: [PROVEN]** — Session 34 — 5 deploy attempts with cached old code. workflow_dispatch added in PR #46. CACHEBUST ARG added in PR #47., retrieved 2026-04-20

## Caveats

None identified yet.
