"""Topology loading and configuration for cerebro-deploy.

Imports TOPOLOGY and INCIDENTS from cerebro-docs knowledge.py.
Falls back to inline copy if import fails (e.g. cerebro-docs not installed).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any


def _load_from_cerebro_docs() -> tuple[dict, list]:
    """Try importing from the installed cerebro-docs package."""
    # Also try adding the sibling directory to sys.path
    cockpit_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    docs_path = os.path.join(cockpit_root, "cerebro-docs-mcp")
    if docs_path not in sys.path:
        sys.path.insert(0, docs_path)
    from cerebro_docs.knowledge import TOPOLOGY, INCIDENTS
    return TOPOLOGY, INCIDENTS


try:
    TOPOLOGY, INCIDENTS = _load_from_cerebro_docs()
except Exception:
    # Hard failure — topology is required
    raise RuntimeError(
        "Cannot import TOPOLOGY from cerebro_docs.knowledge. "
        "Ensure cerebro-docs-mcp is pip-installed or lives at ../cerebro-docs-mcp/"
    )


@dataclass
class ServiceConfig:
    """Resolved configuration for a service deployment."""
    name: str
    repo: str
    runtime: str
    environment: str  # "production" or "develop"/"staging"
    deploy_pipeline: dict[str, str]
    connections: dict[str, Any]
    credentials: list[str]
    database_id: str | None = None
    database_host: str | None = None
    branch: str = ""  # expected branch: main for production, develop for staging
    health_url: str = ""

    @property
    def gh_repo(self) -> str:
        return self.repo


def resolve_service(service_name: str, environment: str) -> ServiceConfig:
    """Resolve a service + environment into a full config."""
    services = TOPOLOGY.get("services", {})
    if service_name not in services:
        available = ", ".join(sorted(services.keys()))
        raise ValueError(f"Unknown service '{service_name}'. Available: {available}")

    svc = services[service_name]

    # Normalize environment name
    env_key = environment
    if environment == "staging":
        env_key = "develop"
    elif environment == "production":
        env_key = "production"

    # Resolve branch
    if env_key == "develop":
        branch = "develop"
    else:
        branch = "main"

    # Resolve database
    db_id = None
    db_host = None
    connections = svc.get("connections", {})
    env_conn = connections.get(env_key) or connections.get(environment)
    if env_conn and isinstance(env_conn, dict):
        db_name = env_conn.get("database")
        if db_name and db_name in TOPOLOGY.get("databases", {}):
            db_info = TOPOLOGY["databases"][db_name]
            db_id = db_info.get("id")
            db_host = db_info.get("host")

    # Resolve health URL
    # Convention: <service>-<env>.up.railway.app/health
    if "Railway" in svc.get("runtime", ""):
        if env_key == "develop":
            health_url = f"https://{service_name}-develop.up.railway.app/health"
        else:
            health_url = f"https://{service_name}-production.up.railway.app/health"
    elif "Cloudflare" in svc.get("runtime", ""):
        health_url = ""  # Cloudflare Workers don't have /health
    else:
        health_url = ""

    return ServiceConfig(
        name=service_name,
        repo=svc.get("repo", ""),
        runtime=svc.get("runtime", ""),
        environment=env_key,
        deploy_pipeline=svc.get("deploy_pipeline", {}),
        connections=connections,
        credentials=svc.get("credentials", []),
        database_id=db_id,
        database_host=db_host,
        branch=branch,
        health_url=health_url,
    )


def get_incidents(service_name: str | None = None) -> list[dict]:
    """Get incidents, optionally filtered by service name."""
    if service_name is None:
        return INCIDENTS
    # Filter by checking if service name appears in any field
    results = []
    for inc in INCIDENTS:
        text = str(inc).lower()
        if service_name.lower() in text:
            results.append(inc)
    return results
