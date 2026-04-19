"""cerebro-data-engineer MCP server.

The AI data engineer for Greenmark Waste Solutions.
Knows every system, every table, every pipeline.
Runs QA, diagnoses issues, answers "why is this number wrong?"

Tools:
  systems()          — List all vendor systems and their connection status
  explain_table()    — What is this table, where does it come from, what depends on it
  pipeline()         — Show the full data flow from vendor to dashboard
  data_qa()          — Run quality checks across the medallion pipeline
  query_gold()       — Query gold tables directly (entity_pnl, gl_summary, ap_aging)
  diagnose()         — Trace a metric from dashboard back to source
  freshness()        — How fresh is the data? When did data-daemon last run?
  parity_check()     — Compare gold data against Alex's verified spreadsheet
"""

from mcp.server.fastmcp import FastMCP

from .topology import ALL_SYSTEMS, MEDALLION_LAYERS, REFRESH_CHAIN, KNOWN_PARITY
from . import qa, db

# Contract: healthy + runs + answers questions.
# "Healthy" → data_qa(), parity_check(), freshness()
# "Runs"    → refresh_gold(), run_sql()
# "Answers" → run_sql(), diagnose(), explain_table(), query_gold()


mcp = FastMCP("cerebro-data-engineer")


# ── System Knowledge ────────────────────────────────────────

@mcp.tool()
def systems(status_filter: str = "") -> dict:
    """List all vendor systems and their connection status.

    Shows which systems are connected, pending, blocked, or deprioritized.
    This is the data engineer's view of the company's technology landscape.

    Args:
        status_filter: Filter by status (connected, pending, blocked, deprioritized). Empty = all.
    """
    results = []
    for s in ALL_SYSTEMS:
        if status_filter and s.status != status_filter:
            continue
        results.append({
            "name": s.name,
            "category": s.category,
            "status": s.status,
            "owner": s.owner,
            "api_type": s.api_type,
            "bronze_schema": s.bronze_schema,
            "table_count": len(s.tables),
            "notes": s.notes,
        })

    connected = sum(1 for s in ALL_SYSTEMS if s.status == "connected")
    pending = sum(1 for s in ALL_SYSTEMS if s.status == "pending")

    return {
        "summary": f"{connected} connected, {pending} pending, {len(ALL_SYSTEMS)} total",
        "systems": results,
    }


@mcp.tool()
def explain_table(table_name: str) -> dict:
    """What is this table, where does it come from, what depends on it.

    The data engineer's answer to "what is sage_gold.entity_pnl?"

    Args:
        table_name: Table name with or without schema (e.g., "entity_pnl" or "sage_gold.entity_pnl")
    """
    # Search across all systems for matching table
    search = table_name.lower()
    for system in ALL_SYSTEMS:
        for table in system.tables:
            full_name = f"{table.schema}.{table.name}"
            if search in (table.name, full_name):
                # Find what depends on this table
                dependents = []
                for s2 in ALL_SYSTEMS:
                    for t2 in s2.tables:
                        if full_name in t2.depends_on:
                            dependents.append(f"{t2.schema}.{t2.name}")

                return {
                    "table": full_name,
                    "description": table.description,
                    "row_count": table.row_count_hint,
                    "refresh_method": table.refresh_method,
                    "source": table.source,
                    "source_system": system.name,
                    "depends_on": table.depends_on,
                    "depended_on_by": dependents,
                    "key_columns": table.key_columns,
                    "layer": "bronze" if "bronze" in table.schema else "silver" if "silver" in table.schema else "gold",
                }

    return {"error": f"Table '{table_name}' not found in topology. Known tables: " +
            ", ".join(f"{t.schema}.{t.name}" for s in ALL_SYSTEMS for t in s.tables)}


