# Fleetio API Probe Results

**Date:** 2026-04-19
**Account:** Greenmark Waste (ID: 397507)
**Plan:** Premium 60 Annual
**API User:** Michael Nguyen (mnguyen@greenmarkwaste.com)
**Base URL:** `https://secure.fleetio.com/api/v1`

## Authentication

Fleetio requires **two headers** on every request:

```
Authorization: Token {API_KEY}
Account-Token: {ACCOUNT_TOKEN}
```

- **API Key:** vaulted as `SECRET_FLEETIO_API_KEY` in Railway (cerebro-vault)
- **Account Token:** vaulted as `SECRET_FLEETIO_ACCOUNT_TOKEN` in Railway (cerebro-vault)

The API key alone returns 401. The Account Token was retrieved from the `/accounts` endpoint which only requires the API key header.

## Account Permissions

All permissions are granted (admin-level access):

| Permission | Value |
|-----------|-------|
| read_vehicles | true |
| manage_vehicles | true |
| create_vehicles | true |
| read_fuel_entries | true |
| manage_fuel_entries | true |
| read_service_entries | true |
| manage_service_entries | true |
| read_issues | true |
| manage_issues | true |
| read_work_orders | true |
| manage_work_orders | true |
| read_service_reminders | true |
| manage_service_reminders | true |
| read_vehicle_renewal_reminders | true |
| manage_vehicle_renewal_reminders | true |
| read_comments | true |
| manage_comments | true |
| read_meter_entries | true |
| manage_meter_entries | true |
| read_groups | true |
| read_contacts | true |
| fleetio_manage | true |
| inspections | true |
| update_parts | true |
| update_inventory | true |

## Capability Matrix

### Core Data Endpoints (v1)

| Endpoint | Status | Est. Total | Pagination | Sample Fields |
|----------|--------|-----------|------------|---------------|
| `/vehicles` | 200 | 55 real + 48 samples = 103 | Cursor | id, name, vin, make, model, year, group_id, group_name, vehicle_type_name, vehicle_status_name, primary_meter_value, ownership, fuel_type_name, custom_fields, driver, labels |
| `/contacts` | 200 | 29 | Array (no cursor) | id, name, first_name, last_name, email, group_id, group_name, technician, vehicle_operator, employee, employee_number, license_number, license_class, job_title, birth_date |
| `/work_orders` | 200 | ~827 | Array (page param) | id, number, vehicle_id, vehicle_name, state, total_amount, labor_subtotal, parts_subtotal, completed_at, started_at, vendor_id, vendor_name, work_order_line_items, labels, custom_fields |
| `/service_entries` | 200 | ~855 | Array (page param) | id, vehicle_id, vehicle_name, vendor_id, vendor_name, date, total_amount, labor_subtotal, parts_subtotal, status, work_order_id, service_entry_line_items |
| `/fuel_entries` | 200 | ~550 | Cursor | id, vehicle_id, date, us_gallons, price_per_volume_unit, total_amount_cents, vendor_id, partial, personal, meter_entry, mpg_us, custom_fields |
| `/issues` | 200 | ~755 | Array (page param) | id, number, name, summary, description, state, vehicle_id, vehicle_name, reported_at, resolved_at, due_date, submitted_inspection_form_id, linked_work_orders, labels, custom_fields |
| `/meter_entries` | 200 | ~550 | Cursor | id, vehicle_id, value, date, category, meter_type, void, auto_voided_at, meterable_id, meterable_type |
| `/submitted_inspection_forms` | 200 | ~550 | Cursor | id, vehicle, inspection_form, submitted_at, started_at, failed_items, starting_latitude, starting_longitude, submitted_latitude, submitted_longitude, user |
| `/vehicle_assignments` | 200 | ~40 | Cursor | id, vehicle_id, contact_id, started_at, ended_at, starting_meter_entry_value, ending_meter_entry_value, current, future |
| `/expense_entries` | 200 | ~35 | Cursor | id, vehicle_id, expense_entry_type_id, expense_entry_type_name, total_amount_cents, occurred_at, notes, vendor_id, custom_fields |
| `/parts` | 200 | ~254 | Cursor | id, number, description, manufacturer_part_number, upc, unit_cost_cents, average_unit_cost_cents, part_category_id, part_manufacturer_id, measurement_unit_id |
| `/purchase_orders` | 200 | ~169 | Cursor | id, number, description, state, vendor_id, subtotal_cents, total_amount_cents, shipping_cents, tax_1_cents, purchased_at, approved_at, closed_at, labels |
| `/comments` | 200 | ~195 | Cursor | id, commentable_id, commentable_type, comment, user_id, author, html_content, rich_content |
| `/service_tasks` | 200 | ~550 | Cursor | id, name, description, archived_at, default_vmrs_system_group_id, default_vmrs_reason_for_repair_id |

