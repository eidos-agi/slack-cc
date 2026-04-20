"""cerebro-deploy CLI entry point with deploy type detection.

Usage:
    cerebro-deploy migration <migration_name> [options]
    cerebro-deploy data-daemon <environment> [options]
    cerebro-deploy cerebro <environment> [options]
    cerebro-deploy mcp <environment> [options]
    cerebro-deploy docs [options]

    # Legacy (defaults to data-daemon for backward compat):
    cerebro-deploy data-daemon production --dry-run
"""

from __future__ import annotations

import argparse
import sys
import time

from cerebro_deploy.config import resolve_service, TOPOLOGY
from cerebro_deploy.runner import Step, run_steps, print_summary


BANNER = r"""
   ___              _                  ___           _
  / __\___ _ __ ___| |__  _ __ ___    /   \___ _ __ | | ___  _   _
 / /  / _ \ '__/ _ \ '_ \| '__/ _ \  / /\ / _ \ '_ \| |/ _ \| | | |
/ /__|  __/ | |  __/ |_) | | | (_) |/ /_//  __/ |_) | | (_) | |_| |
\____/\___|_|  \___|_.__/|_|  \___/___,' \___| .__/|_|\___/ \__, |
                                              |_|            |___/
"""

DEPLOY_TYPES = {
    "migration":   "Apply a cerebro-migrations DDL",
    "data-daemon": "Deploy the extraction pipeline (full 32-step ADR-005 process)",
    "cerebro":     "Deploy the Next.js dashboard",
    "mcp":         "Deploy Cloudflare Worker MCP server",
    "docs":        "Verify documentation matches reality",
}


def _build_steps_for_type(deploy_type: str) -> list[Step]:
    """Build the step list for a given deploy type."""

    if deploy_type == "data-daemon":
        # Full 32-step ADR-005 process — uses the rich existing step modules
        from cerebro_deploy.steps.preflight import PREFLIGHT_STEPS
        from cerebro_deploy.steps.deploy import DEPLOY_STEPS
        from cerebro_deploy.steps.verify import VERIFY_STEPS
        from cerebro_deploy.steps.postdeploy import POSTDEPLOY_STEPS

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

    elif deploy_type == "migration":
        from cerebro_deploy.types.migration import build_steps as _build
        # build_steps needs config+ctx but we just need the step list structure
        # We return a builder function instead — handled in main()
        return None  # type: ignore  # sentinel — built in main()

    elif deploy_type == "cerebro":
        from cerebro_deploy.types.cerebro_app import build_steps as _build
        return None  # type: ignore

    elif deploy_type == "mcp":
        from cerebro_deploy.types.mcp_worker import build_steps as _build
        return None  # type: ignore

    elif deploy_type == "docs":
        from cerebro_deploy.types.docs_verify import build_steps as _build
        return None  # type: ignore

    raise ValueError(f"Unknown deploy type: {deploy_type}")


def _resolve_config_and_steps(deploy_type: str, target: str | None, ctx: dict):
    """Resolve config and steps for any deploy type.

    Returns (config, steps).
    """
    if deploy_type == "data-daemon":
        config = resolve_service("data-daemon", target)
        from cerebro_deploy.steps.preflight import PREFLIGHT_STEPS
        from cerebro_deploy.steps.deploy import DEPLOY_STEPS
        from cerebro_deploy.steps.verify import VERIFY_STEPS
        from cerebro_deploy.steps.postdeploy import POSTDEPLOY_STEPS

        steps = []
        for phase_name, step_list in [
            ("Phase 1: Pre-flight", PREFLIGHT_STEPS),
            ("Phase 2: Deploy", DEPLOY_STEPS),
            ("Phase 3: Verify", VERIFY_STEPS),
            ("Phase 4: Post-deploy", POSTDEPLOY_STEPS),
        ]:
            for number, name, fn in step_list:
                steps.append(Step(number=number, phase=phase_name, name=name, fn=fn))
        return config, steps

    elif deploy_type == "cerebro":
        # Reuse preflight from existing steps + type-specific deploy/verify
        config = resolve_service("cerebro", target)
        from cerebro_deploy.types.cerebro_app import build_steps
        steps = build_steps(config, ctx)
        return config, steps

    elif deploy_type == "mcp":
        config = resolve_service("cerebro-mcp", target)
        from cerebro_deploy.types.mcp_worker import build_steps
        steps = build_steps(config, ctx)
        return config, steps

    elif deploy_type == "migration":
        from cerebro_deploy.types.migration import build_config, build_steps
        config = build_config(target)
        ctx["target"] = target  # migration name
        steps = build_steps(config, ctx)
        return config, steps

    elif deploy_type == "docs":
        from cerebro_deploy.types.docs_verify import build_config, build_steps
        config = build_config()
        steps = build_steps(config, ctx)
        return config, steps

    raise ValueError(f"Unknown deploy type: {deploy_type}")


