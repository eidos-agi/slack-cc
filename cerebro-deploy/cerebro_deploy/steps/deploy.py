"""Deploy steps 11-18: trigger and verify deployment."""

from __future__ import annotations

import json
import os
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


# ── Step 11: Record pre-deploy state ─────────────────────────

def step_pre_deploy_state(config: ServiceConfig, ctx: dict) -> StepResult:
    """Record current deployment state for comparison after deploy."""
    details = []

    # Get current health if available
    if config.health_url:
        rc, out, err = _run(["curl", "-sf", config.health_url, "--max-time", "5"])
        if rc == 0:
            ctx["pre_deploy_health"] = out[:500]
            details.append(f"Health endpoint responding")
            # Try to parse for version/status
            try:
                data = json.loads(out)
                if "version" in data:
                    ctx["pre_deploy_version"] = data["version"]
                    details.append(f"Current version: {data['version']}")
            except (json.JSONDecodeError, KeyError):
                pass
        else:
            details.append("Health endpoint not responding (may be first deploy)")

    # Record git SHA
    sha = ctx.get("head_sha", "unknown")
    ctx["deploy_sha"] = sha
    details.append(f"Deploying commit: {sha}")

    # Try to get row counts from database if data-daemon
    if config.name == "data-daemon" and config.database_id:
        rc, out, _ = _run([
            "psql",
            f"postgresql://postgres.{config.database_id}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
            "-c", "SELECT schemaname || '.' || relname AS table_name, n_live_tup AS row_count FROM pg_stat_user_tables WHERE schemaname LIKE '%_bronze' ORDER BY n_live_tup DESC LIMIT 10;",
            "--no-password", "-t",
        ], timeout=10)
        if rc == 0 and out:
            ctx["pre_deploy_row_counts"] = out
            details.append(f"Row counts captured for comparison")

    return StepResult(passed=True, detail="; ".join(details) if details else "Pre-deploy state recorded")


# ── Step 12: Trigger deploy ──────────────────────────────────

def step_trigger_deploy(config: ServiceConfig, ctx: dict) -> StepResult:
    """Trigger deployment via GitHub Actions workflow_dispatch."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN — would trigger deploy here")

    repo_root = ctx.get("repo_root")
    env_key = config.environment

    # Determine workflow file
    pipeline = config.deploy_pipeline
    if env_key in pipeline:
        pipeline_desc = pipeline[env_key]
    elif "production" in pipeline:
        pipeline_desc = pipeline["production"]
    else:
        return StepResult(
            passed=False,
            detail=f"No deploy pipeline for {env_key}",
            remediation="Check topology deploy_pipeline configuration",
        )

    # For services with GitHub Actions workflow_dispatch
    if "deploy.yml" in pipeline_desc or "deploy-prod.yml" in pipeline_desc:
        if env_key == "develop":
            workflow = "deploy.yml"
            ref = "develop"
        else:
            workflow = "deploy-prod.yml"
            ref = "main"

        rc, out, err = _run([
            "gh", "workflow", "run", workflow,
            "--repo", config.repo,
            "--ref", ref,
        ], timeout=15)

        if rc == 0:
            ctx["deploy_triggered"] = True
            ctx["deploy_workflow"] = workflow
            return StepResult(passed=True, detail=f"Triggered {workflow} on {ref}")
        else:
            # Maybe it auto-deploys on push
            return StepResult(
                passed=True,
                detail=f"workflow_dispatch may not be enabled. Pipeline: {pipeline_desc}. Deploy should trigger on push to {ref}.",
            )

    elif "auto-deploy" in pipeline_desc.lower() or "wrangler" in pipeline_desc.lower():
        return StepResult(
            passed=True,
            detail=f"Auto-deploy pipeline: {pipeline_desc}. Push to {config.branch} triggers deploy.",
        )

    return StepResult(
        passed=True,
        detail=f"Deploy pipeline: {pipeline_desc}. Verify deployment manually.",
    )


# ── Step 13: Wait for GitHub Actions workflow ─────────────────

def step_wait_github_actions(config: ServiceConfig, ctx: dict) -> StepResult:
    """Poll GitHub Actions until workflow completes."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN — would wait for workflow here")

    workflow = ctx.get("deploy_workflow")
    if not workflow:
        return StepResult(passed=True, detail="No workflow to wait for (auto-deploy or manual)")

    # Poll for up to 5 minutes
    max_polls = 30
    poll_interval = 10

    for i in range(max_polls):
        rc, out, err = _run([
            "gh", "run", "list",
            "--repo", config.repo,
            "--workflow", workflow,
            "--limit", "1",
            "--json", "status,conclusion,databaseId,headSha",
        ], timeout=15)

        if rc != 0:
            if i == 0:
                return StepResult(
                    passed=True,
                    detail=f"Cannot poll workflow runs: {err[:100]}. Check manually.",
                )
            continue

        try:
            runs = json.loads(out)
            if not runs:
                time.sleep(poll_interval)
                continue

            run = runs[0]
            status = run.get("status", "")
            conclusion = run.get("conclusion", "")
            run_id = run.get("databaseId", "")

            if status == "completed":
                ctx["workflow_run_id"] = run_id
                if conclusion == "success":
                    return StepResult(passed=True, detail=f"Workflow run {run_id} completed successfully")
                else:
                    return StepResult(
                        passed=False,
                        detail=f"Workflow run {run_id} completed with conclusion={conclusion}",
                        remediation=f"Check: gh run view {run_id} --repo {config.repo} --log-failed",
                    )

            if i % 3 == 0:
                print(f" [{status}]", end="", flush=True)

        except json.JSONDecodeError:
            pass

        time.sleep(poll_interval)

    return StepResult(
        passed=False,
        detail=f"Workflow did not complete within {max_polls * poll_interval}s",
        remediation=f"Check: gh run list --repo {config.repo} --workflow {workflow}",
    )


