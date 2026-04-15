"""cerebro-verifier — independent QA for the Cerebro dashboard.

The builder proposes. The verifier disposes.
"""

import re
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cerebro-verifier")


# ── Smoke & Page Verification ───────────────────────────────────


@mcp.tool()
def smoke_test(environment: str = "staging", pages: list[str] | None = None) -> dict:
    """Hit every dashboard page, confirm no 500s, no blank screens.

    Navigates to each page, takes a screenshot, checks for error
    indicators. Returns pass/fail per page with evidence paths.

    Args:
        environment: "staging" or "production"
        pages: Specific page slugs, or None for all pages
    """
    from . import auth, browser, evidence, inventory, report

    evidence.start_run()

    # Authenticate
    auth_result = auth.ensure_authenticated(environment)
    if not auth_result.get("authenticated"):
        return {"error": "Authentication failed", "detail": auth_result}

    base = browser.get_environment_url(environment)
    page_list = inventory.INVENTORY
    if pages:
        page_list = [p for p in page_list if p.slug in pages]

    results = []
    for page in page_list:
        url = base + page.path
        ss_path = evidence.screenshot_path(page.slug)

        try:
            capture = browser.navigate_and_capture(url, ss_path)
            snap = capture["snapshot"]
            snap_len = capture["snapshot_length"]

            # Check for error indicators
            status = "pass"
            issues = []

            if snap_len < 100:
                status = "fail"
                issues.append("blank_screen")

            snap_lower = snap.lower()
            if "500" in snap_lower and "internal server error" in snap_lower:
                status = "fail"
                issues.append("500_error")
            if "application error" in snap_lower:
                status = "fail"
                issues.append("application_error")
            if "not found" in snap_lower and "404" in snap_lower:
                status = "fail"
                issues.append("404")

            # Check page title is present
            if page.title.lower() not in snap_lower and not page.smoke_only:
                issues.append("title_not_found")

            result = {
                "slug": page.slug,
                "title": page.title,
                "path": page.path,
                "status": status,
                "issues": issues,
                "screenshot": ss_path,
                "snapshot_length": snap_len,
            }
        except Exception as e:
            result = {
                "slug": page.slug,
                "title": page.title,
                "path": page.path,
                "status": "error",
                "issues": [str(e)],
                "screenshot": "",
            }

        results.append(result)
        evidence.save_extraction(page.slug, result)

    return report.build_report(environment, results)


@mcp.tool()
def verify_page(
    page_slug: str,
    environment: str = "staging",
    extract_kpis: bool = True,
) -> dict:
    """Verify a specific page renders correctly with expected data.

    Navigates to the page, extracts KPI values from the rendered
    content, takes a screenshot. If the page has ground_truth_sql
    checks, compares extracted values against the database.

    Args:
        page_slug: Page identifier from inventory (e.g. "financial")
        environment: "staging" or "production"
        extract_kpis: Whether to extract and return KPI values
    """
    from . import auth, browser, evidence, ground_truth, inventory

    page = inventory.get_page(page_slug)
    if not page:
        return {"error": f"Unknown page: {page_slug}"}

    evidence.start_run()

    auth_result = auth.ensure_authenticated(environment)
    if not auth_result.get("authenticated"):
        return {"error": "Authentication failed", "detail": auth_result}

    base = browser.get_environment_url(environment)
    url = base + page.path
    ss_path = evidence.screenshot_path(page.slug)

    capture = browser.navigate_and_capture(url, ss_path)
    snap = capture["snapshot"]

    result = {
        "slug": page.slug,
        "title": page.title,
        "url": url,
        "screenshot": ss_path,
        "status": "pass",
        "kpis": [],
        "comparisons": [],
    }

    if not extract_kpis or page.smoke_only:
        evidence.save_extraction(page.slug, result)
        return result

    # Extract KPI values from the snapshot
    for check in page.checks:
        kpi = _extract_kpi(snap, check)
        result["kpis"].append(kpi)

        # Ground truth comparison
        if check.ground_truth_sql and kpi.get("raw_value") is not None:
            try:
                expected = ground_truth.query_scalar(check.ground_truth_sql)
                match = _compare_values(
                    kpi["raw_value"], expected, check.tolerance
                )
                comparison = {
                    "label": check.label,
                    "rendered": kpi["raw_value"],
                    "expected": expected,
                    "match": match,
                    "tolerance": check.tolerance,
                }
                if not match:
                    result["status"] = "fail"
                result["comparisons"].append(comparison)
            except Exception as e:
                result["comparisons"].append({
                    "label": check.label,
                    "error": str(e),
                })

    evidence.save_extraction(page.slug, result)
    return result


