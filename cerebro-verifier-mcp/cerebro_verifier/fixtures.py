"""Fixture management — bless, load, compare golden fixtures."""

import json
from datetime import datetime
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def list_fixtures() -> list[dict]:
    """List all blessed fixtures with provenance."""
    results = []
    if not FIXTURES_DIR.exists():
        return results

    for d in sorted(FIXTURES_DIR.iterdir()):
        if not d.is_dir():
            continue
        prov_path = d / "provenance.json"
        if prov_path.exists():
            with open(prov_path) as f:
                prov = json.load(f)
            results.append({"name": d.name, "provenance": prov})
        else:
            results.append({"name": d.name, "provenance": None})

    return results


def load_fixture(name: str) -> dict | None:
    """Load a fixture set by name. Returns all tables + provenance."""
    fixture_dir = FIXTURES_DIR / name
    if not fixture_dir.exists():
        return None

    result: dict = {"name": name}

    prov_path = fixture_dir / "provenance.json"
    if prov_path.exists():
        with open(prov_path) as f:
            result["provenance"] = json.load(f)

    for table_file in fixture_dir.glob("*.json"):
        if table_file.name == "provenance.json":
            continue
        table_name = table_file.stem
        with open(table_file) as f:
            result[table_name] = json.load(f)

    return result


def bless_fixture(name: str, period: str, source: str = "sage_gold") -> dict:
    """Bless current sage_gold data as a golden fixture for a closed period."""
    from . import ground_truth

    fixture_dir = FIXTURES_DIR / name
    fixture_dir.mkdir(parents=True, exist_ok=True)

    # Query live data for this period
    pnl = ground_truth.query(
        "SELECT * FROM sage_gold.entity_pnl WHERE period = %s ORDER BY entity", [period]
    )
    gl = ground_truth.query(
        "SELECT * FROM sage_gold.gl_summary WHERE period = %s ORDER BY entity, account_no", [period]
    )
    ap = ground_truth.query("SELECT * FROM sage_gold.ap_aging ORDER BY entity, vendor_name")

    # Write table files
    for table_name, rows in [("entity_pnl", pnl), ("gl_summary", gl), ("ap_aging", ap)]:
        with open(fixture_dir / f"{table_name}.json", "w") as f:
            json.dump(rows, f, indent=2, default=str)

    # Write provenance
    provenance = {
        "blessed_at": datetime.now().isoformat(),
        "period": period,
        "source": source,
        "row_counts": {
            "entity_pnl": len(pnl),
            "gl_summary": len(gl),
            "ap_aging": len(ap),
        },
    }
    with open(fixture_dir / "provenance.json", "w") as f:
        json.dump(provenance, f, indent=2)

    return {"name": name, "provenance": provenance}


def compare_fixture_to_live(name: str) -> dict:
    """Compare a fixture against live sage_gold data."""
    fixture = load_fixture(name)
    if not fixture:
        return {"error": f"Fixture '{name}' not found"}

    from . import ground_truth

    period = fixture.get("provenance", {}).get("period", "")
    results = {"name": name, "period": period, "tables": {}}

    # Compare entity_pnl
    if "entity_pnl" in fixture:
        live = ground_truth.query(
            "SELECT * FROM sage_gold.entity_pnl WHERE period = %s ORDER BY entity", [period]
        )
        results["tables"]["entity_pnl"] = _compare_rows(
            fixture["entity_pnl"],
            live,
            key_cols=["entity", "period"],
            value_cols=["revenue", "cogs", "gross_profit", "operating_expenses", "net_income"],
        )

    return results


def _compare_rows(
    fixture_rows: list[dict],
    live_rows: list[dict],
    key_cols: list[str],
    value_cols: list[str],
    tolerance: float = 0.01,
) -> dict:
    """Compare fixture rows against live rows."""
    live_index = {}
    for row in live_rows:
        k = tuple(str(row.get(c, "")).lower() for c in key_cols)
        live_index[k] = row

    passed = 0
    failed = 0
    diffs = []

    for frow in fixture_rows:
        k = tuple(str(frow.get(c, "")).lower() for c in key_cols)
        lrow = live_index.get(k)

        if lrow is None:
            failed += 1
            diffs.append({"key": dict(zip(key_cols, k)), "issue": "missing_in_live"})
            continue

        row_ok = True
        for col in value_cols:
            fval = frow.get(col)
            lval = lrow.get(col)
            if fval is None and lval is None:
                continue
            if fval is None or lval is None:
                row_ok = False
                diffs.append({
                    "key": dict(zip(key_cols, k)),
                    "column": col,
                    "fixture": fval,
                    "live": lval,
                })
                continue
            if abs(float(fval) - float(lval)) > tolerance:
                row_ok = False
                diffs.append({
                    "key": dict(zip(key_cols, k)),
                    "column": col,
                    "fixture": float(fval),
                    "live": float(lval),
                    "delta": abs(float(fval) - float(lval)),
                })

        if row_ok:
            passed += 1
        else:
            failed += 1

    return {"passed": passed, "failed": failed, "diffs": diffs[:20]}