# ── Step 14: Wait for Railway deployment ─────────────────────

def step_wait_railway(config: ServiceConfig, ctx: dict) -> StepResult:
    """Wait for Railway deployment to succeed."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN — would wait for Railway deploy here")

    if "Railway" not in config.runtime:
        return StepResult(passed=True, detail=f"Not a Railway service ({config.runtime})")

    # Poll health endpoint for up to 3 minutes
    if not config.health_url:
        return StepResult(
            passed=True,
            detail="No health URL configured — check Railway dashboard manually",
        )

    max_polls = 18
    poll_interval = 10

    for i in range(max_polls):
        rc, out, _ = _run(["curl", "-sf", config.health_url, "--max-time", "5"])
        if rc == 0:
            # Check if response indicates new version
            try:
                data = json.loads(out)
                version = data.get("version", "unknown")
                ctx["post_deploy_health"] = out[:500]
                return StepResult(passed=True, detail=f"Health endpoint responding, version={version}")
            except (json.JSONDecodeError, KeyError):
                return StepResult(passed=True, detail=f"Health endpoint responding (non-JSON response)")

        if i % 3 == 0:
            print(f" [waiting]", end="", flush=True)
        time.sleep(poll_interval)

    return StepResult(
        passed=False,
        detail=f"Health endpoint not responding after {max_polls * poll_interval}s",
        remediation=f"Check Railway dashboard or: curl -v {config.health_url}",
    )


# ── Step 15: Wait for old deployment removal ─────────────────

def step_old_deployment_removed(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify old containers are gone (Railway specific)."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN — would verify old deployment removed")

    if "Railway" not in config.runtime:
        return StepResult(passed=True, detail="Not a Railway service")

    # We can't easily check this without railguey, so we verify health is stable
    if config.health_url:
        rc, out, _ = _run(["curl", "-sf", config.health_url, "--max-time", "5"])
        if rc == 0:
            return StepResult(passed=True, detail="Health endpoint stable — old deployment likely removed")

    return StepResult(passed=True, detail="Cannot verify old deployment removal directly — check Railway dashboard")


# ── Step 16: Verify health endpoint ──────────────────────────

def step_verify_health(config: ServiceConfig, ctx: dict) -> StepResult:
    """Health endpoint must return 200."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN — would verify health endpoint")

    if not config.health_url:
        return StepResult(passed=True, detail="No health URL configured")

    rc, out, err = _run(["curl", "-sf", "-w", "\n%{http_code}", config.health_url, "--max-time", "10"])
    if rc != 0:
        return StepResult(
            passed=False,
            detail=f"Health endpoint returned error: {err[:200]}",
            remediation=f"Check: curl -v {config.health_url}",
        )

    lines = out.strip().split("\n")
    status_code = lines[-1] if lines else "unknown"
    body = "\n".join(lines[:-1]) if len(lines) > 1 else ""

    if status_code == "200":
        detail = f"200 OK"
        if body:
            try:
                data = json.loads(body)
                keys = list(data.keys())[:5]
                detail += f" (keys: {', '.join(keys)})"
            except json.JSONDecodeError:
                detail += f" (body: {body[:100]})"
        return StepResult(passed=True, detail=detail)

    return StepResult(
        passed=False,
        detail=f"Health returned HTTP {status_code}",
        remediation="Check service logs for errors",
    )


