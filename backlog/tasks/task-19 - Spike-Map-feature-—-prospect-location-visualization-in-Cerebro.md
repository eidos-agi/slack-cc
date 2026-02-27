---
id: TASK-19
title: 'Spike: Map feature — prospect/location visualization in Cerebro'
status: Done
assignee:
  - Daniel
created_date: '2026-02-26 22:10'
updated_date: '2026-02-27 00:44'
labels:
  - spike
  - cerebro
  - map
  - hubspot
  - navusoft
milestone: MVP
dependencies: []
references:
  - 'https://github.com/greenmark-waste-solutions/cerebro'
  - infra/decisions/ADR-2026-01.md
  - infra/vendors/hubspot/api-data-model.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a custom map to Cerebro showing prospect locations, eventually overlaying Navusoft route/operations data. The team wants to see visually where prospects are. This is a spike to evaluate options, prototype, and choose an approach before full implementation.

## Data Sources (phased)
- **Phase 1: HubSpot** — contacts/companies with address fields (street, city, state, zip) and IP-derived location (ip_city, ip_state). Use CRM v3 APIs.
- **Phase 2: Navusoft** — routing/operations data (stops, territories, routes) as overlay layers.

## Architecture Layers
1. **Data source layer**: Pull geocoded records from HubSpot (later Navusoft)
2. **Enrichment/geocoding**: Batch geocode addresses to lat/lng, cache in DB. Start with IP-location if "good enough"
3. **App API layer**: Internal endpoint `GET /api/prospects/map` returning `{ id, name, type, lat, lng, status, source, last_activity }` with filters (owner, lifecycle stage, geography)
4. **Front-end map**: JS map library with markers, clustering, filters, detail panels

## 15 UI Options Evaluated (shadcn/Vercel/Tailwind stack)
1. **Leaflet via React-Leaflet + shadcn wrappers** — OSM tiles, no vendor lock-in, great plugin ecosystem
2. **Shadcn Map / mapcn components** — pre-built shadcn-aligned Leaflet components, fastest time-to-first-map
3. **Google Maps via @react-google-maps/api** — familiar, rich POI data, requires billing
4. **Mapbox GL JS via react-map-gl** — vector tiles, 3D, deck.gl layers, good for heavy viz
5. **Pigeon Maps** — ultra-lightweight React map, minimal bundle impact
6. **Server-rendered static maps + shadcn overlays** — cheap, great for reports/PDFs
7. **Heatmap-centric view** — density viz instead of individual markers, good for "where are we strong/weak"
8. **Territory polygons + prospect markers** — GeoJSON boundaries for sales territory planning
9. **"Prospect detail in Drawer/Sheet" pattern** — clean map + shadcn Sheet for details on click
10. **"Map as filter" above Data Table** — draw regions to filter, power-user workflow
11. **Saved map views & segments** — named filter presets, recall via Combobox
12. **Directions/route planning overlay** — bridges toward Navusoft integration
13. **Mobile-first mini-map components** — compact map in cards, expand on tap
14. **Map selection baked into shadcn patterns** — ButtonGroup for layers, Toggle for visibility
15. **Analytics-heavy "Map dashboard"** — map + Recharts + metric cards synchronized to viewport

## Data Mapping Primitives to Apply
- **Field-to-field mapping**: HubSpot address fields → canonical location model
- **Lookup table mapping**: lifecycle stages, territory codes
- **Canonical model**: Design a `Location` model that HubSpot and Navusoft both map into
- **Hierarchical mapping**: Company → Contacts (company-level markers with contact drill-down)
- **Aggregation/roll-up**: Contact count per region, deal value per territory
- **Incremental/CDC mapping**: Sync only changed records from HubSpot
- **Privacy-aware mapping**: PII handling for contact addresses

## Key Decision: Canonical Model First
Need to decide which domain to model first: Prospect, Location, or Route. Location is likely the foundation since both HubSpot prospects and Navusoft routes need geocoded coordinates.

## Implementation Phases
1. **Prototype**: Choose map library, hard-code example points from HubSpot export, validate UX with team
2. **MVP HubSpot integration**: /api/prospects/map endpoint, nightly sync, geocoding + caching, basic filters
3. **Productionize**: Auth/permissions, advanced filters, performance tuning, territory overlays
4. **Navusoft integration**: Routes/territories as separate layers, layer toggle
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Map library chosen with documented rationale (Leaflet vs Mapbox vs Google vs Pigeon)
- [ ] #2 Canonical Location model designed (lat/lng, source, entity type, metadata)
- [ ] #3 Prototype with real HubSpot addresses plotted on map in Cerebro
- [ ] #4 Geocoding strategy decided (batch vs IP-location vs hybrid) with cost estimate
- [ ] #5 API endpoint spec for /api/prospects/map with filter params defined
- [ ] #6 UX pattern chosen (drawer/sheet, map-as-filter, heatmap, or hybrid) with team feedback
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Prospect map built and shipped in Cerebro. Includes: Leaflet map with circle markers sized by contact count and colored by opportunity stage, interactive legend (click/alt+click for single/multi-select), filter pills (type, stage, team, rep), detail panel integration (layout-level slide-in), JSON toggle with syntax highlighting, ECharts sparkline cards with hover tooltips, dark-styled Leaflet tooltips. All acceptance criteria exceeded — this went well beyond a spike into a full feature.
<!-- SECTION:FINAL_SUMMARY:END -->
