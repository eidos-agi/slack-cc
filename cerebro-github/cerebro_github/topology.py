"""Infrastructure topology — the system model the ceremony operates over.

This is the map. The ceremony tools are the traffic cops.
Every deploy, credential provision, and health check references this.
"""

import os
from dataclasses import dataclass, field


@dataclass
class SupabaseProject:
    ref: str
    name: str
    pooler_host: str = "aws-1-us-east-1.pooler.supabase.com"
    port: int = 5432


@dataclass
class VendorCredentials:
    """Which env vars a vendor needs and where they come from."""
    vendor: str
    env_vars: list[str]
    source: str  # "warp-speed-excel .env", "Railway shared", etc.
    same_both_envs: bool = True  # True = same creds for staging and prod
    notes: str = ""


@dataclass
class Service:
    """A Railway service — one deployable unit."""
    name: str
    repo: str
    domains: dict[str, str] = field(default_factory=dict)  # env → domain
    workspace_path: str = ""  # local path for railguey


@dataclass
class Environment:
    """A deployment environment with its own credentials, DB, and domains."""
    name: str  # "develop" or "production"
    railway_token_env: str  # env var name holding the Railway token
    supabase: SupabaseProject | None = None
    services: list[Service] = field(default_factory=list)


# ── The Topology ────────────────────────────────────────────

SUPABASE_STAGING = SupabaseProject(
    ref="izmuckuepryqneebwwol",
    name="staging",
)

SUPABASE_PRODUCTION = SupabaseProject(
    ref="wwmcgtyngnziepeynccz",
    name="production",
)

SERVICES = {
    "cerebro": Service(
        name="cerebro",
        repo="cerebro",
        domains={
            "develop": "staging-cerebro-greenmark.jettaintelligence.com",
            "production": "cerebro.greenmark.jettaintelligence.com",
        },
        workspace_path="/home/dev/repos/cerebro",
    ),
    "data-daemon": Service(
        name="data-daemon",
        repo="data-daemon",
        domains={
            "develop": "",  # internal service, no public domain
            "production": "",
        },
        workspace_path="/home/dev/repos/data-daemon",
    ),
    "cerebro-qa": Service(
        name="cerebro-qa",
        repo="cerebro-qa",
        domains={
            "develop": "",
            "production": "qa.cerebro.greenmark.jettaintelligence.com",
        },
        workspace_path="/home/dev/repos/cerebro-qa",
    ),
    "cerebro-ai-services": Service(
        name="cerebro-ai-services",
        repo="cerebro-ai-services",
        domains={
            "develop": "",
            "production": "cerebro-ai-services-production.up.railway.app",
        },
        workspace_path="/home/dev/repos/cerebro-ai-services",
    ),
    "cerebro-bot-farm": Service(
        name="cerebro-bot-farm",
        repo="cerebro-bot-farm",
        domains={"develop": "", "production": ""},
        workspace_path="/home/dev/repos/cerebro-bot-farm",
    ),
    "cerebro-warp-speed": Service(
        name="cerebro-warp-speed",
        repo="cerebro-warp-speed",
        domains={
            "develop": "",
            "production": "cerebro-warp-speed-production.up.railway.app",
        },
        workspace_path="/home/dev/repos/cerebro-warp-speed",
    ),
}

ENVIRONMENTS = {
    "develop": Environment(
        name="develop",
        railway_token_env="RAILWAY_TOKEN_DEVELOP",
        supabase=SUPABASE_STAGING,
    ),
    "production": Environment(
        name="production",
        railway_token_env="RAILWAY_TOKEN_PRODUCTION",
        supabase=SUPABASE_PRODUCTION,
    ),
}

# Railway tokens — loaded from env or local files
RAILWAY_TOKENS = {
    "develop": os.environ.get("RAILWAY_TOKEN_DEVELOP", ""),
    "production": os.environ.get("RAILWAY_TOKEN_PRODUCTION", ""),
}

VENDOR_CREDENTIALS = [
    VendorCredentials(
        vendor="sage-intacct",
        env_vars=[
            "SAGE_SENDER_ID",
            "SAGE_SENDER_PASSWORD",
            "SAGE_COMPANY_ID",
            "SAGE_USER_ID",
            "SAGE_USER_PASSWORD",
        ],
        source="warp-speed-excel .env (proven against 1.38M GL entries)",
        same_both_envs=True,  # Sage has no sandbox — same API for staging and prod
        notes="Read-only. No agent writes to Sage. Human-in-the-loop for all entries.",
    ),
    VendorCredentials(
        vendor="hubspot",
        env_vars=["HUBSPOT_TOKEN"],
        source="Alex Kaye (deprioritized per Michael 2026-04-06)",
        same_both_envs=True,
        notes="Deprioritized. Sage is priority #1.",
    ),
    VendorCredentials(
        vendor="supabase",
        env_vars=[
            "NEXT_PUBLIC_SUPABASE_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_DB_PASSWORD",
        ],
        source="Supabase dashboard per project",
        same_both_envs=False,  # Different per environment
        notes="staging=izmuckuepryqneebwwol, production=wwmcgtyngnziepeynccz",
    ),
]

# ── Deploy ordering ─────────────────────────────────────────
# When a change spans multiple repos, deploy in this order.
# Migrations before apps. Data pipeline after schema changes.

DEPLOY_ORDER = [
    "cerebro-migrations",  # Schema changes first
    "cerebro",             # Dashboard app (reads from DB)
    "data-daemon",         # Pipeline (writes to DB)
    "cerebro-qa",          # QA (reads from DB)
    "cerebro-ai-services", # AI services
    "cerebro-bot-farm",    # Bot farm
]

# ── Full change lifecycle ───────────────────────────────────
# This is what the ceremony SHOULD enforce end-to-end.

CHANGE_LIFECYCLE = [
    "1. create_work() — issue + project board + milestone link",
    "2. Write code on feature branch",
    "3. open_pr() — PR with Closes #N, CI triggered",
    "4. check_ci() — wait for green",
    "5. merge_pr() — squash merge to develop",
    "6. verify_staging() — deploy landed, health check passes, feature works",
    "7. If DB change: verify migration applied on staging Supabase",
    "8. If credentials needed: provision_credentials() on both envs",
    "9. promote_to_production() — merge develop → main (manual dispatch for migrations)",
    "10. verify_production() — deploy landed, health check passes",
    "11. update_stakeholders() — Wrike card updated, changelog generated",
    "12. close_milestone() — if all sub-issues done, close the milestone",
]
