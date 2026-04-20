"""Post-deploy steps 26-30: log, summarize, update topology."""

from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone

from cerebro_deploy.config import ServiceConfig, get_incidents
from cerebro_deploy.runner import StepResult


def _run(cmd: list[str], cwd: str | None = None, timeout: int = 60) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"


# ── Step 26: Update topology ─────────────────────────────────

def step_update_topology_file(config: ServiceConfig, ctx: dict) -> StepResult:
    """Update .railguey/topology.json with deploy result."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    topology_path = os.path.expanduser("~/.railguey/topology.json")
    now = datetime.now(timezone.utc).isoformat()

    deploy_record = {
        "service": config.name,
        "environment": config.environment,
        "sha": ctx.get("deploy_sha", "unknown"),
        "timestamp": now,
        "workflow_run_id": ctx.get("workflow_run_id"),
        "status": "success",
    }

    # Read existing topology or create new
    topology = {}
    if os.path.isfile(topology_path):
        try:
            with open(topology_path) as f:
                topology = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    # Append to deploys list
    if "deploys" not in topology:
        topology["deploys"] = []
    topology["deploys"].append(deploy_record)

    # Keep last 50 deploys
    topology["deploys"] = topology["deploys"][-50:]

    try:
        os.makedirs(os.path.dirname(topology_path), exist_ok=True)
        with open(topology_path, "w") as f:
            json.dump(topology, f, indent=2)
        return StepResult(passed=True, detail=f"Deploy record written to {topology_path}")
    except OSError as e:
        return StepResult(passed=True, detail=f"Cannot write topology file: {e} (non-critical)")


# ── Step 27: Log incidents ───────────────────────────────────

def step_log_incidents(config: ServiceConfig, ctx: dict) -> StepResult:
    """Log any issues that occurred during deployment."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    failed_jobs = ctx.get("failed_jobs", [])

    if not failed_jobs:
        return StepResult(passed=True, detail="No issues to log")

    # Log to a local incidents file
    incidents_path = os.path.expanduser("~/.railguey/deploy-incidents.jsonl")
    now = datetime.now(timezone.utc).isoformat()

    try:
        os.makedirs(os.path.dirname(incidents_path), exist_ok=True)
        with open(incidents_path, "a") as f:
            for job in failed_jobs:
                record = {
                    "timestamp": now,
                    "service": config.name,
                    "environment": config.environment,
                    "type": "failed_job",
                    "source": job.get("source_type"),
                    "error": job.get("error", "")[:200],
                }
                f.write(json.dumps(record) + "\n")
        return StepResult(passed=True, detail=f"Logged {len(failed_jobs)} issues to {incidents_path}")
    except OSError as e:
        return StepResult(passed=True, detail=f"Cannot write incidents: {e} (non-critical)")


# ── Step 28: Print summary ───────────────────────────────────

def step_print_summary(config: ServiceConfig, ctx: dict) -> StepResult:
    """Print deployment summary with before/after comparison."""
    parts = []

    parts.append(f"Service: {config.name}")
    parts.append(f"Environment: {config.environment}")
    parts.append(f"Commit: {ctx.get('deploy_sha', 'unknown')}")

    pre_version = ctx.get("pre_deploy_version")
    if pre_version:
        parts.append(f"Pre-deploy version: {pre_version}")

    workflow_run = ctx.get("workflow_run_id")
    if workflow_run:
        parts.append(f"Workflow run: {workflow_run}")

    triggered = ctx.get("triggered_sources", [])
    if triggered:
        parts.append(f"Extractions triggered: {', '.join(triggered)}")

    completed = ctx.get("completed_jobs", [])
    if completed:
        parts.append(f"Jobs completed: {len(completed)}")

    failed = ctx.get("failed_jobs", [])
    if failed:
        parts.append(f"Jobs failed: {len(failed)}")

    if ctx.get("dry_run"):
        parts.insert(0, "DRY RUN — no actual deployment performed")

    return StepResult(passed=True, detail="; ".join(parts))


# ── Step 29: Update cerebro-docs topology ─────────────────────

def step_update_cerebro_docs(config: ServiceConfig, ctx: dict) -> StepResult:
    """Remind to update cerebro-docs if deploy pipeline changed."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    # This is informational — we don't auto-edit knowledge.py
    return StepResult(
        passed=True,
        detail="If deploy pipeline changed, update TOPOLOGY in cerebro-docs-mcp/cerebro_docs/knowledge.py",
    )


# ── Step 30: Done ────────────────────────────────────────────

def step_done(config: ServiceConfig, ctx: dict) -> StepResult:
    """Final confirmation."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN complete — pre-flight passed, no deploy performed")

    sha = ctx.get("deploy_sha", "unknown")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return StepResult(
        passed=True,
        detail=f"Deploy of {config.name} to {config.environment} verified at {now}, commit {sha}",
    )


# ── Collect post-deploy steps ─────────────────────────────────

POSTDEPLOY_STEPS = [
    (26, "Update topology record", step_update_topology_file),
    (27, "Log incidents (if any)", step_log_incidents),
    (28, "Print summary", step_print_summary),
    (29, "Update cerebro-docs (if needed)", step_update_cerebro_docs),
    (30, "Done", step_done),
]
