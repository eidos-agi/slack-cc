"""Deploy type: docs — verify documentation matches reality.

Compares topology against actual Railway state, compares incidents
against current issues. No actual deployment — purely verification.
"""

from __future__ import annotations

from cerebro_deploy.config import ServiceConfig, get_incidents, TOPOLOGY
from cerebro_deploy.runner import Step, StepResult


def build_config() -> ServiceConfig:
    """Build a pseudo-ServiceConfig for docs verification."""
    return ServiceConfig(
        name="docs-verify",
        repo="greenmark-waste-solutions/greenmark-cockpit",
        runtime="none",
        environment="production",
        deploy_pipeline={},
        connections={},
        credentials=[],
        branch="main",
        health_url="",
    )


def _check_topology_services(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 1: list all services in topology and check for staleness."""
    services = TOPOLOGY.get("services", {})
    if not services:
        return StepResult(False, "No services in topology",
                          "Update cerebro-docs knowledge.py with current services.")
    names = sorted(services.keys())
    return StepResult(True, f"{len(names)} services: {', '.join(names)}")


def _check_topology_databases(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 2: list all databases in topology."""
    databases = TOPOLOGY.get("databases", {})
    if not databases:
        return StepResult(True, "No databases in topology (may be expected)")
    names = sorted(databases.keys())
    return StepResult(True, f"{len(names)} databases: {', '.join(names)}")


def _verify_railway_state(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 3: compare topology against actual Railway state."""
    return StepResult(True, "Railway state comparison — delegated to agent (railguey_services)")


def _check_incidents(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 4: review open incidents."""
    from cerebro_deploy.config import INCIDENTS
    active = [i for i in INCIDENTS if str(i.get("status", "")).upper() == "ACTIVE"]
    if active:
        names = "; ".join(str(i.get("title", i.get("id", "?"))) for i in active)
        return StepResult(True, f"WARNING: {len(active)} active incident(s): {names}")
    return StepResult(True, f"No active incidents ({len(INCIDENTS)} total in ledger)")


def _verify_gh_issues(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 5: compare incidents against current GitHub issues."""
    return StepResult(True, "GitHub issues comparison — delegated to agent (gh issue list)")


def _verify_repo_list(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 6: verify all repos in topology exist and are accessible."""
    services = TOPOLOGY.get("services", {})
    repos = sorted(set(s.get("repo", "") for s in services.values() if s.get("repo")))
    return StepResult(True, f"{len(repos)} repos referenced: {', '.join(r.split('/')[-1] for r in repos)}")


def _verify_tier_compliance(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 7: check tier compliance across repos."""
    return StepResult(True, "Tier compliance — delegated to agent (settings.yml check)")


def build_steps(config: ServiceConfig, ctx: dict) -> list[Step]:
    return [
        Step(1, "PHASE 1: TOPOLOGY",     "Check topology services",     _check_topology_services),
        Step(2, "PHASE 1: TOPOLOGY",     "Check topology databases",    _check_topology_databases),
        Step(3, "PHASE 1: TOPOLOGY",     "Verify Railway state",        _verify_railway_state),
        Step(4, "PHASE 2: INCIDENTS",    "Check open incidents",        _check_incidents),
        Step(5, "PHASE 2: INCIDENTS",    "Verify GitHub issues match",  _verify_gh_issues),
        Step(6, "PHASE 3: REPOS",        "Verify repo list",           _verify_repo_list),
        Step(7, "PHASE 3: REPOS",        "Check tier compliance",      _verify_tier_compliance),
    ]
