"""cerebro-web-builder MCP server.

Knowledge-first MCP for the Cerebro web deployment pipeline.
An agent using this MCP never rediscovers deploy topology,
CI ceremony, login flows, or test account setup.

Tools split into three categories:
  1. Knowledge queries — return encoded facts
  2. Browser verification — login + navigate + screenshot
  3. Shipping orchestration — return step-by-step ceremony instructions
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "cerebro-web-builder",
    instructions=(
        "cerebro-web-builder encodes the Cerebro web deployment pipeline as executable knowledge. "
        "Use it when you need to SHIP CODE or CHECK DEPLOYS. "
        "Use `topology` for deploy topology, `test_accounts` for credentials, "
        "`login` for automated browser login, `verify_page`/`smoke_test` to check pages load, "
        "`ship_to_staging`/`promote_to_production` for deployment ceremony, "
        "`deploy_status` for Railway state. "
        "Use `docs` to learn about this MCP."
        "\n\n"
        "WHEN TO USE WHICH MCP:\n"
        "- cerebro-web-builder (this): shipping code, deploy topology, browser login, "
        "page smoke tests ('does the page load?'), deploy status\n"
        "- cerebro-verifier: data correctness — 'are the NUMBERS right?' "
        "Ground truth SQL, golden fixtures, KPI extraction, evidence trails\n"
        "- cerebro-builder: session orchestration, mission, what to work on next\n"
        "- cerebro-data-engineer: warehouse queries, freshness, parity, pipeline diagnostics\n"
        "- cerebro-github: git ceremony — issues, PRs, CI, merges\n\n"
        "For full ecosystem documentation, use cerebro-docs."
    ),
)


# ── Knowledge tools ────────────────────────────────────────


@mcp.tool()
def docs(query: str = "") -> dict:
    """Learn about cerebro-web-builder — what it does, how it works, what tools are available.

    Call with no query to see the full overview.
    Call with a keyword to find specific information.

    Examples:
        docs()               → full overview of all tools and capabilities
        docs("login")        → how automated login works
        docs("ship")         → how shipping ceremony works
        docs("topology")     → deploy topology details
        docs("browserbase")  → browser automation details
    """
    overview = {
        "name": "cerebro-web-builder",
        "purpose": (
            "Encodes the Cerebro web deployment pipeline as executable knowledge. "
            "An agent using this MCP never needs to rediscover deploy topology, "
            "CI ceremony, login flows, or test account credentials."
        ),
        "tools": {
            "knowledge": {
                "topology": "Full deploy topology: environments, branches, URLs, Railway accounts, CI checks, merge rules",
                "test_accounts": "Test account credentials with TOTP secrets for automated MFA",
            },
            "browser_verification": {
                "login": "Automated browser login with TOTP — delegates to ab-login script",
                "verify_page": "Login, navigate to a page, screenshot, check for errors",
                "verify_sidebar": "Login and verify Dashboard/Preview/Tools sidebar sections present",
                "smoke_test": "Login once, visit all pages, screenshot each, report pass/fail",
                "test_overlay": "Navigate to a preview page, verify overlay appears, attempt dismiss",
            },
            "shipping": {
                "ship_to_staging": "Generate step-by-step ceremony to ship a branch to staging (develop)",
                "promote_to_production": "Generate step-by-step ceremony to promote to production (main) with Rhea gate",
                "deploy_status": "Instructions to check Railway deployment status via railguey",
            },
        },
        "architecture": {
            "knowledge_pattern": "Facts encoded in typed dataclasses in knowledge.py — not discovered at runtime",
            "browser_automation": "Uses tools/agent-browser/ab CLI with Browserbase cloud browsers",
            "login_delegation": "auth.py delegates to the proven ab-login bash script for full login+MFA flow",
            "shipping_pattern": "Returns step-by-step instructions with exact MCP tool calls — does NOT execute them directly",
        },
        "environments": {
            "staging": {"branch": "develop", "url": "https://staging-cerebro-greenmark.jettaintelligence.com"},
            "production": {"branch": "main", "url": "https://cerebro.greenmark.jettaintelligence.com"},
        },
        "integration": {
            "cerebro-github": "create_work, open_pr, check_ci, merge_pr for shipping ceremony",
            "railguey": "account_default, deployments, service_info for deploy polling",
            "cerebro-verifier": "take_evidence, verify_page for verification fixtures",
            "cerebro-builder": "tools can be called within convene/adjourn sessions",
        },
    }

    if not query.strip():
        return overview

    # Search by keyword
    query_lower = query.lower()
    matches = {}
    for section, content in overview.items():
        if section == "name":
            continue
        if isinstance(content, str):
            if query_lower in content.lower() or query_lower in section.lower():
                matches[section] = content
        elif isinstance(content, dict):
            section_matches = {}
            for key, val in content.items():
                searchable = f"{key} {val}" if isinstance(val, str) else f"{key} {val}"
                if query_lower in searchable.lower():
                    section_matches[key] = val
            if section_matches:
                matches[section] = section_matches

    if not matches:
        return {
            "query": query,
            "matches": 0,
            "hint": f"No matches for '{query}'. Try: login, ship, topology, browserbase, verify, ceremony",
            "available_sections": list(overview.keys()),
        }

    return {"query": query, "results": matches}


@mcp.tool()
def topology() -> dict:
    """Return the full deploy topology: environments, branches, URLs, accounts.

    Use this at session start to understand how Cerebro deploys.
    """
    from .knowledge import (
        ENVIRONMENTS, BRANCH_PROTECTION, MERGE_RULES,
        CI_CHECKS, RAILWAY_PROJECT, LOGIN_STEPS,
    )
    return {
        "environments": {
            name: {
                "branch": env.branch,
                "url": env.url,
                "railguey_account": env.railguey_account,
            }
            for name, env in ENVIRONMENTS.items()
        },
        "branch_protection": BRANCH_PROTECTION,
        "merge_rules": MERGE_RULES,
        "ci_checks": [c.name for c in CI_CHECKS],
        "railway_project": RAILWAY_PROJECT,
        "login_steps": LOGIN_STEPS,
        "key_rule": "NEVER merge untested code to main. Always verify on staging (develop) first.",
    }


@mcp.tool()
def test_accounts() -> dict:
    """Return test account info for automated browser testing.

    These accounts have known TOTP secrets for programmatic MFA.
    """
    from .knowledge import TEST_ACCOUNTS
    return {
        role: {
            "email": acct.email,
            "totp_secret": acct.totp_secret,
            "note": "Password available in cerebro/.env.local",
        }
        for role, acct in TEST_ACCOUNTS.items()
    }


# ── Browser verification tools ─────────────────────────────


@mcp.tool()
def login(environment: str = "staging", role: str = "viewer") -> dict:
    """Automated login with TOTP. No human needed.

    Opens a Browserbase session, fills credentials, generates and
    enters TOTP code, waits for dashboard.

    Args:
        environment: "staging" or "production"
        role: "viewer" or "admin"
    """
    from .auth import login as do_login
    return do_login(environment, role)


@mcp.tool()
def verify_page(
    url: str,
    environment: str = "staging",
    role: str = "viewer",
) -> dict:
    """Login, navigate to a page, screenshot, check for errors.

    Args:
        url: Full URL or path (e.g. "/dashboard/financial")
        environment: "staging" or "production"
        role: "viewer" or "admin"
    """
    from .verification import verify_page as do_verify
    return do_verify(url, environment, role)


@mcp.tool()
def verify_sidebar(
    environment: str = "staging",
    role: str = "viewer",
) -> dict:
    """Login and verify sidebar sections (Dashboard/Preview/Tools) are present.

    Args:
        environment: "staging" or "production"
        role: "viewer" or "admin"
    """
    from .verification import verify_sidebar as do_verify
    return do_verify(environment, role)


@mcp.tool()
def smoke_test(
    environment: str = "staging",
    role: str = "viewer",
    pages: list[str] | None = None,
) -> dict:
    """Login once, visit every page, screenshot each. Report pass/fail.

    Args:
        environment: "staging" or "production"
        role: "viewer" or "admin"
        pages: Page paths to visit. Defaults to core live pages.
    """
    from .verification import smoke_test as do_smoke
    return do_smoke(environment, role, pages)


@mcp.tool()
def test_overlay(
    page_slug: str,
    environment: str = "staging",
) -> dict:
    """Navigate to a preview page and verify the overlay appears.

    Logs in as admin (to access all pages), checks for overlay
    with vendor info, attempts to dismiss it.

    Args:
        page_slug: Page path (e.g. "/dashboard/operations")
        environment: "staging" or "production"
    """
    from .verification import test_overlay as do_test
    return do_test(page_slug, environment)


# ── Shipping orchestration tools ────────────────────────────


@mcp.tool()
def ship_to_staging(
    branch: str,
    title: str = "",
    closes_issue: int | None = None,
) -> dict:
    """Generate the full ship-to-staging ceremony.

    Returns step-by-step instructions with exact MCP tool calls
    the agent should execute. Does NOT execute them directly.

    Args:
        branch: Git branch to ship
        title: PR title
        closes_issue: Existing issue number, or will instruct to create one
    """
    from .shipping import ship_to_staging as do_ship
    return do_ship(branch, title, closes_issue)


@mcp.tool()
def promote_to_production(
    pr_number: int | None = None,
    branch: str = "",
    closes_issue: int | None = None,
) -> dict:
    """Generate the full promote-to-production ceremony.

    Returns step-by-step instructions including the Rhea gate.
    Assumes code is already verified on staging.

    Args:
        pr_number: Existing PR against main
        branch: Promotion branch name
        closes_issue: Issue number for the promotion
    """
    from .shipping import promote_to_production as do_promote
    return do_promote(pr_number, branch, closes_issue)


@mcp.tool()
def deploy_status(environment: str = "staging") -> dict:
    """Check Railway deployment status instructions.

    Returns the steps to check deploy status via railguey.

    Args:
        environment: "staging" or "production"
    """
    from .deploy import deploy_status as do_status
    return do_status(environment)
