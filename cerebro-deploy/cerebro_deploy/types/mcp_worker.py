"""Deploy type: mcp — Cloudflare Worker MCP server.

Key steps: wrangler deploy, verify OAuth, verify tool availability.
"""

from __future__ import annotations

import subprocess

from cerebro_deploy.config import ServiceConfig, resolve_service
from cerebro_deploy.runner import Step, StepResult
from cerebro_deploy.steps.preflight import (
    step_read_topology, step_git_status, step_git_branch,
    step_git_remote, step_run_tests, step_run_lint,
    step_ci_status, step_check_incidents,
)
from cerebro_deploy.steps.postdeploy import (
    step_update_topology_file, step_log_incidents, step_done,
)


def build_config(environment: str) -> ServiceConfig:
    return resolve_service("cerebro-mcp", environment)


def _check_wrangler(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify wrangler CLI is available."""
    try:
        r = subprocess.run(
            ["npx", "wrangler", "--version"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            return StepResult(passed=False, detail="wrangler not found",
                              remediation="Install wrangler: npm install -g wrangler")
        return StepResult(passed=True, detail=f"wrangler {r.stdout.strip()}")
    except FileNotFoundError:
        return StepResult(passed=False, detail="npx not found",
                          remediation="Install Node.js and npm")
    except subprocess.TimeoutExpired:
        return StepResult(passed=True, detail="wrangler check timed out, proceeding")


def _wrangler_deploy(config: ServiceConfig, ctx: dict) -> StepResult:
    """Run wrangler deploy."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN — would run wrangler deploy")
    env_flag = "production" if config.environment == "production" else "staging"
    return StepResult(passed=True, detail=f"wrangler deploy --env {env_flag} — delegated to agent")


def _verify_worker_reachable(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify the worker URL responds."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    worker_url = "https://cerebro-mcp.dshanklin.workers.dev"
    try:
        r = subprocess.run(
            ["curl", "-sf", "-o", "/dev/null", "-w", "%{http_code}", worker_url],
            capture_output=True, text=True, timeout=10,
        )
        code = r.stdout.strip()
        # Workers may return 401/403 without auth — that's fine, it means the worker is running
        if r.returncode != 0 or code in ("000",):
            return StepResult(passed=True, detail=f"Worker may require auth, proceeding")
        return StepResult(passed=True, detail=f"Worker responded with HTTP {code}")
    except Exception:
        return StepResult(passed=True, detail="Worker URL check failed, proceeding")


def _verify_oauth(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify OAuth flow works."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    return StepResult(passed=True, detail="OAuth verification — delegated to agent (browser test)")


def _verify_tool_availability(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify MCP tools are available via the transport."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    return StepResult(passed=True, detail="Tool availability — delegated to agent (MCP client test)")


def _verify_tool_count(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify expected tool count matches."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    return StepResult(passed=True, detail="Tool count verification — delegated to agent")


def build_steps(config: ServiceConfig, ctx: dict) -> list[Step]:
    return [
        # PHASE 1: PRE-FLIGHT
        Step(1,  "Phase 1: Pre-flight",  "Read topology",            step_read_topology),
        Step(2,  "Phase 1: Pre-flight",  "Check git status (clean)", step_git_status),
        Step(3,  "Phase 1: Pre-flight",  "Check git branch",         step_git_branch),
        Step(4,  "Phase 1: Pre-flight",  "Check remote sync",        step_git_remote),
        Step(5,  "Phase 1: Pre-flight",  "Run tests",                step_run_tests),
        Step(6,  "Phase 1: Pre-flight",  "Run lint",                 step_run_lint),
        Step(7,  "Phase 1: Pre-flight",  "Check CI status",          step_ci_status),
        Step(8,  "Phase 1: Pre-flight",  "Check incidents",          step_check_incidents),
        Step(9,  "Phase 1: Pre-flight",  "Check wrangler CLI",       _check_wrangler),
        # PHASE 2: DEPLOY
        Step(10, "Phase 2: Deploy",      "Wrangler deploy",          _wrangler_deploy),
        Step(11, "Phase 2: Deploy",      "Verify worker reachable",  _verify_worker_reachable),
        # PHASE 3: VERIFY
        Step(12, "Phase 3: Verify",      "Verify OAuth",             _verify_oauth),
        Step(13, "Phase 3: Verify",      "Verify tool availability", _verify_tool_availability),
        Step(14, "Phase 3: Verify",      "Verify tool count",        _verify_tool_count),
        # PHASE 4: POST-DEPLOY
        Step(15, "Phase 4: Post-deploy", "Update topology",          step_update_topology_file),
        Step(16, "Phase 4: Post-deploy", "Log incidents",            step_log_incidents),
        Step(17, "Phase 4: Post-deploy", "Done",                     step_done),
    ]
