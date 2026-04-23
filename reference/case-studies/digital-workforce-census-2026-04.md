# Digital Workforce Census — April 2026

**Company:** Greenmark Waste Solutions (3 entities: NTX, Hometown, Memphis)
**Human technology staff:** 1 (Daniel Shanklin, Director of AI & Technology)
**Digital employees:** 27
**Estimated labor equivalent:** 333 hours/week (~8.3 FTEs)

## The Thesis

One engineer manages 27 autonomous systems that extract data from vendor APIs, serve executive dashboards, answer questions in Slack, enforce deployment governance, run daily data audits, and manage their own project boards. The digital employees have memories, specialized roles, credentials, and a compliance officer that won't let them ship code without proving they followed the rules.

This is not a demo. This is production infrastructure for a waste management company with real revenue, real trucks, and real customers.

## The Roster

### Always-On Services (Railway, 24/7)

| # | Name | Role | What It Does | Est. hrs/week saved |
|---|------|------|-------------|-------------------|
| 1 | data-daemon | ETL Engineer | Extracts from Sage Intacct on schedule, refreshes gold materialized views, manages job queue | 20 |
| 2 | cerebro | Dashboard Developer | Next.js executive dashboard served to Michael/Alex/Robert 24/7. Live financial data, RBAC, 601 security tests | 40 |
| 3 | cerebro-telemetry | Observability Engineer | Ingests events from every service. 2,443+ events. Node/Hono + SQLite on Railway volume | 10 |
| 4 | cerebro-qa | Data Quality Analyst | Continuous reconciliation, null checks, freshness validation, vendor connectivity monitoring | 15 |
| 5 | cerebro-ai-services | AI/ML Engineer | Self-hosted transcription, extraction, classification, summarization. Logs all usage to audit table | 20 |
| 6 | cerebro-bot-farm | 4 Slack Domain Analysts | Sales, Ops, Executive, Finance channels. Each has own system prompt, tools, and model. Writes heartbeat every 15 min | 40 |
| 7 | cerebro-warp-speed | BI Analyst | Interactive data exploration via WebSocket chat. Claude Agent SDK backend | 15 |
| 8 | cerebro-mcp | Remote Analyst | Cloudflare Worker serving claude.ai. OAuth 2.1, RLS, stakeholders query warehouse data directly | 10 |

### MCP Agents (On-Demand, run during engineering sessions)

| # | Name | Role | What It Does | Est. hrs/week saved |
|---|------|------|-------------|-------------------|
| 9 | cerebro-builder | Project Manager | 19 tools. Session planning, mission tracking, Ariadne knowledge surfacing, Rhea adversarial review | 15 |
| 10 | cerebro-github | Release Engineer | 16 tools. Issues, PRs, CI, merges, changelog, health checks, incident ledger. Rate-governed | 20 |
| 11 | cerebro-web-builder | Deployment Engineer | Ship to staging/production ceremony, smoke tests, deploy status, browser login automation | 10 |
| 12 | cerebro-verifier | QA Analyst | Ground truth SQL comparison, golden fixtures, KPI extraction, evidence screenshots | 15 |
| 13 | cerebro-data-engineer | Data Engineer | Warehouse queries via natural language, freshness checks, parity validation, pipeline diagnostics | 15 |
| 14 | cerebro-docs | Technical Writer | Ecosystem documentation, routing between MCPs, topology maps. Always current | 10 |
| 15 | cerebro-vault | IT Security Admin | Secrets management (get/set/list/delete) across all services via Railway | 5 |
| 16 | StepProof | Compliance Officer | Governance enforcement. No deploy without ceremony proof. Runbooks for every deploy type | 10 |
| 17 | research-md | Research Analyst | Evidence-graded, peer-reviewed, phase-gated decisions. Criteria locking, scoring matrices | 10 |
| 18 | ike-md | Project Coordinator | Task tracking, milestones, definition of done. Named after Eisenhower | 10 |
| 19 | visionlog | Strategy Advisor | Goals, guardrails, ADRs, SOPs. The contracts all execution must honor | 5 |
| 20 | railguey | Infrastructure Engineer | Railway deployment management, service health, rollbacks, volume management | 10 |
| 21 | slack-cc | Executive Assistant | Two-way Slack bridge. Daniel manages the digital workforce from his phone | 5 |

