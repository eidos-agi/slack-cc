"""Browser automation — wraps agent-browser ab via subprocess."""

import os
import subprocess
import time
from pathlib import Path

AB_PATH = Path(__file__).parent.parent.parent / "tools" / "agent-browser" / "ab"
SESSION_NAME = "cerebro-verifier"


def _ab(*args: str, timeout: int = 30) -> str:
    """Run an agent-browser command. Returns stdout."""
    cmd = [str(AB_PATH), "--session-name", SESSION_NAME] + list(args)
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, cwd=str(AB_PATH.parent)
    )
    if result.returncode != 0 and result.stderr:
        return f"ERROR: {result.stderr.strip()}"
    return result.stdout.strip()


def navigate(url: str) -> str:
    """Open a URL in the browser."""
    return _ab("open", url)


def screenshot(path: str) -> str:
    """Take a screenshot, save to path."""
    return _ab("screenshot", path)


def snapshot(interactive_only: bool = True) -> str:
    """Get the accessibility tree. Returns AI-friendly text."""
    args = ["snapshot"]
    if interactive_only:
        args.append("-i")
    return _ab(*args, timeout=15)


def snapshot_full() -> str:
    """Full accessibility tree (not just interactive elements)."""
    return _ab("snapshot", "--compact", timeout=15)


def get_text(selector: str) -> str:
    """Extract text content from an element."""
    return _ab("get", "text", selector)


def get_title() -> str:
    """Get the page title."""
    return _ab("get", "title")


def get_url() -> str:
    """Get the current URL."""
    return _ab("get", "url")


def fill(selector: str, text: str) -> str:
    """Fill a form field."""
    return _ab("fill", selector, text)


def click(selector: str) -> str:
    """Click an element."""
    return _ab("click", selector)


def press(key: str) -> str:
    """Press a key."""
    return _ab("press", key)


def wait_for_load(delay: float = 3.0):
    """Wait for page to load.

    Uses a time delay instead of networkidle — agent-browser's
    wait --load networkidle hangs on heavy SPAs.
    """
    time.sleep(delay)


def navigate_and_capture(url: str, screenshot_path: str) -> dict:
    """Navigate to URL, wait, take screenshot, return snapshot.

    The standard verification sequence for every page.
    """
    nav_result = navigate(url)
    wait_for_load()
    ss_result = screenshot(screenshot_path)
    snap = snapshot_full()

    return {
        "url": url,
        "nav_result": nav_result,
        "screenshot": screenshot_path,
        "screenshot_result": ss_result,
        "snapshot_length": len(snap),
        "snapshot": snap,
    }


def get_environment_url(environment: str) -> str:
    """Get the base URL for an environment."""
    urls = {
        "staging": os.environ.get(
            "STAGING_URL",
            "https://staging-cerebro-greenmark.jettaintelligence.com",
        ),
        "production": os.environ.get(
            "PRODUCTION_URL",
            "https://cerebro.greenmark.jettaintelligence.com",
        ),
    }
    return urls.get(environment, urls["staging"])
