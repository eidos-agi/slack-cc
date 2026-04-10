---
id: TASK-0039
title: Ship to staging via develop → PR → main pipeline
status: To Do
created: '2026-04-10'
priority: high
milestone: 'M-06: Sage Live on Staging Cerebro'
tags:
  - sage
  - cerebro
  - deploy
  - staging
dependencies:
  - 'M-06: Update Financial dashboard page to render real Sage data'
  - 'M-06: Update Executive Summary page with real Sage numbers'
acceptance-criteria:
  - PR opened, CI green
  - PR merged to main
  - Staging deploy succeeds
  - Post-deploy smoke tests green
  - Sage parity check green on staging
  - Daniel can open staging financial page and see real numbers
  - Screenshot captured for stakeholder communication
---
Create PR against cerebro main from the Sage work branch. CI must pass (type check, lint, tests, build). Post-deploy smoke tests must pass (health check, auth gate, and critically: the new sage parity check). Merge. Verify staging deploy succeeds. Open the staging dashboard and confirm Sage data renders. Capture a screenshot.