def list_services() -> None:
    """Print available services from topology."""
    services = TOPOLOGY.get("services", {})
    print("\nAvailable services:")
    for name, svc in sorted(services.items()):
        envs = list(svc.get("deploy_pipeline", {}).keys())
        print(f"  {name:25s} environments: {', '.join(envs)}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="cerebro-deploy",
        description=(
            "Rigid deployment CLI with verification gates. No exceptions.\n\n"
            "Deploy types:\n"
            + "\n".join(f"  {k:15s} {v}" for k, v in DEPLOY_TYPES.items())
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  cerebro-deploy data-daemon production\n"
            "  cerebro-deploy cerebro staging --dry-run\n"
            "  cerebro-deploy migration add_fleet_tables\n"
            "  cerebro-deploy mcp production\n"
            "  cerebro-deploy docs\n"
        ),
    )
    parser.add_argument(
        "type",
        metavar="TYPE",
        help="Deploy type: " + ", ".join(DEPLOY_TYPES.keys()),
    )
    parser.add_argument(
        "target",
        nargs="?",
        metavar="TARGET",
        help=(
            "Environment (staging/production) for service deploys, "
            "or migration name for 'migration' type. "
            "Not required for 'docs'."
        ),
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
        "--force",
        action="store_true",
        help="Force rebuild (--no-cache for Docker if applicable)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all intermediate output",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available services and environments from topology",
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

    deploy_type: str = args.type
    target: str | None = args.target

    # Validate deploy type
    if deploy_type not in DEPLOY_TYPES:
        print(f"Error: unknown deploy type '{deploy_type}'")
        print(f"Available types: {', '.join(DEPLOY_TYPES.keys())}")
        return 1

    # Validate target requirements
    if deploy_type == "docs":
        pass  # no target needed
    elif target is None:
        if deploy_type == "migration":
            print("Error: migration requires a migration name")
            print("Usage: cerebro-deploy migration <migration_name>")
        else:
            print(f"Error: {deploy_type} requires an environment")
            print(f"Usage: cerebro-deploy {deploy_type} <staging|production>")
        return 1

    # Validate environment for service deploys
    if deploy_type in ("data-daemon", "cerebro", "mcp"):
        if target not in ("staging", "production", "develop"):
            print(f"Error: environment must be 'staging', 'production', or 'develop', got '{target}'")
            return 1

    # Print banner
    color = not args.no_color
    print(BANNER)

    # Build context
    context: dict = {
        "deploy_type": deploy_type,
        "target": target,
        "dry_run": args.dry_run,
        "skip_tests": args.skip_tests,
        "force": args.force,
        "verbose": args.verbose,
    }

    # Resolve config and steps for this deploy type
    try:
        config, all_steps = _resolve_config_and_steps(deploy_type, target, context)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        return 1

    # Print warnings
    if args.skip_tests:
        if color:
            print(f"\033[93m  WARNING: --skip-tests flag active. Tests and lint will be skipped.\033[0m")
            print(f"\033[93m  This is for EMERGENCY DEPLOYS ONLY.\033[0m")
        else:
            print("  WARNING: --skip-tests flag active. Tests and lint will be skipped.")
            print("  This is for EMERGENCY DEPLOYS ONLY.")

    if args.dry_run:
        if color:
            print(f"\033[94m  DRY RUN mode -- pre-flight only, no deploy will be triggered.\033[0m")
        else:
            print("  DRY RUN mode -- pre-flight only, no deploy will be triggered.")

    print(f"  Type:        {deploy_type} — {DEPLOY_TYPES[deploy_type]}")
    print(f"  Service:     {config.name}")
    print(f"  Environment: {config.environment}")
    print(f"  Branch:      {config.branch}")
    print(f"  Repo:        {config.repo}")
    print(f"  Runtime:     {config.runtime}")
    if deploy_type == "migration" and target:
        print(f"  Migration:   {target}")
    print(f"  Steps:       {len(all_steps)}")

    # Determine stop phase for dry run
    stop_phase = None
    if args.dry_run:
        # Stop after the first readiness/pre-flight phase
        phases_seen = []
        for s in all_steps:
            if s.phase not in phases_seen:
                phases_seen.append(s.phase)
        # Stop after second phase (identity + readiness) if it exists, else first
        if len(phases_seen) >= 2:
            stop_phase = phases_seen[1]
        elif phases_seen:
            stop_phase = phases_seen[0]

    t0 = time.monotonic()
    success, results = run_steps(
        all_steps,
        config,
        context,
        color=color,
        stop_after_phase=stop_phase,
    )
    elapsed = time.monotonic() - t0

    # Print summary
    print_summary(config, results, success, color=color)

    if color:
        print(f"  \033[2mTotal time: {elapsed:.1f}s\033[0m\n")
    else:
        print(f"  Total time: {elapsed:.1f}s\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
