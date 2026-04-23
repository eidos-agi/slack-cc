"""GitHub App authentication for cerebro-github.

Generates installation access tokens from a GitHub App's private key,
giving cerebro-github its own rate limit bucket (5,000-12,500/hr)
separate from Daniel's personal PAT.

Setup:
    1. Create a GitHub App in the greenmark-waste-solutions org
    2. Set permissions: repo, issues, PRs, checks, actions (read/write)
    3. Install the app on the org
    4. Set env vars:
        CEREBRO_GITHUB_APP_ID=<app_id>
        CEREBRO_GITHUB_APP_PRIVATE_KEY=<base64-encoded PEM>
        CEREBRO_GITHUB_APP_INSTALLATION_ID=<installation_id>

If env vars are not set, falls back to gh CLI's default auth (PAT).
"""

import base64
import json
import os
import time
import urllib.request
from typing import Optional


# Cache the installation token — they're valid for 1 hour,
# we refresh 5 minutes early to avoid mid-request expiry.
_cached_token: Optional[str] = None
_cached_token_expires: float = 0
_REFRESH_MARGIN = 300  # seconds before expiry to refresh


# Defaults — App ID and Installation ID aren't secrets.
# Only the private key needs external config.
_DEFAULTS = {
    "CEREBRO_GITHUB_APP_ID": "3479857",
    "CEREBRO_GITHUB_APP_INSTALLATION_ID": "126482862",
    "CEREBRO_GITHUB_APP_PRIVATE_KEY_FILE": "/home/dev/.claude/cerebro-github-app.pem",
}


def _env(name: str) -> Optional[str]:
    """Read an env var with fallback to defaults."""
    val = os.environ.get(name, "").strip()
    return val or _DEFAULTS.get(name)


def is_app_auth_configured() -> bool:
    """Check if GitHub App credentials are available."""
    has_key = _env("CEREBRO_GITHUB_APP_PRIVATE_KEY") or _env("CEREBRO_GITHUB_APP_PRIVATE_KEY_FILE")
    return all([
        _env("CEREBRO_GITHUB_APP_ID"),
        has_key,
        _env("CEREBRO_GITHUB_APP_INSTALLATION_ID"),
    ])


def _generate_jwt() -> str:
    """Generate a JWT signed with the app's private key.

    The JWT is used to authenticate as the app itself (not as an
    installation). It's short-lived (10 minutes) and only used to
    request an installation access token.
    """
    import jwt  # PyJWT

    app_id = _env("CEREBRO_GITHUB_APP_ID")

    if not app_id:
        raise RuntimeError("CEREBRO_GITHUB_APP_ID must be set")

    # Try file path first (most reliable — no encoding issues),
    # then fall back to base64 env var
    key_file = _env("CEREBRO_GITHUB_APP_PRIVATE_KEY_FILE")
    if key_file:
        with open(key_file) as f:
            private_key = f.read()
    else:
        private_key_b64 = _env("CEREBRO_GITHUB_APP_PRIVATE_KEY")
        if not private_key_b64:
            raise RuntimeError(
                "Set CEREBRO_GITHUB_APP_PRIVATE_KEY_FILE (path to PEM) "
                "or CEREBRO_GITHUB_APP_PRIVATE_KEY (base64-encoded PEM)"
            )
        private_key = base64.b64decode(private_key_b64).decode("utf-8")

    now = int(time.time())
    payload = {
        "iat": now - 60,       # issued at (60s in the past for clock drift)
        "exp": now + 600,      # expires in 10 minutes
        "iss": app_id,          # GitHub App ID (string)
    }

    return jwt.encode(payload, private_key, algorithm="RS256")


def _request_installation_token() -> tuple[str, float]:
    """Exchange the JWT for an installation access token.

    Returns (token, expires_at_epoch).
    """
    installation_id = _env("CEREBRO_GITHUB_APP_INSTALLATION_ID")
    if not installation_id:
        raise RuntimeError("CEREBRO_GITHUB_APP_INSTALLATION_ID must be set")

    app_jwt = _generate_jwt()

    url = (
        f"https://api.github.com/app/installations/"
        f"{installation_id}/access_tokens"
    )
    req = urllib.request.Request(
        url,
        method="POST",
        headers={
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())

    token = data["token"]

    # Parse expires_at (ISO 8601) to epoch
    expires_at_str = data.get("expires_at", "")
    if expires_at_str:
        from datetime import datetime, timezone
        dt = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        expires_at = dt.timestamp()
    else:
        # Default: 1 hour from now
        expires_at = time.time() + 3600

    return token, expires_at


def get_token() -> Optional[str]:
    """Get a valid installation access token, or None if app auth isn't configured.

    Caches the token and refreshes 5 minutes before expiry.
    """
    global _cached_token, _cached_token_expires

    if not is_app_auth_configured():
        return None

    now = time.time()
    if _cached_token and now < (_cached_token_expires - _REFRESH_MARGIN):
        return _cached_token

    token, expires_at = _request_installation_token()
    _cached_token = token
    _cached_token_expires = expires_at
    return token
