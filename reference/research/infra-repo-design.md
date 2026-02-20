# 10 Ways to Make Greenmark's Infra Repo Better Than AIC's

*Thinking through what AIC infra does well, what it's missing, and what Greenmark's situation uniquely requires.*

---

## What AIC Infra Gets Right
- CLAUDE.md as index, not source of truth
- Conventions with rationale (never re-ask "why")
- Subscriptions registry (every bill in one place)
- Service map (repo → deployment → purpose)
- Each concern gets its own folder + README
- TODOs live in context, not a global list

## What's Different About Greenmark
- **Non-technical stakeholders** — Michael, Lannis, Alex need to read and contribute. AIC infra is engineer-only.
- **15 third-party systems** — AIC built its own tools. Greenmark is integrating with vendor software.
- **Field operations** — Trucks, drivers, routes, physical assets. Not a software company.
- **Two entities merging** — NTX (new, commercial) + Hometown (acquired, residential) with completely different tech stacks.
- **Trust but verify culture** — Michael was explicit: audit trails, data quality checks, no blind trust in automation.
- **Portfolio company economics** — AIC leadership wants to see ROI on every dollar spent on tech.
- **Rapid growth** — NTX went from $628/mo to $75K/mo in 12 months. Infra has to keep up.

---

## The 10 Improvements

### 1. Connector Research Templates
AIC doesn't need this — they built their own tools. Greenmark has 15 vendor systems that each need investigation.

Create a structured template for every data provider:
```
## [System Name]
- Vendor: / Website:
- API Type: REST / SOAP / CSV export / screen scrape / none
- Authentication: API key / OAuth / basic auth / unknown
- Documentation: [link]
- Rate Limits:
- Data Freshness: real-time / daily / on-export
- Sample Payload: (actual JSON/CSV snippet)
- Known Gotchas:
- Connector Status: not started / researching / prototype / production
- Estimated Integration Effort: hours
- Contact at Vendor:
```

This turns the "connector research" task from a vague todo into a structured, parallelizable workstream. Luke and Daniel can each take systems and fill in templates independently.

### 2. Stakeholder-Readable Status Layer
AIC infra is pure engineer docs. Michael said "we're going to be pretty involved throughout the whole process." Add a `status/` folder with non-technical summaries:

- `status/weekly-update.md` — Plain-English summary of what changed this week
- `status/system-health.md` — Green/yellow/red status for each integration
- `status/roadmap.md` — Visual timeline of what's coming (that Michael can show Collin/William)

This is also how you deliver on the "frequent check-ins" promise without scrambling before each meeting. The status docs ARE the meeting prep.

### 3. Data Dictionary with Metric Definitions
Greenmark tracks ~50+ KPIs across 5 pages. Each metric needs a formal definition:

```
## Revenue per Haul (Roll-Off)
- Definition: Total roll-off revenue / number of hauls in period
- Includes: hauling charge + tonnage fee + delivery fee
- Source Systems: Navusoft (billing) + Sage (GL reconciliation)
- Calculation: SUM(navusoft.roll_off_invoices.total) / COUNT(navusoft.roll_off_invoices.haul_id)
- Grain: Monthly, by entity (NTX / Hometown)
- Owner: Alex Kaye
- Quality Check: Should be between $300-$600; flag if outside range
```

This is the foundation of "trust but verify." When the dashboard says $425.90/haul and that seems low, anyone can look up the definition and trace it back to source. AIC doesn't need this because AIC's metrics are simpler (portfolio values from one API). Greenmark's metrics come from 6+ systems and require joins.

### 4. Entity Architecture Document
NTX and Hometown run completely different stacks:

| Concern | NTX | Hometown |
|---------|-----|----------|
| Ops system | Navusoft | WAM |
| GPS/Telematics | 3rd Eye | LB Technologies |
| Revenue model | Commercial (per-haul) | Residential (per-cart) |
| Driver count | 4 (growing) | 16 (stable) |

This needs its own document that answers:
- What's the long-term plan? Consolidate onto one stack?
- Which system wins? (Probably Navusoft — WAM is "legacy")
- What's the migration timeline?
- What data do we lose or gain in migration?
- Can the warehouse abstract over both during transition?

AIC never had this problem. Greenmark has it as a core architectural challenge.

### 5. Cost-Benefit Tracking Per System
For a portfolio company, every tech dollar needs justification. Add a cost-benefit column to the subscriptions registry:

```
## Navusoft
- Annual cost: $X
- Manual hours saved by integration: Y hrs/month
- Value of real-time data vs. monthly exports: (qualitative)
- ROI: X% payback in N months
```

