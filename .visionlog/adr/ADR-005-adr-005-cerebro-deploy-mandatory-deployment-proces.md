---
id: "ADR-005"
type: "decision"
title: "ADR-005: cerebro-deploy \u2014 mandatory deployment process with 32 verification gates"
status: "accepted"
date: "2026-04-20"
---

Every deployment must go through cerebro-deploy. No exceptions. No guessing. No skipping steps.

Usage: `cerebro-deploy <service> <environment>`
Example: `cerebro-deploy data-daemon production`

---

PHASE 1: IDENTITY (who are we, where are we going)

Step 1: LOAD TOPOLOGY
- Read cerebro-docs topology() for this service
- Extract: repo, database, deploy pipeline, credentials, Railway environment
- GATE: service must exist in topology. If not → STOP, "Unknown service. Run cerebro-docs overview()."

Step 2: LOAD INCIDENTS  
- Read cerebro-docs incidents() filtered by service name
- Display any open/recent incidents
- GATE: if any incident has status "ACTIVE" → WARN, ask for confirmation

Step 3: CHECK ENVIRONMENT ARGUMENT
- Map environment to Railway account (production → production, staging → develop)
- GATE: environment must be "staging" or "production". Nothing else.

Step 4: CHECK GIT CLEAN
- `git status --porcelain`
- GATE: must be clean. If dirty → STOP, "Uncommitted changes. Commit or stash first."

Step 5: CHECK GIT BRANCH
- For staging: must be on `develop`
- For production: must be on `main`
- GATE: wrong branch → STOP, "You're on <branch>. Switch to <expected> first."

Step 6: CHECK GIT SYNC
- `git fetch origin`
- `git diff HEAD origin/<branch>`
- GATE: if local is behind → STOP, "Local is behind remote. Pull first."
- GATE: if local is ahead → WARN, "Local has unpushed commits. Push first?"

---

PHASE 2: READINESS (is the code ready to deploy)

Step 7: RUN TESTS
- `pytest -x --tb=short`
- GATE: any failure → STOP, "Tests failed. Fix before deploying."

Step 8: RUN LINT
- `ruff check .`
- GATE: any error → STOP, "Lint errors. Fix before deploying."

Step 9: CHECK CI ON LATEST COMMIT
- `gh api repos/<org>/<repo>/commits/<sha>/check-runs`
- GATE: all checks must be "success". Any failure → STOP, "CI failed on <check>."
- GATE: any pending → STOP, "CI still running. Wait for completion."

Step 10: CHECK REQUIRED CREDENTIALS
- For each credential in topology.services[service].credentials:
  - Check Railway env var exists on the target environment via railguey_variables
- GATE: any missing → STOP, "Missing credential <name> on <environment>. Set it via railguey_variable_set."

Step 11: CHECK DATABASE CONNECTIVITY
- psql to target database (from topology.databases[environment])
- `SELECT 1`
- GATE: connection failure → STOP, "Cannot connect to <database>. Check DATABASE_URL."

Step 12: CHECK SCHEMA EXISTS
- For data-daemon: verify target bronze schema exists (e.g., fleetio_bronze)
- `SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '<schema>'`
- GATE: 0 tables → STOP, "Schema <schema> doesn't exist. Run cerebro-migrations first."

---

PHASE 3: DEPLOY (execute the deployment)

Step 13: RECORD PRE-DEPLOY STATE
- Current deployment ID from railguey_deployments
- Row counts on key tables (for data-daemon)
- Current health endpoint response
- Save to /tmp/cerebro-deploy-<service>-<timestamp>.json

Step 14: TRIGGER DEPLOY
- For GitHub Actions: `gh workflow run <workflow>.yml --repo <repo> --ref <branch>`
- Record the run ID
- GATE: if workflow doesn't exist → STOP, "Workflow <name> not found on <branch>."

Step 15: WAIT FOR GITHUB ACTIONS
- Poll `gh run list --workflow <workflow> --limit 1` every 10 seconds
- GATE: if status=failure → STOP, "Deploy workflow failed. Check: gh run view <id> --log-failed"
- Timeout: 5 minutes → STOP, "Deploy workflow timed out."

