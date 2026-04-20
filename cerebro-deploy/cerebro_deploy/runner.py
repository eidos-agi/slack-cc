"""Step executor with gate logic.

Each step is a callable that returns a StepResult. The runner executes
them sequentially. On failure, it prints the remediation and exits.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Callable

from cerebro_deploy.config import ServiceConfig


@dataclass
class StepResult:
    """Result of a single deployment step."""
    passed: bool
    detail: str
    remediation: str | None = None


# Type alias for step functions
StepFn = Callable[[ServiceConfig, dict], StepResult]


@dataclass
class Step:
    """A named deployment step with phase info."""
    number: int
    phase: str
    name: str
    fn: StepFn


# ANSI colors
class C:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def run_steps(
    steps: list[Step],
    config: ServiceConfig,
    context: dict,
    *,
    color: bool = True,
    stop_after_phase: str | None = None,
) -> tuple[bool, list[tuple[Step, StepResult]]]:
    """Execute steps sequentially with gate logic.

    Returns (all_passed, results).
    """
    use_color = color and _supports_color()
    results: list[tuple[Step, StepResult]] = []
    phase_header_printed: set[str] = set()

    for step in steps:
        # Print phase header
        if step.phase not in phase_header_printed:
            phase_header_printed.add(step.phase)
            if use_color:
                print(f"\n{C.BLUE}{C.BOLD}{'=' * 60}{C.RESET}")
                print(f"{C.BLUE}{C.BOLD}  {step.phase}{C.RESET}")
                print(f"{C.BLUE}{C.BOLD}{'=' * 60}{C.RESET}")
            else:
                print(f"\n{'=' * 60}")
                print(f"  {step.phase}")
                print(f"{'=' * 60}")

        # Run step
        if use_color:
            print(f"\n{C.DIM}Step {step.number:2d}{C.RESET} {step.name} ", end="", flush=True)
        else:
            print(f"\nStep {step.number:2d} {step.name} ", end="", flush=True)

        t0 = time.monotonic()
        try:
            result = step.fn(config, context)
        except Exception as e:
            result = StepResult(
                passed=False,
                detail=f"Exception: {e}",
                remediation="Fix the error and re-run cerebro-deploy",
            )
        elapsed = time.monotonic() - t0

        results.append((step, result))

        # Print result
        elapsed_str = f" ({elapsed:.1f}s)" if elapsed > 0.5 else ""
        if result.passed:
            if use_color:
                print(f"{C.GREEN}PASS{C.RESET}{elapsed_str}")
                if result.detail:
                    print(f"  {C.DIM}{result.detail}{C.RESET}")
            else:
                print(f"PASS{elapsed_str}")
                if result.detail:
                    print(f"  {result.detail}")
        else:
            if use_color:
                print(f"{C.RED}FAIL{C.RESET}{elapsed_str}")
                print(f"\n{C.RED}{C.BOLD}STEP {step.number} FAILED: {step.name}{C.RESET}")
                print(f"  {C.RED}Detail: {result.detail}{C.RESET}")
                if result.remediation:
                    print(f"  {C.YELLOW}Fix: {result.remediation}{C.RESET}")
            else:
                print(f"FAIL{elapsed_str}")
                print(f"\nSTEP {step.number} FAILED: {step.name}")
                print(f"  Detail: {result.detail}")
                if result.remediation:
                    print(f"  Fix: {result.remediation}")
            return False, results

        # Check phase boundary
        if stop_after_phase and step.phase == stop_after_phase:
            # Check if next step is a different phase
            idx = steps.index(step)
            if idx + 1 >= len(steps) or steps[idx + 1].phase != step.phase:
                if use_color:
                    print(f"\n{C.YELLOW}Stopped after phase: {stop_after_phase}{C.RESET}")
                else:
                    print(f"\nStopped after phase: {stop_after_phase}")
                return True, results

    return True, results


def print_summary(
    config: ServiceConfig,
    results: list[tuple[Step, StepResult]],
    success: bool,
    *,
    color: bool = True,
) -> None:
    """Print deployment summary."""
    use_color = color and _supports_color()

    passed = sum(1 for _, r in results if r.passed)
    failed = sum(1 for _, r in results if not r.passed)
    total = len(results)

    if use_color:
        print(f"\n{C.BOLD}{'=' * 60}{C.RESET}")
        print(f"{C.BOLD}  DEPLOYMENT SUMMARY{C.RESET}")
        print(f"{C.BOLD}{'=' * 60}{C.RESET}")
    else:
        print(f"\n{'=' * 60}")
        print(f"  DEPLOYMENT SUMMARY")
        print(f"{'=' * 60}")

    print(f"  Service:     {config.name}")
    print(f"  Environment: {config.environment}")
    print(f"  Branch:      {config.branch}")
    print(f"  Repo:        {config.repo}")
    print(f"  Steps:       {passed}/{total} passed", end="")
    if failed:
        print(f", {failed} failed")
    else:
        print()

    if success:
        if use_color:
            print(f"\n  {C.GREEN}{C.BOLD}DEPLOY SUCCEEDED{C.RESET}")
        else:
            print(f"\n  DEPLOY SUCCEEDED")
    else:
        if use_color:
            print(f"\n  {C.RED}{C.BOLD}DEPLOY FAILED{C.RESET}")
        else:
            print(f"\n  DEPLOY FAILED")

    # Show pre/post row counts if available
    context_data = {}
    for step, result in results:
        if "row_counts" in result.detail.lower() or "rows" in result.detail.lower():
            context_data[step.name] = result.detail

    if context_data:
        print(f"\n  Data changes:")
        for name, detail in context_data.items():
            print(f"    {name}: {detail}")

    print()
