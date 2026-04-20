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

# Contract: healthy + runs + answers questions + measures itself.
# "Healthy"  → data_qa(), parity_check(), freshness()
# "Runs"     → refresh_gold(), run_sql() (escape hatch)
# "Answers"  → query_gold(), diagnose(), explain_table(), explain_account()
# "Measures" → self_check() — am I using tools well or over-relying on run_sql?

# Tool call counter — tracks which tools are called in this session
# so self_check() can report imbalance.
_tool_calls: dict[str, int] = {}


def _track(name: str) -> None:
    """Increment the session-local call counter for a tool."""
    _tool_calls[name] = _tool_calls.get(name, 0) + 1


mcp = FastMCP(
    "cerebro-data-engineer",
    instructions=(
        "cerebro-data-engineer is for warehouse operations — querying gold views, "
        "checking data freshness, running parity checks, and diagnosing pipeline issues. "
        "Use `self_check` to verify connectivity, `query_gold` for natural language queries, "
        "`freshness` for staleness checks, `parity_check` to compare against references, "
        "`diagnose` for end-to-end issue tracing."
        "\n\n"
        "WHEN TO USE WHICH MCP:\n"
        "- cerebro-data-engineer (this): warehouse queries, freshness, parity, pipeline diagnostics\n"
        "- cerebro-verifier: data correctness on rendered pages — 'are the numbers right?'\n"
        "- cerebro-web-builder: shipping code, deploy topology, browser login\n"
        "- cerebro-builder: session orchestration, mission, what to work on next\n"
        "- cerebro-github: git ceremony — issues, PRs, CI, merges\n\n"
        "For full ecosystem documentation, use cerebro-docs."
    ),
)


# ── System Knowledge ────────────────────────────────────────

@mcp.tool()
def systems(status_filter: str = "") -> dict:
    """List all vendor systems and their connection status.

    Shows which systems are connected, pending, blocked, or deprioritized.
    This is the data engineer's view of the company's technology landscape.

    Args:
        status_filter: Filter by status (connected, pending, blocked, deprioritized). Empty = all.
    """
    _track("systems")
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
    _track("pipeline")
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
    _track("freshness")
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
    _track("parity_check")
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
    """Escape hatch: run read-only SQL against the Greenmark warehouse.

    USE THE SPECIALIZED TOOLS FIRST. This tool exists for questions that
    no other tool can answer — ad-hoc exploration, debugging, one-off
    investigations. If you find yourself using run_sql repeatedly for
    the same query pattern, that's a signal to create a dedicated tool.

    Prefer these over run_sql:
    - query_gold()       → entity_pnl, gl_summary, ap_aging
    - explain_table()    → table lineage and dependencies
    - explain_account()  → GL account lookup
    - parity_check()     → compare gold vs Alex's spreadsheet
    - row_counts()       → table sizes across the pipeline
    - diagnose()         → trace a metric from dashboard to source
    - data_qa()          → run all quality checks

    Only reach for run_sql when the above can't answer the question.

    Runs via Supabase exec_sql() RPC with service role access.
    Read-only. Schemas: sage_bronze, sage_silver, sage_gold, public.

    Args:
        query: SQL query to execute (read-only)
        limit: Maximum rows to return (default 100, max 1000)
    """
    _track("run_sql")
    if limit > 1000:
        limit = 1000
    return db.run_sql(query, limit=limit)


@mcp.tool()
def refresh_gold() -> dict:
    """Refresh the sage_gold materialized views.

    Calls sage_gold.refresh_all() which refreshes entity_pnl, gl_summary,
    and ap_aging from their silver-tier sources. This is what makes the
    dashboard show updated numbers after a data-daemon extraction.

    Takes ~5-30 seconds depending on data volume. Safe to call anytime —
    the views are CONCURRENTLY refreshed so existing queries aren't blocked.
    """
    _track("refresh_gold")
    return db.call_rpc("refresh_all")


