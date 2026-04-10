---
id: DOC-0004
title: VALIDATION — Excel Workbook as Golden Oracle
created: '2026-04-10'
tags:
  - validation
  - golden-fixtures
  - refactor-forge
  - sage
---
# Excel Workbook as Golden Oracle

**Purpose:** Codify how the cerebro-warp-speed-excel workbook becomes the validation oracle for the Postgres Sage pipeline. This is the refactor-forge discipline (golden fixtures prove behavioral parity) applied to a pipeline rebuild instead of a language port.

## Why This Matters

Without this, "Sage is working" is a feeling — the operator looks at the dashboard, sees reasonable-looking numbers, and declares victory. That is demo-grade work. With this, "Sage is working" is a proof — every gold metric in Postgres has been compared to its Excel counterpart and matches to 2 decimal places. That is production-grade work.

The grade boundary essay makes this argument at length: software that has been actively disbelieved is categorically different from software that hasn't. Excel is the disbeliever for Sage. Its numbers were proven to the penny against Alex's expectations, across 2.5M rows of real data, signed off by the CFO on 2026-04-06. The Postgres pipeline is the challenger. If it cannot match the oracle, it is wrong — not "different," not "close enough," wrong.

## The Discipline

### Step 1: Extract Golden Fixtures from Excel

warp-speed already has a SPA export step that writes gold tables as JSON. Reuse it.

```
cerebro-warp-speed-excel/spa/export.py
  → outputs gold_{table}.json for every gold_ table in cerebro.db
```

Copy the relevant fixtures into a stable location:
```
cerebro-migrations/validation/fixtures/sage/
├── gold_chart_of_accounts.json
├── gold_gl_summary.json
├── gold_entity_pnl.json
├── gold_ap_aging.json
├── gold_ar_aging.json
├── gold_vendor_summary.json
└── gold_customer_summary.json
```

These fixtures are **immutable snapshots of proven reality**. They represent what the workbook computed from the 2.5M rows extracted on 2026-04-02. They do not get regenerated casually. They get regenerated only when the underlying Excel metrics change AND Alex re-validates them.

### Step 2: Write the Validation Script

**Location:** `cerebro-migrations/validation/sage_excel_parity.py`

**Contract:**
- Connects to staging Supabase
- Connects to the warp-speed SQLite (or reads the JSON fixtures)
- For each gold metric, runs the equivalent query on both sides
- Normalizes any platform differences (nothing substantive — just formatting)
- Compares cell-by-cell to 2 decimal places
- Prints a diff report for any mismatches
- Exits non-zero if ANY mismatch exists

**Example query pair:**

```python
# Oracle (from Excel/SQLite)
oracle_revenue = sqlite_conn.execute("""
    SELECT entity, period, SUM(revenue) as revenue
    FROM gold_entity_pnl
    WHERE period >= '2026-01-01'
    GROUP BY entity, period
    ORDER BY entity, period
""").fetchall()

# Challenger (from Postgres)
challenger_revenue = postgres_conn.execute("""
    SELECT entity_id, period, SUM(revenue) as revenue
    FROM gold.sage_revenue_by_period
    WHERE period >= '2026-01-01'
    GROUP BY entity_id, period
    ORDER BY entity_id, period
""").fetchall()

# Compare
for (o, c) in zip(oracle_revenue, challenger_revenue):
    assert o.entity == c.entity_id, f"Entity mismatch: {o.entity} vs {c.entity_id}"
    assert o.period == c.period, f"Period mismatch: {o.period} vs {c.period}"
    assert round(o.revenue, 2) == round(c.revenue, 2), f"Revenue mismatch for {o.entity} {o.period}: {o.revenue} vs {c.revenue}"
```

### Step 3: Normalization Rules

Some differences between Excel/SQLite and Postgres are platform, not behavior. Normalize these before comparison:

- **Date formats:** Excel stores `'2026-01-01'`, Postgres may return `datetime.date(2026, 1, 1)`. Normalize to ISO string for comparison.
- **Numeric precision:** Round both sides to 2 decimal places before equality check. Don't use `==` on floats.
- **NULL vs empty string:** If Excel has `''` and Postgres has `NULL` for the same field, normalize both to `None`.
- **Ordering:** Sort both result sets by the same keys before comparison. Do not depend on natural SQL order.

What NOT to normalize:
- **Row count differences** — if Excel has 124 P&L rows and Postgres has 120, that's a bug, not a platform difference.
- **Numeric deltas beyond rounding** — if Excel says $487,200 and Postgres says $487,201.50, that's a bug, not drift.
- **Missing entities or periods** — if Excel covers Jan-Dec 2026 and Postgres only covers Jan-Jun, that's a bug.

If you find yourself normalizing something substantive, stop. You have a bug in the pipeline, not in the test.

### Step 4: The Mismatch Protocol

When the script fails, the protocol is:

1. **Read the diff.** What's different? Which rows?
2. **Check the fixture first.** Is the Excel number correct? (Hint: yes. Excel was signed off by Alex.)
3. **Check the query.** Does the Postgres query replicate the Excel logic exactly? Often the difference is a filter, a join, or an aggregation that Excel does differently.
4. **Check the source data.** Do Postgres bronze tables have the same rows as warp-speed SQLite? If not, the connector is dropping data.
5. **Fix the pipeline, not the test.** The test is the oracle. The pipeline is the hypothesis.
6. **Re-run until 100% parity.**

### Step 5: Continuous Validation

Once parity is achieved, the script becomes a **permanent quality gate**:

- **After every data-daemon run**, the script runs against the latest gold tables
- **Before every migration to production**, the script runs against staging
- **Any failure blocks the merge** (wire it into the CI pipeline we just built)
- **The script is itself version-controlled** — any change to it requires a PR, because changing the validator changes what "working" means

## Why Not Just "Write More Unit Tests"

Unit tests verify that the code does what the code says it does. They do not verify that the pipeline produces correct business numbers. You can have 100% unit test coverage on a pipeline that produces wrong financial totals — the tests pass, the numbers are wrong, and no test will ever catch it because no test was written against the business truth.

Golden fixtures verify that the pipeline produces **numbers that match an external, authoritative source**. That is a categorically different kind of test. It is the difference between "this code compiles" and "this code produces what Alex signed off on." Only the second kind of test protects the trajectory.

## Relationship to refactor-forge

The refactor-forge skill captures golden fixtures from an original implementation and replays them against a port in a different language. It proves behavioral parity at the tool-call level.

This validation discipline does the same thing at the pipeline level:
- **Original:** warp-speed-excel SQLite pipeline
- **Port:** data-daemon → Postgres medallion pipeline
- **Fixtures:** gold table JSON exports from the original
- **Replay:** query the port, compare to fixtures
- **Pass condition:** 100% match to 2 decimal places

Same discipline. Different layer. Same grade-boundary argument — a port without golden fixture validation is demo-grade by default.

## When to Deprecate the Oracle

The Excel workbook becomes the oracle for the first pipeline rebuild. Once the Postgres pipeline has run in production for 30+ days without a validation failure AND Alex has independently reviewed 3 consecutive weekly reports generated from Postgres (not from Excel) without flagging a number, Postgres becomes the new authoritative source.

At that point, the Excel workbook demotes from "oracle" to "archival reference." Its cron (if any) becomes a validation check, not a production feed. It stops being infrastructure per M-07 in the master plan.

Until that point, **Excel is the truth and Postgres is the challenger**. Not the other way around.
