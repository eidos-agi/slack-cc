# Fleetio API Deep Exploration

**Date**: 2026-04-19
**Account**: Greenmark Waste Solutions (Account ID: 397507)
**Plan**: Premium 60 Annual
**API User**: Michael Nguyen (mnguyen@greenmarkwaste.com, admin)
**Base URL**: `https://secure.fleetio.com/api/v1`

## Summary

53 working endpoints discovered across v1 and v2. The API covers fleet vehicles, maintenance (work orders, service entries, inspections), parts/inventory, contacts/drivers, fuel tracking, tire management, and GPS location entries. No telematics, geofencing, GPS streaming, compliance/DOT, reports, or analytics endpoints are exposed via API.

---

## All Working Endpoints (v1)

### Core Fleet Data

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/vehicles` | 106 | cursor | Fleet vehicles (same data as `/assets`) |
| `/assets` | 53 | page-offset | Vehicles with full specs, meter values, group, status, labels |
| `/contacts` | 29 | page-offset | Drivers, operators, technicians, employees |
| `/groups` | 6 | cursor | Organizational groups (Dallas, Memphis, etc.) |
| `/vehicle_assignments` | 40 | cursor | Driver-to-vehicle assignments with date ranges |
| `/labels` | 217+ | cursor | Tags applied to vehicles, WOs, etc. |

### Maintenance & Service

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/work_orders` | 827 | page-offset | Full work orders with line items, meter entries, VMRS codes, costs |
| `/service_entries` | 855 | page-offset | Completed service records |
| `/service_tasks` | 600+ | cursor | Individual service task definitions (PMA, oil change, etc.) |
| `/service_reminders` | 75 | page-offset | Scheduled service reminders with meter/time thresholds |
| `/issues` | 755 | page-offset | Reported vehicle issues/defects |
| `/faults` | 0 | cursor | Diagnostic fault codes (none currently) |
| `/fault_rules` | 0 | cursor | Fault code rules (none currently) |

### Inspections

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/inspection_forms` | 2 | page-offset | DVIR and Pre-Trip inspection form definitions |
| `/submitted_inspection_forms` | 600+ | cursor | Completed inspection submissions |
| `/inspection_schedules` | 365+ | cursor | Vehicle-to-form schedules with recurrence rules |

### Fuel & Meters

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/fuel_entries` | 600+ | cursor | Fuel purchase records with volume, cost, vendor |
| `/meter_entries` | 600+ | cursor | Odometer/hour meter readings |
| `/fuel_types` | 24 | cursor | Fuel type definitions (Gasoline, Diesel, CNG, etc.) |

### Parts & Inventory

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/parts` | 304+ | cursor | Parts catalog with quantities, costs, locations |
| `/purchase_orders` | 219+ | cursor | POs for parts procurement |
| `/inventory_journal_entries` | 493+ | cursor | Stock movement audit trail |
| `/part_locations` | 6 | cursor | Inventory storage locations (Dallas, Memphis, Tire bay) |
| `/part_categories` | 11 | page-offset | Part classification (Filters, Belts, Fluids, etc.) |
| `/part_manufacturers` | 7 | array | Manufacturer definitions (Mack, Eaton, Fleetguard, etc.) |

### Expenses & Costs

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/expense_entries` | 70 | cursor | Non-maintenance vehicle expenses |
| `/expense_entry_types` | 36 | cursor | Expense categories (Tires, Tolls, Fines, Insurance, etc.) |

### Tires

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/tires` | 202+ | cursor | Individual tire records with pressure, tread depth, health status |
| `/axle_configs` | 92 | cursor | Vehicle axle configurations with tire positions |

### Vehicles: Types, Statuses, Renewals

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/vehicle_types` | 42 | cursor | Vehicle classifications (Front Loader, Roll Off, etc.) |
| `/vehicle_statuses` | 10 | cursor | Status definitions (Active, Out of Service, etc.) |
| `/vehicle_renewal_reminders` | 120 | cursor | Registration, insurance, inspection renewal tracking |
| `/vehicle_renewal_types` | 8 | cursor | Renewal categories (Registration, Insurance, Inspection, Emission Test) |