### Reference / Lookup Endpoints (v1)

| Endpoint | Status | Total | Data |
|----------|--------|-------|------|
| `/groups` | 200 | 3 | **Dallas** (id: 1972878), **Fort Worth** (id: 1982244), **Memphis** (id: 2273962) |
| `/vehicle_types` | 200 | 21 | Rear Loader (22), Roll Off (6), Pickup Truck (6), Front Loader (3), Container Truck (3), Trailer (3), Shop (2), Portable (2), Loader (2), etc. |
| `/vehicle_statuses` | 200 | 5 | Active (green), Inactive (blue), In Shop (orange), Out of Service (red), Sold (gray) |
| `/vendors` | 200 | ~121 | id, name, city, contact_email, contact_phone, fuel/parts/service flags |
| `/labels` | 200 | ~167 | id, name, color, taggings_count |
| `/custom_fields` | 200 | 0 | No custom fields defined |
| `/inspection_forms` | 200 | 2 | **DVIR** (id: 355862), **PREVENTIVE MAINTENANCE INSPECTION PMA** (id: 357672) |
| `/vehicle_renewal_types` | 200 | 4 | Reference data for renewal reminders |
| `/work_order_statuses` | 200 | 3 | Open (teal), Pending (orange), Completed (olive) |
| `/expense_entry_types` | 200 | 18 | Expense categories |
| `/part_locations` | 200 | 3 | **Dallas** (id: 148454), **Tire bay** (id: 209950), **Memphis** (id: 187600) |
| `/part_categories` | 200 | 11 | Part classification |
| `/part_manufacturers` | 200 | 7 | Part manufacturer reference |
| `/measurement_units` | 200 | 8 | Unit of measure reference |
| `/contact_renewal_types` | 200 | 2 | Contact renewal categories |
| `/service_reminders` | 200 | 75 | Active service reminder rules |
| `/vehicle_renewal_reminders` | 200 | ~55 | Vehicle renewal tracking |
| `/contact_renewal_reminders` | 200 | 0 | None configured |
| `/inventory_journal_entries` | 200 | ~443 | Parts inventory transactions |
| `/webhooks` | 200 | 0 | No webhooks configured |
| `/faults` | 200 | 0 | No telematics faults |
| `/fault_rules` | 200 | 0 | No fault rules configured |

### Endpoints Not Available (v1)

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/locations` | 404 | Not a valid endpoint |
| `/users` | 404 | Use `/users/me` instead |
| `/inventory` | 404 | Use `/inventory_journal_entries` |
| `/tire_entries` | 404 | Not available on this plan |
| `/purchase_order_statuses` | 404 | Not a separate endpoint |

### v2 Endpoints Tested

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/api/v2/contacts` | 200 | Available |
| `/api/v2/work_orders` | 200 | Available |
| `/api/v2/service_entries` | 200 | Available |
| `/api/v2/vehicles` | 404 | Not available in v2 |
| `/api/v2/fuel_entries` | 404 | Not available in v2 |
| `/api/v2/parts` | 404 | Not available in v2 |

