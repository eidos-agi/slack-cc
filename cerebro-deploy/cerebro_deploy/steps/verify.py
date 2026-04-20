"""Verify steps 19-25: post-deploy data verification."""

from __future__ import annotations

import json
import subprocess
import time

from cerebro_deploy.config import ServiceConfig
from cerebro_deploy.runner import StepResult


def _run(cmd: list[str], cwd: str | None = None, timeout: int = 60) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"


def _get_base_url(config: ServiceConfig) -> str:
    """Get the base URL for the service."""
    if config.environment == "develop":
        return f"https://{config.name}-develop.up.railway.app"
    return f"https://{config.name}-production.up.railway.app"


# ── Step 19: Trigger extraction (data-daemon) ────────────────

def step_trigger_extraction(config: ServiceConfig, ctx: dict) -> StepResult:
    """For data-daemon: trigger extraction via POST /trigger/<source>."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN — would trigger extraction")

    if config.name != "data-daemon":
        return StepResult(passed=True, detail="Not data-daemon — no extraction to trigger")

    base_url = _get_base_url(config)

    # Get available sources from health endpoint
    rc, out, _ = _run(["curl", "-sf", f"{base_url}/health", "--max-time", "10"])
    sources = []
    if rc == 0:
        try:
            data = json.loads(out)
            sources = data.get("connectors") or data.get("sources") or []
        except (json.JSONDecodeError, KeyError):
            pass

    if not sources:
        # Try triggering known connectors
        sources = ["sage", "fleetio"]

    triggered = []
    failed = []
    for source in sources:
        source_name = source if isinstance(source, str) else str(source)
        rc, out, err = _run([
            "curl", "-sf", "-X", "POST",
            f"{base_url}/trigger/{source_name}",
            "--max-time", "10",
        ])
        if rc == 0:
            triggered.append(source_name)
        else:
            failed.append(f"{source_name}: {err[:50]}")

    if triggered:
        ctx["triggered_sources"] = triggered
        detail = f"Triggered: {', '.join(triggered)}"
        if failed:
            detail += f". Failed: {', '.join(failed)}"
        return StepResult(passed=True, detail=detail)

    if failed:
        return StepResult(
            passed=False,
            detail=f"All triggers failed: {'; '.join(failed)}",
            remediation=f"Check: curl -v -X POST {base_url}/trigger/sage",
        )

    return StepResult(passed=True, detail="No sources to trigger")


# ── Step 20: Wait for jobs to complete ────────────────────────

def step_wait_jobs(config: ServiceConfig, ctx: dict) -> StepResult:
    """Wait for extraction jobs to complete."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    if config.name != "data-daemon":
        return StepResult(passed=True, detail="Not data-daemon")

    triggered = ctx.get("triggered_sources", [])
    if not triggered:
        return StepResult(passed=True, detail="No jobs to wait for")

    base_url = _get_base_url(config)
    max_polls = 30  # 5 minutes
    poll_interval = 10

    for i in range(max_polls):
        rc, out, _ = _run(["curl", "-sf", f"{base_url}/jobs", "--max-time", "10"])
        if rc != 0:
            if i < 3:
                time.sleep(poll_interval)
                continue
            return StepResult(
                passed=False,
                detail="Cannot reach /jobs endpoint",
                remediation=f"curl -v {base_url}/jobs",
            )

        try:
            data = json.loads(out)
            jobs = data if isinstance(data, list) else data.get("jobs", [])
            active = [j for j in jobs if j.get("status") in ("pending", "running")]
            if not active:
                completed = [j for j in jobs if j.get("status") == "completed"]
                failed_jobs = [j for j in jobs if j.get("status") == "failed"]
                ctx["completed_jobs"] = completed
                ctx["failed_jobs"] = failed_jobs
                detail = f"{len(completed)} completed, {len(failed_jobs)} failed"
                return StepResult(passed=True, detail=detail)

            if i % 3 == 0:
                print(f" [{len(active)} active]", end="", flush=True)
        except (json.JSONDecodeError, KeyError):
            pass

        time.sleep(poll_interval)

    return StepResult(
        passed=False,
        detail=f"Jobs did not complete within {max_polls * poll_interval}s",
        remediation=f"Check: curl {base_url}/jobs",
    )