### Equipment (separate from vehicles)

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/equipment_types` | 24 | cursor | Equipment classifications (Trailer, Pump, Sprayer, etc.) |
| `/equipment_statuses` | 8 | cursor | Equipment status definitions (Active, Out-of-Service, Missing, Disposed) |

### Vendors

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/vendors` | 142 | cursor | Service providers and parts suppliers |

### Documents & Media

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/documents` | 1,021 | page-offset | Attached files (PDFs, invoices) linked to parts, expenses, etc. |
| `/images` | 31 | page-offset | Photos linked to vehicles, contacts, inspection items |

### Account & Users

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/accounts` | 2 | cursor | Account details, permissions, settings, VMRS config |
| `/users/me` | 1 | single | Current API user profile |
| `/roles` | 8 | cursor | Permission roles (Admin, Viewer, Mechanic, etc.) |

### System & Reference Data

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/vmrs_reason_for_repairs` | 59 | page-offset | VMRS repair reason codes (Preventive Maintenance, Damage, Warranty, etc.) |
| `/issue_priorities` | 10 | cursor | Issue priority levels (Critical, High, Medium, Low, No Priority) |
| `/work_order_statuses` | 6 | cursor | WO lifecycle states (Open, In Progress, Pending, Completed) |
| `/custom_fields` | 0 | cursor | Custom field definitions (none configured) |
| `/webhooks` | 0 | cursor | Webhook subscriptions (none configured) |

### Administrative

| Endpoint | Records | Pagination | Description |
|----------|---------|------------|-------------|
| `/imports` | 134 | cursor | CSV import history (MeterEntryImport, etc.) |
| `/notifications` | 33 | page-offset | In-app notification feed (report exports, etc.) |
| `/contact_renewal_reminders` | 0 | cursor | Driver license/cert renewal tracking (none configured) |
| `/places` | 0 | cursor | Named geographic places (none configured) |

---

## V2 Endpoints

Seven v2 endpoints exist. They use a different pagination scheme (no `per_page` parameter; the `per_page=1` value is rejected as "out of range"). Default page size appears to be 50.

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/api/v2/contacts` | 200 | Same 29 contacts, same schema as v1 |
| `/api/v2/work_orders` | 200 | Same data, possibly different schema |
| `/api/v2/service_entries` | 200 | 50 records per page |
| `/api/v2/issues` | 200 | Same data as v1 |
| `/api/v2/inspection_forms` | 200 | Returns forms WITH embedded inspection_items (richer than v1) |
| `/api/v2/service_reminders` | 200 | Same data as v1 |
| `/api/v2/vehicle_renewal_reminders` | 200 | Same data as v1 |
| `/api/v2/comments` | 200 | Same data as v1 |

**Key v2 difference**: `/api/v2/inspection_forms` embeds full `inspection_items` array with item types, labels, instructions, dropdown options, and requirement settings. This is the richest inspection form representation.

---

## Nested Vehicle Resources

Tested on vehicle ID 4368489. These sub-resources work:

| Nested Endpoint | Description |
|----------------|-------------|
| `/vehicles/{id}/fuel_entries` | Fuel entries for this vehicle |
| `/vehicles/{id}/service_entries` | Service entries for this vehicle |
| `/vehicles/{id}/meter_entries` | Meter readings for this vehicle |
| `/vehicles/{id}/vehicle_assignments` | Driver assignments for this vehicle |
| `/vehicles/{id}/location_entries` | GPS location history for this vehicle |

All other nested resources returned 404 (work_orders, issues, documents, images, comments, faults, tires, labels, etc. are NOT available as vehicle sub-resources).

---

## Endpoints That Do NOT Exist (404)

Confirmed not available via API:

- **GPS/Telematics**: No `/telematics`, `/gps_entries`, `/gps_tracks`, `/telematics_devices`
- **Geofencing**: No `/geofences`, `/geofence_entries`
- **Compliance/DOT**: No `/compliance`, `/dot`, `/dot_inspections`
- **Reports/Analytics**: No `/reports`, `/analytics`, `/dashboards`, `/fleet_costs`, `/cost_per_mile`
- **Integrations**: No `/integrations`, `/integration_logs`
- **Users list**: No `/users` (only `/users/me`)
- **Routes/Trips**: No `/trips`, `/routes`, `/schedules`, `/dispatches`
- **Drivers**: No standalone `/drivers` endpoint (contacts with `vehicle_operator: true`)
- **Leases/Loans**: No `/vehicle_leases`, `/leases`, `/loans`
- **V2 general**: Most resources do not have v2 endpoints

---

## Endpoints That Return 403 (Forbidden)

| Endpoint | Notes |
|----------|-------|
| `/equipments` | Exists but access denied (role-gated, visible in module_access) |

---

## Endpoints That Return 500 (Server Error)

| Endpoint | Notes |
|----------|-------|
| `/settings` | Server error, may be internal-only |

---

## Key Data Relationships

```
Account
  |-- Groups (Dallas, Memphis, etc.)
  |-- Contacts (drivers, technicians, employees)
  |-- Vehicles/Assets
  |     |-- Vehicle Type, Vehicle Status
  |     |-- Fuel Entries, Meter Entries
  |     |-- Service Entries, Work Orders
  |     |-- Vehicle Assignments (-> Contact)
  |     |-- Location Entries (GPS coordinates)
  |     |-- Inspection Schedules -> Inspection Forms
  |     |-- Submitted Inspection Forms
  |     |-- Vehicle Renewal Reminders -> Vehicle Renewal Types
  |     |-- Tires -> Axle Configs
  |     |-- Labels
  |     |-- Documents, Images
  |
  |-- Work Orders
  |     |-- Work Order Line Items (inline, not separate endpoint)
  |     |-- Service Tasks
  |     |-- VMRS codes (reason for repair, system group)
  |     |-- Meter Entries (starting/ending)
  |     |-- Vendor
  |     |-- Labels, Comments, Documents, Images
  |
  |-- Parts
  |     |-- Part Categories, Part Manufacturers
  |     |-- Part Locations (inventory warehouses)
  |     |-- Inventory Journal Entries
  |
  |-- Purchase Orders
  |-- Expense Entries -> Expense Entry Types
  |-- Issues -> Issue Priorities
  |-- Vendors
```

---

## Notable Findings

### 1. Location/GPS Data IS Available
Despite no standalone GPS endpoint, `/vehicles/{id}/location_entries` returns GPS coordinates with full address resolution. Data comes from inspection form submissions. Each entry includes:
- Latitude/longitude as `POINT()` geometry
- Full address components (street, city, state, zip)
- Linked to the source event (SubmittedInspectionForm, etc.)

### 2. VMRS Coding System Active
Work orders use VMRS (Vehicle Maintenance Reporting Standards) codes:
- 59 reason-for-repair codes enabled
- System group coding enabled (Chassis, Cab, etc.)
- Assembly and component coding disabled
- Repair priority classes (Scheduled, Unscheduled, Emergency)

### 3. Rich Work Order Line Items
Work order line items are embedded in the work order response (not a separate endpoint). Each includes:
- Labor and parts cost breakdown
- VMRS reason for repair
- VMRS system group
- Sub-line items

### 4. Tire Management Module Active
202+ tire records with health monitoring:
- Tread depth tracking with health status (low, normal, etc.)
- Pressure monitoring with health status
- Linked to axle configurations and tire positions

### 5. Two Pagination Schemes
- **Cursor-based** (most endpoints): Uses `start_cursor`, `next_cursor`, `estimated_remaining_count`
- **Page-offset** (older endpoints): Uses `X-Pagination-Total-Count`, `X-Pagination-Current-Page`, `X-Pagination-Total-Pages` headers

### 6. Account Configuration
- Premium 60 Annual plan
- VMRS system group required on service line items
- Meter entry required on service entries and completed work orders
- RPC (Repair Priority Class) required
- No custom fields configured
- 3 inventory locations: Dallas (id 148454), Memphis (id 187600), Tire bay (id 209950)

