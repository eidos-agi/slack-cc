"""Deploy status checking.

Returns instructions for checking Railway deploy status
since we can't call railguey directly from Python.
"""

from .knowledge import get_environment, RAILWAY_PROJECT


def deploy_status(environment: str = "staging") -> dict:
    """Check Railway deployment status for a given environment.

    Returns instructions for the agent to check deploy status.

    Args:
        environment: "staging" or "production"
    """
    env = get_environment(environment)

    return {
        "environment": environment,
        "url": env.url,
        "railway_project": RAILWAY_PROJECT,
        "check_steps": [
            {
                "step": 1,
                "action": f"Switch railguey to {env.railguey_account} account",
                "tool": "mcp__railguey__railguey_account_default",
                "args": {"name": env.railguey_account},
            },
            {
                "step": 2,
                "action": "Check service info",
                "tool": "mcp__railguey__railguey_service_info",
                "args": {"workspace": "/home/dev/repos/cerebro", "service": "cerebro"},
                "note": "latestDeployment.status should be 'SUCCESS'",
            },
            {
                "step": 3,
                "action": "Health check",
                "command": f"curl -s -o /dev/null -w '%{{http_code}}' {env.url}/api/health",
                "expected": "200",
            },
        ],
    }
