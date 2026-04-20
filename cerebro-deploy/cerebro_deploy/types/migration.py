"""Deploy type: migration — apply a cerebro-migrations DDL.

Key steps: check schema parity between staging/prod, apply via supabase CLI,
register in tracking table, verify tables exist.
"""

from __future__ import annotations

import os

from cerebro_deploy.config import ServiceConfig
from cerebro_deploy.runner import Step, StepResult
from cerebro_deploy.steps.preflight import (
    step_git_status, step_git_branch, step_git_remote,
    step_check_incidents,
)


def build_config(migration_name: str) -> ServiceConfig:
    """Build a pseudo-ServiceConfig for migration deploys.

    Migrations target the cerebro-migrations repo and the Supabase database.
    """
    return ServiceConfig(
        name="cerebro-migrations",
        repo="greenmark-waste-solutions/cerebro-migrations",
        runtime="Supabase",
        environment="production",
        deploy_pipeline={"method": "supabase-cli"},
        connections={},
        credentials=["SUPABASE_DB_URL"],
        branch="main",
        health_url="",
    )


def _find_migration_file(config: ServiceConfig, ctx: dict) -> StepResult:
    """Locate the migration file in cerebro-migrations repo."""
    migration_name = ctx.get("target", "")
    repo_dir = os.path.expanduser("~/repos/cerebro-migrations")

    if not os.path.isdir(repo_dir):
        return StepResult(
            passed=False,
            detail=f"cerebro-migrations repo not found at {repo_dir}",
            remediation="Clone: gh repo clone greenmark-waste-solutions/cerebro-migrations ~/repos/cerebro-migrations",
        )

    # Walk to find matching migration file
    candidates = []
    for root, _dirs, files in os.walk(repo_dir):
        # Skip .git
        if ".git" in root:
            continue
        for f in files:
            if migration_name in f and f.endswith(".sql"):
                candidates.append(os.path.join(root, f))

    if not candidates:
        return StepResult(
            passed=False,
            detail=f"No migration file matching '{migration_name}' found in {repo_dir}",
            remediation="Check spelling. List available: ls ~/repos/cerebro-migrations/supabase/migrations/",
        )

    ctx["migration_file"] = candidates[0]
    return StepResult(passed=True, detail=f"Found: {candidates[0]}")


def _check_schema_parity(config: ServiceConfig, ctx: dict) -> StepResult:
    """Compare staging and production schemas for drift."""
    return StepResult(
        passed=True,
        detail="Schema parity check — delegated to agent (run_sql on both envs)",
    )


def _validate_sql(config: ServiceConfig, ctx: dict) -> StepResult:
    """Basic SQL validation of migration file."""
    migration_file = ctx.get("migration_file")
    if not migration_file:
        return StepResult(passed=False, detail="No migration file in context")

    try:
        with open(migration_file) as f:
            sql = f.read()
    except OSError as e:
        return StepResult(passed=False, detail=f"Cannot read migration: {e}")

    if not sql.strip():
        return StepResult(passed=False, detail="Migration file is empty")

    # Greenmark rule: soft deletes only
    dangerous = ["DROP DATABASE", "TRUNCATE", "DROP SCHEMA"]
    for d in dangerous:
        if d.upper() in sql.upper():
            return StepResult(
                passed=False,
                detail=f"Migration contains dangerous statement: {d}",
                remediation="Greenmark uses soft deletes only. Review the migration.",
            )

    line_count = len(sql.strip().split("\n"))
    return StepResult(passed=True, detail=f"{line_count} lines, no dangerous statements detected")


def _apply_migration(config: ServiceConfig, ctx: dict) -> StepResult:
    """Apply migration via supabase CLI or psql."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN — would apply migration")
    return StepResult(
        passed=True,
        detail="Migration apply — delegated to agent (supabase db push or psql)",
    )


def _register_in_tracking(config: ServiceConfig, ctx: dict) -> StepResult:
    """Register migration in tracking table."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    return StepResult(
        passed=True,
        detail="Tracking registration — delegated to agent (INSERT into migrations table)",
    )


def _verify_tables_exist(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify the migration created expected objects."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    return StepResult(
        passed=True,
        detail="Table verification — delegated to agent (information_schema query)",
    )


def _verify_rls(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify RLS policies on new tables."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    return StepResult(
        passed=True,
        detail="RLS verification — delegated to agent (pg_policies query)",
    )


def build_steps(config: ServiceConfig, ctx: dict) -> list[Step]:
    return [
        # PHASE 1: PRE-FLIGHT
        Step(1,  "Phase 1: Pre-flight", "Find migration file",      _find_migration_file),
        Step(2,  "Phase 1: Pre-flight", "Check incidents",          step_check_incidents),
        Step(3,  "Phase 1: Pre-flight", "Check git status (clean)", step_git_status),
        Step(4,  "Phase 1: Pre-flight", "Check git branch",         step_git_branch),
        Step(5,  "Phase 1: Pre-flight", "Check remote sync",        step_git_remote),
        # PHASE 2: READINESS
        Step(6,  "Phase 2: Readiness",  "Check schema parity",     _check_schema_parity),
        Step(7,  "Phase 2: Readiness",  "Validate SQL",            _validate_sql),
        # PHASE 3: APPLY
        Step(8,  "Phase 3: Apply",      "Apply migration",         _apply_migration),
        Step(9,  "Phase 3: Apply",      "Register in tracking",    _register_in_tracking),
        # PHASE 4: VERIFY
        Step(10, "Phase 4: Verify",     "Verify tables exist",     _verify_tables_exist),
        Step(11, "Phase 4: Verify",     "Verify RLS policies",     _verify_rls),
    ]