@mcp.tool()
def pipeline() -> dict:
    """Show the full data flow from vendor to dashboard.

    The medallion architecture: bronze → silver → gold → dashboard.
    """
    return {
        "architecture": "medallion",
        "layers": MEDALLION_LAYERS,
        "refresh_chain": REFRESH_CHAIN,
        "database": "Supabase (PostgreSQL) — project wwmcgtyngnziepeynccz",
        "plan": "Pro ($25/mo, 8GB disk)",
        "dashboard_api": "/api/financial → sage_gold via PostgREST",
        "extraction_engine": "data-daemon (Railway, production)",
        "known_parity_periods": list(KNOWN_PARITY.keys()),
    }


# ── Data QA ─────────────────────────────────────────────────

@mcp.tool()
def data_qa(checks: str = "all") -> dict:
    """Run quality checks across the medallion pipeline.

    Checks parity, freshness, table health, and vendor connectivity.
    This is the data engineer's daily health check.

    Args:
        checks: Which checks to run — "all", "parity", "freshness", "tables", "vendors"
    """
    if checks == "all":
        results = qa.run_full_qa()
    elif checks == "parity":
        results = qa.check_parity()
    elif checks == "freshness":
        results = qa.check_freshness()
    elif checks == "tables":
        results = qa.check_table_health()
    elif checks == "vendors":
        results = qa.check_vendor_connectivity()
    else:
        return {"error": f"Unknown check type: {checks}. Use: all, parity, freshness, tables, vendors"}

    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    warnings = sum(1 for r in results if r.status == "warn")

    return {
        "summary": f"{passed} passed, {failed} failed, {warnings} warnings",
        "healthy": failed == 0,
        "results": [{"check": r.check, "status": r.status, "detail": r.detail, "severity": r.severity} for r in results],
    }


@mcp.tool()
def query_gold(table: str, entity: str = "", period: str = "", limit: int = 20) -> dict:
    """Query gold tables directly — entity_pnl, gl_summary, or ap_aging.

    The data engineer's direct line to the business metrics.

    Args:
        table: Gold table name — "entity_pnl", "gl_summary", or "ap_aging"
        entity: Filter by entity — "hometown" or "ntx" (optional)
        period: Filter by period — "2025-12" format (optional)
        limit: Max rows to return (default 20)
    """
    try:
        if table == "entity_pnl":
            rows = db.query_entity_pnl(
                entity=entity or None,
                period=period or None,
            )
        elif table == "gl_summary":
            rows = db.query_gl_summary(
                entity=entity or None,
                period=period or None,
                limit=limit,
            )
        elif table == "ap_aging":
            rows = db.query_ap_aging(limit=limit)
        else:
            return {"error": f"Unknown table: {table}. Use: entity_pnl, gl_summary, ap_aging"}

        return {
            "table": f"sage_gold.{table}",
            "row_count": len(rows),
            "rows": rows[:limit],
        }
    except RuntimeError as e:
        return {"error": str(e)}


# ── Diagnostics ─────────────────────────────────────────────

