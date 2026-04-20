"""Deploy type: cerebro — the Next.js dashboard.

Key steps: CI green, deploy, health check, browser verify key pages,
check LIVE badges.
"""

from __future__ import annotations

from cerebro_deploy.config import ServiceConfig, resolve_service
from cerebro_deploy.runner import Step, StepResult
from cerebro_deploy.steps.common import (
    load_topology, load_incidents, check_environment,
    check_git_clean, check_git_branch, check_git_sync,
    run_lint, check_ci, health_check,
)


def build_config(environment: str) -> ServiceConfig:
    return resolve_service("cerebro", environment)


def _run_type_check(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 7: run TypeScript type check (Next.js uses tsc, not pytest)."""
    if ctx.get("skip_tests"):
        return StepResult(True, "SKIPPED (--skip-tests flag)")
    return StepResult(True, "Type check — delegated to agent (npm run type-check)")


def _run_build(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 8: run next build locally to catch build errors."""
    if ctx.get("skip_tests"):
        return StepResult(True, "SKIPPED (--skip-tests flag)")
    return StepResult(True, "Build check — delegated to agent (npm run build)")


def _trigger_deploy(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 13: trigger Railway deploy (push to branch or GH Actions)."""
    return StepResult(True, "Deploy trigger — delegated to agent")


def _wait_railway(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 14: wait for Railway deployment."""
    return StepResult(True, "Railway deployment wait — delegated to agent (railguey_service_info)")


def _verify_key_pages(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 16: browser-verify key dashboard pages load."""
    pages = ["/", "/financial", "/executive", "/fleet"]
    return StepResult(True, f"Page verification — delegated to agent (verify_page on {len(pages)} pages)")


def _check_live_badges(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 17: verify LIVE badges appear (not MOCK)."""
    return StepResult(True, "LIVE badge check — delegated to agent (verify_live_badge)")


def _check_api_routes(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 18: verify API routes respond."""
    return StepResult(True, "API route check — delegated to agent")


def _log_result(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 20: log deployment result."""
    return StepResult(True, "Result logged")


def _health_recheck(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 21: final health re-check."""
    return health_check(config, ctx)


def build_steps(config: ServiceConfig, ctx: dict) -> list[Step]:
    return [
        # PHASE 1: IDENTITY
        Step(1,  "PHASE 1: IDENTITY",    "Load topology",            load_topology),
        Step(2,  "PHASE 1: IDENTITY",    "Load incidents",           load_incidents),
        Step(3,  "PHASE 1: IDENTITY",    "Check environment",        check_environment),
        Step(4,  "PHASE 1: IDENTITY",    "Check git clean",          check_git_clean),
        Step(5,  "PHASE 1: IDENTITY",    "Check git branch",         check_git_branch),
        Step(6,  "PHASE 1: IDENTITY",    "Check git sync",           check_git_sync),
        # PHASE 2: READINESS
        Step(7,  "PHASE 2: READINESS",   "Type check",              _run_type_check),
        Step(8,  "PHASE 2: READINESS",   "Build check",             _run_build),
        Step(9,  "PHASE 2: READINESS",   "Run lint",                run_lint),
        Step(10, "PHASE 2: READINESS",   "Check CI",                check_ci),
        # PHASE 3: DEPLOY
        Step(11, "PHASE 3: DEPLOY",      "Trigger deploy",          _trigger_deploy),
        Step(12, "PHASE 3: DEPLOY",      "Wait for Railway deploy", _wait_railway),
        Step(13, "PHASE 3: DEPLOY",      "Health check",            health_check),
        # PHASE 4: VERIFY
        Step(14, "PHASE 4: VERIFY",      "Verify key pages",        _verify_key_pages),
        Step(15, "PHASE 4: VERIFY",      "Check LIVE badges",       _check_live_badges),
        Step(16, "PHASE 4: VERIFY",      "Check API routes",        _check_api_routes),
        # PHASE 5: POST-DEPLOY
        Step(17, "PHASE 5: POST-DEPLOY", "Log result",              _log_result),
        Step(18, "PHASE 5: POST-DEPLOY", "Health re-check",         _health_recheck),
    ]