This gives Collin and William the business case, not just the tech case. When Michael says "we need to connect 15 systems," leadership can see which 3 deliver 80% of the value.

### 6. Operational Runbooks (Current State)
Before we automate anything, document the manual process AS IT EXISTS TODAY:

- `runbooks/monthly-metrics.md` — How Alex currently builds the metrics report (which exports, which spreadsheets, how long it takes)
- `runbooks/new-customer-onboarding.md` — What systems get touched when a new customer signs up (HubSpot → Navusoft → billing)
- `runbooks/new-driver-onboarding.md` — Paylocity + AssureHire + Samba Safety + FleetIO + 3rd Eye
- `runbooks/invoice-processing.md` — Current expense invoice flow (the scanning/anomaly detection project)

Why this matters: You can't automate what you don't understand. These runbooks become the spec for automation. They also surface where the real pain is — maybe the monthly metrics report takes Alex 3 hours, but new customer onboarding takes 45 minutes across 4 people. That changes prioritization.

### 7. Data Quality Framework (Built-In from Day One)
Daniel's hospital data quality background is an asset. Build quality checks into the infra, not as an afterthought:

```
data-quality/
├── expectations.md       — Expected ranges, freshness SLAs per metric
├── reconciliation.md     — Source system ↔ warehouse reconciliation rules
├── anomaly-rules.md      — What triggers an alert (e.g., roll-off $/haul < $300)
└── quality-log.md        — Running log of quality issues found and resolved
```

The alert bar in the operations dashboard mockup ("NTX Roll-Off revenue/haul dropped to $425.90") is a preview of this. Make it systematic.

### 8. Access Matrix
Who has access to what, at what level. AIC doesn't track this because it's 2 engineers. Greenmark has 10+ people touching 15+ systems:

```
| Person | Navusoft | Sage | HubSpot | FleetIO | Dashboard | GitHub |
|--------|---------|------|---------|---------|-----------|--------|
| Michael | Admin | Admin | Admin | Admin | View | Read |
| Alex | View | Admin | View | - | View | - |
| Lannis | User | - | Admin | View | View | - |
| Robert | User | - | - | Admin | View | - |
| Daniel | API | API | API | API | Admin | Admin |
| Luke | API | API | API | API | Admin | Admin |
```

This is also a security document. When someone leaves, you know exactly what to revoke. When you build integrations, you know what access level exists vs. what you need to request.

### 9. Decision Log (Linked to Meetings)
Every infra decision should trace back to a meeting or conversation where it was made:

```
## 2026-02-11: Greenmark as separate tech org
- Decision: Greenmark will be treated as a separate organization in tech systems
- Made by: Daniel Shanklin
- Consulted: Luke Huntley, Aubrey Zastoupil
- Context: Simpler than intercompany reimbursements
- Meeting: areas/meetings/2026-02-11-project-cerebro-kickoff/
- Implications: Separate GitHub org, separate database, separate billing

## 2026-02-11: Dashboards before AI agent
- Decision: Priority 1 is traditional dashboards, AI querying is Phase 2
- Made by: Michael Nguyen
- Rationale: "Most people aren't used to finding data that way"
- Meeting: areas/meetings/2026-02-11-project-cerebro-kickoff/
```

This creates a chain: meeting recording → diarized transcript → decision log → infra change. Fully traceable. AIC's infra has conventions with rationale, but they're not linked to specific conversations. This is better.

### 10. Vendor Relationship Tracker
Greenmark depends on 15 vendors. Track the relationship, not just the technical integration:

```
## Navusoft
- Account rep: [name]
- Support tier: [basic/premium]
- Contract renewal: [date]
- API program: [status — are we in an early access program?]
- Last conversation: [date, topic]
- Open tickets: [list]
- Strategic notes: Michael mentioned they're "building out an API" — is this beta? GA? Timeline?
```

This matters because 3rd Eye is a blocker BECAUSE we don't know the vendor relationship. If we had a contact and knew their API roadmap, it might not be a blocker at all — or it might be worse than we think.

---

## Summary: The Greenmark Advantage

AIC infra was built bottom-up by engineers solving their own problems. Greenmark's infra can be built top-down with lessons learned. The key differences:

| AIC Infra | Greenmark Infra |
|-----------|-----------------|
| Engineer-only audience | Stakeholder-readable |
| Built own tools | Integrating vendor systems |
| 2-person team | 10+ people, multiple roles |
| Organic growth | Designed from day one |
| Static docs | Living status + decision trail |
| Tech-focused | Business-value-focused |

The biggest unlock: **every doc in the infra repo should be useful to both an engineer AND a business stakeholder.** Michael and Alex should be able to open the infra repo and understand what's happening without asking Daniel to translate.
