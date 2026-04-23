"""Recall pattern — cooperative polling for MCP tools.

Server blocks up to `window` seconds polling internally. If not resolved,
returns recall=True telling the agent to call again. 3-5 paced calls
replace 15+ rapid-fire polls.

Usage:
    from .recall import poll_until_or_recall

    @mcp.tool()
    def check_ci(repo, pr_number, wait=False):
        def poll():
            checks = gh.get_pr_checks(org, repo, pr_number)
            classified = _classify_checks(checks)
            classified["resolved"] = classified["all_green"] or bool(classified["failed"])
            return classified

        if not wait:
            return poll()
        return poll_until_or_recall(poll)
"""

import time
from typing import Any, Callable


def poll_until_or_recall(
    poll_fn: Callable[[], dict[str, Any]],
    window: int = 60,
    interval: int = 15,
    resolved_key: str = "resolved",
) -> dict[str, Any]:
    """Block up to `window` seconds, polling `poll_fn` every `interval`.

    poll_fn must return a dict with a `resolved_key` boolean field.
    When True, returns the result immediately.
    When the window expires with resolved still False, returns
    the latest result with `recall=True` and `recall_advisory`.

    Args:
        poll_fn: Zero-arg function returning a dict with at least {resolved: bool}.
        window: Max seconds to block per call (default 60).
        interval: Seconds between polls (default 15).
        resolved_key: Key in poll result that signals completion (default "resolved").

    Returns:
        The poll result dict, possibly with `recall` and `recall_advisory` added.
    """
    deadline = time.time() + window

    while True:
        result = poll_fn()

        if result.get(resolved_key):
            result.pop(resolved_key, None)
            return result

        if time.time() >= deadline:
            result.pop(resolved_key, None)
            result["recall"] = True
            result["recall_advisory"] = (
                f"Not yet resolved after {window}s. "
                "Call this tool with wait=True again to continue waiting."
            )
            return result

        time.sleep(interval)
