# Greenmark Cockpit

AI Cockpit for Greenmark Waste Solutions — projects, decisions, meetings, and session orchestration.

**Start here.** This README is the central hub. Everything links back to it.

| You are... | Start with |
|------------|-----------|
| **Michael or Alex** (checking project status) | [Active Projects](#active-projects) · [Open Tasks](#open-tasks) · [Meetings](#meetings) |
| **Daniel** (engineering work) | [Engineering Practices](#engineering-practices) · [Related Repos](#related-repos) · [tools/](tools/README.md) |
| **An AI session** (new context) | [CLAUDE.md](CLAUDE.md) — full rules, glossary, vendor systems, current state |

## Active Projects

| Project | Status | Owner | Details |
|---------|--------|-------|---------|
| **Sage Pipeline (Cerebro)** | M-03 done | Daniel | [infra repo](https://github.com/greenmark-waste-solutions/infra) — sage_bronze live on staging, SageIntacctConnector merged, 6 of 15 vendor APIs researched. Next: sage_silver + sage_gold views (M-04). |
| **SEO / New Website** | Active | Daniel | [greenmarkwaste.com](projects/seo-improvement/greenmarkwaste.com/seo-plan.md) / [new-website](projects/new-website/) — **Astro rebuild: mobile 92, desktop 99.** LCP 17.5→2.7s, CLS 0.176→0.001. |
| **Dashboard Mockups** | Awaiting feedback | Daniel | [3 HTML prototypes](projects/data-mockups/checklist.md) — executive, operations, financial. Need Michael + Alex review. |
| **Tech Org Setup** | In progress | Daniel + Alex | [checklist](projects/tech-org-setup/checklist.md) — GitHub org done, Sage access active, HubSpot deprioritized |
| **Recording Solution** | Phase 1+2 done | Daniel | [checklist](projects/recording-solution/checklist.md) — diarize skill built + tested, glossary created |
| **Auth Upgrade** | Active | Daniel | [plan](projects/auth-upgrade/README.md) — Phase 1 before Sage goes live. Shared password → individual accounts + SSO. |
| **Cerebro ROI** | Active | Daniel | [plan](projects/cerebro-roi/) — 90-day execution plan, progress tracking |
| **Warehouse Strategy** | Scoping | TBD | [checklist](projects/warehouse-strategy/checklist.md) — kickoff recording now available |

## Meetings

| Date | Meeting | Attendees | Artifacts |
|------|---------|-----------|-----------|
| Feb 19 | [Stakeholder Call](meetings/2026-02-19-stakeholder-call/README.md) | Daniel, Michael, Alex, *(Collin briefly)* | 11 decisions, 14 action items, 6 feature ideas |
| Feb 11 | [Project Cerebro Kickoff](meetings/2026-02-11-project-cerebro-kickoff/README.md) | Daniel, Michael, Alex, Lannis, Collin, Luke | 6 decisions, 8 action items, 3 feature ideas |

## Open Tasks

Engineering work is tracked in the [Cerebro Engineering](https://github.com/orgs/greenmark-waste-solutions/projects/1) GitHub Project. Milestones M-01 through M-07 track the Sage pipeline rebuild. See the project board for current status, linked PRs, and sub-issue progress.

## Engineering Practices

All 13 Greenmark repos follow a tiered release system — production apps get full ceremony, internal tools get lighter gates, docs repos get minimal. One command audits everything.

- **[ADR-2026-02: Tiered Release Practices](decisions/ADR-2026-02.md)** — why tiers, what each level gets, what we skipped and when to revisit
- **[tools/README.md](tools/README.md)** — full tool index, common operations, how to add a new repo
- **[ADR-2026-01: Microsoft Security Stack](decisions/ADR-2026-01.md)** — identity, auth, and secrets strategy

Quick reference:
```
./tools/ensure-release.sh          # audit all repos — are we compliant?
./tools/ensure-release.sh --apply  # fix any drift
```

## Reference

- [Greenmark glossary](reference/glossary/README.md) — systems, entities, people, industry terms, financial terms, transcription corrections
- [Why we refine before we ship](reference/skill-development-methodology.md) — how AI meeting processing gets calibrated on real data, and why skipping it breaks trust
- [Stakeholder org chart](reference/stakeholders/greenmark-org.md)

## Weekly Updates

See the [weekly-updates repo](https://github.com/greenmark-waste-solutions/weekly-updates) for engineering progress reports.

## Related Repos

| Repo | Purpose |
|------|---------|
| [data-daemon](https://github.com/greenmark-waste-solutions/data-daemon) | Data extraction pipeline (code) |
| [cerebro](https://github.com/greenmark-waste-solutions/cerebro) | Dashboard app (code) |
| [infra](https://github.com/greenmark-waste-solutions/infra) | Vendor docs, data dictionary, integration specs |
| [cerebro-qa](https://github.com/greenmark-waste-solutions/cerebro-qa) | Data quality monitoring |
| [weekly-updates](https://github.com/greenmark-waste-solutions/weekly-updates) | Automated engineering reports |

## Archive

- [Kickoff Feb 2026](archive/kickoff-2026-02/) — original meeting artifacts, correspondence, and initial research
