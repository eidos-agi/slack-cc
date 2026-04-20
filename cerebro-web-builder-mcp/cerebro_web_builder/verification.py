"""Page verification tools — verify_page, verify_sidebar, smoke_test, test_overlay.

All verification tools login first (via auth.login), then navigate and inspect.
"""

import time
from .auth import login, _run_ab, generate_totp
from .knowledge import get_environment, get_account


def verify_page(
    url: str,
    environment: str = "staging",
    role: str = "viewer",
) -> dict:
    """Open a Browserbase session, login, navigate to a page, screenshot.

    Args:
        url: Full URL or path (e.g. "/dashboard/financial")
        environment: "staging" or "production"
        role: "viewer" or "admin"
    """
    # Login first
    result = login(environment, role)
    if not result.get("logged_in"):
        return {"error": f"Login failed: {result.get('error', 'unknown')}", "page": url}

    env = get_environment(environment)

    # Navigate if url is a path
    if url.startswith("/"):
        full_url = f"{env.url}{url}"
    else:
        full_url = url

    code, out = _run_ab("open", full_url)
    time.sleep(1)

    screenshot_path = f"/tmp/cwb-verify-{url.replace('/', '-').strip('-')}.png"
    _run_ab("screenshot", screenshot_path)
    _, snap = _run_ab("snapshot")

    # Check for errors
    errors = []
    if "error" in snap.lower() and "500" in snap:
        errors.append("500 error detected on page")
    if not snap.strip():
        errors.append("Page appears blank")

    return {
        "page": url,
        "screenshot": screenshot_path,
        "content_summary": snap[:500] if snap else "(empty)",
        "errors": errors,
        "environment": environment,
        "role": role,
    }


def verify_sidebar(
    environment: str = "staging",
    role: str = "viewer",
) -> dict:
    """Login and verify sidebar sections are present.

    Checks that Dashboard, Preview, and Tools sections exist.
    """
    result = login(environment, role)
    if not result.get("logged_in"):
        return {"error": f"Login failed: {result.get('error', 'unknown')}"}

    _, snap = _run_ab("snapshot", "-i")

    # Parse sections from snapshot
    sections_found = []
    expected = ["DASHBOARD", "PREVIEW", "TOOLS"]

    for section in expected:
        # Look for section header or button
        if section.lower() in snap.lower():
            sections_found.append(section)

    screenshot_path = "/tmp/cwb-sidebar.png"
    _run_ab("screenshot", screenshot_path)

    missing = [s for s in expected if s not in sections_found]

    return {
        "screenshot": screenshot_path,
        "sections_found": sections_found,
        "sections_expected": expected,
        "missing": missing,
        "passed": len(missing) == 0,
        "environment": environment,
        "role": role,
    }


def smoke_test(
    environment: str = "staging",
    role: str = "viewer",
    pages: list[str] | None = None,
) -> dict:
    """Login once, visit pages, screenshot each. Report pass/fail.

    Args:
        environment: "staging" or "production"
        role: "viewer" or "admin"
        pages: List of paths to visit. Defaults to core live pages.
    """
    if pages is None:
        pages = [
            "/dashboard",
            "/dashboard/financial",
            "/dashboard/metrics",
            "/dashboard/changelog",
        ]

    result = login(environment, role)
    if not result.get("logged_in"):
        return {"error": f"Login failed: {result.get('error', 'unknown')}"}

    env = get_environment(environment)
    results = []
    passed = 0
    failed = 0

    for page in pages:
        full_url = f"{env.url}{page}"
        code, out = _run_ab("open", full_url)
        time.sleep(1)

        slug = page.replace("/", "-").strip("-") or "root"
        screenshot_path = f"/tmp/cwb-smoke-{slug}.png"
        _run_ab("screenshot", screenshot_path)
        _, snap = _run_ab("snapshot")

        # Basic check: page has content
        has_content = bool(snap.strip()) and "error" not in snap.lower()

        if has_content:
            passed += 1
            results.append({"page": page, "screenshot": screenshot_path, "status": "pass"})
        else:
            failed += 1
            results.append({"page": page, "screenshot": screenshot_path, "status": "fail", "error": "Page appears empty or errored"})

    return {
        "total_pages": len(pages),
        "passed": passed,
        "failed": failed,
        "results": results,
        "environment": environment,
        "role": role,
    }


def test_overlay(
    page_slug: str,
    environment: str = "staging",
) -> dict:
    """Navigate to a preview page and verify the overlay appears.

    Args:
        page_slug: Page path (e.g. "/dashboard/operations")
        environment: "staging" or "production"
    """
    # Use admin to ensure access to all pages
    result = login(environment, "admin")
    if not result.get("logged_in"):
        return {"error": f"Login failed: {result.get('error', 'unknown')}"}

    env = get_environment(environment)
    full_url = f"{env.url}{page_slug}"

    _run_ab("open", full_url)
    time.sleep(1)

    # Screenshot with overlay
    screenshot_with = f"/tmp/cwb-overlay-{page_slug.replace('/', '-').strip('-')}.png"
    _run_ab("screenshot", screenshot_with)
    _, snap = _run_ab("snapshot")

    overlay_present = "isn't live yet" in snap.lower() or "this page" in snap.lower()
    vendor = None
    if "Data source:" in snap:
        for line in snap.split("\n"):
            if "Data source:" in line:
                vendor = line.split("Data source:")[-1].strip()
                break

    # Try to dismiss
    dismissed = False
    if overlay_present:
        # Look for dismiss button
        for line in snap.split("\n"):
            if "view page preview" in line.lower() or "close" in line.lower():
                import re
                match = re.search(r'ref=(e\d+)', line)
                if match:
                    _run_ab("click", f"@{match.group(1)}")
                    time.sleep(1)
                    dismissed = True
                    break

    screenshot_after = f"/tmp/cwb-overlay-dismissed-{page_slug.replace('/', '-').strip('-')}.png"
    if dismissed:
        _run_ab("screenshot", screenshot_after)

    return {
        "overlay_present": overlay_present,
        "overlay_vendor": vendor,
        "dismissed": dismissed,
        "screenshot_with_overlay": screenshot_with,
        "screenshot_after_dismiss": screenshot_after if dismissed else None,
        "page": page_slug,
        "environment": environment,
    }
