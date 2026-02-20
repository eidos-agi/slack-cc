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
- [ ] Connect second real source (HubSpot) — blocked on API access

## Data Quality (cerebro-qa)
- [x] QA repo created
- [ ] Validation rules for bronze data
- [ ] Anomaly detection baseline

## Blocked On
- Sage user account for Daniel (Alex) → API key → real data
- HubSpot API access for Daniel (Alex/Michael) → second source
