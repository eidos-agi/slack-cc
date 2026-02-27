---
id: TASK-13
title: Design entity resolution strategy for cross-vendor normalization
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:39'
updated_date: '2026-02-27 00:43'
labels:
  - architecture
  - data-daemon
  - silver-layer
milestone: MVP
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The dashboard has a Consolidated / NTX / Hometown toggle. This requires matching customers, accounts, and transactions across vendors that use different IDs, names, and schemas. "Greenmark NTX" in Sage may be "Greenmark Waste Solutions" in HubSpot. Nobody has designed how entity resolution works. Needs at least a design doc before Silver layer work begins.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Design doc covering entity ID mapping across Sage, HubSpot, and Navusoft
- [ ] #2 Entity resolution approach chosen (manual mapping vs fuzzy matching vs hybrid)
- [ ] #3 Alex and Michael reviewed and confirmed entity naming conventions
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Feb 27: **Second opinion (GPT-5.2)** — Manual mapping table is the correct approach at this scale. Fuzzy matching is over-engineered and dangerous for entity tagging (drives financial rollups). Use vendor-specific keys (subsidiary ID, location ID, ledger/book) not name matching. Build `entity_source_map(source_system, source_entity_key, canonical_entity_id)`. Records that don't match → UNRESOLVED status, surfaced via exception report. Customer dedup across vendors is a separate problem — defer to Silver layer, start with deterministic linking (tax ID, email). Pitfall: some vendors (Fleetio, Paylocity) represent company as one org with tags/locations, not subsidiaries — map cost center or department to entity. Action needed: confirm how Sage identifies entities (subsidiary ID?) and whether HubSpot uses a custom property.
<!-- SECTION:NOTES:END -->
