---
id: TASK-0045
title: Security decisions punted — receipt and revisit triggers
status: To Do
created: '2026-04-10'
priority: low
tags:
  - security
  - hardening
  - backlog
  - punted-decisions
  - post-m10
updated: '2026-04-10'
---
This task is the receipt for every security decision consciously deferred during Session 22 (the Sage rebuild, April 2026). Each item records the decision, the rationale, and the specific trigger that should re-open it. Nothing here was forgotten — all were considered and kicked with cause.

**Framing:** Cerebro is an analytics tool, not a transactional system of record. The authoritative data lives upstream (Sage Intacct, HubSpot, Navusoft). The worst plausible failure is "dashboard down for hours while we re-ingest from source," not "irrecoverable data loss." The defense stack matches that threat model.

## Decisions punted

### 1. Auto-deploy CI credentials pattern
**Decision:** Ship Option 1 — pooler DB URL per environment, using the existing `SUPABASE_STAGING_DB_PASSWORD` and `SUPABASE_DB_PASSWORD` secrets. No Supabase account-level access token. No scoped migration role. Each workflow only sees its own environment's password.
**Rationale:** Two physically separate Supabase projects + per-environment DB passwords matches existing `rbac_contract.py` / `smoke.py` pattern. Consistent with current security posture. No new risk introduced.
**Revisit trigger:** Compliance requirement (SOC2, HIPAA, PCI). Second engineer with CI write access. Any CI secret leak across the ecosystem.

### 2. Password rotation cadence
**Decision:** No scheduled rotation. No calendar reminder.
**Rationale:** Rotation alone doesn't protect against the actual threat (AI agent destructive SQL). Marginal real benefit. Adds operational toil for a solo operator.
**Revisit trigger:** 12 months elapsed since last rotation. Any suspected credential leak. Any near-miss incident.

### 3. Scoped migration role (svc_migration_runner)
**Decision:** Not created. Migrations continue running as the Supabase `postgres` role.
**Rationale:** Existing migrations already perform CREATE ROLE, ALTER DEFAULT PRIVILEGES, and other near-superuser operations. A scoped role would need almost all the same privileges, so blast-radius reduction is marginal. Implementation cost is 30-60 min plus risk of hitting permission gaps in future migrations.
**Revisit trigger:** Multi-engineer CI write access. Compliance audit. First time a scoped role would have meaningfully stopped an incident.

### 4. Destructive-keyword CI guard
**Decision:** Not added to verify-migrations.yml. No grep for DROP/TRUNCATE/DELETE WHERE in migration files.
**Rationale:** Fresh-db CI test already catches the common failure (migration doesn't apply cleanly). The threat is low-stakes for an analytics tool because re-ingestion recovers data. The guard itself would slow down legitimate DROPs during iteration.
**Revisit trigger:** First near-miss where a destructive migration slipped past review. Second engineer writing migrations. Compliance audit.

### 5. Point-in-time recovery (Supabase PITR)
**Decision:** Not enabled. Declined explicitly as "wrong cost/benefit for analytics."
**Rationale:** Upstream vendor systems are the source of truth. Recovery mechanism is "re-ingest from Sage/HubSpot/Navusoft" not "restore from backup." PITR protects against data loss; we don't have a data loss problem, we have a downtime problem, and a few hours of downtime on an analytics dashboard is acceptable.
**Revisit trigger:** Cerebro becomes the system of record for any data (not just a view on vendor data). Data sensitivity increases (PII/PHI/PCI). Alex or Michael explicitly asks for higher durability guarantees.

### 6. Nightly pg_dump of RBAC + platform schemas
**Decision:** Not built. No automated backup of the born-in-Cerebro tables.
**Rationale:** RBAC state is tiny (users, roles, tenant config) and reconstructible from migration seed data + a handful of manual inserts. Current user/tenant volume is low enough that rebuilding takes under an hour.
**Revisit trigger:** RBAC complexity grows. Tenant count exceeds ~20. First time we have to manually rebuild RBAC and it takes more than an hour.

### 7. Re-ingest playbook (documented + tested)
**Decision:** Not yet written or tested. This is the one that probably should come before M10 of the Greenmark Metrics Roadmap, but is not urgent today.
**Rationale:** We're explicitly relying on "re-ingest from upstream" as the recovery mechanism. That mechanism is theoretical until it's been tested on staging once. An untested recovery procedure is a prayer, not a plan.
**Revisit trigger:** M9 (Navusoft integration) complicates the data graph enough that recovery isn't obvious. First time we actually need to re-ingest. Before Cerebro becomes load-bearing for operations.

### 8. OIDC / short-lived credentials for CI
**Decision:** Not implemented. DB-password model in GitHub Actions secrets continues.
**Rationale:** Significant setup cost. Supabase CLI support for OIDC is uncertain. DB-password model sufficient at current scale with two isolated databases.
**Revisit trigger:** SOC2 or similar compliance requirement. Multi-engineer team. Supabase adds first-class OIDC support with clear docs.

### 9. GitHub environment protection with reviewer approval on production
**Decision:** Workflow is configured with `environment: production` so the protection rules can be applied, but the actual reviewer requirement has not been set up in repo settings. Requires manual configuration by Daniel in GitHub web UI.
**Rationale:** Manual setup step; will do it the first time a production deploy is actually needed (not part of the first workflow run).
**Revisit trigger:** First production migration deploy. Should be done BEFORE clicking the manual dispatch button, not after.

### 10. GitHub branch protection API
**Decision:** Not upgraded to GitHub Pro to enable branch protection rules.
**Rationale:** Local pre-push hooks + CI checks cover the main failure modes at current scale. The one specific bug (delete develop via --delete-branch) has been addressed by tools/gh-guard.sh.
**Revisit trigger:** Multi-engineer team. GitHub Pro already purchased for another reason. First time branch protection would have caught an incident the hooks missed.

## NOT punted (still must build before session close)

- **tools/gh-guard.sh** — DONE. Shell wrapper that blocks `gh pr merge --delete-branch` when HEAD is a long-lived branch. Tested against cerebro-migrations PR #3, passed feature branch through correctly.
- **Claude PreToolUse hook** — Not yet built. Same failure mode as the gh wrapper but triggered when I run the command, not Daniel. Belongs in ~/.claude/settings.json.
- **tools/ensure-flow.sh** — Not yet built. Audits all deployable repos in ~/repos/, creates develop branch where missing, installs pre-push hook. Hardcoded allowlist of ~8 repos. This is what would have prevented the original "feature → main (no develop)" mistake.
- **Extend setup-ci.sh** — Not yet built. New repos should start with develop branch + pre-push hook by default.

## When to re-open this task

This task gets reopened when ANY of the triggers above fire, OR when we reach M10 of the Greenmark Metrics Roadmap (the "three-level drill works" finish line). M10 is when Cerebro transitions from "research project" to "thing Michael and Alex actually use." The security posture that makes sense for a research project is not the same as the one that makes sense for a load-bearing business tool.

Until then: this task stays open as a receipt, so nothing in it gets forgotten, but no work happens on it.
