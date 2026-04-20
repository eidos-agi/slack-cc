---
id: "ADR-003"
type: "decision"
title: "data-daemon deploys to production via GitHub Actions, not develop"
status: "accepted"
date: "2026-04-20"
---

RAILWAY_ENVIRONMENT=production in GitHub Actions variables. The deploy.yml workflow runs `railway up --environment production` on every push to develop.

There is NO automated deploy to the develop Railway environment. Develop runs whatever was last manually pushed.

Docker cache trap: setting env vars via railguey triggers a Railway redeploy from cached layers, NOT from source. To deploy fresh code, merge to develop and let GitHub Actions run, or bust the cache by changing a cached layer input (requirements.txt).

Discovered: Session 34, after 3 hours of debugging why the FleetioConnector wasn't running on the deployed service.