## Entity Mapping Discovery

Groups map to geographic locations, **not** to NTX/Hometown entity names as originally hypothesized:

| Group | Fleetio ID | Vehicle Count | Entity Mapping |
|-------|-----------|---------------|----------------|
| Dallas | 1972878 | ~18 | NTX |
| Fort Worth | 1982244 | 0 | NTX |
| Memphis | 2273962 | ~33 | Hometown (Indiana) or Memphis entity |

**Key finding:** The entity mapping is `Dallas + Fort Worth = NTX`, `Memphis = Hometown/Memphis`. This needs validation with Robert Heath -- Memphis might map to the nascent Memphis entity rather than Hometown (Indiana).

**Note:** 2 vehicles have no group assigned (null group_id).

## Data Volume Summary

| Resource | Count | Notes |
|----------|-------|-------|
| Vehicles | 55 real + 48 sample | ~103 total, 55 operational |
| Work Orders | ~827 | Historical maintenance records |
| Service Entries | ~855 | Maintenance service logs |
| Issues | ~755 | Reported problems / inspection failures |
| Fuel Entries | ~550 | Fuel fill-up records |
| Meter Entries | ~550 | Odometer / hour meter readings |
| Inspections | ~550 | DVIR and PMA submissions |
| Parts | ~254 | Parts catalog |
| Purchase Orders | ~169 | Parts procurement |
| Vendors | ~121 | Service providers and fuel stations |
| Contacts | 29 | Drivers, technicians, employees |
| Vehicle Assignments | ~40 | Driver-vehicle assignment history |
| Expense Entries | ~35 | Non-maintenance expenses |
| Labels | ~167 | Tags/categories |
| Inventory Journal | ~443 | Parts inventory movements |
| Comments | ~195 | Notes on work orders, issues, etc. |
| Service Reminders | 75 | Scheduled maintenance rules |

## Schema Notes

**Work Orders** use `total_amount` (dollars as string/float), not `total_cost_cents` as documented in our research. The research doc assumed cents, but the actual API returns dollar amounts in `total_amount`, `labor_subtotal`, and `parts_subtotal` fields. Update bronze schema accordingly.

**Work Orders** use `state` field (not `status`), with values: Open, Pending, Completed.

**Vehicles** include a `driver` nested object and `specs` nested object, not just flat fields.

**Service Entries** include nested `service_entry_line_items` and `service_tasks` arrays.

**Fuel Entries** include computed fields like `mpg_us`, `cost_per_mi`, `cost_per_hr`.

**Submitted Inspection Forms** nest `vehicle`, `inspection_form`, and `user` as objects rather than flat ID fields.

## Rate Limits

Premium tier: 250 requests/minute. With ~4,700 total records across all key resources, a full initial sync would take approximately 94 pages (50 records/page or 100 records/page depending on endpoint), well within rate limits.

## Recommendations for data-daemon Connector

1. **Use v1 for all endpoints** -- v2 coverage is spotty (only contacts, work_orders, service_entries).
2. **Two auth headers required** -- store both `fleetio-api-key` and `fleetio-account-token` in vault.
3. **Mixed pagination** -- some endpoints use cursor-based (`start_cursor`/`next_cursor`), others use page-based (`page=N`). The connector must handle both.
4. **Entity derivation** -- derive entity from `group_name`: Dallas/Fort Worth = NTX, Memphis = Memphis/Hometown. Confirm mapping with Robert.
5. **Update bronze schema** -- `total_amount` is dollars not cents for work_orders; `state` not `status`; nested objects need flattening.
6. **Sample records** -- Fleetio includes demo/sample records (`is_sample: true`). Filter these in the connector or silver layer.
7. **No custom fields** -- the account has no custom fields defined, simplifying the schema.
8. **Webhooks available** -- no webhooks configured yet. Consider `work_order.completed` for real-time R&M updates.
