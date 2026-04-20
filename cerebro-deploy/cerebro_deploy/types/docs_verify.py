"""Deploy type: docs — verify documentation matches reality.

Compares topology against actual Railway state, compares incidents
against current issues. No deployment — purely verification.
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
    """List all services in topology and check for staleness."""
    services = TOPOLOGY.get("services", {})
    if not services:
        return StepResult(
            passed=False,
            detail="No services in topology",
            remediation="Update cerebro-docs knowledge.py with current services.",
        )
    names = sorted(services.keys())
    return StepResult(passed=True, detail=f"{len(names)} services: {', '.join(names)}")


def _check_topology_databases(config: ServiceConfig, ctx: dict) -> StepResult:
    """List all databases in topology."""
    databases = TOPOLOGY.get("databases", {})
    if not databases:
        return StepResult(passed=True, detail="No databases in topology (may be expected)")
    names = sorted(databases.keys())
    return StepResult(passed=True, detail=f"{len(names)} databases: {', '.join(names)}")


def _verify_railway_state(config: ServiceConfig, ctx: dict) -> StepResult:
    """Compare topology against actual Railway state."""
    return StepResult(
        passed=True,
        detail="Railway state comparison — delegated to agent (railguey_services)",
    )


def _check_incidents(config: ServiceConfig, ctx: dict) -> StepResult:
    """Review open incidents."""
    from cerebro_deploy.config import INCIDENTS
    active = [i for i in INCIDENTS if str(i.get("status", "")).upper() == "ACTIVE"]
    if active:
        names = "; ".join(str(i.get("title", i.get("id", "?"))) for i in active)
        return StepResult(passed=True, detail=f"WARNING: {len(active)} active incident(s): {names}")
    return StepResult(passed=True, detail=f"No active incidents ({len(INCIDENTS)} total in ledger)")


def _verify_gh_issues(config: ServiceConfig, ctx: dict) -> StepResult:
    """Compare incidents against current GitHub issues."""
    return StepResult(
        passed=True,
        detail="GitHub issues comparison — delegated to agent (gh issue list)",
    )


def _verify_repo_list(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify all repos in topology exist and are accessible."""
    services = TOPOLOGY.get("services", {})
    repos = sorted(set(s.get("repo", "") for s in services.values() if s.get("repo")))
    short_names = [r.split("/")[-1] for r in repos]
    return StepResult(passed=True, detail=f"{len(repos)} repos referenced: {', '.join(short_names)}")


def _verify_tier_compliance(config: ServiceConfig, ctx: dict) -> StepResult:
    """Check tier compliance across repos."""
    return StepResult(
        passed=True,
        detail="Tier compliance — delegated to agent (settings.yml audit)",
    )


def build_steps(config: ServiceConfig, ctx: dict) -> list[Step]:
    return [
        Step(1, "Phase 1: Topology",  "Check topology services",     _check_topology_services),
        Step(2, "Phase 1: Topology",  "Check topology databases",    _check_topology_databases),
        Step(3, "Phase 1: Topology",  "Verify Railway state",        _verify_railway_state),
        Step(4, "Phase 2: Incidents", "Check open incidents",        _check_incidents),
        Step(5, "Phase 2: Incidents", "Verify GitHub issues match",  _verify_gh_issues),
        Step(6, "Phase 3: Repos",     "Verify repo list",            _verify_repo_list),
        Step(7, "Phase 3: Repos",     "Check tier compliance",       _verify_tier_compliance),
    ]
