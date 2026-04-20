"""Common steps shared across deploy types.

Each function takes (config: ServiceConfig, context: dict) -> StepResult.
"""

from __future__ import annotations

import os
import subprocess

from cerebro_deploy.config import ServiceConfig, get_incidents
from cerebro_deploy.runner import StepResult


def _run(cmd: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=120)


# ---------------------------------------------------------------------------
# PHASE 1: IDENTITY
# ---------------------------------------------------------------------------

def load_topology(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 1: verify service exists in topology."""
    if not config.repo:
        return StepResult(False, f"Service '{config.name}' has no repo in topology",
                          "Run cerebro-docs overview() to check available services.")
    return StepResult(True, f"repo={config.repo} runtime={config.runtime}")


def load_incidents(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 2: check for active incidents."""
    incidents = get_incidents(config.name)
    active = [i for i in incidents if str(i.get("status", "")).upper() == "ACTIVE"]
    if active:
        names = ", ".join(str(i.get("title", i.get("id", "?"))) for i in active)
        return StepResult(True, f"WARNING: {len(active)} active incident(s): {names}")
    return StepResult(True, f"No active incidents for {config.name}")


def check_environment(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 3: validate environment argument."""
    env = config.environment
    if env not in ("production", "develop"):
        return StepResult(False, f"Invalid environment '{env}'",
                          "Environment must be 'staging' or 'production'.")
    return StepResult(True, f"environment={env} branch={config.branch}")


def check_git_clean(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 4: working tree must be clean."""
    repo_dir = _find_repo_dir(config)
    if not repo_dir:
        return StepResult(True, "Repo dir not found locally, skipping git check")
    r = _run(["git", "status", "--porcelain"], cwd=repo_dir)
    if r.returncode != 0:
        return StepResult(False, f"git status failed: {r.stderr.strip()}",
                          "Check that the repo directory is valid.")
    if r.stdout.strip():
        return StepResult(False, "Uncommitted changes detected",
                          "Commit or stash first.")
    return StepResult(True, "Working tree clean")


def check_git_branch(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 5: must be on the correct branch."""
    repo_dir = _find_repo_dir(config)
    if not repo_dir:
        return StepResult(True, "Repo dir not found locally, skipping branch check")
    r = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir)
    if r.returncode != 0:
        return StepResult(False, f"git rev-parse failed: {r.stderr.strip()}")
    branch = r.stdout.strip()
    if branch != config.branch:
        return StepResult(False, f"On branch '{branch}', expected '{config.branch}'",
                          f"Switch to {config.branch} first.")
    return StepResult(True, f"On branch {branch}")


def check_git_sync(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 6: local must be in sync with remote."""
    repo_dir = _find_repo_dir(config)
    if not repo_dir:
        return StepResult(True, "Repo dir not found locally, skipping sync check")
    _run(["git", "fetch", "origin"], cwd=repo_dir)
    r = _run(["git", "rev-list", "--count", f"HEAD..origin/{config.branch}"], cwd=repo_dir)
    behind = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else 0
    r2 = _run(["git", "rev-list", "--count", f"origin/{config.branch}..HEAD"], cwd=repo_dir)
    ahead = int(r2.stdout.strip()) if r2.returncode == 0 and r2.stdout.strip().isdigit() else 0

    if behind > 0:
        return StepResult(False, f"Local is {behind} commit(s) behind remote",
                          "Pull first: git pull origin " + config.branch)
    if ahead > 0:
        return StepResult(True, f"WARNING: Local is {ahead} commit(s) ahead. Push first?")
    return StepResult(True, "In sync with remote")


def run_tests(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 7: run pytest."""
    if ctx.get("skip_tests"):
        return StepResult(True, "SKIPPED (--skip-tests flag)")
    repo_dir = _find_repo_dir(config)
    if not repo_dir:
        return StepResult(True, "Repo dir not found locally, skipping tests")
    r = _run(["python", "-m", "pytest", "-x", "--tb=short", "-q"], cwd=repo_dir)
    if r.returncode != 0:
        detail = r.stdout.strip().split("\n")[-3:] if r.stdout else [r.stderr.strip()]
        return StepResult(False, "\n".join(detail), "Fix test failures before deploying.")
    passed_line = r.stdout.strip().split("\n")[-1] if r.stdout else "OK"
    return StepResult(True, passed_line)


def run_lint(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 8: run ruff."""
    if ctx.get("skip_tests"):
        return StepResult(True, "SKIPPED (--skip-tests flag)")
    repo_dir = _find_repo_dir(config)
    if not repo_dir:
        return StepResult(True, "Repo dir not found locally, skipping lint")
    r = _run(["ruff", "check", "."], cwd=repo_dir)
    if r.returncode != 0:
        lines = r.stdout.strip().split("\n")[-5:] if r.stdout else [r.stderr.strip()]
        return StepResult(False, "\n".join(lines), "Fix lint errors: ruff check . --fix")
    return StepResult(True, "Clean")


def check_ci(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 9: check CI status on latest commit."""
    repo_dir = _find_repo_dir(config)
    if not repo_dir:
        return StepResult(True, "Repo dir not found locally, skipping CI check")
    sha_r = _run(["git", "rev-parse", "HEAD"], cwd=repo_dir)
    if sha_r.returncode != 0:
        return StepResult(False, "Cannot get HEAD SHA")
    sha = sha_r.stdout.strip()
    r = _run(["gh", "api", f"repos/{config.gh_repo}/commits/{sha}/check-runs",
              "--jq", ".check_runs[] | .name + \": \" + .conclusion"])
    if r.returncode != 0:
        return StepResult(True, "Could not query CI (gh cli issue), proceeding")
    lines = [l for l in r.stdout.strip().split("\n") if l]
    if not lines:
        return StepResult(True, "No CI checks found")
    failures = [l for l in lines if "failure" in l.lower() or "null" in l.lower()]
    if failures:
        return StepResult(False, f"CI failures: {'; '.join(failures)}",
                          "Wait for CI to pass or fix the failures.")
    return StepResult(True, f"{len(lines)} checks passed")


def health_check(config: ServiceConfig, ctx: dict) -> StepResult:
    """Step 18/31: verify health endpoint returns 200."""
    if not config.health_url:
        return StepResult(True, "No health URL configured, skipping")
    r = _run(["curl", "-sf", "-o", "/dev/null", "-w", "%{http_code}", config.health_url])
    if r.returncode != 0:
        return StepResult(False, f"Health check failed: {config.health_url}",
                          "Service is not running or unreachable.")
    code = r.stdout.strip()
    if code != "200":
        return StepResult(False, f"Health returned {code}",
                          "Service reports unhealthy.")
    return StepResult(True, f"200 OK from {config.health_url}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_repo_dir(config: ServiceConfig) -> str | None:
    """Find the local clone of the repo. Looks in ~/repos/."""
    if not config.repo:
        return None
    repo_name = config.repo.split("/")[-1] if "/" in config.repo else config.repo
    candidates = [
        os.path.expanduser(f"~/repos/{repo_name}"),
        os.path.expanduser(f"~/repos/greenmark-cockpit"),  # for cockpit itself
    ]
    for c in candidates:
        if os.path.isdir(os.path.join(c, ".git")):
            return c
    return None
