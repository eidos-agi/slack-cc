"""Database access — PostgREST for structured queries, raw psql for ad-hoc SQL.

Two access paths:
1. PostgREST (anon key) — for gold/silver/bronze queries via the REST API.
   No direct connection needed. Works from anywhere.
2. Direct Postgres (DATABASE_URL) — for ad-hoc SQL. Required for run_sql().
   Uses psycopg2. Read-only by default; SET TRANSACTION READ ONLY.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Any


SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wwmcgtyngnziepeynccz.supabase.co")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")


def _request(path: str, schema: str = "public", params: str = "") -> list[dict[str, Any]]:
    """Make a PostgREST request."""
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    if params:
        url += f"?{params}"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Accept-Profile": schema,
    })
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"PostgREST {e.code}: {body}") from e


def query_entity_pnl(entity: str | None = None, period: str | None = None) -> list[dict]:
    """Query sage_gold.entity_pnl with optional filters."""
    params = "select=entity,period,revenue,cogs,gross_profit,operating_expenses,net_income,gross_margin&order=period.desc,entity"
    if entity:
        params += f"&entity=eq.{entity}"
    if period:
        params += f"&period=eq.{period}"
    return _request("entity_pnl", schema="sage_gold", params=params)


def query_gl_summary(entity: str | None = None, period: str | None = None, limit: int = 100) -> list[dict]:
    """Query sage_gold.gl_summary."""
    params = f"select=*&order=period.desc,entity&limit={limit}"
    if entity:
        params += f"&entity=eq.{entity}"
    if period:
        params += f"&period=eq.{period}"
    return _request("gl_summary", schema="sage_gold", params=params)


def query_ap_aging(limit: int = 50) -> list[dict]:
    """Query sage_gold.ap_aging."""
    return _request("ap_aging", schema="sage_gold", params=f"select=*&limit={limit}")


def check_table_accessible(table: str, schema: str) -> dict:
    """Check if a table is accessible and return row count estimate."""
    try:
        rows = _request(table, schema=schema, params="select=*&limit=1")
        return {"accessible": True, "has_data": len(rows) > 0, "sample": rows[0] if rows else None}
    except RuntimeError as e:
        return {"accessible": False, "error": str(e)}


# ── SQL execution via Supabase exec_sql RPC ─────────────────

def run_sql(query: str, limit: int = 100) -> dict[str, Any]:
    """Execute a read-only SQL query against the warehouse.

    Uses the Supabase exec_sql() RPC function with the service role key.
    No direct Postgres connection needed — works from any environment.
    The exec_sql function enforces read-only at the Postgres level.

    Returns rows as a list of dicts. If the query fails, returns an
    error dict with the Postgres error code and message.
    """
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not service_key:
        return {"error": "SUPABASE_SERVICE_ROLE_KEY not set — cannot run SQL"}

    # Append LIMIT if not already present (prevent accidental full-table scans)
    q = query.strip().rstrip(";")
    if "limit" not in q.lower():
        q += f" LIMIT {limit}"

    body = json.dumps({"query": q}).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
        data=body,
        method="POST",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        rows = json.loads(resp.read())
        if isinstance(rows, list):
            return {
                "rows": rows[:limit],
                "row_count": len(rows[:limit]),
                "columns": list(rows[0].keys()) if rows else [],
                "truncated": len(rows) > limit,
            }
        return {"rows": [], "row_count": 0, "result": rows}
    except urllib.error.HTTPError as e:
        error_body = json.loads(e.read().decode())
        return {
            "error": f"SQL error: {error_body.get('message', str(e))}",
            "code": error_body.get("code"),
            "hint": error_body.get("hint"),
        }


def call_rpc(function_name: str, params: dict | None = None) -> dict[str, Any]:
    """Call a Supabase RPC function (e.g., sage_gold.refresh_all).

    Uses the service role key for elevated access.
    """
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not service_key:
        return {"error": "SUPABASE_SERVICE_ROLE_KEY not set — cannot call RPC functions"}

    url = f"{SUPABASE_URL}/rest/v1/rpc/{function_name}"
    body = json.dumps(params or {}).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        result = resp.read().decode()
        return {"success": True, "result": json.loads(result) if result.strip() else None}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        return {"error": f"RPC {function_name} failed ({e.code}): {body_text}"}
