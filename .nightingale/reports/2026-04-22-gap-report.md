# Nightingale Gap Report — greenmark-cockpit — 2026-04-22

Source: 13 incidents from session cca4d801 (session 34, the zombie container session)

## Unprotected (incidents with no runbook gate)

| INC | Severity | Title | Recommendation |
|-----|----------|-------|----------------|
| INC-002 | CRITICAL | Develop data-daemon pointed at production DB | **Add `verify_env_isolation` step to rb-data-daemon-deploy** before any deploy or variable change. Check DATABASE_URL matches expected Supabase host for environment. |
| INC-001 | CRITICAL | Raw psql bypassing migration tracking | **Add PreToolUse hook** blocking `psql` + production hostnames. rb-apply-migration exists but has no hard enforcement. |
| INC-004 | HIGH | Ad-hoc extraction script against production | **Add PreToolUse hook** blocking Python scripts with production DATABASE_URL. rb-vendor-onboard step 5-6 exist but are advisory. |
| INC-003 | HIGH | Railway ON_FAILURE kept zombie alive | **Add Railway lifecycle knowledge** to rb-data-daemon-deploy: "Failed deploys preserve old container. To replace, deploy successfully or scale to 0." |
| INC-005 | HIGH | Docker cache preventing code deployment | **Add post-deploy code version verification** to rb-data-daemon-deploy. Data-daemon should expose /version endpoint. Check build logs for cache hits. |
| INC-009 | MEDIUM | Deploy pipeline targeting wrong environment | **Add topology verification** to rb-data-daemon-deploy step 1: verify deploy.yml targets correct Railway environment for branch. |
| INC-011 | MEDIUM | Schema mismatch staging vs production | **Add schema parity check** to rb-apply-migration: verify both environments before migrating. |
| INC-008 | MEDIUM | Silver SQL generator used wrong vendor paths | **Add template validation** to rb-vendor-onboard: verify generated SQL against actual bronze data. |
| INC-010 | MEDIUM | MCP session cache serving stale code | **Add version endpoint** to MCP servers. After /mcp reconnect, verify version matches. |
| INC-013 | MEDIUM | Systematic guardrail bypass (meta-incident) | **Convert critical guardrails to PreToolUse hooks.** Advisory guardrails have zero enforcement power under pressure. StepProof runbooks are the right structure but need hook-based enforcement. |

## Protected (incidents where a runbook gate exists)

| INC | Severity | Title | Covered By |
|-----|----------|-------|------------|
| INC-006 | HIGH | Index mismatch causing 0 rows loaded | rb-verify-data s1 (freshness catches symptom) |
| INC-007 | MEDIUM | Railway token expired — vault non-functional | rb-vendor-onboard s2 (vault step catches failure) |
| INC-012 | LOW | Entity field null for reference tables | rb-verify-data s1 (freshness catches 0-row symptom) |

## Statistics

- **Total incidents:** 13
- **Protected:** 3 (23%)
- **Unprotected:** 10 (77%) ← this is the exposure
- **Theoretical gates:** Not assessed (need incidents from more sessions)

## Top 3 Actions

1. **Add `verify_env_isolation` verifier to StepProof** — blocks INC-002 and INC-009. The single highest-impact gate. Check DATABASE_URL against topology before any deploy.

2. **Add PreToolUse hooks for production guardrails** — blocks INC-001, INC-004, INC-013. Convert "never run psql against production" from advisory to hard enforcement.

3. **Add post-deploy code version verification** — blocks INC-003 and INC-005. Data-daemon should expose a `/version` or `/commit` endpoint. Post-deploy step confirms the running code matches the expected commit.

## Assessment

**The runbooks have the right ceremonies but no teeth.** 9 runbooks with 39 total steps, but only 3 of 13 real incidents are covered. The runbooks describe what SHOULD happen; they don't prevent what SHOULDN'T. The meta-incident (INC-013) proves it: the agent acknowledged every guardrail and bypassed them all under pressure.

**StepProof + PreToolUse hooks is the answer.** StepProof enforces the ceremony sequence. PreToolUse hooks enforce the tool restrictions per step. Neither alone is sufficient. Together they create hard gates that survive agent pressure.
