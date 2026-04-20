"""Encoded knowledge — the facts an agent never has to rediscover.

Every fact here was learned the hard way in sessions 29-33.
Changing a fact here changes how every tool behaves.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Environment:
    name: str
    branch: str
    url: str
    railguey_account: str


@dataclass(frozen=True)
class TestAccount:
    role: str
    email: str
    password: str
    totp_secret: str


@dataclass(frozen=True)
class CICheck:
    name: str
    required: bool = True


# ── Deploy topology ────────────────────────────────────────

STAGING = Environment(
    name="staging",
    branch="develop",
    url="https://staging-cerebro-greenmark.jettaintelligence.com",
    railguey_account="develop",
)

PRODUCTION = Environment(
    name="production",
    branch="main",
    url="https://cerebro.greenmark.jettaintelligence.com",
    railguey_account="production",
)

ENVIRONMENTS = {"staging": STAGING, "production": PRODUCTION}

RAILWAY_PROJECT = "greenmark-waste-solutions"

# Both branches are protected — PR required, no direct push
BRANCH_PROTECTION = {
    "develop": "PR required, direct merge after CI",
    "main": "PR required, Rhea gate required for merge",
}

# ── CI ceremony ────────────────────────────────────────────

CI_CHECKS = [
    CICheck("Type Check"),
    CICheck("Lint"),
    CICheck("Unit Tests"),
    CICheck("Security File Check"),
    CICheck("Build"),
]

# ── Test accounts ──────────────────────────────────────────

VIEWER = TestAccount(
    role="viewer",
    email="dshanklin+test1@greenmarkwaste.com",
    password="test-viewer-2026",
    totp_secret="IBIISTGZO6JR2R7DMQ5KS2U6RZXWEEOQ",
)

ADMIN = TestAccount(
    role="admin",
    email="dshanklin+e2eadmin@greenmarkwaste.com",
    password="e2e-superadmin-2026!",
    totp_secret="LCPM4CU6EPRLDF7FGQ4FZDJZWH7GEPNO",
)

TEST_ACCOUNTS = {"viewer": VIEWER, "admin": ADMIN}

# ── Browserbase ────────────────────────────────────────────

BROWSERBASE_API_KEY = "bb_live_ykBt2_UNkOT0yZoSYSSdx9eR4k8"
BROWSERBASE_PROJECT_ID = "2080dfe2-9805-4fc7-be2f-512dc5762e90"
BROWSERBASE_API_URL = "https://api.browserbase.com/v1"

# ── Login flow ─────────────────────────────────────────────
# Steps encoded for documentation; auth.py implements them.
LOGIN_STEPS = [
    "Navigate to {base_url}/login",
    "Fill email field",
    "Fill password field",
    "Click submit",
    "Wait for MFA page (Two-factor verification)",
    "Generate TOTP code (HMAC-SHA1, 6 digits, 30s period)",
    "Fill TOTP field",
    "Click Verify",
    "Wait for dashboard",
]

# ── Merge ceremony ─────────────────────────────────────────

MERGE_RULES = {
    "develop": "Direct merge after CI passes. No Rhea gate.",
    "main": "Rhea gate required. Use cerebro-github merge_pr which triggers the gate.",
}

# ── Page registry ──────────────────────────────────────────

PAGE_REGISTRY_PATH = "lib/page-registry.ts"  # relative to cerebro repo root


def get_environment(name: str) -> Environment:
    env = ENVIRONMENTS.get(name)
    if not env:
        raise ValueError(f"Unknown environment: {name}. Use 'staging' or 'production'.")
    return env


def get_account(role: str) -> TestAccount:
    acct = TEST_ACCOUNTS.get(role)
    if not acct:
        raise ValueError(f"Unknown role: {role}. Use 'viewer' or 'admin'.")
    return acct