Step 16: WAIT FOR RAILWAY DEPLOYMENT SUCCESS
- Poll railguey_service_info every 10 seconds
- GATE: if status=FAILED → STOP, "Railway deployment failed. Check: railguey_deployment_logs"
- Timeout: 5 minutes → STOP, "Railway deployment timed out."

Step 17: WAIT FOR PREVIOUS DEPLOYMENT REMOVED
- Poll railguey_deployments, check second entry status
- GATE: if previous deployment is not REMOVED after 2 minutes → WARN, "Old containers may still be running."

Step 18: VERIFY HEALTH ENDPOINT
- `curl -s https://<domain>/health`
- GATE: non-200 → STOP, "Health check failed. Service is not running."
- GATE: status=unhealthy → STOP, "Service reports unhealthy."

Step 19: VERIFY CONNECTOR REGISTRY (data-daemon only)
- Check deployment logs for "Connector registry:" line
- GATE: expected connector not in registry → STOP, "Connector <name> not in registry. Docker cache may have served old code. Re-trigger deploy with --force."

---

PHASE 4: EXTRACTION VERIFICATION (data-daemon only)

Step 20: CLEAN STALE JOBS
- `UPDATE daemon.jobs SET deleted_at = NOW() WHERE service_name = '<svc>' AND status = 'failed' AND deleted_at IS NULL`
- Report how many cleaned

Step 21: TRIGGER EXTRACTION
- `POST /trigger/<service_name>`
- GATE: non-200 response → STOP, "Trigger endpoint failed."
- Record number of jobs enqueued

Step 22: WAIT FOR ALL JOBS TO COMPLETE
- Poll daemon.jobs every 15 seconds
- Display progress: X completed, Y running, Z pending, W failed
- GATE: any failed → record failure, continue to check remaining
- Timeout: 10 minutes per table → STOP on timeout

Step 23: CHECK FOR FAILURES
- Query daemon.jobs for status=failed
- GATE: any failures → STOP, "N jobs failed. Check error_message."
- Display each failure: table_name, error_message

Step 24: VERIFY ROW COUNTS
- For each table: query COUNT(*) from bronze table
- Compare rows_extracted vs rows_loaded from daemon.run_history
- GATE: if rows_loaded < rows_extracted → STOP, "Table <name>: extracted <N> but loaded <M>. Check upsert conflict / entity / NOT NULL constraints."

Step 25: COMPARE AGAINST EXPECTED
- If warp-speed SQLite exists: compare row counts
- GATE: if production count < 50% of warp-speed count → WARN, "Table <name> has significantly fewer rows than expected."

---

PHASE 5: POST-DEPLOY (record and report)

Step 26: UPDATE TOPOLOGY
- Write deploy result to .railguey/topology.json

Step 27: LOG RESULT
- If any issues occurred: create incident in cerebro-docs
- If clean: log success

Step 28: PRINT SUMMARY
```
cerebro-deploy data-daemon production — SUCCESS
  Duration: 3m 42s
  Deployment: <id>
  Tables loaded: 17/17
  Total rows: 28,412
  Failures: 0
  Pre-deploy rows: 0 → Post-deploy rows: 28,412
```

Step 29: VERIFY AGAINST PRE-DEPLOY STATE
- Compare row counts before/after
- Flag any regressions (tables that had data before but don't now)

Step 30: PARITY CHECK (if golden fixture exists)
- Run cerebro-verifier compare_fixture if a fixture exists for this data
- GATE: if parity fails → WARN, "Parity check failed. Review before considering deploy complete."

Step 31: HEALTH RE-CHECK
- Hit health endpoint one more time
- GATE: degraded or unhealthy → WARN

Step 32: DONE
- Print final status
- Exit 0 on success, exit 1 on any failure

---

FLAGS:
- `--dry-run`: run Phase 1 + 2 only (pre-flight), don't deploy
- `--skip-tests`: skip steps 7-8 (emergency only, logs WARNING)
- `--force`: force rebuild (passes --no-cache to Docker if applicable)
- `--verbose`: show all intermediate output

HOOKS:
- Pre-deploy hook: agent must call cerebro-docs workflow() for this service before cerebro-deploy
- Post-deploy hook: agent must verify the deployment in a browser (cerebro-web-builder) if it's a web service

Earned from: Session 34 — 10+ hours of debugging deployment failures that a rigid process would have caught in step 17 (connector registry), step 24 (row count verification), or step 5 (wrong branch).