@mcp.tool()
def row_counts() -> dict:
    """Row counts for every table in the medallion pipeline.

    The first thing a data engineer checks when something looks wrong.
    Shows bronze, silver, and gold table sizes side by side so you can
    spot anomalies (e.g., silver has 1M rows but gold has 0 → refresh
    needed; bronze grew by 500K overnight → check extraction).
    """
    _track("row_counts")
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
    results = db.run_sql(f"""
        SELECT source_id as account_no, title, category, entity, status
        FROM sage_silver.gl_accounts
        WHERE source_id = '{account_no}'
        LIMIT 5
    """)
    if "error" in results:
        return results
    if not results["rows"]:
        return {"error": f"Account {account_no} not found in sage_silver.gl_accounts"}

    # Map to P&L category based on account number prefix
    prefix = account_no[0] if account_no else ""
    pnl_category = {
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
        "accounts": results["rows"],
        "pnl_category": pnl_category,
        "note": f"In sage_gold.entity_pnl, revenue = 4xxx, COGS = 5xxx, OpEx = 6-9xxx.",
    }


# ── Self-measurement ───────────────────────────────────────

@mcp.tool()
def self_check() -> dict:
    """How am I doing? Am I using the right tools or over-relying on run_sql?

    Reports this session's tool call distribution and flags imbalances:
    - run_sql > 30% of total calls → "over-relying on escape hatch"
    - No health checks (data_qa/parity/freshness) called → "not checking health"
    - Only querying, never diagnosing → "answering but not understanding"

    Call this periodically to stay honest about how you're working.
    """
    _track("self_check")

    total = sum(_tool_calls.values())
    if total == 0:
        return {"message": "No tools called yet this session.", "calls": {}}

    sql_count = _tool_calls.get("run_sql", 0)
    sql_pct = sql_count / total * 100

    health_tools = {"data_qa", "parity_check", "freshness"}
    health_count = sum(_tool_calls.get(t, 0) for t in health_tools)

    answer_tools = {"query_gold", "explain_table", "explain_account", "diagnose"}
    answer_count = sum(_tool_calls.get(t, 0) for t in answer_tools)

    ops_tools = {"refresh_gold", "row_counts"}
    ops_count = sum(_tool_calls.get(t, 0) for t in ops_tools)

    warnings = []
    if sql_pct > 30:
        warnings.append(
            f"run_sql is {sql_pct:.0f}% of calls ({sql_count}/{total}). "
            "Over-relying on the escape hatch. Use query_gold, explain_table, "
            "or diagnose instead — they encode domain knowledge."
        )
    if total > 5 and health_count == 0:
        warnings.append(
            "No health checks called (data_qa, parity_check, freshness). "
            "A data engineer should verify health before answering questions."
        )
    if answer_count > 10 and health_count == 0:
        warnings.append(
            "Answering lots of questions but never checking if the data is right. "
            "Run data_qa() or parity_check() to validate before trusting."
        )
    if total > 3 and ops_count == 0 and sql_count == 0:
        warnings.append(
            "Only reading, never operating. Consider refresh_gold() or row_counts() "
            "to check if the pipeline needs attention."
        )

    return {
        "session_calls": dict(sorted(_tool_calls.items(), key=lambda x: -x[1])),
        "total": total,
        "distribution": {
            "health": {"count": health_count, "pct": f"{health_count/total*100:.0f}%"},
            "answers": {"count": answer_count, "pct": f"{answer_count/total*100:.0f}%"},
            "operations": {"count": ops_count, "pct": f"{ops_count/total*100:.0f}%"},
            "escape_hatch": {"count": sql_count, "pct": f"{sql_pct:.0f}%"},
            "meta": {"count": _tool_calls.get("self_check", 0)},
        },
        "warnings": warnings if warnings else ["Looking good — balanced tool usage."],
        "guidance": "Ideal balance: health checks first, then targeted answers via specialized tools, run_sql only for genuinely novel questions.",
    }
