---
id: TASK-54
title: 'Scaffold repo, Dockerfile, Railway config'
status: Done
assignee: []
created_date: '2026-02-27 08:21'
updated_date: '2026-02-27 08:29'
labels:
  - infra
  - scaffold
milestone: m-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create cerebro-ai-services/ repo with: git init, .gitignore, requirements.txt, Dockerfile (python:3.12-slim + ffmpeg + models baked in at build), railway.toml (DOCKERFILE builder, /health, 120s timeout). Verify directory structure matches plan.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dockerfile builds successfully
- [ ] #2 railway.toml has correct builder and healthcheck
- [ ] #3 requirements.txt has all dependencies pinned
- [ ] #4 .gitignore covers Python, models, .env
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Scaffolded cerebro-ai-services repo with 35 files: Dockerfile (python:3.12-slim + models baked in), railway.toml, requirements.txt, .gitignore, .env.example. All directories created.
<!-- SECTION:FINAL_SUMMARY:END -->
