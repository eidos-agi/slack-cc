"""Deploy type: cerebro — the Next.js dashboard.

Key steps: CI green, deploy, health check, browser verify key pages,
check LIVE badges.
"""

from __future__ import annotations

from cerebro_deploy.config import ServiceConfig, resolve_service
from cerebro_deploy.runner import Step, StepResult
from cerebro_deploy.steps.preflight import (
    step_read_topology, step_git_status, step_git_branch,
    step_git_remote, step_run_lint, step_ci_status,
    step_check_incidents, step_verify_credentials,
)
from cerebro_deploy.steps.deploy import step_verify_health
from cerebro_deploy.steps.postdeploy import (
    step_update_topology_file, step_log_incidents, step_done,
)


def build_config(environment: str) -> ServiceConfig:
    return resolve_service("cerebro", environment)


def _run_type_check(config: ServiceConfig, ctx: dict) -> StepResult:
    """Run TypeScript type check (Next.js uses tsc, not pytest)."""
    if ctx.get("skip_tests"):
        return StepResult(passed=True, detail="SKIPPED (--skip-tests flag)")
    return StepResult(passed=True, detail="Type check — delegated to agent (npm run type-check)")


def _run_build(config: ServiceConfig, ctx: dict) -> StepResult:
    """Run next build locally to catch build errors."""
    if ctx.get("skip_tests"):
        return StepResult(passed=True, detail="SKIPPED (--skip-tests flag)")
    return StepResult(passed=True, detail="Build check — delegated to agent (npm run build)")


def _trigger_deploy(config: ServiceConfig, ctx: dict) -> StepResult:
    """Trigger Railway deploy (push to branch or GH Actions)."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN — would trigger deploy")
    return StepResult(passed=True, detail="Deploy trigger — delegated to agent (railguey_deploy)")


def _wait_railway(config: ServiceConfig, ctx: dict) -> StepResult:
    """Wait for Railway deployment to succeed."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    return StepResult(passed=True, detail="Railway deployment wait — delegated to agent (railguey_service_info)")


def _verify_key_pages(config: ServiceConfig, ctx: dict) -> StepResult:
    """Browser-verify key dashboard pages load."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    pages = ["/", "/financial", "/executive", "/fleet"]
    return StepResult(passed=True, detail=f"Page verification — delegated to agent (verify_page on {len(pages)} pages)")


def _check_live_badges(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify LIVE badges appear (not MOCK)."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    return StepResult(passed=True, detail="LIVE badge check — delegated to agent (verify_live_badge)")


def _check_api_routes(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify API routes respond."""
    if ctx.get("dry_run"):
        return StepResult(passed=True, detail="DRY RUN")
    return StepResult(passed=True, detail="API route check — delegated to agent")


def build_steps(config: ServiceConfig, ctx: dict) -> list[Step]:
    return [
        # PHASE 1: PRE-FLIGHT (reuses existing data-daemon preflight steps)
        Step(1,  "Phase 1: Pre-flight",  "Read topology",            step_read_topology),
        Step(2,  "Phase 1: Pre-flight",  "Check git status (clean)", step_git_status),
        Step(3,  "Phase 1: Pre-flight",  "Check git branch",         step_git_branch),
        Step(4,  "Phase 1: Pre-flight",  "Check remote sync",        step_git_remote),
        Step(5,  "Phase 1: Pre-flight",  "Type check",               _run_type_check),
        Step(6,  "Phase 1: Pre-flight",  "Build check",              _run_build),
        Step(7,  "Phase 1: Pre-flight",  "Run lint",                 step_run_lint),
        Step(8,  "Phase 1: Pre-flight",  "Check CI status",          step_ci_status),
        Step(9,  "Phase 1: Pre-flight",  "Check incidents",          step_check_incidents),
        Step(10, "Phase 1: Pre-flight",  "Verify credentials",       step_verify_credentials),
        # PHASE 2: DEPLOY
        Step(11, "Phase 2: Deploy",      "Trigger deploy",           _trigger_deploy),
        Step(12, "Phase 2: Deploy",      "Wait for Railway deploy",  _wait_railway),
        Step(13, "Phase 2: Deploy",      "Verify health endpoint",   step_verify_health),
        # PHASE 3: VERIFY
        Step(14, "Phase 3: Verify",      "Verify key pages",         _verify_key_pages),
        Step(15, "Phase 3: Verify",      "Check LIVE badges",        _check_live_badges),
        Step(16, "Phase 3: Verify",      "Check API routes",         _check_api_routes),
        # PHASE 4: POST-DEPLOY
        Step(17, "Phase 4: Post-deploy", "Update topology",          step_update_topology_file),
        Step(18, "Phase 4: Post-deploy", "Log incidents",            step_log_incidents),
        Step(19, "Phase 4: Post-deploy", "Done",                     step_done),
    ]