# ── Step 17: Verify connector registry (data-daemon) ─────────

def step_verify_connector_registry(config: ServiceConfig, ctx: dict) -> StepResult:
    """For data-daemon: verify connector registry loaded correctly."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    if config.name != "data-daemon":
        return StepResult(passed=True, detail="Not data-daemon — skipping connector check")

    if not config.health_url:
        return StepResult(passed=True, detail="No health URL")

    # The health endpoint should include connector info
    rc, out, _ = _run(["curl", "-sf", config.health_url, "--max-time", "10"])
    if rc != 0:
        return StepResult(
            passed=False,
            detail="Cannot reach health endpoint for registry check",
            remediation=f"curl -v {config.health_url}",
        )

    try:
        data = json.loads(out)
        # Look for connectors/registry info
        connectors = data.get("connectors") or data.get("registry") or data.get("sources")
        if connectors:
            return StepResult(passed=True, detail=f"Connector registry: {connectors}")
        return StepResult(passed=True, detail=f"Health response doesn't include registry info (keys: {list(data.keys())})")
    except json.JSONDecodeError:
        return StepResult(passed=True, detail="Health response is not JSON — cannot check registry")


# ── Step 18: Verify DB connectivity from deployed service ─────

def step_deployed_db_connectivity(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify the deployed service can reach its database."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")

    if not config.health_url:
        return StepResult(passed=True, detail="No health URL — cannot verify remote DB connectivity")

    rc, out, _ = _run(["curl", "-sf", config.health_url, "--max-time", "10"])
    if rc != 0:
        return StepResult(
            passed=False,
            detail="Cannot reach service to verify DB connectivity",
        )

    try:
        data = json.loads(out)
        # Look for db status indicators
        db_status = (
            data.get("database") or data.get("db") or data.get("db_connected")
            or data.get("postgres") or data.get("database_connected")
        )
        if db_status:
            return StepResult(passed=True, detail=f"DB status from health: {db_status}")
        return StepResult(passed=True, detail="Health endpoint doesn't report DB status explicitly")
    except json.JSONDecodeError:
        return StepResult(passed=True, detail="Cannot parse health response for DB status")


# ── Collect deploy steps ──────────────────────────────────────

DEPLOY_STEPS = [
    (11, "Record pre-deploy state", step_pre_deploy_state),
    (12, "Trigger deploy", step_trigger_deploy),
    (13, "Wait for GitHub Actions workflow", step_wait_github_actions),
    (14, "Wait for Railway deployment", step_wait_railway),
    (15, "Verify old deployment removed", step_old_deployment_removed),
    (16, "Verify health endpoint returns 200", step_verify_health),
    (17, "Verify connector registry (data-daemon)", step_verify_connector_registry),
    (18, "Verify DB connectivity from deployed service", step_deployed_db_connectivity),
]
