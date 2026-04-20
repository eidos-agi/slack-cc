---
id: "ADR-004"
type: "decision"
title: "Environment isolation: develop\u2192staging, main\u2192production, separate databases"
status: "accepted"
date: "2026-04-20"
supersedes: "ADR-003"
source_research_id: "39622d8d-5c6d-4b44-8371-cd3f5ba79d05"
---

data-daemon adopts the same deploy model as cerebro:
- Push to develop → deploy to develop Railway environment → dev Supabase (izmuckuepryqneebwwol)
- Push to main → deploy to production Railway environment → prod Supabase (wwmcgtyngnziepeynccz)

Each environment is fully isolated: own database, own job queue, own workers, own migrations.

Implementation plan:
1. Prove one extraction against dev Supabase (precondition from Rhea)
2. Get dev Supabase password, set develop's DATABASE_URL
3. Apply fleetio_bronze migration to dev database
4. Change deploy.yml: develop branch → develop Railway environment
5. Add deploy-prod.yml: main branch → production Railway environment
6. Define concrete smoke test SQL for staging verification
7. Add staleness check to Rhea gate on main promotion

Earned via research.md project "Environment Isolation" — 5 findings (all PROVEN), 3 candidates scored, Rhea debate, Approach B scored 43/50.

Supersedes: ADR-003 (which documented the broken state where develop deployed to production)
