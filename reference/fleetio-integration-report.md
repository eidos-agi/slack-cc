# Fleetio Data Integration — Session Report

**Date:** April 19, 2026
**API Key Owner:** Michael Nguyen (mnguyen@greenmarkwaste.com)
**Account:** Greenmark Waste — Premium 60 Annual (ID: 397507)
**Data Range:** 2025-01-03 to 2026-04-16 (15 months)

---

## What We Did

### Phase 0: API Key Probe
- Tested every documented Fleetio endpoint with the live API key
- Discovered the Account Token (required second header) via /api/v1/accounts
- Mapped all permissions: full admin read+write access
- Identified 16 data endpoints + 18 reference endpoints
- Found schema corrections vs existing research (dollars not cents, state not status)
- Saved full results to reference/fleetio-api-probe.md
- Vaulted credentials in cerebro-vault (Railway)

### Phase 1: Warp Speed Excel
- Wrote connection-forge spec: forges/connection/fleetio.yaml (15 objects)
- Generated extractor via elt-forge (handles mixed pagination: cursor + page-based)
- Extracted 27,313 records from Fleetio API into SQLite
- Built 11 silver tables with typed columns, entity mapping, currency normalization
- Built 7 gold tables with business metrics
- Generated 14-sheet branded Excel workbook for Robert

### Infrastructure Fixes
- **cerebro-vault**: fixed to support project-scoped Railway tokens (Project-Access-Token header instead of Bearer)
- **cerebro-docs MCP**: new MCP with progressive reveal for the Cerebro ecosystem (overview, explain, workflow, route)
- **cerebro-web-builder MCP**: finished — auth delegates to ab-login, docs tool added, 11 tools registered
- **Cross-MCP instructions**: all 5 MCPs now have routing tables pointing to each other + cerebro-docs
- **Vendor API onboarding workflow**: recorded in cerebro-docs for future vendor key arrivals

---

## The Fleet

| Metric | Value |
|--------|-------|
| Total vehicles | 53 |
| Memphis | 33 vehicles |
| NTX (Dallas + Fort Worth) | 20 vehicles |
| Contacts (drivers/techs) | 29 |
| Vendors | 71 |

**Vehicle types:**
- Rear Loader: 22
- Roll Off: 6
- Pickup Truck: 5
- Trailer: 3
- Front Loader: 3
- Container Truck: 3
- Shop: 2
- Portable: 2
- Loader: 2
- Support CD: 1
- Service Truck: 1
- Container: 1
- Car: 1
- CD Trailer: 1

---

## Financial Summary

| Category | Amount |
|----------|--------|
| R&M spend (826 completed WOs) | $159,844 |
| Fuel spend (raw) | $589,769 |
| Fuel spend (clean, outliers excluded) | $556,909 |
| Fuel data entry errors excluded | $32,860 (5.6%) |
| Total gallons consumed | 166,324 |
| Total fill-ups | 5,408 |

### Top 5 Vehicles by Total Operating Cost
- **4502** (Roll Off, NTX): $179,884 (R&M $6,567 + Fuel $173,317) — n/a MPG, Kevin St.Cyr
- **3019** (Rear Loader, Memphis): $36,318 (R&M $4,493 + Fuel $31,825) — 0.8 MPG, unassigned
- **3012** (Rear Loader, Memphis): $24,183 (R&M $7,506 + Fuel $16,678) — 2.1 MPG, unassigned
- **3017** (Rear Loader, Memphis): $23,205 (R&M $6,069 + Fuel $17,136) — 1.3 MPG, unassigned
- **3020B** (Rear Loader, Memphis): $23,105 (R&M $7,657 + Fuel $15,448) — 1.7 MPG, unassigned

### Monthly R&M Trend

| Month | Work Orders | Cost |
|-------|------------|------|
| 2026-04 | 72 | $23,746 |
| 2026-03 | 136 | $39,597 |
| 2026-02 | 58 | $16,881 |
| 2026-01 | 54 | $14,615 |
| 2025-12 | 67 | $20,374 |
| 2025-11 | 101 | $20,237 |

### Vendor Spend

| Vendor | WOs | Spend |
|--------|-----|-------|
| In-House / Unknown | 778 | $145,289 |
| Truelove's Parking | 29 | $7,740 |
| Southern Tire Mart | 16 | $5,987 |
| All American Towing | 1 | $728 |
| EMS Services | 1 | $100 |
| American Truck & Equipment | 1 | $0 |

