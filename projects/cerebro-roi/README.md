# Project Cerebro — Progress & Execution Plan

Where we are, where we're going, and what each of us needs to do to get there.

---

## What's Been Built (Weeks 1–2)

| Deliverable | What It Does | Status |
|---|---|---|
| [data-daemon](https://github.com/greenmark-waste-solutions/data-daemon) | Pulls data from vendor systems into our warehouse automatically | Built, 82 tests passing, waiting for live credentials |
| [cerebro](https://github.com/greenmark-waste-solutions/cerebro) | Dashboard app — financial, CRM, and operations views | Built, running on Railway with synthetic data |
| [cerebro-qa](https://github.com/greenmark-waste-solutions/cerebro-qa) | Checks that dashboard data matches the source systems | Built — the "verify" in "trust but verify" |
| [cerebro-warp-speed](https://github.com/greenmark-waste-solutions/cerebro-warp-speed) | AI assistant that can answer questions across multiple systems at once | Built, 190 tests passing across 17 query types |
| [infra](https://github.com/greenmark-waste-solutions/infra) | Vendor API documentation, data dictionary, integration specs | 6 of 15 vendor systems deeply researched, 65 database tables designed |
| [gmw-dot-com-astro](https://github.com/greenmark-waste-solutions/gmw-dot-com-astro) | Rebuilt greenmarkwaste.com for speed | Mobile performance: 47 → 92. Page load: 17.5s → 2.7s |
| [weekly-updates](https://github.com/greenmark-waste-solutions/weekly-updates) | Automated engineering progress reports from commit history | Running weekly |
| [greenmark-cockpit](https://github.com/greenmark-waste-solutions/greenmark-cockpit) | This repo — project plans, meeting notes, decisions, checklists | You're reading it |

### Infrastructure Cost

| Service | Monthly Cost |
|---|---|
| Railway (5 services) | ~$50 |
| Supabase (database) | ~$25–50 |
| **Total** | **Under $150/mo** |

### Ownership

Every repository, database, and deployment belongs to Greenmark. GitHub org, Supabase account, Railway project — all under Greenmark credentials. The code is documented, tested, and maintainable by any engineer.

---

## What's Next: 90-Day Plan

**Week 1 starts the week live credentials arrive.** HubSpot is connected and verified (02/28). Sage Intacct is the remaining blocker — waiting on Alex for a user account.

### Phase 1 — "First Light" (Weeks 1–4)

**Goal:** Real Greenmark data in Cerebro. First live dashboard.

#### What We Need From Each Other

| Who | What | Time Required | Why It Matters |
|---|---|---|---|
| **Alex** | Create a read-only Sage Intacct user for Daniel | ~5 min admin task | Unlocks the financial dashboard with real numbers |
| ~~**Michael**~~ | ~~Enable CRM read permissions for Daniel in HubSpot~~ | ~~Done~~ | ✅ Completed 02/23 — Daniel has full CRM access |
| **Daniel** | Connect data-daemon to real APIs, validate data, deploy live dashboards | 3–5 days per connector | Turns synthetic demos into real tools |
| **Michael + Alex** | 30-min walkthrough to review the first live dashboard | 30 min | Your feedback shapes what gets built next |

#### Checklist

- [ ] Alex: Sage Intacct user account for Daniel (dshanklin@aicholdings.com)
- [ ] Daniel: Create read-only API key once account exists
- [x] Michael: HubSpot CRM read permissions for Daniel ✅ (completed 02/23)
- [x] Daniel: Create HubSpot Private App key with read-only CRM scopes ✅ (completed 02/28)
- [x] Daniel: Verify HubSpot API returns real data — contacts, companies, deals ✅ (completed 02/28)
- [ ] Daniel: Connect data-daemon to Sage — first extraction, validate against Sage UI
- [ ] Daniel: Connect data-daemon to HubSpot — first extraction, validate against CRM
- [ ] Daniel: Deploy live financial dashboard (AR aging, AP aging, GL balances, revenue by entity)
- [ ] Daniel: Deploy live CRM dashboard (pipeline value, prospect map, deal stages)
- [ ] Daniel: Build 10 validated KPI queries — confirmed to match source systems exactly
- [ ] All: 30-minute walkthrough — "Here's your real data. What's missing? What's wrong?"
- [ ] Daniel: Fix top 3 feedback items same week

#### Parallel Work (no credentials needed)

- [ ] Transfer Railway billing to it@greenmarkwaste.com
- [ ] Transfer Supabase org ownership to it@greenmarkwaste.com
- [ ] Transfer GitHub org admin to Michael
- [ ] Build remaining Astro pages (about, services, FAQ, contact)
- [ ] Set up GA4 + Google Search Console for both domains

#### What This Unlocks

Alex stops building monthly Excel reports from Sage exports. The dashboard pulls the same data automatically and keeps it current.

---

### Phase 2 — "Expanding the View" (Weeks 5–8)

**Goal:** Systems start talking to each other. The AI assistant answers real questions. Sales team gets a daily tool.

#### What We Need From Each Other

| Who | What | Why It Matters |
|---|---|---|
| **Alex** | Validate cross-system entity matching — "Is this HubSpot account the same as this Sage billing entity?" | You know the accounts. The system needs your confirmation to get matching right. |
| **Michael** | Navusoft API access (if available) | Adds service and route data to the picture |
| **Michael** | Identify 2–3 sales reps for early CRM dashboard access | Real users find real issues |
| **Daniel** | Entity resolution, AI assistant on real data, prospect map, auth upgrade | Connecting the dots between systems |

#### Checklist

- [ ] Daniel: Cross-system identity matching — HubSpot account ↔ Sage billing entity
- [ ] Alex: Validate matching accuracy against known accounts
- [ ] Daniel: Point cerebro-warp-speed at real data (currently synthetic)
- [ ] Daniel + Michael: Test 10 AI queries against real data — verify answers
- [ ] Daniel: Prospect map with real HubSpot data — color-coded by deal stage
- [ ] Michael: Navusoft API access → Daniel: build connector (conditional on availability)
- [ ] Daniel: Role-based access — admin, finance view, CRM-only view
- [ ] Michael: Identify initial users beyond leadership

#### What This Unlocks

Michael's sales team has a daily tool — prospect map, pipeline view, route planning context. Michael and Alex can ask the AI assistant questions instead of pulling reports from three systems manually.

---

### Phase 3 — "Self-Sustaining" (Weeks 9–12)

**Goal:** The system monitors itself. The team uses it without Daniel in the room. We plan what's next together.

#### What We Need From Each Other

| Who | What | Why It Matters |
|---|---|---|
| **Alex** | Define which financial anomalies matter — "Alert me if revenue drops 30% week-over-week" | You decide what's signal vs. noise |
| **Michael** | Define which operational anomalies matter — "Alert me if extraction fails" | Same — your priorities drive the alerts |
| **All** | 30-minute guided session — full walkthrough of every feature | Everyone confident using the tools independently |
| **All** | Phase 2 scope planning session | What do we build next? Driven by what you've learned using the system. |

#### Checklist

- [ ] Daniel: Data quality rules — row counts, null rates, freshness checks
- [ ] Alex + Daniel: Define financial alert thresholds
- [ ] Michael + Daniel: Define operational alert thresholds
- [ ] Daniel: pg_cron for auto-refreshing KPI views
- [ ] Daniel: Training page in Cerebro + 3 short walkthrough videos
- [ ] All: 30-minute guided session with Michael + Alex
- [ ] Daniel: Architecture one-pager for the team
- [ ] Daniel: Emergency runbook — "If something breaks, here's what to check"
- [ ] All: Phase 2 scope planning — what's next, based on what we've learned
- [ ] Daniel: Verify all accounts under Greenmark billing, credentials documented

#### What This Unlocks

The system runs itself. Quality alerts catch problems before anyone notices. The team uses dashboards and the AI assistant as part of their daily workflow. Daniel shifts from building to improving — guided by what the team actually needs.

---

## Cost Summary

| Phase | Monthly Infrastructure | What Changes |
|---|---|---|
| Phase 1 (Weeks 1–4) | ~$100/mo | First live dashboards |
| Phase 2 (Weeks 5–8) | ~$125/mo | Cross-system intelligence, AI assistant, sales tools |
| Phase 3 (Weeks 9–12) | ~$125/mo | Self-monitoring, alerts, team onboarding |

90-day infrastructure total: ~$350–$450.

---

## Known Risks and How We Handle Them

| Risk | Impact | How We Handle It |
|---|---|---|
| Credential delays | Pushes all phases back | This plan is designed so Daniel has parallel work (website, ownership transfers, GA4) while waiting. No idle time. |
| Data quality surprises when real data arrives | Dashboard shows wrong numbers | cerebro-qa exists for this. We validate before anyone sees a dashboard. Alex spot-checks financials against Sage. |
| Navusoft API not available or immature | Phase 2 loses one data source | Plan doesn't depend on Navusoft. It's additive — Sage + HubSpot carry the value. |
| Entity resolution is harder than expected | Matching accounts across systems takes longer | Start with exact matches, add fuzzy matching iteratively. Alex validates. We don't ship until it's right. |
| Team adoption is slow | Tools sit unused | Don't force it. Show the value, make it available, let usage follow utility. Training videos for self-serve. |

---

## How to Track Progress

This checklist is the source of truth. As items complete, Daniel checks them off and the team can see progress here in GitHub at any time. The [weekly-updates repo](https://github.com/greenmark-waste-solutions/weekly-updates) also generates automated engineering reports from commit history — so there's always a record of what's moving.

Questions, feedback, or priority changes — bring them to our next call or email Daniel directly.