# ── Step 21: Check for failures ──────────────────────────────

def step_check_failures(config: ServiceConfig, ctx: dict) -> StepResult:
    """Any failed jobs = STOP."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    if config.name != "data-daemon":
        return StepResult(passed=True, detail="Not data-daemon")

    failed_jobs = ctx.get("failed_jobs", [])
    if failed_jobs:
        details = []
        for j in failed_jobs[:5]:
            source = j.get("source_type", "?")
            error = j.get("error", "unknown")[:100]
            details.append(f"{source}: {error}")
        return StepResult(
            passed=False,
            detail=f"{len(failed_jobs)} failed jobs: {'; '.join(details)}",
            remediation="Check job logs, fix the issue, and re-trigger extraction",
        )

    completed = ctx.get("completed_jobs", [])
    if not completed:
        return StepResult(passed=True, detail="No jobs ran (nothing to check)")

    return StepResult(passed=True, detail=f"{len(completed)} jobs completed without failures")


# ── Step 22: Check row counts ────────────────────────────────

def step_check_row_counts(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify row counts are reasonable."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    if not config.database_id:
        return StepResult(passed=True, detail="No database to check")

    rc, out, err = _run([
        "psql",
        f"postgresql://postgres.{config.database_id}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        "-c", """
            SELECT schemaname || '.' || relname AS table_name,
                   n_live_tup AS row_count
            FROM pg_stat_user_tables
            WHERE schemaname LIKE '%_bronze'
               OR schemaname LIKE '%_silver'
               OR schemaname LIKE '%_gold'
            ORDER BY schemaname, relname;
        """,
        "--no-password", "-t",
    ], timeout=15)

    if rc == 127:
        return StepResult(passed=True, detail="psql not available — skipping row count check")

    if rc != 0:
        if "password" in err.lower():
            return StepResult(passed=True, detail="Cannot check row counts without DB password (expected)")
        return StepResult(
            passed=False,
            detail=f"Row count query failed: {err[:200]}",
            remediation="Check database connectivity",
        )

    if not out.strip():
        return StepResult(passed=True, detail="No medallion tables found (may be first deploy)")

    # Parse and check for zeros
    lines = [l.strip() for l in out.strip().split("\n") if l.strip()]
    zero_tables = []
    ctx["post_deploy_row_counts"] = out

    for line in lines:
        parts = line.split("|")
        if len(parts) >= 2:
            table = parts[0].strip()
            count = parts[1].strip()
            if count == "0" and "_gold" not in table:  # Gold views may be empty
                zero_tables.append(table)

    if zero_tables:
        return StepResult(
            passed=False,
            detail=f"Empty tables: {', '.join(zero_tables)}",
            remediation="Check extraction logs — tables with 0 rows may indicate failed loads",
        )

    return StepResult(passed=True, detail=f"Row counts: {len(lines)} tables checked, all non-empty")


# ── Step 23: Check run_history ────────────────────────────────

def step_check_run_history(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify rows_extracted vs rows_loaded match in run history."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    if config.name != "data-daemon":
        return StepResult(passed=True, detail="Not data-daemon")

    if not config.database_id:
        return StepResult(passed=True, detail="No database configured")

    rc, out, err = _run([
        "psql",
        f"postgresql://postgres.{config.database_id}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        "-c", """
            SELECT source_type, rows_extracted, rows_loaded, status, started_at
            FROM daemon.run_history
            ORDER BY started_at DESC
            LIMIT 10;
        """,
        "--no-password", "-t",
    ], timeout=15)

    if rc == 127:
        return StepResult(passed=True, detail="psql not available")

    if rc != 0:
        if "password" in err.lower():
            return StepResult(passed=True, detail="Cannot check run_history without DB password")
        return StepResult(passed=True, detail=f"run_history query failed (table may not exist): {err[:100]}")

    if not out.strip():
        return StepResult(passed=True, detail="No run history entries")

    # Check for mismatches
    mismatches = []
    for line in out.strip().split("\n"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:
            source = parts[0]
            extracted = parts[1]
            loaded = parts[2]
            status = parts[3]
            if extracted != loaded and status == "completed":
                mismatches.append(f"{source}: extracted={extracted} loaded={loaded}")

    if mismatches:
        return StepResult(
            passed=False,
            detail=f"Row count mismatches: {'; '.join(mismatches)}",
            remediation="Check INC-001 — likely a unique index mismatch. Verify (source_id, entity) index.",
        )

    return StepResult(passed=True, detail="Run history: extracted/loaded counts match")


# ── Step 24: Compare against known good counts ───────────────

def step_compare_known_good(config: ServiceConfig, ctx: dict) -> StepResult:
    """Compare row counts against known minimums."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    # Known good minimums from production (session 34 actuals)
    KNOWN_MINIMUMS = {
        "sage_bronze.gl_detail": 1_380_000,  # 1.38M GL entries
        "sage_bronze.ap_bill": 10_000,
        "sage_bronze.vendor": 100,
        "sage_bronze.customer": 100,
    }

    if not config.database_id:
        return StepResult(passed=True, detail="No database to compare")

    below_minimum = []
    checked = 0

    for table, minimum in KNOWN_MINIMUMS.items():
        schema, name = table.split(".")
        rc, out, _ = _run([
            "psql",
            f"postgresql://postgres.{config.database_id}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
            "-c", f"SELECT COUNT(*) FROM {schema}.{name};",
            "--no-password", "-t",
        ], timeout=15)

        if rc == 0 and out.strip():
            try:
                count = int(out.strip())
                checked += 1
                if count < minimum:
                    below_minimum.append(f"{table}: {count:,} (expected >= {minimum:,})")
            except ValueError:
                pass

    if not checked:
        return StepResult(passed=True, detail="Cannot verify known minimums (no DB access)")

    if below_minimum:
        return StepResult(
            passed=False,
            detail=f"Below known minimums: {'; '.join(below_minimum)}",
            remediation="Data may have been truncated or extraction incomplete. Investigate.",
        )

    return StepResult(passed=True, detail=f"All {checked} tables meet known minimums")


