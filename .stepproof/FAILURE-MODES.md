# Failure Modes — Mined from Session History

17 real incidents extracted from past sessions. Each maps to a runbook gate.

## Critical (production data at risk)

### 1. Develop data-daemon pointed at production DB (session 34)
- **Runbook:** rb-data-daemon-deploy s3 — verify DATABASE_URL matches environment
- **Gate:** Pre-deploy env var check: develop must use staging Supabase, production must use production

### 2. Agent ran raw psql against production despite guardrails (session 34)
- **Runbook:** rb-apply-migration — NEVER raw psql
- **Gate:** Migration authority is cerebro-migrations repo only (ADR-2026-38)

### 3. Railway ON_FAILURE kept zombie container alive (session 34)
- **Runbook:** rb-data-daemon-deploy s3 — post-deploy verify RUNNING container matches DEPLOYED code
- **Gate:** After deploy, check health endpoint returns expected version

## High (deploy/data failures)

### 4. Docker cache: redeployed but ran old code (session 34, 5x)
- **Runbook:** rb-data-daemon-deploy s4 — verify row counts changed after extraction
- **Gate:** Post-extraction row_counts > 0 proves new code is running

### 5. CI template applied wrong language to 3 repos (session 25)
- **Runbook:** rb-merge-t1 s1 — CI must pass, not just exist
- **Gate:** Canary test on one repo before bulk operations

### 6. 7 tables with RLS disabled (session 26)
- **Runbook:** rb-apply-migration s3 — post-migration security check
- **Gate:** Automated RLS audit after any DDL change

### 7. Mock data shipped to production (session 26-28)
- **Runbook:** rb-promote-to-production s3 — PR approval gate
- **Gate:** verify_live_badge before production merge

### 8. Stale RBAC checker blocked valid deploy (session 29)
- **Runbook:** rb-ship-to-staging — if contract checker fails, verify checker is current
- **Gate:** Contract checkers must be tested against current schema

### 9. Silver views stale (10K vs 1.38M rows) (session 29)
- **Runbook:** rb-verify-data s1 — freshness check
- **Gate:** Row count comparison across medallion layers

## Medium (process/ceremony failures)

### 10. Convene asked human instead of running autonomously (session 24)
- Feedback memory: `feedback_convene_self_sufficient.md`

### 11. Migrations not pushed before deploy (session 16)
- **Runbook:** rb-apply-migration s2 — PR merged means pushed

### 12. Staging schema diverged from production (session 34)
- **Runbook:** rb-data-daemon-deploy — schema parity check needed

### 13. UI changes shipped without browser test (session 26)
- **Runbook:** rb-ship-to-staging s6 — smoke_test is mandatory

### 14. Jargon leaked in executive briefs (session 20)
- Not a deploy ceremony — content generation quality issue

### 15. Branch protection set in UI, forgotten (session 30)
- Fixed by settings-yml-audit.yml workflow

### 16. Duplicate security audit functions (session 26)
- Code quality — not ceremony

### 17. Uncommitted work across repos (session 25)
- `/land` and `clean-sweep` skills address this

## Pattern Summary

| Category | Incidents | StepProof Answer |
|----------|-----------|------------------|
| Environment cross-wiring | #1, #3, #12 | Pre-deploy env var verification |
| Ceremony bypass | #2, #5, #10, #13 | Tool allow-lists per step |
| Stale state | #4, #8, #9, #15 | Post-deploy freshness + row count verification |
| Missing stakeholder gates | #7, #14 | Human approval step before production |
| No incident memory | #4, #17 | learnings.md / FAILURE-MODES.md consulted |
