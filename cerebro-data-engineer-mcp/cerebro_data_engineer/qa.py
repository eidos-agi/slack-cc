"""Data QA — quality checks across the medallion pipeline.

Each check is a function that returns a QAResult.
The data engineer runs these proactively and on-demand.
"""

from dataclasses import dataclass
from .db import query_entity_pnl, query_gl_summary, query_ap_aging, check_table_accessible
from .topology import KNOWN_PARITY, ALL_SYSTEMS


@dataclass
class QAResult:
    check: str
    status: str  # "pass", "fail", "warn", "skip"
    detail: str
    severity: str = "info"  # "info", "warning", "critical"


def check_parity(period: str = "2025-12") -> list[QAResult]:
    """Compare entity_pnl against known-good values from Alex's spreadsheet."""
    results = []
    known = KNOWN_PARITY.get(period, {})
    if not known:
        return [QAResult("parity", "skip", f"No known parity data for period {period}")]

    try:
        rows = query_entity_pnl(period=period)
    except RuntimeError as e:
        return [QAResult("parity", "fail", f"Cannot query entity_pnl: {e}", "critical")]

    row_map = {r["entity"]: r for r in rows}

    for entity, expected in known.items():
        actual_row = row_map.get(entity)
        if not actual_row:
            results.append(QAResult("parity", "fail", f"{entity} {period}: no data in entity_pnl", "critical"))
            continue

        actual_rev = actual_row["revenue"]
        expected_rev = expected["revenue"]
        diff = abs(actual_rev - expected_rev)

        if diff < 0.01:
            results.append(QAResult("parity", "pass", f"{entity} {period}: ${actual_rev:,.2f} matches (diff ${diff:.2f})"))
        elif diff < expected_rev * 0.01:
            results.append(QAResult("parity", "warn", f"{entity} {period}: ${actual_rev:,.2f} vs expected ${expected_rev:,.2f} (diff ${diff:.2f}, <1%)", "warning"))
        else:
            results.append(QAResult("parity", "fail", f"{entity} {period}: ${actual_rev:,.2f} vs expected ${expected_rev:,.2f} (diff ${diff:.2f})", "critical"))

    return results


def check_freshness() -> list[QAResult]:
    """Check how fresh the gold data is — are recent periods populated?"""
    results = []
    try:
        rows = query_entity_pnl()
    except RuntimeError as e:
        return [QAResult("freshness", "fail", f"Cannot query entity_pnl: {e}", "critical")]

    if not rows:
        return [QAResult("freshness", "fail", "entity_pnl is EMPTY", "critical")]

    # Find most recent period with meaningful revenue (>$1K)
    revenue_periods = [r for r in rows if r["revenue"] > 1000]
    if not revenue_periods:
        results.append(QAResult("freshness", "fail", "No periods with revenue > $1K", "critical"))
        return results

    latest = revenue_periods[0]  # already ordered desc
    results.append(QAResult(
        "freshness", "pass",
        f"Latest meaningful period: {latest['period']} {latest['entity']} (${latest['revenue']:,.2f})"
    ))

    # Check if we have both entities in the latest period
    latest_period = latest["period"]
    entities_in_latest = [r["entity"] for r in rows if r["period"] == latest_period and r["revenue"] > 1000]
    if len(entities_in_latest) < 2:
        results.append(QAResult(
            "freshness", "warn",
            f"Only {entities_in_latest} have revenue in {latest_period} — expected both hometown and ntx",
            "warning"
        ))

    return results


def check_table_health() -> list[QAResult]:
    """Check that all expected gold tables are accessible and non-empty."""
    results = []
    gold_tables = [
        ("entity_pnl", "sage_gold"),
        ("gl_summary", "sage_gold"),
        ("ap_aging", "sage_gold"),
    ]
    for table, schema in gold_tables:
        status = check_table_accessible(table, schema)
        if not status["accessible"]:
            results.append(QAResult("table_health", "fail", f"{schema}.{table}: {status['error']}", "critical"))
        elif not status["has_data"]:
            results.append(QAResult("table_health", "warn", f"{schema}.{table}: accessible but EMPTY", "warning"))
        else:
            results.append(QAResult("table_health", "pass", f"{schema}.{table}: accessible, has data"))

    return results


def check_vendor_connectivity() -> list[QAResult]:
    """Report which vendor systems are connected vs pending."""
    results = []
    for system in ALL_SYSTEMS:
        if system.status == "connected":
            results.append(QAResult("vendor", "pass", f"{system.name}: {system.status} ({system.category})"))
        elif system.status == "deprioritized":
            results.append(QAResult("vendor", "skip", f"{system.name}: {system.status} — {system.notes[:80]}"))
        else:
            results.append(QAResult("vendor", "warn", f"{system.name}: {system.status} — {system.notes[:80]}", "warning"))

    return results


def run_full_qa() -> list[QAResult]:
    """Run all QA checks and return combined results."""
    results = []
    results.extend(check_parity())
    results.extend(check_freshness())
    results.extend(check_table_health())
    results.extend(check_vendor_connectivity())
    return results