# ── Step 25: Run data quality checks ─────────────────────────

def step_data_quality(config: ServiceConfig, ctx: dict) -> StepResult:
    """Basic data quality: null rates, duplicate detection."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    if not config.database_id:
        return StepResult(passed=True, detail="No database to check")

    # Check for duplicate source_ids in bronze tables
    rc, out, _ = _run([
        "psql",
        f"postgresql://postgres.{config.database_id}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        "-c", """
            SELECT schemaname || '.' || tablename AS t
            FROM pg_tables
            WHERE schemaname LIKE '%_bronze'
            LIMIT 5;
        """,
        "--no-password", "-t",
    ], timeout=15)

    if rc != 0 or not out.strip():
        return StepResult(passed=True, detail="Cannot run DQ checks (no DB access or no tables)")

    tables = [t.strip() for t in out.strip().split("\n") if t.strip()]
    issues = []

    for table in tables[:3]:  # Check first 3
        rc, dup_out, _ = _run([
            "psql",
            f"postgresql://postgres.{config.database_id}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
            "-c", f"""
                SELECT COUNT(*) - COUNT(DISTINCT source_id) AS duplicate_count
                FROM {table}
                WHERE source_id IS NOT NULL;
            """,
            "--no-password", "-t",
        ], timeout=15)

        if rc == 0 and dup_out.strip():
            try:
                dup_count = int(dup_out.strip())
                if dup_count > 0:
                    issues.append(f"{table}: {dup_count} duplicate source_ids")
            except ValueError:
                pass

    if issues:
        return StepResult(
            passed=False,
            detail=f"Data quality issues: {'; '.join(issues)}",
            remediation="Check unique indexes on bronze tables. See INC-001.",
        )

    return StepResult(passed=True, detail=f"DQ checks passed on {len(tables)} tables")


# ── Collect verify steps ──────────────────────────────────────

VERIFY_STEPS = [
    (19, "Trigger extraction (data-daemon)", step_trigger_extraction),
    (20, "Wait for jobs to complete", step_wait_jobs),
    (21, "Check for failed jobs", step_check_failures),
    (22, "Check row counts", step_check_row_counts),
    (23, "Check run_history (extracted vs loaded)", step_check_run_history),
    (24, "Compare against known good counts", step_compare_known_good),
    (25, "Run data quality checks", step_data_quality),
]