### Scheduled Autonomous (GitHub Actions cron)

| # | Name | Role | Frequency | Est. hrs/week saved |
|---|------|------|-----------|-------------------|
| 22 | ci-health-audit | DevOps Monitor | Daily | Scans all 13 repos for consecutive CI failures, opens issues | 5 |
| 23 | sage-parity | Data Auditor | Daily 6 AM UTC | Validates warehouse against Alex's verified spreadsheet | 5 |
| 24 | schema-drift | DBA | Daily | Detects unauthorized schema changes in Supabase | 3 |
| 25 | ab-selftest | QA Tester | Every 6 hours | Automated browser test against production, emits telemetry | 5 |
| 26 | settings-yml-audit | Compliance Auditor | Every 6 hours | Repo governance drift detection across all repos | 3 |
| 27 | bot-farm-healthcheck | SRE | Every 15 minutes | Liveness check on Slack bots, alerts if stale | 2 |

## By the Numbers

| Metric | Value |
|--------|-------|
| Total digital employees | 27 |
| Human technology staff | 1 |
| Estimated labor hours/week | 333 |
| Full-time equivalent | 8.3 FTEs |
| Always-on services | 8 (Railway, 24/7) |
| On-demand agents | 13 (MCP, session-based) |
| Scheduled autonomous | 6 (GitHub Actions cron) |
| Railway services | 8 |
| GitHub repos managed | 13 |
| Vendor systems integrated | 6 of 15 researched |
| Security tests | 601 across 23 files |
| KPIs in registry | 44 (9 live, 35 pending) |
| Telemetry events collected | 2,443+ |
| Gold view parity | Dec 2025 matches to the penny |

## What Makes Them "Employees"

| Attribute | How it works |
|-----------|-------------|
| **Memories** | visionlog (strategic contracts), research-md (decision history), ike-md (task state), bookmarks (session continuity), cerebro-builder Ariadne (learned knowledge) |
| **Credentials** | GitHub App installation tokens (own rate limit bucket), Supabase OAuth JWTs, Railway deploy tokens, TOTP-authenticated test accounts, vendor API keys |
| **Specialized roles** | Each MCP has a bounded domain. cerebro-github doesn't touch data. cerebro-verifier doesn't deploy. cerebro-data-engineer doesn't manage PRs |
| **Compliance** | StepProof enforces governance. No deploy without runbook ceremony. The compliance officer won't let the release engineer skip steps |
| **Self-monitoring** | bot-farm writes its own heartbeat. ci-health-audit watches all other employees. ab-selftest tests the dashboard every 6 hours |
| **Communication** | slack-cc bridges Slack and Claude Code. cerebro-bot-farm responds in domain-specific channels. Daniel manages from his phone |

## What It Costs

The entire digital workforce runs on:
- Railway (hosting) — shared Greenmark infrastructure budget
- Cloudflare Workers (cerebro-mcp) — free tier
- GitHub Actions (CI/cron) — free for private repos under limits
- Anthropic API (Claude) — usage-based
- Supabase (database) — Pro tier

No Datadog. No PagerDuty. No Jira. No Confluence. The digital employees built their own observability (cerebro-telemetry), their own project management (ike-md), their own documentation (cerebro-docs), and their own compliance (StepProof).

## The Punchline

Dr. Funk expected AI employees to walk into HR and fill out a W-4. What actually happened is 27 Python processes on Railway and Cloudflare, managed by one engineer who talks to them in Slack from his phone, doing 333 hours/week of work that would otherwise require hiring 8 people.

They don't have legs. They have rate limit budgets.