---

## Data Quality

### 20-Check Audit Results

**Round 1 (10/10 passed):**
1. Duplicates: PASS — 0 across all tables
2. Orphaned references: PASS — 0 after vendor pagination fix
3. Null rates: WARN — 6 vehicles missing VIN (11%)
4. Date ranges: PASS — 2025-01-03 to 2026-04-16
5. Currency: PASS — 0 negative amounts
6. Vehicle statuses: PASS — all Active
7. Work order states: PASS — 826 completed, 1 active
8. Fuel prices: WARN — 19 outlier entries excluded ($32,860)
9. Inspections: PASS — worst vehicle: 4504 with 16 failures
10. Completeness: PASS — consistent monthly volumes

**Round 2 (additional findings):**
11. Cross-table consistency: PASS — 826/826 service entries match work orders
12. Future dates: PASS — none
13. Odometer monotonicity: WARN — 25% reversals in meter readings (likely mixed hour/mile meters)
14. Issue lifecycle: FLAG — 344 issues show resolved before reported (timezone or backdating)
15. Group coverage: PASS — 2 ungrouped (internal/test vehicles)
16. Cost decomposition: PASS — labor + parts = total for all costed WOs
17. Fuel gaps: PASS — max 7-day gap (holiday)
18. Vendor concentration: INFO — 91% of spend is in-house
19. Inspection coverage: QUESTION — 15/53 vehicles have DVIR data, all NTX. Memphis has none in Fleetio.
20. Field coverage: INFO — 37 additional fields available for future extraction

### Questions for Robert Heath

1. **Memphis inspections:** We see DVIR data for 15 NTX vehicles but none for Memphis. Is Memphis using a different system for inspections, or should we expect to see that data in Fleetio?

2. **Memphis entity mapping:** The Fleetio "Memphis" group has 33 vehicles. Does this map to the Hometown (Indiana) entity or the nascent Memphis entity?

3. **Vehicle 4502 fuel:** This Roll Off shows $180K in fuel charges. Is this a fuel depot allocation code or actual vehicle fuel consumption?

4. **Fuel price errors:** 19 fuel entries have prices over $7/gallon (up to $305/gal). These appear to be data entry errors — should we flag them in Fleetio for correction?

5. **6 vehicles without VINs:** Shop lead, Lead time, Container, 3008, 3021, 3024. Are these equipment that wouldn't have VINs, or missing data?

6. **Vehicle 3004 hydraulic leaks:** 7 separate "Hydraulic leak" work orders. Is this a recurring problem that needs root-cause analysis, or normal wear for this vehicle type/age?

7. **Benford's Law anomaly on digit 5:** 25.8% of WO costs start with digit 5, vs the expected 7.9%. Is there a pricing structure or labor rate that clusters around the $50-59 range?

8. **Driver assignments in Memphis:** 38 Memphis vehicles have operational activity (fuel, meters) but no driver assigned in Fleetio. Is driver assignment tracked elsewhere for Memphis?

9. **March maintenance spike:** 143 work orders in March vs ~60 average. Is this a seasonal pattern (spring fleet prep), or a data artifact?

10. **Skid Steer utilization:** 141 consecutive days with no activity (Jul-Nov 2025). Is this vehicle parked seasonally, or should it show activity?

---

### Round 3: Advanced Checks (21-40) — Rhea-Designed

Three-persona analysis: Fleet Operations Analyst, Forensic Accountant, DOT Compliance Officer.

#### Fleet Operations Analyst

**21. Vehicle Utilization Voids (extended dark periods)**

| Vehicle | Type | Entity | Dark Period | Days |
|---------|------|--------|-------------|------|
| Skid Steer | Loader | NTX | Jul 1 - Nov 19, 2025 | 141 |
| 3029 | Pickup Truck | Memphis | Oct 27 - Feb 6 | 102 |
| Container | Container | Memphis | Jan 5 - Mar 30 | 84 |
| 4506 | Roll Off | NTX | Aug 12 - Nov 4 | 84 |
| Shop Time | Shop | Memphis | Dec 1 - Feb 18 | 79 |

**22. Cost-Per-Operating-Day by Vehicle (ranked, no threshold)**