### 7. Groups (Organizational Units)
6 groups total, mapping to Greenmark entities. Key groups visible: Dallas, Memphis.

---

## Data Volume Summary

| Category | Endpoint | Count |
|----------|----------|-------|
| **Vehicles** | vehicles | 106 |
| **Contacts** | contacts | 29 |
| **Work Orders** | work_orders | 827 |
| **Service Entries** | service_entries | 855 |
| **Fuel Entries** | fuel_entries | 600+ |
| **Issues** | issues | 755 |
| **Meter Entries** | meter_entries | 600+ |
| **Inspections** | submitted_inspection_forms | 600+ |
| **Parts** | parts | 304+ |
| **Purchase Orders** | purchase_orders | 219+ |
| **Tires** | tires | 202+ |
| **Labels** | labels | 217+ |
| **Vendors** | vendors | 142 |
| **Inventory Journals** | inventory_journal_entries | 493+ |
| **Vehicle Renewals** | vehicle_renewal_reminders | 120 |
| **Inspection Schedules** | inspection_schedules | 365+ |
| **Expense Entries** | expense_entries | 70 |
| **Documents** | documents | 1,021 |
| **Vehicle Assignments** | vehicle_assignments | 40 |
| **Comments** | comments | 195 |
| **Service Tasks** | service_tasks | 600+ |
| **Imports** | imports | 134 |

---

## Recommended Bronze Tables for data-daemon

Based on this exploration, the following bronze tables would capture the full Fleetio dataset:

### High Priority (core operational data)
1. `fleetio_bronze.vehicles` - 106 records
2. `fleetio_bronze.contacts` - 29 records
3. `fleetio_bronze.work_orders` - 827 records (includes line items inline)
4. `fleetio_bronze.service_entries` - 855 records
5. `fleetio_bronze.fuel_entries` - 600+ records
6. `fleetio_bronze.issues` - 755 records
7. `fleetio_bronze.meter_entries` - 600+ records
8. `fleetio_bronze.submitted_inspection_forms` - 600+ records
9. `fleetio_bronze.vehicle_assignments` - 40 records
10. `fleetio_bronze.parts` - 304+ records
11. `fleetio_bronze.purchase_orders` - 219+ records
12. `fleetio_bronze.expense_entries` - 70 records

### Medium Priority (reference/lookup data)
13. `fleetio_bronze.vendors` - 142 records
14. `fleetio_bronze.groups` - 6 records
15. `fleetio_bronze.vehicle_types` - 42 records
16. `fleetio_bronze.vehicle_statuses` - 10 records
17. `fleetio_bronze.labels` - 217+ records
18. `fleetio_bronze.service_reminders` - 75 records
19. `fleetio_bronze.vehicle_renewal_reminders` - 120 records
20. `fleetio_bronze.inspection_forms` - 2 records
21. `fleetio_bronze.service_tasks` - 600+ records
22. `fleetio_bronze.inventory_journal_entries` - 493+ records

### Lower Priority (supporting/config data)
23. `fleetio_bronze.tires` - 202+ records
24. `fleetio_bronze.axle_configs` - 92 records
25. `fleetio_bronze.inspection_schedules` - 365+ records
26. `fleetio_bronze.documents` - 1,021 records (metadata only, not file contents)
27. `fleetio_bronze.fuel_types` - 24 records
28. `fleetio_bronze.expense_entry_types` - 36 records
29. `fleetio_bronze.part_categories` - 11 records
30. `fleetio_bronze.part_locations` - 6 records
31. `fleetio_bronze.part_manufacturers` - 7 records
32. `fleetio_bronze.work_order_statuses` - 6 records
33. `fleetio_bronze.vehicle_renewal_types` - 8 records
34. `fleetio_bronze.issue_priorities` - 10 records
35. `fleetio_bronze.vmrs_reason_for_repairs` - 59 records
36. `fleetio_bronze.equipment_types` - 24 records
37. `fleetio_bronze.equipment_statuses` - 8 records
38. `fleetio_bronze.roles` - 8 records
39. `fleetio_bronze.comments` - 195 records
40. `fleetio_bronze.images` - 31 records (metadata only)
