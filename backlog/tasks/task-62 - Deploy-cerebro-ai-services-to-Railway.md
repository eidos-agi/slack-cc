---
id: TASK-62
title: Deploy cerebro-ai-services to Railway
status: To Do
assignee: []
created_date: '2026-02-27 08:35'
labels:
  - deploy
  - railway
milestone: m-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create new service in Railway greenmark-waste-solutions project. Link to GitHub repo greenmark-waste-solutions/cerebro-ai-services. Railway auto-detects railway.toml + Dockerfile. Set env vars: DATABASE_URL, API_KEYS, MODEL_DIR. First build downloads ~3GB of models. Verify /health returns healthy.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Service created in Railway greenmark-waste-solutions project
- [ ] #2 Linked to GitHub repo for auto-deploy on push
- [ ] #3 Environment variables set (DATABASE_URL, API_KEYS, MODEL_DIR)
- [ ] #4 Dockerfile builds successfully (~3GB models baked in)
- [ ] #5 GET /health returns {status: healthy, models: {whisper: {loaded: true}, phi3: {loaded: true}}}
<!-- AC:END -->