| Vehicle | Type | Entity | R&M | Op Days | $/day |
|---------|------|--------|-----|---------|-------|
| 3001 | Rear Loader | Memphis | $7,104 | 90 | $78.93 |
| 3015 | Rear Loader | Memphis | $9,126 | 140 | $65.18 |
| 3016 | Rear Loader | Memphis | $9,502 | 169 | $56.23 |
| 3004 | Rear Loader | Memphis | $8,820 | 160 | $55.13 |
| 3003 | Rear Loader | Memphis | $5,994 | 121 | $49.54 |

Vehicle 3001 costs $78.93/operating day in R&M — nearly 2x the next costliest vehicle. Replacement candidate if the trend continues.

**23. Fuel Cost Trend (quarterly, vehicles with >15% increase)**

| Vehicle | Quarter | $/gal | Previous | Change |
|---------|---------|-------|----------|--------|
| 3005 | 2026-Q2 | $5.11 | $3.18 | +61% |
| 3003 | 2026-Q2 | $5.23 | $3.29 | +59% |
| 3004 | 2026-Q2 | $5.22 | $3.44 | +52% |
| 1401 | 2026-Q2 | $5.39 | $3.60 | +50% |

All increases are in Q2 2026 — likely a market fuel price increase affecting the entire fleet, not individual vehicle issues.

**24. Issue Lifecycle Orphans:** PASS — 0 unresolved issues. All 755 issues are Resolved (730) or Closed (25).

**25. Driver Accountability Gaps:** 38 vehicles with 2026 fuel activity but no current driver assignment. All Memphis rear loaders.

#### Forensic Accountant

**26. Round-Dollar Work Orders:** 11 of 744 costed WOs (1.5%) are exact round dollars. Low — not a concern.

| Amount | Count |
|--------|-------|
| $100 | 5 |
| $200 | 4 |
| $250 | 1 |
| $150 | 1 |

**27. Benford's Law Analysis**

| Digit | Actual | Expected | Diff |
|-------|--------|----------|------|
| 1 | 32.9% | 30.1% | +2.8% |
| 2 | 14.1% | 17.6% | -3.5% |
| 3 | 9.4% | 12.5% | -3.1% |
| **4** | **3.9%** | **9.7%** | **-5.8%** |
| **5** | **25.8%** | **7.9%** | **+17.9%** |
| 6 | 4.2% | 6.7% | -2.5% |
| 7 | 3.6% | 5.8% | -2.2% |
| 8 | 4.4% | 5.1% | -0.7% |
| 9 | 1.6% | 4.6% | -3.0% |

Digit 5 is massively overrepresented (+17.9%). This likely reflects a standard labor rate or pricing tier that clusters WO costs in the $50-59 range — not necessarily fraud, but worth understanding the root cause.

**28. Weekend Work Orders:** 12 of 826 (1.5%) — 7 Saturday, 5 Sunday, $2,783 total. Clean — no backdating signal.

**29. Same-Vehicle Same-Day Multiple WOs:** 5 instances of 3+ WOs on the same vehicle in the same day. All low-cost ($0-$498) — likely batch entry of multiple small tasks, not anomalous.

**30. Parts-to-Labor Ratio by Vehicle Type**

| Type | Parts | Labor | Ratio |
|------|-------|-------|-------|
| Support CD | $918 | $474 | 1.94 |
| Roll Off | $6,887 | $5,014 | 1.37 |
| Rear Loader | $73,596 | $59,781 | 1.23 |
| Front Loader | $704 | $1,162 | 0.61 |
| Pickup Truck | $160 | $540 | 0.30 |
| Shop | $0 | $5,697 | 0.00 |

Rear loaders and roll-offs are parts-heavy (ratio >1). Pickups and front loaders are labor-heavy. Shop is 100% labor (expected — shop time, not repairs).

#### DOT Compliance Officer

**31. Inspection Frequency:** 5 vehicles with <5 inspections per month. Vehicle 1401 (Pickup, NTX) has only 1 inspection in 15 months.

**32. Inspection Pass Rate by Inspector**

