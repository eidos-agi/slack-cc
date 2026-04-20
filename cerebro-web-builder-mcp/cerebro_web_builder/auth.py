"""TOTP generation and login flow automation.

Delegates to the proven ab-login bash script for the full login flow.
Uses pyotp for standalone TOTP generation when needed.
"""

import subprocess
import shutil
from pathlib import Path

import pyotp

from .knowledge import get_account, get_environment


# ── Paths ─────────────────────────────────────────────────────

COCKPIT_ROOT = Path(__file__).resolve().parent.parent.parent


def _find_ab() -> str:
    """Find the ab CLI binary."""
    ab_path = COCKPIT_ROOT / "tools" / "agent-browser" / "ab"
    if ab_path.exists():
        return str(ab_path)
    ab_in_path = shutil.which("ab")
    if ab_in_path:
        return ab_in_path
    raise FileNotFoundError(
        "Cannot find agent-browser 'ab' CLI. "
        "Expected at tools/agent-browser/ab or in PATH."
    )


def _find_ab_login() -> str:
    """Find the ab-login script."""
    script = COCKPIT_ROOT / "tools" / "agent-browser" / "ab-login"
    if script.exists():
        return str(script)
    raise FileNotFoundError(
        "Cannot find ab-login script. "
        "Expected at tools/agent-browser/ab-login."
    )


def _run_ab(*args: str, timeout: int = 30) -> tuple[int, str]:
    """Run an ab command, return (exit_code, output)."""
    ab = _find_ab()
    result = subprocess.run(
        [ab, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = result.stdout + result.stderr
    return result.returncode, output.strip()


def generate_totp(secret: str) -> str:
    """Generate a 6-digit TOTP code from a base32 secret."""
    return pyotp.TOTP(secret).now()


def login(
    environment: str = "staging",
    role: str = "viewer",
) -> dict:
    """Automated login with TOTP via ab-login. No human needed.

    Delegates to the proven tools/agent-browser/ab-login bash script
    which handles credentials, TOTP generation, MFA detection, and
    dashboard verification.

    Args:
        environment: "staging" or "production"
        role: "viewer" or "admin"

    Returns:
        {logged_in, screenshot, environment, role, url, error?}
    """
    env = get_environment(environment)
    acct = get_account(role)

    try:
        ab_login = _find_ab_login()
    except FileNotFoundError as e:
        return {"logged_in": False, "error": str(e)}

    # ab-login reads creds from env vars
    login_env = {
        "E2E_TEST_EMAIL": acct.email,
        "E2E_TEST_PASSWORD": acct.password,
        "E2E_TEST_TOTP_SECRET": acct.totp_secret,
        "E2E_ADMIN_EMAIL": acct.email,
        "E2E_ADMIN_PASSWORD": acct.password,
        "E2E_ADMIN_TOTP_SECRET": acct.totp_secret,
    }

    import os
    run_env = {**os.environ, **login_env}

    try:
        result = subprocess.run(
            [ab_login, environment, role],
            capture_output=True,
            text=True,
            timeout=60,
            env=run_env,
        )
    except subprocess.TimeoutExpired:
        return {"logged_in": False, "error": "ab-login timed out after 60s"}

    output = result.stdout + result.stderr
    logged_in = result.returncode == 0

    return {
        "logged_in": logged_in,
        "screenshot": "/tmp/ab-login-result.png",
        "environment": environment,
        "role": role,
        "url": env.url,
        "output": output[-500:] if output else "",
        **({"error": f"ab-login exited {result.returncode}: {output[-200:]}"} if not logged_in else {}),
    }
