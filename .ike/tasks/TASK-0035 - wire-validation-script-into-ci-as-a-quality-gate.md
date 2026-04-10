---
id: TASK-0035
title: Wire validation script into CI as a quality gate
status: To Do
created: '2026-04-10'
priority: medium
milestone: 'M-05: Excel Parity Proven'
tags:
  - sage
  - validation
  - ci
dependencies:
  - 'M-05: Run validation and fix until 100% parity'
acceptance-criteria:
  - GitHub Actions workflow runs parity script on sage-touching PRs
  - Failing parity check blocks merge
  - Script version-controlled with the rest of the repo
  - Script runs against staging, not production
---
Add validation script to cerebro-migrations CI workflow. Runs on every PR touching sage_bronze, sage_silver, or sage_gold. Also runs after every data-daemon deploy. Any mismatch blocks the merge. The validator becomes a permanent quality gate, not a one-off check.
