---
id: DOC-0002
title: ARCH — Medallion Pattern for Sage (HubSpot as Template)
created: '2026-04-10'
tags:
  - architecture
  - sage
  - hubspot
  - medallion
---
# Medallion Pattern for Sage — HubSpot as Template

**Purpose:** Technical reference for the Sage rebuild. Every decision below is "copy the HubSpot pattern, swap the columns." This is a transcription exercise, not a design exercise.

## The Three Layers

### Bronze — Raw, Entity-Tagged, Lineage-Tracked

**Schema:** `sage_bronze`

**Standard columns on every bronze table** (enforced by elt-forge patterns.py):
```sql
id              BIGSERIAL PRIMARY KEY,
source_id       TEXT NOT NULL,
source_system   TEXT NOT NULL DEFAULT 'sage_intacct',
entity          TEXT NOT NULL CHECK (entity IN ('ntx', 'hometown')),
-- vendor-specific columns derived from warp-speed SQLite schema
raw_data        JSONB,
row_hash        TEXT,
_job_id         BIGINT,
synced_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
deleted_at      TIMESTAMPTZ
```

**Partial unique index:**
```sql
CREATE UNIQUE INDEX idx_sage_{table}_source
    ON sage_bronze.{table} (source_id, entity)
    WHERE deleted_at IS NULL;
```

**Watermark index** for incremental sync:
```sql
CREATE INDEX idx_sage_{table}_watermark
    ON sage_bronze.{table} ({watermark_column})
    WHERE deleted_at IS NULL;
```

