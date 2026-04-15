"""Authentication — site password + Supabase login with TOTP."""

import os
import re

from . import browser


def _get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def is_authenticated(environment: str = "staging") -> bool:
    """Check if the current browser session is authenticated.

    Opens the dashboard and checks if we land on a login page
    or the actual dashboard content.
    """
    base = browser.get_environment_url(environment)
    browser.navigate(base + "/dashboard")
    browser.wait_for_load(2.0)

    url = browser.get_url()
    snap = browser.snapshot_full()

    # If redirected to /login or snapshot contains login indicators
    if "/login" in url.lower():
        return False
    if any(kw in snap.lower() for kw in ["sign in", "log in", "password"]):
        # Could be site password gate or Supabase login
        return False

    # Check for dashboard content
    if any(kw in snap.lower() for kw in ["executive", "financial", "dashboard"]):
        return True

    return False


def _handle_site_password() -> bool:
    """Enter the site password if the gate is showing."""
    snap = browser.snapshot(interactive_only=True)

    # Look for a password input
    password_ref = None
    for line in snap.split("\n"):
        if "password" in line.lower() and "ref=" in line:
            match = re.search(r"ref=(\w+)", line)
            if match:
                password_ref = f"@{match.group(1)}"
                break

    if not password_ref:
        return False

    site_password = _get_env("SITE_PASSWORD", "cerebro2026")
    browser.fill(password_ref, site_password)

    # Find and click submit
    snap = browser.snapshot(interactive_only=True)
    for line in snap.split("\n"):
        if "button" in line.lower() and "ref=" in line:
            match = re.search(r"ref=(\w+)", line)
            if match:
                browser.click(f"@{match.group(1)}")
                break
    else:
        browser.press("Enter")

    browser.wait_for_load(2.0)
    return True


def _handle_supabase_login() -> bool:
    """Handle Supabase email/password login + TOTP."""
    email = _get_env("VERIFIER_EMAIL")
    password = _get_env("VERIFIER_PASSWORD")

    if not email or not password:
        return False

    snap = browser.snapshot(interactive_only=True)

    # Find email field
    email_ref = None
    for line in snap.split("\n"):
        if any(kw in line.lower() for kw in ["email", "username"]) and "ref=" in line:
            match = re.search(r"ref=(\w+)", line)
            if match:
                email_ref = f"@{match.group(1)}"
                break

    if email_ref:
        browser.fill(email_ref, email)

    # Find password field
    password_ref = None
    snap = browser.snapshot(interactive_only=True)
    for line in snap.split("\n"):
        if "password" in line.lower() and "ref=" in line:
            match = re.search(r"ref=(\w+)", line)
            if match:
                password_ref = f"@{match.group(1)}"
                break

    if password_ref:
        browser.fill(password_ref, password)

    # Submit
    for line in snap.split("\n"):
        if "button" in line.lower() and any(
            kw in line.lower() for kw in ["sign in", "log in", "submit"]
        ) and "ref=" in line:
            match = re.search(r"ref=(\w+)", line)
            if match:
                browser.click(f"@{match.group(1)}")
                break
    else:
        browser.press("Enter")

    browser.wait_for_load(3.0)

    # Check for TOTP
    snap = browser.snapshot(interactive_only=True)
    if _needs_totp(snap):
        return _handle_totp(snap)

    return True


def _needs_totp(snap: str) -> bool:
    """Check if the page is showing a TOTP prompt."""
    lower = snap.lower()
    return any(
        kw in lower
        for kw in ["verification code", "authenticator", "totp", "6-digit", "one-time"]
    )


def _handle_totp(snap: str) -> bool:
    """Generate and enter TOTP code."""
    secret = _get_env("VERIFIER_TOTP_SECRET")
    if not secret:
        return False

    try:
        code = _generate_totp(secret)
    except Exception:
        return False

    # Find the code input
    for line in snap.split("\n"):
        if "ref=" in line and any(
            kw in line.lower() for kw in ["code", "token", "textbox", "input"]
        ):
            match = re.search(r"ref=(\w+)", line)
            if match:
                browser.fill(f"@{match.group(1)}", code)
                browser.press("Enter")
                browser.wait_for_load(3.0)
                return True

    return False


def _generate_totp(secret: str) -> str:
    """Generate a TOTP code from a base32 secret.

    Pure Python implementation — no external dependency.
    """
    import base64
    import hashlib
    import hmac
    import struct
    import time as _time

    # Decode base32 secret
    key = base64.b32decode(secret.upper() + "=" * (8 - len(secret) % 8), casefold=True)

    # Time-based counter (30-second window)
    counter = int(_time.time()) // 30
    counter_bytes = struct.pack(">Q", counter)

    # HMAC-SHA1
    hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()

    # Dynamic truncation
    offset = hmac_hash[-1] & 0x0F
    code = struct.unpack(">I", hmac_hash[offset : offset + 4])[0] & 0x7FFFFFFF

    return str(code % 1000000).zfill(6)


def ensure_authenticated(environment: str = "staging") -> dict:
    """Ensure the browser session is authenticated.

    Returns status and what was needed to authenticate.
    """
    if is_authenticated(environment):
        return {"authenticated": True, "method": "existing_session"}

    base = browser.get_environment_url(environment)
    browser.navigate(base + "/dashboard")
    browser.wait_for_load(2.0)

    steps = []

    # Try site password first
    url = browser.get_url()
    snap = browser.snapshot_full()

    if "password" in snap.lower() and "/login" not in url.lower():
        _handle_site_password()
        steps.append("site_password")
        browser.wait_for_load(2.0)

    # Check if we need Supabase login
    url = browser.get_url()
    if "/login" in url.lower():
        success = _handle_supabase_login()
        steps.append("supabase_login")
        if not success:
            return {
                "authenticated": False,
                "method": "failed",
                "steps": steps,
                "error": "Supabase login failed. Check VERIFIER_EMAIL, VERIFIER_PASSWORD, VERIFIER_TOTP_SECRET.",
            }

    # Final check
    if is_authenticated(environment):
        return {"authenticated": True, "method": "fresh_login", "steps": steps}

    return {
        "authenticated": False,
        "method": "failed",
        "steps": steps,
        "error": "Could not authenticate after all steps.",
    }
