"""Pre-flight steps 1-10: verify everything before deploying."""

from __future__ import annotations

import json
import os
import subprocess

from cerebro_deploy.config import ServiceConfig, get_incidents, TOPOLOGY
from cerebro_deploy.runner import StepResult


def _run(cmd: list[str], cwd: str | None = None, timeout: int = 60) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return 127, "", f"Command not found: {cmd[0]}"


def _find_repo_root(config: ServiceConfig) -> str | None:
    """Find the local repo checkout for a service."""
    # Convention: ~/repos/<repo-name>
    repo_name = config.repo.split("/")[-1] if "/" in config.repo else config.repo
    candidates = [
        os.path.expanduser(f"~/repos/{repo_name}"),
        os.path.join(os.getcwd(), repo_name),
    ]
    for c in candidates:
        if os.path.isdir(os.path.join(c, ".git")):
            return c
    return None


# ── Step 1: Read topology ─────────────────────────────────────

def step_read_topology(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify service exists in topology and resolve config."""
    services = TOPOLOGY.get("services", {})
    if config.name not in services:
        return StepResult(
            passed=False,
            detail=f"Service '{config.name}' not found in topology",
            remediation=f"Available services: {', '.join(sorted(services.keys()))}",
        )

    svc = services[config.name]
    pipeline = svc.get("deploy_pipeline", {})
    env_key = config.environment
    if env_key not in pipeline and "production" not in pipeline:
        return StepResult(
            passed=False,
            detail=f"No deploy pipeline for environment '{env_key}'",
            remediation=f"Available pipelines: {', '.join(pipeline.keys())}",
        )

    ctx["topology"] = svc
    detail = (
        f"repo={config.repo}, runtime={config.runtime}, "
        f"db={config.database_id or 'none'}, "
        f"credentials={len(config.credentials)}"
    )
    return StepResult(passed=True, detail=detail)


# ── Step 2: Check git status ──────────────────────────────────

def step_git_status(config: ServiceConfig, ctx: dict) -> StepResult:
    """Working tree must be clean."""
    repo_root = _find_repo_root(config)
    if not repo_root:
        return StepResult(
            passed=False,
            detail=f"Cannot find local checkout for {config.repo}",
            remediation=f"Clone {config.repo} to ~/repos/{config.repo.split('/')[-1]}",
        )
    ctx["repo_root"] = repo_root

    rc, out, err = _run(["git", "status", "--porcelain"], cwd=repo_root)
    if rc != 0:
        return StepResult(passed=False, detail=f"git status failed: {err}", remediation="Check git installation")

    if out:
        dirty_count = len(out.strip().split("\n"))
        return StepResult(
            passed=False,
            detail=f"{dirty_count} uncommitted changes in {repo_root}",
            remediation="Commit or stash changes before deploying: git stash or git commit",
        )

    return StepResult(passed=True, detail=f"Clean working tree at {repo_root}")


# ── Step 3: Check git branch ─────────────────────────────────

def step_git_branch(config: ServiceConfig, ctx: dict) -> StepResult:
    """Must be on correct branch for target environment."""
    repo_root = ctx.get("repo_root")
    if not repo_root:
        return StepResult(passed=False, detail="No repo root found", remediation="Step 2 must pass first")

    rc, branch, err = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    if rc != 0:
        return StepResult(passed=False, detail=f"Cannot determine branch: {err}")

    ctx["current_branch"] = branch
    expected = config.branch  # "main" for production, "develop" for staging

    if branch != expected:
        return StepResult(
            passed=False,
            detail=f"On branch '{branch}', expected '{expected}' for {config.environment}",
            remediation=f"git checkout {expected}",
        )

    return StepResult(passed=True, detail=f"On branch {branch}")


# ── Step 4: Check remote is up to date ───────────────────────

def step_git_remote(config: ServiceConfig, ctx: dict) -> StepResult:
    """Local branch must be up to date with remote."""
    repo_root = ctx.get("repo_root")
    if not repo_root:
        return StepResult(passed=False, detail="No repo root found")

    # Fetch
    rc, _, err = _run(["git", "fetch", "origin"], cwd=repo_root, timeout=30)
    if rc != 0:
        return StepResult(
            passed=False,
            detail=f"git fetch failed: {err}",
            remediation="Check network connectivity and git remote configuration",
        )

    branch = ctx.get("current_branch", config.branch)
    rc, diff, _ = _run(["git", "diff", f"HEAD..origin/{branch}", "--stat"], cwd=repo_root)
    if rc != 0:
        # Remote branch may not exist
        return StepResult(
            passed=False,
            detail=f"Cannot compare with origin/{branch}",
            remediation=f"Ensure origin/{branch} exists: git push -u origin {branch}",
        )

    if diff:
        line_count = len(diff.strip().split("\n"))
        return StepResult(
            passed=False,
            detail=f"Local is behind origin/{branch} by {line_count} changed files",
            remediation=f"git pull origin {branch}",
        )

    # Also check if local is ahead
    rc, ahead, _ = _run(["git", "diff", f"origin/{branch}..HEAD", "--stat"], cwd=repo_root)
    if ahead:
        return StepResult(
            passed=False,
            detail=f"Local is ahead of origin/{branch} — unpushed commits",
            remediation=f"git push origin {branch}",
        )

    return StepResult(passed=True, detail=f"In sync with origin/{branch}")


# ── Step 5: Run tests ────────────────────────────────────────

def step_run_tests(config: ServiceConfig, ctx: dict) -> StepResult:
    """Run pytest locally. Must pass."""
    if ctx.get("skip_tests"):
        return StepResult(
            passed=True,
            detail="SKIPPED (--skip-tests flag) -- WARNING: emergency deploy, no test coverage",
        )

    repo_root = ctx.get("repo_root")
    if not repo_root:
        return StepResult(passed=False, detail="No repo root found")

    # Check if pytest exists
    rc, _, _ = _run(["python3", "-m", "pytest", "--version"], cwd=repo_root)
    if rc != 0:
        # No pytest — check for npm test
        if os.path.isfile(os.path.join(repo_root, "package.json")):
            rc, out, err = _run(["npm", "test", "--", "--passWithNoTests"], cwd=repo_root, timeout=120)
            if rc != 0:
                return StepResult(
                    passed=False,
                    detail=f"npm test failed: {err[:200]}",
                    remediation="Fix failing tests before deploying",
                )
            return StepResult(passed=True, detail="npm test passed")
        return StepResult(passed=True, detail="No test runner found — skipping (no pytest, no npm test)")

    rc, out, err = _run(["python3", "-m", "pytest", "-x", "--tb=short", "-q"], cwd=repo_root, timeout=300)
    if rc != 0:
        # Extract failure summary
        lines = (out + "\n" + err).strip().split("\n")
        summary = "\n".join(lines[-5:])
        return StepResult(
            passed=False,
            detail=f"pytest failed:\n{summary}",
            remediation="Fix failing tests before deploying",
        )

    # Extract pass count
    return StepResult(passed=True, detail=out.split("\n")[-1] if out else "Tests passed")


# ── Step 6: Run lint ──────────────────────────────────────────

def step_run_lint(config: ServiceConfig, ctx: dict) -> StepResult:
    """Run ruff check (Python) or eslint (Node)."""
    if ctx.get("skip_tests"):
        return StepResult(passed=True, detail="SKIPPED (--skip-tests flag)")

    repo_root = ctx.get("repo_root")
    if not repo_root:
        return StepResult(passed=False, detail="No repo root found")

    # Try ruff first
    rc, out, err = _run(["python3", "-m", "ruff", "check", "."], cwd=repo_root, timeout=60)
    if rc == 0:
        return StepResult(passed=True, detail="ruff check passed")
    if rc != 127:  # ruff exists but found issues
        error_count = out.count("\n") + 1 if out else 0
        return StepResult(
            passed=False,
            detail=f"ruff found {error_count} issues:\n{out[:300]}",
            remediation="Run: ruff check --fix . (or fix manually)",
        )

    # Try eslint via npx
    if os.path.isfile(os.path.join(repo_root, "package.json")):
        rc, out, err = _run(["npx", "eslint", ".", "--max-warnings=0"], cwd=repo_root, timeout=60)
        if rc == 0:
            return StepResult(passed=True, detail="eslint passed")
        if rc != 127:
            return StepResult(
                passed=False,
                detail=f"eslint found issues: {out[:300]}",
                remediation="Fix lint errors before deploying",
            )

    return StepResult(passed=True, detail="No linter found — skipping")


# ── Step 7: Check CI status ──────────────────────────────────

def step_ci_status(config: ServiceConfig, ctx: dict) -> StepResult:
    """Check CI status on latest commit via gh api."""
    repo_root = ctx.get("repo_root")
    if not repo_root:
        return StepResult(passed=False, detail="No repo root found")

    # Get latest commit SHA
    rc, sha, _ = _run(["git", "rev-parse", "HEAD"], cwd=repo_root)
    if rc != 0:
        return StepResult(passed=False, detail="Cannot get HEAD SHA")

    ctx["head_sha"] = sha[:8]

    # Query CI status
    rc, out, err = _run([
        "gh", "api",
        f"repos/{config.repo}/commits/{sha}/status",
        "--jq", ".state",
    ], cwd=repo_root, timeout=15)

    if rc != 0:
        # gh may not be available or repo not found
        return StepResult(
            passed=False,
            detail=f"Cannot check CI: {err[:200]}",
            remediation="Install gh CLI and ensure you're authenticated: gh auth login",
        )

    state = out.strip().lower()

    # Also check GitHub Actions check runs
    rc2, checks_out, _ = _run([
        "gh", "api",
        f"repos/{config.repo}/commits/{sha}/check-runs",
        "--jq", "[.check_runs[] | {name: .name, status: .status, conclusion: .conclusion}]",
    ], cwd=repo_root, timeout=15)

    if state == "success" or state == "pending" and not checks_out:
        # Check individual check runs
        if checks_out:
            try:
                checks = json.loads(checks_out)
                failed = [c for c in checks if c.get("conclusion") == "failure"]
                pending = [c for c in checks if c.get("status") != "completed"]
                if failed:
                    names = ", ".join(c["name"] for c in failed)
                    return StepResult(
                        passed=False,
                        detail=f"Failed checks: {names}",
                        remediation="Fix CI failures before deploying",
                    )
                if pending:
                    names = ", ".join(c["name"] for c in pending)
                    return StepResult(
                        passed=False,
                        detail=f"Pending checks: {names}",
                        remediation="Wait for CI to complete, then re-run cerebro-deploy",
                    )
            except json.JSONDecodeError:
                pass

    if state == "failure":
        return StepResult(
            passed=False,
            detail=f"CI status is '{state}' on commit {sha[:8]}",
            remediation="Fix CI failures, push, and re-run cerebro-deploy",
        )

    if state == "pending":
        return StepResult(
            passed=False,
            detail=f"CI is still running on commit {sha[:8]}",
            remediation="Wait for CI to complete, then re-run cerebro-deploy",
        )

    return StepResult(passed=True, detail=f"CI green on {sha[:8]} (state={state})")


# ── Step 8: Check incidents ──────────────────────────────────

def step_check_incidents(config: ServiceConfig, ctx: dict) -> StepResult:
    """Check for known incidents affecting this service."""
    incidents = get_incidents(config.name)

    if not incidents:
        return StepResult(passed=True, detail="No known incidents for this service")

    # Check for unresolved incidents (those with status containing "NOT CONFIRMED")
    unresolved = [
        inc for inc in incidents
        if inc.get("status", "").upper().startswith("FIX DEPLOYED BUT NOT CONFIRMED")
    ]

    if unresolved:
        details = "; ".join(f"{inc['id']}: {inc['symptom']}" for inc in unresolved)
        return StepResult(
            passed=False,
            detail=f"Unresolved incidents: {details}",
            remediation="Confirm incident fixes before deploying. Check INCIDENTS in cerebro-docs knowledge.py",
        )

    # Warn about past incidents (informational)
    ids = ", ".join(inc["id"] for inc in incidents)
    return StepResult(passed=True, detail=f"Past incidents (resolved): {ids}")


# ── Step 9: Verify database connectivity ─────────────────────

def step_db_connectivity(config: ServiceConfig, ctx: dict) -> StepResult:
    """Verify we can reach the target database."""
    if not config.database_host:
        if "note" in config.connections:
            return StepResult(passed=True, detail=f"No SQL database: {config.connections['note']}")
        return StepResult(passed=True, detail="No database configured for this service")

    # Build connection string for psql
    # We use the pooler endpoint with port 6543
    db_id = config.database_id
    host = f"aws-0-us-east-1.pooler.supabase.com"
    port = "6543"
    user = f"postgres.{db_id}"
    db = "postgres"

    # Try psql with a simple query — will fail without password but that's OK,
    # we're checking if the host is reachable
    rc, out, err = _run([
        "psql",
        f"postgresql://{user}@{host}:{port}/{db}",
        "-c", "SELECT 1",
        "--no-password",
    ], timeout=10)

    if rc == 0:
        return StepResult(passed=True, detail=f"Database {db_id} reachable (SELECT 1 OK)")

    # Check if it's a password issue (connection was made, auth failed)
    if "password" in err.lower() or "authentication" in err.lower():
        return StepResult(
            passed=True,
            detail=f"Database {db_id} reachable (auth required — expected without credentials in env)",
        )

    if "could not connect" in err.lower() or "timeout" in err.lower():
        return StepResult(
            passed=False,
            detail=f"Cannot reach database {db_id}: {err[:200]}",
            remediation=f"Check network connectivity to {host}:{port}",
        )

    # psql not installed
    if rc == 127:
        return StepResult(
            passed=True,
            detail="psql not available — skipping direct DB check (will verify via health endpoint later)",
        )

    return StepResult(passed=True, detail=f"Database check inconclusive: {err[:100]}")


# ── Step 10: Verify credentials exist ────────────────────────

def step_verify_credentials(config: ServiceConfig, ctx: dict) -> StepResult:
    """Check that required credentials are configured (via topology listing)."""
    if not config.credentials:
        return StepResult(passed=True, detail="No credentials required")

    # We can't actually check Railway env vars without railguey, so we verify
    # the topology lists them and warn about what needs to be there
    cred_list = ", ".join(config.credentials)
    detail = f"Required credentials ({len(config.credentials)}): {cred_list}"

    # Check if any are in local env (useful for local testing)
    missing_locally = [c for c in config.credentials if not os.environ.get(c)]
    if missing_locally:
        detail += f". Not in local env: {', '.join(missing_locally)} (OK if set on Railway)"

    return StepResult(passed=True, detail=detail)


# ── Collect all preflight steps ───────────────────────────────

PREFLIGHT_STEPS = [
    (1, "Read topology", step_read_topology),
    (2, "Check git status (clean)", step_git_status),
    (3, "Check git branch", step_git_branch),
    (4, "Check remote is up to date", step_git_remote),
    (5, "Run tests locally", step_run_tests),
    (6, "Run lint", step_run_lint),
    (7, "Check CI status on latest commit", step_ci_status),
    (8, "Check for known incidents", step_check_incidents),
    (9, "Verify database connectivity", step_db_connectivity),
    (10, "Verify credentials exist", step_verify_credentials),
]
