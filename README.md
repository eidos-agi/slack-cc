# Greenmark Cockpit

AI Cockpit for Greenmark Waste Solutions — projects, decisions, meetings, and session orchestration.

## Active Projects

| Project | Status | Owner | Details |
|---------|--------|-------|---------|
| **Data Integration (Cerebro)** | Researching | Daniel | [checklist](projects/data-integration/checklist.md) / [infra repo](https://github.com/greenmark-waste-solutions/infra) — 6 of 15 vendor APIs researched. Next: HubSpot API data model. |
| **SEO Improvement** | Active | Daniel | [greenmarkwaste.com](projects/seo-improvement/greenmarkwaste.com/seo-plan.md) / [htdisposal.com](projects/seo-improvement/htdisposal.com/seo-plan.md) — **Astro rebuild: mobile 92, desktop 99.** LCP 17.5→2.7s, CLS 0.176→0.001. [changelog](projects/seo-improvement/greenmarkwaste.com/changelog.md) |
| **Dashboard Mockups** | Awaiting feedback | Daniel | [3 HTML prototypes](projects/data-mockups/checklist.md) — executive, operations, financial. Need Michael + Alex review. |
| **Tech Org Setup** | In progress | Daniel + Alex | [checklist](projects/tech-org-setup/checklist.md) — GitHub org done, Sage/HubSpot access pending |
| **Recording Solution** | Phase 1+2 done | Daniel | [checklist](projects/recording-solution/checklist.md) — diarize skill built + tested, glossary created |
| **Auth Upgrade** | Active | Daniel | [plan](projects/auth-upgrade/README.md) / [print-out](projects/auth-upgrade/auth-upgrade-plan.html) — **Phase 1 before Sage goes live.** Shared password → individual accounts + SSO. |
| **Warehouse Strategy** | Scoping | TBD | [checklist](projects/warehouse-strategy/checklist.md) — kickoff recording now available |

## Meetings

| Date | Meeting | Attendees | Artifacts |
|------|---------|-----------|-----------|
| Feb 19 | [Stakeholder Call](meetings/2026-02-19-stakeholder-call/README.md) | Daniel, Michael, Alex, *(Collin briefly)* | 11 decisions, 14 action items, 6 feature ideas |
| Feb 11 | [Project Cerebro Kickoff](meetings/2026-02-11-project-cerebro-kickoff/README.md) | Daniel, Michael, Alex, Lannis, Collin, Luke | 6 decisions, 8 action items, 3 feature ideas |

## Open Tasks

**[12 open tasks](tasks/README.md)** — 4 waiting on Alex, 4 waiting on Michael, 1 waiting on both, 2 blocked, 1 self-unblockable.

| Who | Open | Oldest |
|-----|------|--------|
| Alex Kaye | 4 tasks | Feb 19 |
| Michael Nguyen | 4 tasks | **Feb 11** (9 days) |
| Daniel Shanklin | 3 tasks (2 blocked, 1 self-unblockable) | Feb 19 |
| Michael + Alex | 1 task | **Feb 11** (9 days) |

Full details, history, and comments: **[tasks/](tasks/README.md)**

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
