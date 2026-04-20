"""Deploy type: migration — apply a cerebro-migrations DDL.

Key steps: check schema parity between staging/prod, apply via supabase CLI,
register in tracking table, verify tables exist.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import Any

from cerebro_deploy.config import ServiceConfig
from cerebro_deploy.runner import Step, StepResult
from cerebro_deploy.steps.common import (
    load_incidents, check_git_clean, check_git_branch, check_git_sync,
    _run, _find_repo_dir,
)


def build_config(migration_name: str) -> ServiceConfig:
    """Build a pseudo-ServiceConfig for migration deploys.

    Migrations target the cerebro-migrations repo and the Supabase database.
    """
    return ServiceConfig(
        name="cerebro-migrations",
        repo="greenmark-waste-solutions/cerebro-migrations",
        runtime="Supabase",
        environment="production",  # migrations apply to both, but we track against prod
        deploy_pipeline={"method": "supabase-cli"},
        connections={},
        credentials=["SUPABASE_DB_URL"],
        branch="main",
        health_url="",
    )


def _find_migration_file(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 1: locate the migration file."""
    migration_name = ctx.get("target", "")
    repo_dir = _find_repo_dir(config)
    if not repo_dir:
        repo_dir = os.path.expanduser("~/repos/cerebro-migrations")

    if not os.path.isdir(repo_dir):
        return StepResult(False, f"cerebro-migrations repo not found at {repo_dir}",
                          "Clone the repo: gh repo clone greenmark-waste-solutions/cerebro-migrations")

    # Look for migration file — could be in migrations/ or supabase/migrations/
    candidates = []
    for root, dirs, files in os.walk(repo_dir):
        for f in files:
            if migration_name in f and f.endswith(".sql"):
                candidates.append(os.path.join(root, f))

    if not candidates:
        return StepResult(False, f"No migration file matching '{migration_name}' found",
                          f"Check migration name. Available files in {repo_dir}")

    ctx["migration_file"] = candidates[0]
    return StepResult(True, f"Found: {candidates[0]}")


def _check_schema_parity(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 2: compare staging and production schemas for drift."""
    return StepResult(True, "Schema parity check — delegated to agent (run_sql on both envs)")


def _validate_sql(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 3: basic SQL validation of migration file."""
    migration_file = ctx.get("migration_file")
    if not migration_file:
        return StepResult(False, "No migration file in context")

    with open(migration_file) as f:
        sql = f.read()

    if not sql.strip():
        return StepResult(False, "Migration file is empty")

    # Basic safety checks
    dangerous = ["DROP DATABASE", "TRUNCATE", "DROP SCHEMA"]
    for d in dangerous:
        if d.upper() in sql.upper():
            return StepResult(False, f"Migration contains dangerous statement: {d}",
                              "Review the migration carefully. Greenmark uses soft deletes only.")

    line_count = len(sql.strip().split("\n"))
    return StepResult(True, f"{line_count} lines, no dangerous statements detected")


def _apply_migration(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 4: apply migration via supabase CLI."""
    return StepResult(True, "Migration apply — delegated to agent (supabase db push or psql)")


def _register_in_tracking(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 5: register migration in tracking table."""
    return StepResult(True, "Tracking registration — delegated to agent (INSERT into migrations table)")


def _verify_tables_exist(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 6: verify the migration created expected objects."""
    return StepResult(True, "Table verification — delegated to agent (information_schema query)")


def _verify_rls(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 7: verify RLS policies on new tables."""
    return StepResult(True, "RLS verification — delegated to agent")


def build_steps(config: ServiceConfig, ctx: dict) -> list[Step]:
    return [
        # PHASE 1: IDENTITY
        Step(1, "PHASE 1: IDENTITY",   "Find migration file",      _find_migration_file),
        Step(2, "PHASE 1: IDENTITY",   "Load incidents",           load_incidents),
        Step(3, "PHASE 1: IDENTITY",   "Check git clean",          check_git_clean),
        Step(4, "PHASE 1: IDENTITY",   "Check git branch",         check_git_branch),
        Step(5, "PHASE 1: IDENTITY",   "Check git sync",           check_git_sync),
        # PHASE 2: READINESS
        Step(6, "PHASE 2: READINESS",  "Check schema parity",      _check_schema_parity),
        Step(7, "PHASE 2: READINESS",  "Validate SQL",             _validate_sql),
        # PHASE 3: APPLY
        Step(8,  "PHASE 3: APPLY",     "Apply migration",          _apply_migration),
        Step(9,  "PHASE 3: APPLY",     "Register in tracking",     _register_in_tracking),
        # PHASE 4: VERIFY
        Step(10, "PHASE 4: VERIFY",    "Verify tables exist",      _verify_tables_exist),
        Step(11, "PHASE 4: VERIFY",    "Verify RLS policies",      _verify_rls),
    ]
