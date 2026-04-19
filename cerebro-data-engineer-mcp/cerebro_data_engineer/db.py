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
DATABASE_URL = os.environ.get("DATABASE_URL", "")


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


# ── Direct Postgres (ad-hoc SQL) ────────────────────────────

def run_sql(query: str, limit: int = 100) -> dict[str, Any]:
    """Execute a read-only SQL query against the warehouse.

    Uses DATABASE_URL (direct Postgres connection via psycopg2).
    Enforces read-only at the transaction level. Returns column names
    + rows as dicts, capped at `limit` rows.
    """
    if not DATABASE_URL:
        return {"error": "DATABASE_URL not set — cannot run ad-hoc SQL. Set it to the Supabase direct connection string."}

    import psycopg2
    import psycopg2.extras

    try:
        conn = psycopg2.connect(DATABASE_URL, options="-c default_transaction_read_only=on")
        conn.set_session(readonly=True, autocommit=True)
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            if cur.description is None:
                # DDL or statement with no results
                return {"columns": [], "rows": [], "row_count": 0, "note": "Statement returned no rows (possibly DDL — blocked by read-only mode)"}
            columns = [d.name for d in cur.description]
            rows = [dict(row) for row in cur.fetchmany(limit)]
            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": cur.rowcount > limit if cur.rowcount >= 0 else False,
            }
    except psycopg2.Error as e:
        return {"error": f"SQL error: {e.pgerror or str(e)}"}
    finally:
        try:
            conn.close()
        except Exception:
            pass


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