**Tables to create** (derived from warp-speed's SQLite schema, NOT the March hypothesis):
- `sage_bronze.gl_accounts` — chart of accounts (252 rows in production)
- `sage_bronze.gl_batches` — journal entry headers (~583K rows)
- `sage_bronze.gl_entries` — journal entry lines (~1.3M rows)
- `sage_bronze.ap_bills` — AP bills (~3K rows)
- `sage_bronze.ar_invoices` — AR invoices (small)
- `sage_bronze.vendors` — vendor master (~418 rows)
- `sage_bronze.customers` — customer master (small)

Each table's specific columns come from observing warp-speed's SQLite, not from a planning document.

### Silver — Cleaned, Typed, Entity-Mapped

**Schema:** `sage_silver`

**Pattern:** Materialized view per bronze table, joined with entity resolution, with NULLIF cleanup and type casting.

**Example structure** (copying HubSpot's `hubspot_silver.deals` pattern):
```sql
CREATE MATERIALIZED VIEW sage_silver.gl_entries AS
SELECT
    b.id AS bronze_id,
    b._job_id,
    b.source_id,
    NULLIF(b.entity, '') AS entity_id,
    NULLIF(b.account_no, '')::TEXT AS account_no,
    NULLIF(b.department, '')::TEXT AS department,
    NULLIF(b.location, '')::TEXT AS location,
    -- L-code → entity mapping proven by Alex Kaye 2026-04-06:
    -- L0100 (Dallas) + L0200 (Fort Worth) → NTX (via E1005)
    -- L0400 (Memphis) → Hometown (via E1008)
    CASE
        WHEN NULLIF(b.location, '') IN ('L0100', 'L0200') THEN 'ntx'
        WHEN NULLIF(b.location, '') = 'L0400' THEN 'hometown'
        ELSE b.entity
    END AS resolved_entity,
    NULLIF(b.trx_amount, '')::NUMERIC AS trx_amount,
    CASE WHEN b.tr_type = '1' THEN 1 ELSE -1 END AS debit_credit_sign,
    TO_DATE(NULLIF(b.entry_date, ''), 'MM/DD/YYYY') AS entry_date,
    -- all other fields with NULLIF + type cast
    b.synced_at,
    b.created_at
FROM sage_bronze.gl_entries b
WHERE b.deleted_at IS NULL
WITH DATA;

CREATE UNIQUE INDEX ON sage_silver.gl_entries (bronze_id);
```

**Refresh:** `REFRESH MATERIALIZED VIEW CONCURRENTLY sage_silver.gl_entries` — called by data-daemon executor after bronze load completes.

### Gold — Business Metrics, RLS-Enforced

**Schema:** `gold` (shared across all vendors, per HubSpot convention)

**Pattern:** Regular tables (not materialized views) with MERGE-based refresh functions. RLS enabled, entity-filtered. Soft deletes via `deleted_at`. The pattern is established in HubSpot's `forge.refresh_pipeline_summary()` — copy it wholesale.

**Initial gold tables** (the first batch — everything Excel already validates):

1. **`gold.sage_revenue_by_period`** — entity × LOB × month
   - Source: `sage_silver.gl_entries` filtered to revenue accounts (4xxxx)
   - Group by: `resolved_entity`, `department` (LOB proxy), `date_trunc('month', entry_date)`
   - Sum: `trx_amount * debit_credit_sign`

2. **`gold.sage_pnl_by_entity`** — full P&L rollup
   - The breakthrough Alex proved: Entity + E1001 corporate allocations = LOB totals
   - Revenue, COGS, SG&A, Operating Income per entity per month
   - Handles E1001 allocation logic (found in warp-speed's `seed_gold_sage.py`)

3. **`gold.sage_ar_aging`** — bucket by invoice age
   - Source: `sage_silver.ar_invoices`
   - Buckets: current / 30 / 60 / 90 / 90+

4. **`gold.sage_gl_balances`** — account × entity × period
   - Source: `sage_silver.gl_entries`
   - Running balance by account, entity, month

**Refresh function pattern** (copying `forge.refresh_pipeline_summary`):
```sql
CREATE OR REPLACE FUNCTION forge.refresh_sage_revenue_by_period()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, gold, sage_silver, forge, audit
AS $$
DECLARE
  v_src BIGINT;
BEGIN
  PERFORM pg_advisory_lock(forge.table_lock_key('gold.sage_revenue_by_period'));

  CREATE TEMP TABLE _stg ON COMMIT DROP AS
  SELECT
    resolved_entity AS entity_id,
    department AS lob,
    DATE_TRUNC('month', entry_date) AS period,
    SUM(trx_amount * debit_credit_sign) AS revenue,
    MAX(_job_id) AS _last_job_id
  FROM sage_silver.gl_entries
  WHERE account_no LIKE '4%'
  GROUP BY 1, 2, 3;

  SELECT COUNT(*) INTO v_src FROM _stg;
  IF v_src = 0 THEN
    RAISE EXCEPTION 'Source empty — aborting refresh';
  END IF;

  MERGE INTO gold.sage_revenue_by_period AS t
  USING _stg AS s
  ON t.entity_id = s.entity_id
     AND t.lob IS NOT DISTINCT FROM s.lob
     AND t.period = s.period
  WHEN MATCHED THEN UPDATE SET
    revenue = s.revenue,
    _last_job_id = s._last_job_id,
    _refreshed_at = NOW(),
    deleted_at = NULL
  WHEN NOT MATCHED THEN INSERT
    (entity_id, lob, period, revenue, _last_job_id)
    VALUES (s.entity_id, s.lob, s.period, s.revenue, s._last_job_id);

  -- Soft-delete rows no longer in source
  UPDATE gold.sage_revenue_by_period SET deleted_at = NOW()
  WHERE deleted_at IS NULL AND NOT EXISTS (
    SELECT 1 FROM _stg s
    WHERE s.entity_id = sage_revenue_by_period.entity_id
      AND s.lob IS NOT DISTINCT FROM sage_revenue_by_period.lob
      AND s.period = sage_revenue_by_period.period
  );

  PERFORM pg_advisory_unlock(forge.table_lock_key('gold.sage_revenue_by_period'));
END;
$$;

GRANT EXECUTE ON FUNCTION forge.refresh_sage_revenue_by_period() TO svc_etl_runner;
```

## Entity Mapping (Proven)

From memory file `project_sage_dimensionality_proven.md`, confirmed by Alex Kaye on 2026-04-06:

- **Revenue:** 100% in L-codes (2026)
- **Costs:** 72% in L-codes, 28% corporate on E-codes (2026)
- **L0100** = Dallas (NTX)
- **L0200** = Fort Worth (NTX)
- **L0400** = Memphis (Hometown)
- **E1001** = Corporate parent (allocations flow from here)
- **E1005** = NTX entity
- **E1008** = Hometown entity
- **BASELOCATION** is unreliable per Alex — do NOT use it
- **2025 Q4** has dimension cleanup noise; Jan 2026 forward is clean
- **GL Account (4/5/6) + Department + Location = full P&L dimensionality**. No dimension tables needed.

## Connector Implementation

**File:** `data-daemon/src/connectors/sage_intacct_connector.py`

**Pattern:** Inherit from `BaseConnector`. Copy structure from `hubspot_connector.py`. Swap REST logic for XML Web Services logic (copied from warp-speed's proven `pipeline/downloaders/sage-intacct.py`).

**Key methods:**
- `test_connection()` → `get_session()` from Sage, return True on success
- `extract(watermark)` → XML `readByQuery` for the table's object, paginate via `readMore`, return `ExtractionResult(rows, watermark_value)`
- `get_row_count()` → XML `query` with count-only, return the total

**Session management:** Single session per extract job, re-authenticate on 401/timeout. Session lifetime ~6 hours, no issue at current scale.

**Pagination:** `readByQuery` returns 1000 rows + `resultId`, `readMore(resultId)` continues. `totalcount` field available for progress tracking.

**Rate limiting:** 100ms delay between requests. No throttling observed at 2.5M record scale.

**Entity resolution:** Rows land in bronze with `entity` column populated via service.yaml default. Silver layer does the L-code → entity mapping.

## What NOT To Do

- **Do not extend elt-forge to generate data-daemon connectors.** It's one connector. Hand-write it following HubSpot's pattern. The elt-forge extension is a 3-day meta-project that delays shipping for no benefit at single-vendor scale.
- **Do not trust the existing `sage_bronze` migration** in `cerebro-migrations` dated March. It was a hand-written hypothesis before the API was observed. Delete and replace.
- **Do not reference the stale `infra/vendors/sage-intacct/connection-spec.yaml`.** It gets archived in M-01 for exactly this reason.
- **Do not build gold metrics that Excel hasn't validated.** Every gold table must have an Excel cell as its oracle. No aspirational metrics in this pass.
