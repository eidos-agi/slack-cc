# Greenmark Waste Solutions - Infrastructure Map
*Built from Project Cerebro notes (2026-02-11) + kickoff call*

## System Landscape

### Accounting & Finance
| System | Functions | API Status | Data Priority |
|--------|-----------|------------|---------------|
| **Sage Intacct** | General Ledger, Accounts Payable | Has connectors (ubiquitous product) | HIGH - feeds financial model & metrics |
| **Comerica** | Treasury / Banking | TBD - likely bank feeds | MEDIUM |
| **Expensify** | Employee expense reimbursement | Has API | LOW |

### Operations (Core)
| System | Functions | API Status | Data Priority |
|--------|-----------|------------|---------------|
| **Navusoft** | Customer system of record, proposals/service agreements, billing, AR, truck routing | API in development (per Michael) | CRITICAL - primary ops system |
| **FleetIO** | Truck maintenance, pre/post-trip, parts inventory, PO log | Has API | HIGH - maintenance & fleet data |
| **3rd Eye** | Telematics, truck cameras | UNKNOWN - potential blocker (per Michael: "don't know how that was built") | MEDIUM |
| **LB Technologies** | GPS tracking, telematics (legacy - Home Town) | TBD | MEDIUM |

### Operations (Legacy - Home Town)
| System | Functions | API Status | Data Priority |
|--------|-----------|------------|---------------|
| **WAM** | Customer system of record, billing, routing (legacy - Home Town) | TBD | HIGH - residential revenue data |

### Sales & CRM
| System | Functions | API Status | Data Priority |
|--------|-----------|------------|---------------|
| **HubSpot** | CRM, deal tracking, contract expiration tracking | Has API (well-documented) | HIGH - sales pipeline |

### People & Safety
| System | Functions | API Status | Data Priority |
|--------|-----------|------------|---------------|
| **Paylocity** | Payroll, benefits | Has API | HIGH - driver hours, payroll data |
| **AssureHire** | Pre-employment screening (criminal, credit, employment, DOT, drug, MVRs) | TBD | LOW |
| **Samba Safety** | CDL/DL expiration monitoring, med card dates, MVR ratings | TBD | MEDIUM - compliance tracking |

### Company-Wide / Productivity
| System | Functions | API Status | Data Priority |
|--------|-----------|------------|---------------|
| **Wrike** | Project management | Has API | LOW (internal PM) |
| **Egnyte** | Document storage | Has API | LOW (file storage) |
| **Vested Network** | Phone system | TBD | LOW |

## Entity Structure
```
Greenmark Waste Solutions
├── Greenmark NTX (Dallas operations)
│   ├── Front End Commercial (dumpster service)
│   ├── Roll-Off (construction/demolition)
│   └── Portable Toilets (sanitation)
└── Greenmark Hometown (acquired residential ops)
    ├── Residential (curbside collection)
    └── Roll-Off (new, Dec 2025)
```

## Data Flow Architecture (Proposed)

```
                    ┌─────────────┐
                    │  Dashboard  │
                    │   Layer     │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Unified    │
                    │  Database   │
                    │ (TBD: Supa/ │
                    │  AWS/Snow)  │
                    └──────┬──────┘
                           │
        ┌──────────┬───────┼───────┬──────────┐
        │          │       │       │          │
   ┌────┴───┐ ┌───┴───┐ ┌─┴──┐ ┌──┴───┐ ┌───┴────┐
   │Navusoft│ │ Sage  │ │Hub │ │Fleet │ │Paylo-  │
   │  + WAM │ │Intacct│ │Spot│ │  IO  │ │ city   │
   └────────┘ └───────┘ └────┘ └──────┘ └────────┘
   Ops/Billing Finance    CRM   Maint.   Payroll
```

## Priority Projects (from Michael)

### P0: KPI Dashboard
1. Set up unified database
2. Build connectors to all systems
3. Data cleanup / ETL
4. Create dashboards:
   - Financial (revenue, costs, margins)
   - Operational (tonnage, hauls, lifts, routes)
   - Drivers (hours, productivity, utilization)
   - Truck maintenance (R&M costs, fleet health)
   - Sales team (pipeline, deal tracking)
   - Customers (revenue per customer, churn)
   - People (headcount, payroll, compliance)
   - Advertising & Marketing

### P1: HubSpot → Navusoft Integration
- Export data from HubSpot into Navusoft
- Bridge CRM pipeline to ops system

### P2: Lunch Timekeeping App
- Tablet app for driver time tracking
- Exports into Paylocity

### P3: Expense Invoice Scanning
- Scan invoices and contracts
- Flag spending anomalies
- AI-powered review

### P4: Claude for Greenmark
- Set up Claude access for Greenmark team
- Phase 2 after dashboards are live

## Connector Research Needed

| System | Connector Type | Research Status |
|--------|---------------|----------------|
| Sage Intacct | REST API / pre-built connectors | Not started |
| Navusoft | New API (in development) | Not started - need to evaluate maturity |
| WAM | Unknown | Not started |
| HubSpot | REST API (well-documented) | Not started |
| FleetIO | REST API | Not started |
| Paylocity | REST API | Not started |
| 3rd Eye | UNKNOWN | Not started - flagged as potential blocker |
| LB Technologies | Unknown | Not started |
| Samba Safety | Unknown | Not started |

## Data Warehouse Decision

**Options discussed in kickoff:**
| Option | Pros | Cons | Fit |
|--------|------|------|-----|
| **Supabase (Postgres)** | Luke's first instinct, team familiarity, real-time subscriptions, Row Level Security | May not scale for large data warehouse needs | Good for app layer, maybe not sole warehouse |
| **AWS (RDS/Redshift)** | Scalable, mature, broad connector ecosystem | More ops overhead, cost at scale | Strong contender |
| **Snowflake** | Purpose-built for analytics, excellent SQL, scales infinitely | Cost per query, overkill for current size? | Best for pure analytics |

**Recommendation:** TBD after connector research reveals data volumes and query patterns.

## Key Metrics Being Tracked Today
*(from Greenmark_Metrics_2.11.26.pdf — 5 pages of monthly data)*

### Revenue
- Consolidated revenue by entity (NTX vs Hometown)
- Revenue by LOB: Front End Commercial, Portable Toilets, Roll-Off, Residential
- Revenue per lift/service/haul/cart
- Revenue per front-line truck (daily, monthly, annualized)
- Revenue per payroll hour and per driver hour

### Volume
- Lifts, services, hauls, carts by LOB
- Tonnage by type (roll-off, FE commercial, residential, special waste)
- Average rate per ton
- Tons/lbs per dump by LOB

### Personnel
- Payroll hours by entity
- Driver count by entity
- Average hours per week
- Driver productive hours
- Average productivity per week (%)

### Fleet
- Front-line truck count by LOB
- Revenue per truck per day/month/year

### Costs
- Disposal costs by type and entity
- R&M costs (repairs & maintenance)
- R&M cost per driver hour
- Total costs (COGS + SG&A - D&A) per driver hour

### Scale Reference (Dec 2025)
- **Total Revenue:** ~$948K/month ($11.4M annualized)
  - NTX: ~$75K/month (growing rapidly from $628 in Jan)
  - Hometown: ~$873K/month (stable residential base)
- **Total Tonnage:** ~3,671 tons/month
- **Drivers:** 4 NTX + 16 Hometown = 20 total
- **Front-line trucks:** ~20 across all LOBs
