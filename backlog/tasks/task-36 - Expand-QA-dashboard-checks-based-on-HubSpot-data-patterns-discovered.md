---
id: TASK-36
title: Expand QA dashboard checks based on HubSpot data patterns discovered
status: To Do
assignee: []
created_date: '2026-02-27 00:33'
labels:
  - cerebro-qa
  - hubspot
  - data-quality
dependencies: []
references:
  - cerebro-qa repo
  - infra/vendor-research/hubspot/api-data-model.md
  - cerebro/lib/mock-prospects.ts
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The cerebro-qa dashboard (qa.cerebro) needs new quality checks informed by what we learned from exploring HubSpot CRM data via the hs-api.sh wrapper. During HubSpot exploration we discovered data model patterns, field naming conventions, and data quality issues that should be monitored.

Areas to add QA checks for:
- **Company records**: Missing fields (industry, annual revenue, lifecycle stage), duplicate detection, entity tagging (NTX vs Hometown vs Both)
- **Deal records**: Deals missing close dates, deals stuck in stages too long, deal amounts vs company size sanity checks, deal-to-company association integrity
- **Contact records**: Contacts without company associations, missing email/phone, lifecycle stage progression validation
- **Custom properties**: Validate that Greenmark's custom properties (waste industry fields) are populated where expected
- **Cross-object integrity**: Deals without contacts, companies without deals in active pipeline, orphaned associations
- **HubSpot-specific conventions**: Deal stage names match expected pipeline stages (Prospect → Qualification → Proposal → Negotiation → Closed Won/Lost), lifecycle stages are sequential

Pull from what we learned about HubSpot terminology (Company, Deal, Deal Stage, Lifecycle Stage, Contact) and Navusoft terminology (Customer, Service Agreement, Site) to ensure QA checks use the right vocabulary for pre-close vs post-close data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 New QA checks cover Company, Deal, and Contact record quality
- [ ] #2 Checks validate custom property population for waste industry fields
- [ ] #3 Cross-object association integrity checks added (deal↔company, contact↔company)
- [ ] #4 Deal pipeline stage progression checks added
- [ ] #5 QA dashboard reflects HubSpot and Navusoft terminology correctly
<!-- AC:END -->