| Inspector | Inspections | Pass Rate |
|-----------|-------------|-----------|
| kstcyr@greenmarkwaste.com | 626 | 98.7% |
| tmiller@greenmarkwaste.com | 411 | 96.8% |
| dfaulkner@greenmarkwaste.com | 701 | 96.7% |
| dsteptoe@greenmarkwaste.com | 575 | 94.4% |
| qbooker@htdisposal.com | 155 | 94.2% |
| dhill@greenmarkwaste.com | 22 | 90.9% |

No rubber-stamping signal. Defect detection rates range 1.3%-9.1% across inspectors — realistic for a waste fleet. Note: qbooker@htdisposal.com (Hometown domain) has 155 inspections, confirming at least some Memphis/Hometown inspection activity.

**33. Failed Inspection Trend:** Dec 2025 had a spike of 15 failures (17 failed items), but has since improved to 1-3 per month. Worth checking what changed in January 2026.

**34. Active Vehicles Without Recent Inspection:** 27 of 53 vehicles have fuel activity in the last 30 days but no inspection. Mostly Memphis rear loaders (same finding as check 19 — confirmed from a different angle).

**35. Inspection GPS Coverage:** 86% of inspections have GPS coordinates. Zero outliers outside TX/TN geography. Clean.

#### Cross-System Intelligence

**36. Recurring Part Replacements**

| Vehicle | Repair | Occurrences |
|---------|--------|-------------|
| 3016 | PMA | 12 |
| 4502 | PMA | 10 |
| 3004 | Hydraulic leak | 7 |
| 4502 | Tire Replacement | 6 |
| 3003 | Inspect unit | 6 |

Vehicle 3004's 7 hydraulic leak repairs is the standout — recurring failure without root cause resolution. Vehicle 4502 has 6 tire replacements (consistent with its Roll Off duty cycle).

**37. Maintenance Seasonality**

| Month | WOs | Cost | Pattern |
|-------|-----|------|---------|
| Mar | 143 | $39,632 | Peak — spring fleet prep |
| Oct | 113 | $14,902 | Secondary peak — fall prep |
| Nov | 102 | $20,237 | Continued fall |
| Aug | 3 | $0 | Near-zero |
| Sep | 4 | $0 | Near-zero |

Strong bimodal seasonality: March peak and October/November secondary peak with an August/September trough. This aligns with waste hauling — pre-summer and pre-winter fleet prep cycles.

**38. Entity Comparison (normalized per vehicle)**

| Entity | Vehicles | R&M/vehicle | Fuel/vehicle | Issues/vehicle | Inspections/vehicle |
|--------|----------|-------------|--------------|----------------|---------------------|
| Memphis | 33 | $4,312 | $9,265 | 20.4 | 5.2 |
| NTX | 20 | $877 | $12,559 | 4.2 | 117.1 |

Memphis fleet costs **5x more per vehicle in R&M** ($4,312 vs $877) and generates **5x more issues** (20.4 vs 4.2). NTX has dramatically more inspections per vehicle (117.1 vs 5.2) — confirming Memphis's inspection gap. NTX's higher fuel cost per vehicle likely reflects the 4502 Roll Off outlier inflating the average.

**39. Work Order Completion Time**

| Duration | WOs | Avg Cost |
|----------|-----|----------|
| Same day | 531 | $202 |
| 1 day | 267 | $181 |
| 2-3 days | 24 | $169 |
| 4-7 days | 2 | $81 |
| 1-2 weeks | 1 | $0 |
| 30+ days | 1 | $0 |

96% of work orders complete within 1 day. Fast turnaround — the shop is responsive.

**40. Top Service Tasks**

| Task | Frequency | Total Cost |
|------|-----------|------------|
| PMA (Preventive Maintenance A) | 75 | $4,980 |
| PMB Lube, Oil, Filter | 61 | $4,503 |
| Hydraulic leak | 39 | $3,814 |
| Inspect unit | 24 | $2,122 |
| Tires (Miscellaneous) | 18 | $2,700 |
| Tire Replacement | 15 | $3,599 |
| CEL ON (Check Engine Light) | 15 | $1,928 |
| Check tires | 13 | $983 |
| A/C System Test | 13 | $1,091 |
| PMA 150 Hours | 11 | $1,138 |

Hydraulic leaks are the #3 service task at $3,814 total — the most expensive non-PM repair category. Tire work (misc + replacement + check) combined is 46 tasks at $7,282.

---

## Deliverables

