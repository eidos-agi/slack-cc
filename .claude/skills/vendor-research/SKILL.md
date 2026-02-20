---
name: vendor-research
description: "Research a vendor system's API and data model, then produce a structured api-data-model.md document in the infra repo. Use when a new vendor needs deep research, when credentials arrive and existing research needs validation, or when updating a vendor's integration spec. Triggers: '/vendor-research <vendor-name>', 'research the <vendor> API', 'deep dive on <vendor>', 'what data can we get from <vendor>'. The skill produces the same A-H section format used by all 6 existing vendor docs."
---

# Vendor Research — API & Data Model Documentation

Research a vendor system's API capabilities and produce a structured `api-data-model.md` document. For most vendors, this gives engineers everything they need to build a connector. For vendors whose data flows through another system (like Expensify → Sage), it documents the API for reference and records the integration decision. The output follows the proven 8-section format (A-H) used across all Greenmark vendor integrations.

## Why this exists

Greenmark integrates 15 vendor systems. Six have been deeply researched (Sage Intacct, HubSpot, Navusoft, Fleetio, Paylocity, WAM). Nine remain. Each deep research doc takes 2-4 hours to produce well. This skill codifies the process so every vendor gets the same depth, follows the same conventions, and fills the same gaps — whether Daniel writes it or an AI agent does.

The output feeds directly into data-daemon connector development: YAML service definitions reference the API overview (Section A), bronze schema DDL comes from Section D, and sync strategy (Section E) configures the scheduler.

## When to use

| Trigger | What happens |
|---------|-------------|
| `/vendor-research sage-intacct` | Full research run on a vendor (or update existing) |
| `/vendor-research hubspot --validate` | Credentials arrived — validate existing research against real API |
| `/vendor-research 3rd-eye` | Research a vendor with no prior deep doc |
| `/vendor-research --status` | Show which vendors have deep research and which don't |

## Inputs

Required:
- **Vendor name** — must match a directory or `.md` file in `infra/vendors/`

Optional:
- `--validate` — credentials available, validate existing research against live API
- `--update` — update an existing `api-data-model.md` with new findings
- `--status` — skip research, just report which vendors have deep docs and which don't

## Workflow

### 0. Load context (always)

Before researching, load these files:
```
infra/CLAUDE.md                          — repo rules and conventions
infra/conventions.md                     — 8 conventions that govern all vendor docs
infra/vendors/<vendor>.md                — existing summary file (has priority, dependencies, entity, checklist)
infra/vendors/<vendor>/api-data-model.md — existing deep doc (if any)
infra/vendor-status.md                   — at-a-glance status of all 15 vendors
infra/database/README.md                 — warehouse architecture and schema conventions
```

Also load one exemplar for reference. Choose based on API type:
- REST API vendor → load `hubspot/api-data-model.md` (cleanest REST example)
- XML/SOAP vendor → load `sage-intacct/api-data-model.md`
- No API / legacy → load `wam/api-data-model.md` (documents inferred data model from industry patterns)

### 1. Assess what we know

Check the vendor's current state:

| State | Action |
|-------|--------|
| No summary file exists | Stop. Create the summary `.md` first (see Section "Creating a summary file") |
| Summary file exists, no subdirectory | This is a new deep research — proceed to Step 2 |
| Subdirectory + `api-data-model.md` exists | This is an update or validation — load existing doc, proceed to Step 2 with delta focus |

**Also check for a resolution path early.** Before deep-diving into API docs, search meeting READMEs and the glossary for integration decisions about this vendor. Some vendors resolve as "flows through another system" — meaning their data reaches the warehouse via an existing connector, not a direct one. Signs:

- Meeting notes say "X already flows through Sage" or "no separate connector needed"
- The summary file says "may be covered by Sage bank feeds" or similar
- The vendor is P3 with a dependency on a P1 system that already has a connector

**If the vendor resolves as "flows through another system":** Still produce the full api-data-model.md (the API research is valuable documentation), but frame it as reference material, not a connector spec. See "Resolution paths" below for how this changes Sections D-F and H.

