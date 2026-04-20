"""Authentication — delegates to the proven ab-login script.

The ab-login script handles credentials, TOTP, MFA detection,
and dashboard verification. This module wraps it for the verifier.
"""

import os
import subprocess
from pathlib import Path

from . import browser

COCKPIT_ROOT = Path(__file__).resolve().parent.parent.parent


def _find_ab_login() -> str:
    """Find the ab-login script."""
    script = COCKPIT_ROOT / "tools" / "agent-browser" / "ab-login"
    if script.exists():
        return str(script)
    raise FileNotFoundError(
        "Cannot find ab-login script. "
        "Expected at tools/agent-browser/ab-login."
    )


def ensure_authenticated(environment: str = "staging", role: str = "viewer") -> dict:
    """Ensure the browser session is authenticated via ab-login.

    Delegates to tools/agent-browser/ab-login which handles:
    - Credential loading from env vars
    - TOTP generation and MFA entry
    - Dashboard verification

    Args:
        environment: "staging" or "production"
        role: "viewer" or "admin"

    Returns:
        {authenticated, method, output?, error?}
    """
    # Quick check — already logged in?
    base = browser.get_environment_url(environment)
    browser.navigate(base + "/dashboard")
    browser.wait_for_load(2.0)

    url = browser.get_url()
    snap = browser.snapshot_full()

    if "/login" not in url.lower() and any(
        kw in snap.lower() for kw in ["executive", "financial", "dashboard"]
    ):
        return {"authenticated": True, "method": "existing_session"}

    # Need to login — delegate to ab-login
    try:
        ab_login = _find_ab_login()
    except FileNotFoundError as e:
        return {"authenticated": False, "method": "failed", "error": str(e)}

    # ab-login reads credentials from E2E_TEST_* / E2E_ADMIN_* env vars.
    # These may already be in the environment from .env.local, or we pass
    # VERIFIER_* vars through if they're set.
    run_env = dict(os.environ)

    # Map VERIFIER_* vars to E2E_* vars if present (backwards compat)
    verifier_email = os.environ.get("VERIFIER_EMAIL", "")
    verifier_password = os.environ.get("VERIFIER_PASSWORD", "")
    verifier_totp = os.environ.get("VERIFIER_TOTP_SECRET", "")

    if verifier_email:
        run_env["E2E_TEST_EMAIL"] = verifier_email
        run_env["E2E_ADMIN_EMAIL"] = verifier_email
    if verifier_password:
        run_env["E2E_TEST_PASSWORD"] = verifier_password
        run_env["E2E_ADMIN_PASSWORD"] = verifier_password
    if verifier_totp:
        run_env["E2E_TEST_TOTP_SECRET"] = verifier_totp
        run_env["E2E_ADMIN_TOTP_SECRET"] = verifier_totp

    try:
        result = subprocess.run(
            [ab_login, environment, role],
            capture_output=True,
            text=True,
            timeout=60,
            env=run_env,
        )
    except subprocess.TimeoutExpired:
        return {"authenticated": False, "method": "failed", "error": "ab-login timed out after 60s"}

    output = result.stdout + result.stderr
    logged_in = result.returncode == 0

    if logged_in:
        return {
            "authenticated": True,
            "method": "ab-login",
            "output": output[-300:] if output else "",
        }

    return {
        "authenticated": False,
        "method": "failed",
        "error": f"ab-login exited {result.returncode}: {output[-200:]}",
    }