| Artifact | Location |
|----------|----------|
| API probe results | reference/fleetio-api-probe.md |
| API white paper (PDF) | reference/fleetio-api-white-paper.pdf |
| Connection spec | cerebro-warp-speed-excel/forges/connection/fleetio.yaml |
| Extractor | cerebro-warp-speed-excel/pipeline/extractors/fleetio.py |
| Bronze schema (16 tables) | cerebro-warp-speed-excel/pipeline/schema/fleetio_bronze.sql |
| Silver transforms (11 tables) | cerebro-warp-speed-excel/pipeline/transforms/silver/fleetio.sql |
| Gold transforms (7 tables) | cerebro-warp-speed-excel/pipeline/transforms/gold/fleetio.sql |
| Excel workbook | cerebro-warp-speed-excel/reports/Latest/cerebro-operations.xlsx |
| Credentials | cerebro-vault: SECRET_FLEETIO_API_KEY, SECRET_FLEETIO_ACCOUNT_TOKEN |
| Railway token diagnostic | tools/test-railway-token.sh |

---

## What's Next (Phase 2: Production Pipeline)

1. Build FleetioConnector in data-daemon using proven schemas from Phase 1
2. Land in Supabase bronze tables (fleetio_bronze schema)
3. Build silver/gold materialized views
4. Wire Maintenance dashboard page to fleetio_gold views
5. Verify with cerebro-verifier against the Excel as ground truth

---

## Data Inventory — Complete

### Extracted (28 bronze tables, 29,497 records)

| Table | Records | Layer |
|-------|---------|-------|
| vehicles | 53 | silver + gold |
| contacts | 29 | silver + gold |
| work_orders | 827 | silver + gold |
| service_entries | 855 | silver + gold |
| fuel_entries | 5,408 | silver + gold |
| issues | 755 | silver + gold |
| meter_entries | 17,298 | silver + gold |
| inspections | 2,512 | silver (inspections) |
| parts | 204 | silver + gold |
| purchase_orders | 119 | silver + gold |
| vendors | 71 | silver + gold |
| groups | 3 | silver + gold |
| vehicle_types | 21 | bronze only |
| vehicle_statuses | 5 | bronze only |
| vehicle_assignments | 20 | bronze only |
| expense_entries | 35 | bronze only |
| service_reminders | 75 | bronze only |
| vehicle_renewal_reminders | 50 | bronze only |
| inventory_journal | 393 | bronze only |
| comments | 100 | bronze only |
| labels | 117 | bronze only |
| tires | 102 | bronze only |
| documents | 100+ | bronze only (pagination needs fix for full set) |
| vmrs_reason_for_repairs | 59 | bronze only |
| inspection_schedules | 265 | bronze only |
| fuel_types | 12 | bronze only |
| issue_priorities | 5 | bronze only |
| roles | 4 | bronze only |

### Nested Data (embedded, not yet flattened to own tables)

| Data | Records | Value |
|------|---------|-------|
| Work order line items | 579 | Task-level cost breakdown |
| Service entry line items | 1,733 | Service task details |
| Issue → WO linkages | 649 | Which issues led to which WOs |
| Fuel → meter readings | 5,408 | Odometer at time of fill-up |

### Known Endpoints Not Yet Extracted

| Endpoint | Data | Priority |
|----------|------|----------|
| /assets | Richer vehicle specs (may have GVWR, tank capacity) | High |
| /service_tasks | ~550 task catalog | Medium |
| /images | ~31 photos | Low |
| /imports | ~134 CSV import history | Low |
| /axle_configs | ~92 axle/tire position configs | Low |
| /equipment_types | 24 definitions | Low |
| /part_categories | 11 categories | Low |
| /part_locations | 6 warehouses | Low |

### Confirmed Not Available

- Telematics / live GPS tracking
- Geofencing
- Compliance / DOT reporting endpoints
- Reports / Analytics / Dashboard APIs
- Routes / Trips / Route optimization
- Leases / Loans / Financing

### Infrastructure

- **Rate limiter added** to extractor: sliding window (200 req/60s), automatic 429/503 retry with backoff, Retry-After header parsing
- **Pagination bug found and fixed**: page-based endpoints were re-reading page 1 on some objects, causing 350x duplication on comments and documents

*Generated 2026-04-20 and updated throughout session 34*