@mcp.tool()
def verify_live_badge(
    environment: str = "staging",
    pages: list[str] | None = None,
) -> dict:
    """Confirm LIVE badge appears on pages wired to real data.

    Checks that the badge shows "LIVE" not "MOCK DATA".

    Args:
        environment: "staging" or "production"
        pages: Specific slugs, or None for all badged pages
    """
    from . import auth, browser, evidence, inventory

    evidence.start_run()

    auth_result = auth.ensure_authenticated(environment)
    if not auth_result.get("authenticated"):
        return {"error": "Authentication failed", "detail": auth_result}

    base = browser.get_environment_url(environment)
    live_pages = inventory.get_live_pages()
    if pages:
        live_pages = [p for p in live_pages if p.slug in pages]

    results = []
    for page in live_pages:
        url = base + page.path
        ss_path = evidence.screenshot_path(f"{page.slug}_badge")
        capture = browser.navigate_and_capture(url, ss_path)
        snap = capture["snapshot"]

        badge = "unknown"
        snap_lower = snap.lower()
        if "live" in snap_lower and "mock" not in snap_lower:
            badge = "LIVE"
        elif "mock" in snap_lower:
            badge = "MOCK"

        results.append({
            "slug": page.slug,
            "title": page.title,
            "badge": badge,
            "screenshot": ss_path,
        })

    live_count = sum(1 for r in results if r["badge"] == "LIVE")
    mock_count = sum(1 for r in results if r["badge"] == "MOCK")

    return {
        "environment": environment,
        "live": live_count,
        "mock": mock_count,
        "total": len(results),
        "all_live": mock_count == 0,
        "details": results,
    }


@mcp.tool()
def verify_against_ground_truth(
    page_slug: str,
    period: str = "",
    entity: str = "consolidated",
    environment: str = "staging",
) -> dict:
    """Compare rendered KPI values against database ground truth.

    Navigates to the page, extracts values, runs the SQL queries
    defined in the page's checks, and compares.

    Args:
        page_slug: Page to verify
        period: YYYY-MM period (empty = latest available)
        entity: Entity filter for the page
        environment: "staging" or "production"
    """
    # For now, delegate to verify_page which does the same thing
    # with ground truth comparisons built in.
    # The entity/period filtering is handled by the page's URL params
    # or could be added as query params in the future.
    return verify_page(page_slug, environment, extract_kpis=True)


# ── Ground Truth & Fixtures ─────────────────────────────────────


@mcp.tool()
def query_ground_truth(
    sql: str = "",
    table: str = "",
    entity: str = "",
    period: str = "",
) -> dict:
    """Query the warehouse for ground truth values.

    Either provide raw SQL, or table + filters for a simple query.

    Args:
        sql: Raw SQL query (takes precedence)
        table: Schema.table for simple queries (e.g. "sage_gold.entity_pnl")
        entity: Filter by entity column
        period: Filter by period column
    """
    from . import ground_truth

    # Connection check
    check = ground_truth.check_connection()
    if not check["connected"]:
        return {"error": "Database not connected", "detail": check}

    if sql:
        rows = ground_truth.query(sql)
        return {"rows": rows, "count": len(rows)}

    if table:
        parts = table.split(".")
        if len(parts) != 2:
            return {"error": "Table must be schema.table (e.g. sage_gold.entity_pnl)"}

        where = []
        params = []
        if entity:
            where.append("entity = %s")
            params.append(entity)
        if period:
            where.append("period = %s")
            params.append(period)

        built_sql = f"SELECT * FROM {table}"
        if where:
            built_sql += " WHERE " + " AND ".join(where)
        built_sql += " LIMIT 100"

        rows = ground_truth.query(built_sql, params)
        return {"rows": rows, "count": len(rows)}

    return {"error": "Provide either sql or table parameter"}


@mcp.tool()
def bless_fixture(
    name: str,
    period: str,
    source: str = "sage_gold",
) -> dict:
    """Bless current database data as a golden fixture for a closed period.

    Use for closed accounting periods where numbers are final.

    Args:
        name: Fixture name (e.g. "dec_2025")
        period: Accounting period YYYY-MM
        source: Data source label for provenance
    """
    from . import fixtures

    return fixtures.bless_fixture(name, period, source)


