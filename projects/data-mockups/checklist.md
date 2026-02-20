# Data Mockups - Engineering Checklist
*Promised during kickoff call 2026-02-11*

## Goal
Create data mockups that help the Greenmark team monitor the business effectively.

## Tasks
- [x] Identify key metrics Greenmark tracks today (review Greenmark_Metrics_2.11.26.pdf)
- [ ] Identify gaps in current reporting
- [x] Design mockup dashboards / data views (3 created)
- [ ] Review mockups with Greenmark stakeholders (Michael + Alex)
- [ ] Refine based on feedback
- [ ] Determine data sources and integration approach

## Mockups Created (2026-02-11)
Three distinct styles for the team to react to:

1. **`mockups/executive-dashboard.html`** — Clean, card-based KPI layout with charts. Entity toggle (Consolidated / NTX / Hometown). Good for Collin & William's monthly view.

2. **`mockups/operations-dashboard.html`** — Dense, alert-driven ops view. Fleet status, driver productivity, volume trends, R&M tracking. Includes automated anomaly alerts. Good for Michael & Lannis daily use.

3. **`mockups/financial-dashboard.html`** — Spreadsheet-style that mirrors Alex's existing Excel workflow. Full-year tables, disposal cost breakdowns, margin visualization. Good for Alex & finance team.

## Metrics Covered (from PDF analysis)
- Revenue: consolidated, by entity, by LOB, per unit, per truck, per driver hour
- Volume: lifts, services, hauls, carts, tonnage
- Personnel: drivers, payroll hours, productive hours, productivity %
- Fleet: truck counts, revenue per truck per day/month/year
- Costs: disposal, R&M, total COGS+SGA, cost per driver hour

## Key Insight from Call
Michael said: "Dashboards first, AI agent second. Most people are used to seeing Excel charts." Alex has a detailed GL-level financial model in Excel. The financial mockup intentionally mirrors that spreadsheet aesthetic.

## New Feature Request (Feb 19 call)
- [ ] **Customer + prospect map page** — separate page in Cerebro, NOT embedded in existing dashboards
  - Data source: HubSpot (customers, prospects, deals)
  - Color-coded by deal pipeline stage
  - Michael: "The sales guys drive around a lot... being able to throw addresses down on a map"
  - Alex: "Plan my week for me, yo" — route/meeting planning from map
  - Sales reps should see only their customers/leads (permissioned)
  - Blocked on: HubSpot data connection

## Next Steps
- [ ] Send mockups to Michael + Alex for feedback ("which one do you like?")
- [ ] Schedule follow-up meeting to walk through
- [ ] Get system access to start real data integration
