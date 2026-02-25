# Data Integration (Cerebro) - Engineering Checklist
*Initiated: 2026-02-11 kickoff*
*Updated: 2026-02-20*

## Context
Connect Greenmark's vendor systems to a central data warehouse, then build dashboards (Cerebro) on top. Strategy: 2+2+2 — connect 2 systems at a time, ordered by business value. First pair: Sage Intacct + HubSpot.

Code lives in external repos: [data-daemon](https://github.com/greenmark-waste-solutions/data-daemon), [cerebro](https://github.com/greenmark-waste-solutions/cerebro), [infra](https://github.com/greenmark-waste-solutions/infra).

## Vendor Research
- [x] Sage Intacct — deep research complete
- [x] Navusoft — deep research complete
- [x] HubSpot — deep research complete
- [x] Fleetio — deep research complete
- [x] Paylocity — deep research complete
- [x] WAM — deep research complete (confirmed no API, transitioning to Navusoft)
- [ ] 3rd Eye — unknown, no API docs found
- [ ] HubSpot API data model study — next up (real field names, bronze schema)
- [ ] Fleetio API data model study
- [ ] Sage Intacct API data model study

## Pipeline (data-daemon)
- [x] Pipeline architecture: YAML-driven, Postgres job queue
- [x] Synthetic data generators: Sage, HubSpot, Fleetio, Navusoft
- [x] 82 tests passing
- [x] Bronze schemas proposed (65 tables across 4 sources)
- [ ] Connect first real source (Sage) — blocked on credentials
- [ ] Connect second real source (HubSpot) — blocked on CRM read permissions

## Data Quality (cerebro-qa)
- [x] QA repo created
- [ ] Validation rules for bronze data
- [ ] Anomaly detection baseline

## HubSpot Setup Progress
- [x] Developer Portal access
- [x] CLI installed and authenticated (data-daemon-testing repo)
- [x] Security review — read-only only
- [x] Test account created (Greenmark Dev, 245316113, Enterprise tier)
- [x] REST API wrapper built (`hs-api.sh` — 9 commands)
- [x] Data exploration complete — 36 scopes mapped, all API patterns proven
- [x] CLI vs REST API capability map documented
- [x] Property groups analyzed: contacts (369/14), companies (245/12), deals (199/9)
- [x] Associations verified: v3, v4, inline all work
- [x] Batch read + search APIs confirmed for data-daemon extraction
- [ ] CRM read permissions on **production** enabled by Michael — [setup instructions](hubspot-setup.md)
- [ ] Expand test PAK scopes for CRM writes (to seed test data)
- [ ] Seed test account with waste industry data
- [ ] Design data-daemon HubSpot connector (TASK-1.17)

## Blocked On
- Sage user account for Daniel (Alex) → API key → real data
- HubSpot CRM read permissions for Daniel (Michael) → [setup instructions](hubspot-setup.md)
- HubSpot pipeline endpoint needs Private App auth (PAK won't work) — deferred