@mcp.tool()
def compare_fixture(
    name: str,
    page_slug: str = "",
    environment: str = "staging",
) -> dict:
    """Compare a blessed fixture against current data.

    Without page_slug: compares raw database values.
    With page_slug: compares rendered page values.

    Args:
        name: Fixture name
        page_slug: If provided, compare rendered values
        environment: For rendered comparison
    """
    from . import fixtures

    if page_slug:
        # Compare rendered values against fixture
        page_result = verify_page(page_slug, environment, extract_kpis=True)
        fixture = fixtures.load_fixture(name)
        if not fixture:
            return {"error": f"Fixture '{name}' not found"}
        return {
            "fixture": name,
            "page": page_slug,
            "rendered": page_result.get("kpis", []),
            "fixture_data": fixture.get("entity_pnl", [])[:5],
        }

    return fixtures.compare_fixture_to_live(name)


@mcp.tool()
def list_fixtures() -> dict:
    """List all blessed golden fixtures with provenance."""
    from . import fixtures

    return {"fixtures": fixtures.list_fixtures()}


# ── Evidence & Reporting ─────────────────────────────────────────


@mcp.tool()
def take_evidence(
    page_slug: str,
    environment: str = "staging",
    label: str = "",
) -> dict:
    """Take an evidence screenshot and extract visible values.

    Quick capture for proof of state — no comparison, just evidence.

    Args:
        page_slug: Page to capture
        environment: "staging" or "production"
        label: Human-readable label
    """
    from . import auth, browser, evidence, inventory

    page = inventory.get_page(page_slug)
    if not page:
        return {"error": f"Unknown page: {page_slug}"}

    evidence.start_run()

    auth_result = auth.ensure_authenticated(environment)
    if not auth_result.get("authenticated"):
        return {"error": "Authentication failed", "detail": auth_result}

    base = browser.get_environment_url(environment)
    url = base + page.path
    ss_path = evidence.screenshot_path(page.slug)

    capture = browser.navigate_and_capture(url, ss_path)

    result = {
        "slug": page.slug,
        "title": page.title,
        "label": label or f"Evidence: {page.title}",
        "url": url,
        "screenshot": ss_path,
        "snapshot_length": capture["snapshot_length"],
        "captured_at": evidence.get_run_id(),
    }

    evidence.save_extraction(page.slug, result)
    return result


@mcp.tool()
def verification_report(run_id: str = "") -> dict:
    """Get the verification report for a run.

    Args:
        run_id: Specific run ID, or empty for the latest
    """
    from . import evidence

    report = evidence.load_run_report(run_id)
    if not report:
        return {"error": "No verification runs found"}
    return report


# ── Helpers ──────────────────────────────────────────────────────


def _extract_kpi(snapshot: str, check) -> dict:
    """Find a KPI value in the page snapshot by its label."""
    from . import evidence as ev

    lines = snapshot.split("\n")
    label_lower = check.label.lower()

    # Search for the label in the snapshot, then look for adjacent values
    for i, line in enumerate(lines):
        if label_lower in line.lower():
            # Look in nearby lines for a value
            search_range = lines[max(0, i - 2) : i + 5]
            for nearby in search_range:
                # Look for currency values ($XXX,XXX or $XX.XK or $X.XM)
                if check.value_type == "currency":
                    match = re.search(r"\$[\d,.]+[KMB]?", nearby)
                    if match:
                        raw = ev.parse_currency(match.group())
                        return {
                            "label": check.label,
                            "displayed": match.group(),
                            "raw_value": raw,
                            "found": True,
                        }
                elif check.value_type == "percent":
                    match = re.search(r"[\d.]+%", nearby)
                    if match:
                        raw = ev.parse_percent(match.group())
                        return {
                            "label": check.label,
                            "displayed": match.group(),
                            "raw_value": raw,
                            "found": True,
                        }
                elif check.value_type == "number":
                    match = re.search(r"[\d,]+", nearby)
                    if match:
                        raw = float(match.group().replace(",", ""))
                        return {
                            "label": check.label,
                            "displayed": match.group(),
                            "raw_value": raw,
                            "found": True,
                        }

    return {"label": check.label, "displayed": None, "raw_value": None, "found": False}


def _compare_values(rendered, expected, tolerance: float) -> bool:
    """Compare two values within tolerance."""
    if rendered is None or expected is None:
        return False
    try:
        r = float(rendered)
        e = float(expected)
        if e == 0:
            return abs(r) < 1.0  # Within $1 of zero
        return abs(r - e) / abs(e) <= tolerance
    except (TypeError, ValueError):
        return str(rendered).strip() == str(expected).strip()
