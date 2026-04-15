"""Ground truth — run arbitrary SQL queries against the warehouse.

The verifier doesn't know about specific tables. The inventory defines
what queries to run. This module just executes them and returns results.
"""

import os
import re
from decimal import Decimal


def _connect():
    """Connect to the warehouse (Supabase Postgres)."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")

    import psycopg2

    return psycopg2.connect(url)


def _normalize(val):
    """Normalize a database value for comparison."""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return round(float(val), 2)
    if isinstance(val, (int, float)):
        return round(float(val), 2)
    return str(val).strip()


def query(sql: str, params: list | None = None) -> list[dict]:
    """Run a SQL query, return rows as list of dicts.

    The inventory defines what to query. This module executes it.
    """
    conn = _connect()
    cur = conn.cursor()
    cur.execute(sql, params or [])
    cols = [d[0] for d in cur.description]
    rows = []
    for row in cur.fetchall():
        rows.append({c: _normalize(v) for c, v in zip(cols, row)})
    conn.close()
    return rows


def query_scalar(sql: str, params: list | None = None):
    """Run a SQL query that returns a single value."""
    conn = _connect()
    cur = conn.cursor()
    cur.execute(sql, params or [])
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return _normalize(row[0])


def table_row_count(schema: str, table: str) -> int:
    """Get row count for a table. Basic health check."""
    # Validate identifiers to prevent injection
    if not re.match(r"^[a-z_][a-z0-9_]*$", schema):
        raise ValueError(f"Invalid schema: {schema}")
    if not re.match(r"^[a-z_][a-z0-9_]*$", table):
        raise ValueError(f"Invalid table: {table}")

    conn = _connect()
    cur = conn.cursor()
    cur.execute(f"SELECT count(*) FROM {schema}.{table}")
    count = cur.fetchone()[0]
    conn.close()
    return int(count)


def check_connection() -> dict:
    """Verify the database connection is working."""
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
        return {"connected": True}
    except Exception as e:
        return {"connected": False, "error": str(e)}
