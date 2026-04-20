"""Ship and promote orchestration.

These tools compose knowledge with instructions for the calling agent.
They don't call child MCPs directly (no MCP-to-MCP calls in Python).
Instead, they return step-by-step instructions with the exact tool
calls the agent should make, pre-filled with the right arguments.

This is the "knowledge as instructions" pattern — the MCP knows
what to do, the agent executes it.
"""

from .knowledge import get_environment, MERGE_RULES, CI_CHECKS, BRANCH_PROTECTION


def ship_to_staging(
    branch: str,
    title: str = "",
    closes_issue: int | None = None,
) -> dict:
    """Generate the full ship-to-staging ceremony.

    Returns step-by-step instructions with exact MCP tool calls.

    Args:
        branch: Git branch to ship
        title: PR title (defaults to branch name)
        closes_issue: Existing issue number, or instructions to create one
    """
    pr_title = title or branch.replace("/", ": ").replace("-", " ")

    steps = []

    if not closes_issue:
        steps.append({
            "step": 1,
            "action": "Create issue",
            "tool": "mcp__cerebro-github__create_work",
            "args": {"title": pr_title, "repo": "cerebro", "status": "in_progress"},
            "note": "Save the returned issue number for the next step",
        })

    steps.append({
        "step": len(steps) + 1,
        "action": "Open PR against develop",
        "tool": "mcp__cerebro-github__open_pr",
        "args": {
            "repo": "cerebro",
            "branch": branch,
            "closes": closes_issue or "<issue_number_from_step_1>",
            "base": "develop",
            "title": pr_title,
        },
    })

    steps.append({
        "step": len(steps) + 1,
        "action": "Wait for CI (poll until all_green)",
        "tool": "mcp__cerebro-github__check_ci",
        "args": {"repo": "cerebro", "pr_number": "<pr_number>"},
        "expected_checks": [c.name for c in CI_CHECKS],
        "note": "Poll every 30s until all_green is true",
    })

    steps.append({
        "step": len(steps) + 1,
        "action": "Merge to develop (no Rhea gate needed)",
        "tool": "mcp__cerebro-github__merge_pr",
        "args": {"repo": "cerebro", "pr_number": "<pr_number>"},
        "note": MERGE_RULES["develop"],
    })

    steps.append({
        "step": len(steps) + 1,
        "action": "Wait for Railway staging deploy",
        "tool": "mcp__railguey__railguey_service_info",
        "args": {"workspace": "/home/dev/repos/cerebro", "service": "cerebro"},
        "pre_step": "Switch to develop account: mcp__railguey__railguey_account_default(name='develop')",
        "note": "Poll until latestDeployment.status is 'SUCCESS'",
    })

    steps.append({
        "step": len(steps) + 1,
        "action": "Verify staging health",
        "command": f"curl -s -o /dev/null -w '%{{http_code}}' {get_environment('staging').url}/api/health",
        "expected": "200",
    })

    steps.append({
        "step": len(steps) + 1,
        "action": "Browser verify on staging",
        "tool": "mcp__cerebro-web-builder__verify_sidebar",
        "args": {"environment": "staging", "role": "viewer"},
        "note": "Or use ab-login: ./tools/agent-browser/ab-login staging viewer",
    })

    return {
        "ceremony": "ship_to_staging",
        "branch": branch,
        "target": "develop",
        "deploy_url": get_environment("staging").url,
        "steps": steps,
    }


def promote_to_production(
    pr_number: int | None = None,
    branch: str = "",
    closes_issue: int | None = None,
) -> dict:
    """Generate the full promote-to-production ceremony.

    This assumes code is already verified on staging (develop).

    Args:
        pr_number: Existing PR against main. If None, instructions to create one.
        branch: Branch to promote (e.g. "promote/feature-name")
        closes_issue: Issue number for the promotion
    """
    steps = []

    if not pr_number:
        if not closes_issue:
            steps.append({
                "step": 1,
                "action": "Create promotion issue",
                "tool": "mcp__cerebro-github__create_work",
                "args": {"title": f"Promote {branch or 'develop'} to production", "repo": "cerebro", "status": "in_progress"},
            })

        steps.append({
            "step": len(steps) + 1,
            "action": "Create promotion branch from develop",
            "commands": [
                "git checkout main && git pull origin main",
                f"git checkout -b {branch or 'promote/to-prod'} && git merge develop --no-edit",
                f"git push -u origin {branch or 'promote/to-prod'}",
            ],
        })

        steps.append({
            "step": len(steps) + 1,
            "action": "Open PR against main",
            "tool": "mcp__cerebro-github__open_pr",
            "args": {
                "repo": "cerebro",
                "branch": branch or "promote/to-prod",
                "closes": closes_issue or "<issue_number>",
                "base": "main",
            },
        })

    steps.append({
        "step": len(steps) + 1,
        "action": "Wait for CI",
        "tool": "mcp__cerebro-github__check_ci",
        "args": {"repo": "cerebro", "pr_number": pr_number or "<pr_number>"},
    })

    steps.append({
        "step": len(steps) + 1,
        "action": "Merge to main (RHEA GATE REQUIRED)",
        "tool": "mcp__cerebro-github__merge_pr",
        "args": {"repo": "cerebro", "pr_number": pr_number or "<pr_number>"},
        "note": MERGE_RULES["main"],
        "warning": "This triggers a Rhea gate. You must run rhea_quick or rhea_challenge with the returned challenge_prompt, then call merge_pr again with gate_token + rhea_decision.",
    })

    steps.append({
        "step": len(steps) + 1,
        "action": "Wait for Railway production deploy",
        "tool": "mcp__railguey__railguey_service_info",
        "args": {"workspace": "/home/dev/repos/cerebro", "service": "cerebro"},
        "pre_step": "Switch to production account: mcp__railguey__railguey_account_default(name='production')",
        "note": "Poll until latestDeployment.status is 'SUCCESS'",
    })

    steps.append({
        "step": len(steps) + 1,
        "action": "Post-deploy smoke check",
        "tool": "mcp__cerebro-web-builder__smoke_test",
        "args": {"environment": "production", "role": "viewer"},
        "alternative": f"curl -s -o /dev/null -w '%{{http_code}}' {get_environment('production').url}/api/health",
    })

    return {
        "ceremony": "promote_to_production",
        "target": "main",
        "deploy_url": get_environment("production").url,
        "steps": steps,
        "warning": "NEVER merge untested code to main. Always verify on staging first.",
    }