@mcp.tool()
def diagnose(question: str) -> dict:
    """Trace a metric from dashboard back to source.

    Ask questions like:
    - "why is hometown revenue $0 for April?"
    - "is the data fresh?"
    - "what systems are disconnected?"

    The data engineer reasons about the topology and data to answer.

    Args:
        question: Natural language question about the data
    """
    q = question.lower()
    findings = []

    # Revenue question
    if "revenue" in q and ("zero" in q or "$0" in q or "wrong" in q or "missing" in q):
        # Check entity_pnl for the entity/period mentioned
        entity = "hometown" if "hometown" in q or "htn" in q else "ntx" if "ntx" in q else None
        pnl_rows = db.query_entity_pnl(entity=entity)

        revenue_periods = [r for r in pnl_rows if r["revenue"] > 1000]
        zero_periods = [r for r in pnl_rows if r["revenue"] == 0 or r["revenue"] < 10]

        findings.append({
            "observation": f"entity_pnl has {len(revenue_periods)} periods with revenue > $1K",
            "periods_with_revenue": [f"{r['period']} {r['entity']}: ${r['revenue']:,.2f}" for r in revenue_periods[:5]],
            "periods_with_zero": [f"{r['period']} {r['entity']}: ${r['revenue']:,.2f}" for r in zero_periods[:5]],
        })

        if zero_periods:
            findings.append({
                "diagnosis": "Current-month periods often show $0 revenue because GL entries land before revenue is booked (L012). "
                             "The dashboard should display the most recent period with substantial revenue (>$1K), not the calendar-current period.",
            })

    # Freshness question
    if "fresh" in q or "stale" in q or "last run" in q or "when" in q:
        freshness_results = qa.check_freshness()
        findings.append({
            "freshness": [{"status": r.status, "detail": r.detail} for r in freshness_results],
        })

    # Disconnected / broken
    if "disconnect" in q or "broken" in q or "down" in q or "error" in q:
        vendor_results = qa.check_vendor_connectivity()
        findings.append({
            "vendor_status": [{"status": r.status, "detail": r.detail} for r in vendor_results],
        })

    # Generic — run full QA
    if not findings:
        all_results = qa.run_full_qa()
        findings.append({
            "full_qa": [{"check": r.check, "status": r.status, "detail": r.detail} for r in all_results],
            "note": "Ran full QA since the question didn't match a specific pattern. If you need a targeted answer, try asking about revenue, freshness, or connectivity.",
        })

    return {
        "question": question,
        "findings": findings,
        "topology_context": {
            "connected_systems": [s.name for s in ALL_SYSTEMS if s.status == "connected"],
            "pending_systems": [s.name for s in ALL_SYSTEMS if s.status == "pending"],
            "gold_tables": ["entity_pnl", "gl_summary", "ap_aging"],
        },
    }


@mcp.tool()
def freshness() -> dict:
    """How fresh is the data? When did the pipeline last refresh?

    Checks entity_pnl for the most recent period with meaningful revenue.
    """
    results = qa.check_freshness()
    return {
        "results": [{"status": r.status, "detail": r.detail, "severity": r.severity} for r in results],
        "note": "The dashboard shows the most recent period with revenue > $1K. Current-month periods may show $0 until revenue is booked.",
    }


@mcp.tool()
def parity_check(period: str = "2025-12") -> dict:
    """Compare gold data against Alex's verified spreadsheet numbers.

    Dec 2025 is the golden fixture: HTN $872,850.23, NTX $75,246.02.
    These numbers were verified by Alex against her Greenmark_Metrics spreadsheet.

    Args:
        period: Period to check in YYYY-MM format (default: 2025-12)
    """
    results = qa.check_parity(period)
    passed = all(r.status == "pass" for r in results)
    return {
        "period": period,
        "parity": "MATCH" if passed else "MISMATCH",
        "results": [{"status": r.status, "detail": r.detail} for r in results],
        "known_values": KNOWN_PARITY.get(period, {}),
    }


# ── Operational tools (the "runs" leg of the contract) ──────

@mcp.tool()
def run_sql(query: str, limit: int = 100) -> dict:
    """Run read-only SQL against the Greenmark warehouse.

    This is the data engineer's most important tool. Any question about
    the data that isn't covered by a specialized tool can be answered
    with SQL. The query runs against the real Supabase Postgres database
    with read-only transaction isolation — it cannot modify data.

    All schemas are accessible: sage_bronze, sage_silver, sage_gold,
    public, auth (with service role). Use schema-qualified names.

    Examples:
        "SELECT * FROM sage_gold.entity_pnl WHERE period = '2025-12'"
        "SELECT count(*) FROM sage_bronze.gl_journal_entries"
        "SELECT account_no, title FROM sage_bronze.gl_accounts WHERE account_no LIKE '4%' LIMIT 20"
        "SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema')"

    Args:
        query: SQL query to execute (read-only enforced)
        limit: Maximum rows to return (default 100, max 1000)
    """
    if limit > 1000:
        limit = 1000
    result = db.run_sql(query, limit=limit)
    if "error" in result and "connection" in result["error"].lower():
        result["hint"] = (
            "Direct Postgres connection failed. This tool requires DATABASE_URL "
            "to be set to a reachable Postgres connection string. On sandboxed "
            "environments without direct DB access, use query_gold() or the "
            "PostgREST-based tools instead."
        )
    return result


