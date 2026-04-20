"""cerebro-deploy CLI entry point.

Usage:
    cerebro-deploy <service> <environment> [options]
    cerebro-deploy data-daemon production
    cerebro-deploy cerebro staging --dry-run
    cerebro-deploy data-daemon production --skip-tests
"""

from __future__ import annotations

import argparse
import sys

from cerebro_deploy.config import resolve_service, TOPOLOGY
from cerebro_deploy.runner import Step, run_steps, print_summary
from cerebro_deploy.steps.preflight import PREFLIGHT_STEPS
from cerebro_deploy.steps.deploy import DEPLOY_STEPS
from cerebro_deploy.steps.verify import VERIFY_STEPS
from cerebro_deploy.steps.postdeploy import POSTDEPLOY_STEPS


BANNER = r"""
   ___              _                  ___           _
  / __\___ _ __ ___| |__  _ __ ___    /   \___ _ __ | | ___  _   _
 / /  / _ \ '__/ _ \ '_ \| '__/ _ \  / /\ / _ \ '_ \| |/ _ \| | | |
/ /__|  __/ | |  __/ |_) | | | (_) |/ /_//  __/ |_) | | (_) | |_| |
\____/\___|_|  \___|_.__/|_|  \___/___,' \___| .__/|_|\___/ \__, |
                                              |_|            |___/
"""


def build_steps(dry_run: bool) -> list[Step]:
    """Build the full step list from all phases."""
    steps = []

    phase_map = [
        ("Phase 1: Pre-flight", PREFLIGHT_STEPS),
        ("Phase 2: Deploy", DEPLOY_STEPS),
        ("Phase 3: Verify", VERIFY_STEPS),
        ("Phase 4: Post-deploy", POSTDEPLOY_STEPS),
    ]

    for phase_name, step_list in phase_map:
        for number, name, fn in step_list:
            steps.append(Step(number=number, phase=phase_name, name=name, fn=fn))

    return steps


def list_services() -> None:
    """Print available services."""
    services = TOPOLOGY.get("services", {})
    print("\nAvailable services:")
    for name, svc in sorted(services.items()):
        envs = list(svc.get("deploy_pipeline", {}).keys())
        print(f"  {name:25s} environments: {', '.join(envs)}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="cerebro-deploy",
        description="Rigid step-by-step deployment CLI with verification gates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: cerebro-deploy data-daemon production --dry-run",
    )
    parser.add_argument(
        "service",
        nargs="?",
        help="Service name from topology (e.g., data-daemon, cerebro, cerebro-mcp)",
    )
    parser.add_argument(
        "environment",
        nargs="?",
        help="Target environment: production, staging, or develop",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pre-flight checks only, do not deploy",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip local tests and lint (emergency deploys only)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available services and environments",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )

    args = parser.parse_args()

    if args.list:
        list_services()
        return 0

    if not args.service or not args.environment:
        parser.print_help()
        print()
        list_services()
        return 1

    # Normalize environment
    env = args.environment.lower()
    if env not in ("production", "staging", "develop"):
        print(f"Error: environment must be 'production', 'staging', or 'develop', got '{env}'")
        return 1

    # Print banner
    color = not args.no_color

    print(BANNER)

    # Resolve service config
    try:
        config = resolve_service(args.service, env)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Build context
    context: dict = {
        "dry_run": args.dry_run,
        "skip_tests": args.skip_tests,
    }

    # Print warnings
    if args.skip_tests:
        if color:
            print(f"\033[93m  WARNING: --skip-tests flag active. Tests and lint will be skipped.\033[0m")
            print(f"\033[93m  This is for EMERGENCY DEPLOYS ONLY.\033[0m")
        else:
            print(f"  WARNING: --skip-tests flag active. Tests and lint will be skipped.")
            print(f"  This is for EMERGENCY DEPLOYS ONLY.")

    if args.dry_run:
        if color:
            print(f"\033[94m  DRY RUN mode -- pre-flight only, no deploy will be triggered.\033[0m")
        else:
            print(f"  DRY RUN mode -- pre-flight only, no deploy will be triggered.")

    print(f"  Service:     {config.name}")
    print(f"  Environment: {config.environment}")
    print(f"  Branch:      {config.branch}")
    print(f"  Repo:        {config.repo}")
    print(f"  Runtime:     {config.runtime}")

    # Build and run steps
    all_steps = build_steps(args.dry_run)

    stop_phase = "Phase 1: Pre-flight" if args.dry_run else None

    success, results = run_steps(
        all_steps,
        config,
        context,
        color=color,
        stop_after_phase=stop_phase,
    )

    # Print summary
    print_summary(config, results, success, color=color)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
