# Vendor Systems

15 systems across Greenmark's operations. Grouped by priority tier from the 2+2+2 integration strategy.

## P1 — Core (first to connect)

### Sage Intacct
- **What:** Cloud accounting / ERP. The system of record.
- **Correct spelling:** Sage Intacct (capital I, double-t)
- **Abbreviation:** "Sage"
- **Owner:** Alex Kaye (CFO)
- **Key detail:** Other systems should flow through Sage where possible, not directly into the warehouse. Expensify already does. Comerica does not (yet).
- **API:** XML Web Services, function-based (readByQuery, create, etc.)

### Navusoft
- **What:** Waste operations management. Routes, customers, billing, dispatch.
- **Correct spelling:** Navusoft (not "Navisoft", not "Nav-u-soft")
- **Owner:** Michael D. Nguyen (President)
- **Key detail:** Hometown (Indiana) is transitioning from WAM to Navusoft "over the next couple months." NTX already uses Navusoft.
- **API:** In development per vendor. Documentation is sparse.

### HubSpot
- **What:** CRM. Customers, prospects, deals, pipeline.
- **Correct spelling:** HubSpot (capital H, capital S, one word)
- **Owner:** Alex Kaye / Michael D. Nguyen
- **Key detail:** Second data source after Sage. Sales team uses it daily.
- **API:** REST, OAuth 2.0, well-documented. Best public API docs of any Greenmark vendor.

## P2 — Operational

### Fleetio
- **What:** Fleet management. Vehicles, maintenance, inspections, fuel.
- **Correct spelling:** Fleetio (not "Fleet IO" or "fleet.io")
- **Owner:** Robert Heath (General Manager)
- **API:** REST, well-documented developer portal.

### Paylocity
- **What:** HR and payroll.
- **Correct spelling:** Paylocity (not "Pay Locity")
- **Owner:** Alex Kaye
- **API:** Enterprise-tier, may need paid access for full docs.

### 3rd Eye
- **What:** Camera and telematics system on trucks.
- **Correct spelling:** 3rd Eye (not "Third Eye" in system context, though speech may say it)
- **Owner:** Michael D. Nguyen
- **Key detail:** Complete unknown from API perspective. Michael: "I don't know how that was built."
- **API:** Unknown. No public documentation found.

### WAM
- **What:** Legacy operations system used by Hometown (Indiana).
- **Correct spelling:** WAM (all caps)
- **Owner:** Michael D. Nguyen
- **Key detail:** Michael: "That thing's still living in the 80s. It's like a DOS interface. You're pressing the F keys a lot." Hometown transitioning to Navusoft — WAM integration may not be needed.
- **API:** Confirmed no API exists.

## P3 — Supporting

### Expensify
- **What:** Expense management.
- **Key detail:** Already flows through Sage. No separate connector needed.

### Comerica
- **What:** Banking.
- **Key detail:** Does NOT flow through Sage yet. Decision tabled — Alex leaning toward flowing through Sage.

### AssureHire
- **What:** Background checks and hiring compliance.

### Samba Safety
- **What:** Driver safety and compliance monitoring.

### Wrike
- **What:** Project management. Daniel's experience: "People don't update it. The tool itself became the thing we were managing."

### Egnyte
- **What:** File storage and collaboration.

### Vested Network
- **What:** Telecom / phone system.

### LB Technologies
- **What:** IT managed service provider for Greenmark.