@mcp.tool()
def refresh_gold() -> dict:
    """Refresh the sage_gold materialized views.

    Calls sage_gold.refresh_all() which refreshes entity_pnl, gl_summary,
    and ap_aging from their silver-tier sources. This is what makes the
    dashboard show updated numbers after a data-daemon extraction.

    Takes ~5-30 seconds depending on data volume. Safe to call anytime —
    the views are CONCURRENTLY refreshed so existing queries aren't blocked.
    """
    return db.call_rpc("refresh_all")


@mcp.tool()
def row_counts() -> dict:
    """Row counts for every table in the medallion pipeline.

    The first thing a data engineer checks when something looks wrong.
    Shows bronze, silver, and gold table sizes side by side so you can
    spot anomalies (e.g., silver has 1M rows but gold has 0 → refresh
    needed; bronze grew by 500K overnight → check extraction).
    """
    try:
        results = db.run_sql("""
            SELECT
                schemaname as schema,
                relname as table_name,
                n_live_tup as row_count
            FROM pg_stat_user_tables
            WHERE schemaname IN ('sage_bronze', 'sage_silver', 'sage_gold', 'public')
            ORDER BY schemaname, relname
        """, limit=200)
        if "error" in results:
            return results

        by_schema: dict[str, list] = {}
        for row in results["rows"]:
            schema = row["schema"]
            if schema not in by_schema:
                by_schema[schema] = []
            by_schema[schema].append({
                "table": row["table_name"],
                "rows": row["row_count"],
            })

        return {"schemas": by_schema, "total_tables": len(results["rows"])}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def explain_account(account_no: str) -> dict:
    """What is this GL account? Revenue? COGS? OpEx?

    Alex and Daniel frequently ask "what is account 4010?" This tool
    looks it up in sage_bronze.gl_accounts and returns the title,
    account type, and which P&L category it maps to.

    Account number patterns:
    - 4xxx = Revenue
    - 5xxx = COGS (Cost of Goods Sold)
    - 6xxx-9xxx = Operating Expenses

    Args:
        account_no: Sage GL account number (e.g., "4010", "5010", "6010")
    """
    try:
        results = db.run_sql(f"""
            SELECT "ACCOUNTNO" as account_no, "TITLE" as title,
                   "ACCOUNTTYPE" as account_type, "NORMALBALANCE" as normal_balance,
                   "STATUS" as status
            FROM sage_bronze.gl_accounts
            WHERE "ACCOUNTNO" = '{account_no}'
            LIMIT 1
        """)
        if "error" in results:
            return results
        if not results["rows"]:
            return {"error": f"Account {account_no} not found in sage_bronze.gl_accounts"}

        acct = results["rows"][0]
        # Map to P&L category
        prefix = account_no[0] if account_no else ""
        category = {
            "4": "Revenue",
            "5": "Cost of Goods Sold (COGS)",
            "6": "Operating Expenses",
            "7": "Operating Expenses",
            "8": "Operating Expenses",
            "9": "Operating Expenses",
            "1": "Assets",
            "2": "Liabilities",
            "3": "Equity",
        }.get(prefix, "Unknown")

        return {
            **acct,
            "pnl_category": category,
            "note": f"This is a {category} account. In sage_gold.entity_pnl, revenue comes from 4xxx accounts, COGS from 5xxx, and OpEx from 6xxx-9xxx.",
        }
    except Exception as e:
        return {"error": str(e)}