### 2. Research the API

**Research sources, in priority order:**

1. **Official API documentation** — the vendor's developer portal. This is the primary source.
2. **API reference / OpenAPI spec** — if the vendor publishes a swagger/OpenAPI spec, download and parse it.
3. **Community SDKs** — Python/Node SDKs often reveal undocumented behavior (auth patterns, pagination quirks, rate limits).
4. **Meeting transcripts** — search `meetings/*/README.md` for mentions of the vendor. Stakeholders often reveal what data they use and how.
5. **Existing synthetic data** — check `data-daemon/fixtures/generators/` for what we already model. The synthetic generator shows what fields we think exist.
6. **Industry patterns** — for vendors with no public API docs (like WAM), infer data models from industry-standard waste management software patterns.

**What to capture for each API endpoint/object:**

| Field | Required? | Notes |
|-------|-----------|-------|
| Object name (vendor's term) | Yes | e.g., `GLACCOUNT`, `Companies`, `work_orders` |
| API endpoint | Yes (if API exists) | e.g., `/crm/v3/objects/companies` |
| HTTP method | Yes | GET for reads, POST for batch |
| Authentication | Yes | Bearer, OAuth, API key, session-based, etc. |
| Pagination | Yes | Cursor, offset, page-based, readMore |
| Rate limits | Yes | Per-second, per-minute, daily caps |
| Key fields | Yes | Primary key, foreign keys, timestamps, entity identifiers |
| Estimated volume | Yes | Monthly record count for sync sizing |
| Watermark column | Yes | For incremental sync — usually `modified_date` or `updated_at` |
| Entity mapping | Yes | How NTX vs Hometown is distinguished in this system |

### 3. Produce the api-data-model.md

Write to `infra/vendors/<vendor>/api-data-model.md`. Follow these 8 sections exactly:

---

#### Section A: API Overview

Table format. Every vendor doc starts with this:

```markdown
## A. API Overview

| Field | Value |
|-------|-------|
| API Type | REST (JSON) / XML / GraphQL / None (CSV/DB) |
| API Version | v3 / v2 / Unknown |
| Base URL | `https://api.vendor.com/...` |
| Authentication | Bearer token / OAuth 2.0 / API key / Session-based / N/A |
| Rate Limits | X requests / Y seconds / Z per day |
| Pagination | Cursor / Offset / Page-based / readMore |
| Page Size | Default X, max Y |
| SDK (Python) | Package name + PyPI link, or "None found" |
| Required Scopes | List of OAuth scopes or API permissions needed |
```

**For vendors with no API** (like WAM): Replace "API" with "System" and document integration method (CSV export, direct DB access, screen scrape, manual).

#### Section B: Core Objects

Table mapping vendor objects to our warehouse:

```markdown
## B. Core Objects

| Vendor Object | API Endpoint | Our Synthetic Table | Proposed Bronze Table |
|---------------|-------------|---------------------|----------------------|
| Companies | `/crm/v3/objects/companies` | `accounts` | `vendor_bronze.companies` |
```

Follow with:
- **Object relationships** — ASCII diagram showing how objects relate (1:many, many:many, etc.)
- **Key decision** — e.g., "Use separate associations table" or "Land headers and line items in separate tables"

#### Section C: Field-Level Data Model

For each core object, list every field we care about:

```markdown
### Object: Companies

| API Field | Type | Our Column | Notes |
|-----------|------|-----------|-------|
| `id` | string | `source_id` | HubSpot internal ID |
| `properties.name` | string | `company_name` | |
| `properties.domain` | string | `domain` | Website domain |
```

**Convention:** Always include these standard columns in every table:
- `source_id` — vendor's primary key
- `source_system` — e.g., `hubspot`, `sage_intacct`
- `entity` — `ntx`, `hometown`, or `memphis`
- `raw_data` — full API response as JSONB
- `row_hash` — SHA256 of raw_data for change detection
- `synced_at` — when this row was last synced
- `created_at`, `updated_at`, `deleted_at` — audit columns (soft deletes only)

#### Section D: Proposed Bronze Schema

Full `CREATE TABLE` statements, ready to become migrations:

```sql
CREATE SCHEMA IF NOT EXISTS vendor_bronze;

CREATE TABLE vendor_bronze.companies (
    id              BIGSERIAL PRIMARY KEY,
    source_id       TEXT NOT NULL,
    source_system   TEXT NOT NULL DEFAULT 'vendor',
    entity          TEXT NOT NULL CHECK (entity IN ('ntx', 'hometown', 'memphis')),
    -- vendor-specific columns here
    raw_data        JSONB,
    row_hash        TEXT,
    synced_at       TIMESTAMPTZ DEFAULT NOW(),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    UNIQUE(source_system, source_id)
);
```

**Convention:** Schema name is always `<vendor>_bronze` (lowercase, underscores). Table names match vendor objects (lowercase, plural).

#### Section E: Sync Strategy

Table format:

```markdown
## E. Sync Strategy

| Table | Sync Mode | Watermark Column | Est. Volume | Refresh |
|-------|-----------|-----------------|-------------|---------|
| companies | full | _(small reference data)_ | ~100-200 | Daily 6am CT |
| work_orders | incremental | `modified_date` | ~800/month | Daily 6am CT |
```

Follow with sync notes:
- Why certain tables use full vs incremental sync
- Schedule rationale (6am CT = before business day)
- `row_hash` usage for idempotent upserts
- `raw_data` JSONB preservation rationale

Include a "When API Becomes Available" YAML snippet if the vendor currently uses SQLite fixtures:

```yaml
source:
  type: rest_api
  rest_api:
    base_url: "${VENDOR_API_URL}"
    auth_type: bearer_token
    token: "${VENDOR_API_TOKEN}"
    pagination:
      type: cursor  # or offset_limit, page_based
      page_size: 100
    rate_limit:
      requests_per_minute: 60
```

#### Section F: Mapping — Synthetic to Real

If we have synthetic data for this vendor (check `data-daemon/fixtures/generators/`), map every current column to the proposed real column:

```markdown
| Current Synthetic Table | Current Column | Proposed Bronze Table | Proposed Column | Notes |
|------------------------|----------------|----------------------|-----------------|-------|
| `customers` | `customer_name` | `customers` | `customer_name` | No change |
| `accounts` | `account_name` | `companies` | `company_name` | Rename to match vendor |
```

**Flag removals** — if the synthetic data has tables or columns that don't exist in the real API, mark them explicitly: "**REMOVE** — not a real vendor object."

**If no synthetic data exists:** Replace this section with "No synthetic data exists for this vendor. Generator will be created after API research is validated."

**If vendor flows through another system (cross-vendor mapping):** Replace the synthetic→real mapping with a cross-vendor mapping showing how this vendor's objects map to the intermediary system's bronze tables. Example (Expensify → Sage):

```markdown
| Expensify Object | Expensify Field | Sage Object | Sage Field | Notes |
|-----------------|-----------------|-------------|------------|-------|
| Report | `submitterEmail` | APBILL | `VENDORID` | Employee mapped to vendor |
| Expense | `category` | APBILLITEM | `GLACCOUNTNO` | GL account mapping |
```

Also document **what's preserved vs lost** in the flow-through. This determines whether a direct connector would ever be needed.

#### Section G: Gaps & Open Questions

Numbered list of unknowns that require credentials or vendor contact to resolve:

```markdown
## G. Gaps & Open Questions

1. **Entity mapping** — How does Greenmark distinguish NTX vs Hometown in this system? **Requires credentials to verify.**
2. **Custom fields** — What custom properties has Greenmark configured? **Requires credentials to verify.**
3. **API tier** — Which plan/tier is Greenmark on? Affects rate limits.
```

**Convention:** Every gap that requires credentials gets the suffix "**Requires credentials to verify.**" This makes it trivially searchable when credentials arrive.

#### Section H: Varies by Vendor

This section adapts to the vendor's specific situation:

| Situation | Section H title | Content |
|-----------|----------------|---------|
| Has synthetic data that needs renaming | "Rename Plan" | Table of current → proposed file/schema/table names |
| Has no API, needs first-day investigation | "First-Day Playbook" | Step-by-step for what to do when credentials arrive |
| Has unusual architecture | "Key Architectural Differences" | What makes this vendor different from the REST API norm |
| Is being deprecated/replaced | "Migration Plan" | Timeline and approach for transitioning away |
| **Data flows through another system** | "Flows Through [System]" | Architecture diagram, decision record (who decided, when, meeting ref), what's preserved vs lost in the flow-through, and "when to revisit" criteria |

**First-Day Playbook** is the most common for new vendors. Template:

```markdown
## H. First-Day Playbook

When credentials arrive, do these in order:

1. **Authentication test** — verify credentials work, note any MFA or IP allowlisting requirements
2. **List endpoints** — hit the API root or docs endpoint to confirm available objects
3. **Sample pull** — GET 1 page of each core object, save raw JSON to `fixtures/samples/<vendor>/`
4. **Schema validation** — compare real fields to proposed bronze tables (Section D). Note any missing/extra columns.
5. **Entity check** — find how NTX vs Hometown is distinguished (custom field, location ID, separate accounts?)
6. **Volume estimation** — count total records per object to size sync strategy
7. **Rate limit test** — hit the API at increasing rates to find the practical limit
8. **Update this doc** — fill in gaps from Section G, correct any assumptions
```

---

### 4. Update the summary file

After producing the deep doc, update `infra/vendors/<vendor>.md`:
- Check off completed items in the research checklist
- Add link to the new deep doc: `see [api-data-model.md](<vendor>/api-data-model.md)`
- Update any fields that changed (API type, authentication, rate limits, etc.)

**For resolved vendors (flows through another system):** The summary file needs a more substantial rewrite:
- Add the integration decision at the top (bold, with meeting reference and who confirmed it)
- Add a "How Data Reaches the Warehouse" section with ASCII flow diagram
- Change "Integration Priority" to note the resolution (e.g., "P3 — **Resolved: flows through Sage**")
- Add "when to revisit" criteria so future readers know when a direct connector would become necessary
- Update the API status table to add "Direct connector needed? **No**"

The resolved summary file becomes a different kind of document — it answers "why don't we connect to this?" instead of "how do we connect to this?"

### 5. Update vendor-status.md

Update `infra/vendor-status.md` to reflect the new research. Use the appropriate status:

| Resolution | Status | Example |
|-----------|--------|---------|
| Needs a connector (standard) | RESEARCHED | "Deep research complete, 10 bronze tables proposed" |
| Flows through another system | RESOLVED | "Flows through Sage — no direct connector needed" |
| Deprecated / being replaced | DEPRECATED | "Replaced by email + Teams" |
| Can't evaluate yet | BLOCKED | "No vendor contact, API status unknown" |

### 6. Quality checklist

Before presenting the doc, verify:

**All vendors (standard and resolved):**
- [ ] All 8 sections (A-H) are present
- [ ] Section A has complete API overview table
- [ ] Section B maps every core object (with relationship diagram)
- [ ] Section C has field-level detail for every core object
- [ ] Section G lists every open question, tagged with what's needed to resolve it
- [ ] Section H is appropriate for this vendor's situation
- [ ] Entity mapping (NTX/Hometown/Memphis) is addressed
- [ ] No secrets or credentials in the doc
- [ ] Stakeholder-readable (Convention 1): a non-engineer can understand overview sections

**Standard vendors (building a connector):**
- [ ] Section D has complete CREATE TABLE statements with all standard columns
- [ ] All standard columns present: source_id, source_system, entity, raw_data, row_hash, synced_at, created_at, updated_at, deleted_at
- [ ] Schema naming follows convention: `<vendor>_bronze.<table_name>`
- [ ] Section E has sync strategy for every table (mode, watermark, volume, refresh)
- [ ] Section F maps synthetic → real (or notes no synthetic data exists)

**Resolved vendors (flows through another system):**
- [ ] Section D has bronze schema marked as "for reference only, not deployed"
- [ ] Section E explains current flow (no direct sync) and documents "if direct sync were needed" as contingency
- [ ] Section F has cross-vendor mapping (this vendor → intermediary system) with "preserved vs lost" analysis
- [ ] Section H has decision record (who, when, meeting ref), architecture diagram, and "when to revisit" criteria
- [ ] Summary file includes integration decision, flow diagram, and resolved status

### 7. Present the result

Show a summary:

```
VENDOR RESEARCH COMPLETE — <Vendor Name>

Sections: A-H ✓
Core objects: N (list them)
Bronze tables: N proposed
Estimated monthly volume: ~N rows
Sync strategy: N incremental, N full refresh
Open questions: N (N require credentials)
Synthetic data: exists / doesn't exist
Next step: <what's needed to move from research to implementation>
```

---

## Validation mode (`--validate`)

When credentials arrive and the user runs `/vendor-research <vendor> --validate`:

1. Load the existing `api-data-model.md`
2. Make real API calls to verify:
   - Authentication works as documented
   - Endpoints exist and return expected objects
   - Fields match what we documented in Section C
   - Pagination works as documented
   - Rate limits are as documented
3. For each gap in Section G: attempt to resolve it with real data
4. Write a validation report at the end of the doc:

```markdown
## Validation Report — YYYY-MM-DD

Validated with real API credentials.

| Section | Status | Notes |
|---------|--------|-------|
| A. API Overview | ✓ Confirmed | Rate limits match documentation |
| B. Core Objects | ⚠ 1 change | New object `tickets` discovered |
| C. Field-Level | ⚠ 3 changes | Custom properties found: X, Y, Z |
| D. Bronze Schema | Needs update | Add `tickets` table, add custom columns |
| E. Sync Strategy | ✓ Confirmed | Volumes match estimates |
| G. Gaps Resolved | 4 of 6 | Entity mapping confirmed: uses LOCATIONID |
```

5. Apply the changes to the doc (update sections, don't just append)

---

## Status mode (`--status`)

When the user runs `/vendor-research --status`:

Scan `infra/vendors/` and report:

```
VENDOR RESEARCH STATUS — YYYY-MM-DD

Deep research complete (6):
  ✓ Sage Intacct    — 569 lines, 10 bronze tables proposed
  ✓ HubSpot         — 394 lines, 10 bronze tables proposed
  ✓ Navusoft         — 1042 lines, 14 bronze tables proposed
  ✓ Fleetio          — 517 lines, 8 bronze tables proposed
  ✓ Paylocity        — 961 lines, 8 bronze tables proposed
  ✓ WAM              — 930 lines, 15 bronze tables proposed (inferred, no API)

Resolved — no direct connector needed (1):
  ✓ Expensify        — RESOLVED: flows through Sage (3 bronze tables documented for reference)

Summary only — needs deep research (8):
  ○ 3rd Eye          — P2, BLOCKED (no API docs, no vendor contact)
  ○ LB Technologies  — P3 (GPS, likely low value)
  ○ Comerica         — P3 (may flow through Sage — could resolve like Expensify)
  ○ AssureHire       — P3 (HR background checks)
  ○ Samba Safety     — P3 (driver safety compliance)
  ○ Wrike            — DEPRECATED (replaced by email + Teams)
  ○ Egnyte           — P3 (document management)
  ○ Vested Network   — P3 (IT services, not a data source)

Total bronze tables proposed: 65 (+ 3 reference-only for Expensify)
Vendors ready for connector development: 5 (blocked on credentials)
Vendors resolved (flow through another system): 1
```

---

## Creating a summary file

If a vendor has no summary file yet (no `infra/vendors/<vendor>.md`), create one following this template:

```markdown
# <Vendor Name>

<One-line description of what the system does>. Account owner: <name>. Entity: <NTX / Hometown / Both>.

## API & Integration Status

| Field | Value |
|-------|-------|
| Has API? | Yes / No / Unknown |
| API Type | REST / XML / GraphQL / None |
| Authentication | <type> |
| Documentation | <link or "None found"> |
| Rate Limits | <value or "Unknown"> |
| Data Freshness | Real-time / Daily / Unknown |
| Sandbox/Test Environment | Yes / No / Unknown |

## Data Available

| Data Type | Description | Frequency | Est. Volume |
|-----------|-------------|-----------|-------------|

## Priority & Dependencies

- **Integration Priority:** P1/P2/P3 — <reason>
- **Depends on:** <what's needed before integration>
- **Blocks:** <what this integration unblocks>

## Research Checklist

- [ ] Obtain API credentials
- [ ] Map data models to warehouse schema
- [ ] Test sample API calls
- [ ] Build prototype connector
- [ ] Deploy connector to production

## What We Need

- [ ] <specific things needed from Greenmark team>

## Related

- **Entity context:** [entities.md](../entities.md)
```

---

## Resolution paths

Not every vendor needs a connector. Research may conclude with one of these:

| Resolution | What it means | Example |
|-----------|--------------|---------|
| **Build connector** | Standard path — research feeds directly into data-daemon YAML + migrations | Sage, HubSpot, Navusoft |
| **Flows through another system** | Data already reaches the warehouse via an existing connector. Document the API but don't build a connector. | Expensify → Sage (AP bills) |
| **Deprecated** | System is being replaced or shut down. Document for historical reference. | Wrike → email + Teams |
| **Not a data source** | System exists but doesn't produce data useful for the warehouse. | Vested Network (VoIP) |
| **Can't evaluate** | No API docs, no vendor contact, complete unknown. | 3rd Eye |

**"Flows through another system" is the most nuanced resolution.** The Expensify test case showed that these vendors still deserve deep research — the API docs, data model, and cross-vendor mapping are valuable even if we don't build a connector. The "when to revisit" criteria in Section H ensure someone knows when the resolution should be reconsidered.

---

## Key rules

- **Follow the 8-section format exactly** — every vendor doc looks the same. Engineers switching between vendors shouldn't have to learn a new layout.
- **Check for a resolution path early** — before spending hours on API docs, search meeting transcripts for integration decisions. "Flows through Sage" is a valid and valuable finding.
- **Standard columns are non-negotiable** — source_id, source_system, entity, raw_data, row_hash, synced_at, created_at, updated_at, deleted_at appear in every table.
- **Entity mapping is always addressed** — even if the answer is "this system is NTX only" or "entity is determined by account/location field X."
- **Tag unknowns for resolution** — "Requires credentials to verify" makes it scannable when credentials arrive.
- **Stakeholder-readable overview, engineer-readable detail** — Sections A-B should make sense to Michael. Sections C-D are for Daniel.
- **Synthetic → Real mapping prevents surprise rework** — if we have synthetic data, Section F tells the engineer exactly what needs to change. No guessing.
- **Cross-vendor mapping for flow-through vendors** — when data flows through another system, Section F maps this vendor's fields to the intermediary's fields, plus documents what's preserved vs lost in the flow.
- **Resolved vendors still get deep research** — the API documentation is valuable even if we don't build a connector. Future requirements may change the resolution.
- **Summary files reflect the resolution** — a resolved vendor's summary is fundamentally different from an open vendor's. It answers "why don't we connect?" not "how do we connect?"
- **No secrets** — API keys, passwords, tokens never appear in the doc. Use `${ENV_VAR}` syntax in YAML examples.
- **Convention 7 applies** — "Vendor files track what we know and what we still need." Every research gap is an explicit checklist item.
