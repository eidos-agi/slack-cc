# cerebro-web-builder MCP -- Plan

Python FastMCP server that encodes the Cerebro web deployment pipeline as executable knowledge. An agent using this MCP never needs to rediscover deploy topology, CI ceremony, login flows, or test account credentials. The MCP knows it all and exposes tools that compose that knowledge into end-to-end workflows.

## Why this exists

Every session that touches Cerebro's frontend rediscovers the same facts: which branch maps to which environment, how to log in with TOTP, what CI checks must pass, when Rhea is required. cerebro-web-builder collapses that rediscovery to zero. The knowledge is the product.

## Directory structure

```
cerebro-web-builder-mcp/
  pyproject.toml
  cerebro_web_builder/
    __init__.py
    cli.py                  # Entry point: `cerebro-web-builder serve`
    server.py               # FastMCP instance + tool registration
    knowledge.py            # Encoded facts: topology, accounts, ceremony rules
    auth.py                 # TOTP generation + delegates to ab-login for login automation
    shipping.py             # ship_to_staging, promote_to_production orchestration
    verification.py         # verify_page, verify_sidebar, smoke_test, test_overlay
    deploy.py               # deploy_status via railguey
```

## Knowledge registry

These facts are encoded in `knowledge.py` as typed dataclasses, not discovered at runtime.

### Deploy topology

| Fact | Value |
|------|-------|
| Production branch | `main` |
| Staging branch | `develop` |
| Production URL | `cerebro.greenmark.jettaintelligence.com` |
| Staging URL | `staging-cerebro-greenmark.jettaintelligence.com` |
| Railway project | `greenmark-waste-solutions` |
| Production railguey account | `production` |
| Staging railguey account | `develop` |
| Both branches protected | PR required for both |

### CI ceremony

| Check | Required |
|-------|----------|
| Type Check | yes |
| Lint | yes |
| Unit Tests | yes |
| Security File Check | yes |
| Build | yes |

CI verified via cerebro-github `check_ci` tool.

### Merge ceremony

| Target | Rule |
|--------|------|
| develop | Direct merge after CI passes |
| main (production) | Rhea gate required via cerebro-github `merge_pr` |

### Browserbase

| Key | Value |
|-----|-------|
| API key | `bb_live_ykBt2_UNkOT0yZoSYSSdx9eR4k8` |
| Project ID | `2080dfe2-9805-4fc7-be2f-512dc5762e90` |
| Persistent contexts | Supported (cookie reuse across sessions) |

### Test accounts

| Role | Email | Password | TOTP secret |
|------|-------|----------|-------------|
| Viewer | `dshanklin+test1@greenmarkwaste.com` | `test-viewer-2026` | `IBIISTGZO6JR2R7DMQ5KS2U6RZXWEEOQ` |
| Admin | `dshanklin+e2eadmin@greenmarkwaste.com` | `e2e-superadmin-2026!` | `LCPM4CU6EPRLDF7FGQ4FZDJZWH7GEPNO` |

### Login flow (encoded in auth.py)

1. Navigate to login page
2. Fill email field
3. Fill password field
4. Click submit
5. Wait for MFA page
6. Generate TOTP code (HMAC-SHA1, 6 digits, 30s period, base32 secret)
7. Fill TOTP field
8. Click submit
9. Wait for dashboard

### Page registry

Source of truth: `lib/page-registry.ts` in the cerebro repo. The MCP reads this at tool-call time (not cached) so it always reflects the current state.

## Tool signatures

### 1. `ship_to_staging`

Push a branch to staging end-to-end: issue, PR, CI, merge, deploy, verify.

```python
def ship_to_staging(
    branch: str,              # Git branch to ship
    closes_issue: int | None = None,  # Existing issue number, or create one
    verify_pages: list[str] | None = None,  # Page slugs to verify after deploy
) -> dict:
    """
    Returns:
        {
            "issue": int,           # GitHub issue number
            "pr": int,              # PR number
            "ci_status": str,       # "passed"
            "merged": bool,
            "deploy_url": str,      # staging URL
            "verification": dict | None,  # smoke_test results if verify_pages provided
        }
    """
```

Orchestration: cerebro-github `create_work` -> `open_pr` (base=develop) -> `check_ci` (poll) -> merge -> railguey `railguey_deployments` (poll) -> optionally `verify_page` on each slug.

### 2. `verify_page`

Open a Browserbase session, login, navigate to a page, screenshot, extract state.

```python
def verify_page(
    url: str,                    # Full URL or path (e.g. "/dashboard/financial")
    environment: str = "staging",  # "staging" or "production"
    role: str = "viewer",        # "viewer" or "admin"
) -> dict:
    """
    Returns:
        {
            "screenshot_path": str,   # Local path to PNG
            "page_title": str,
            "status_code": int,
            "errors": list[str],      # Console errors captured
            "content_summary": str,   # AI-friendly page description
        }
    """
```

### 3. `verify_sidebar`

Login and screenshot sidebar in both collapsed and expanded states.

```python
def verify_sidebar(
    environment: str = "staging",
    role: str = "viewer",
) -> dict:
    """
    Returns:
        {
            "expanded_screenshot": str,
            "collapsed_screenshot": str,
            "sections_found": list[str],
            "sections_expected": list[str],
            "missing": list[str],
        }
    """
```

### 4. `smoke_test`

Login once, visit every page accessible to the given role, screenshot each.

```python
def smoke_test(
    environment: str = "staging",
    role: str = "viewer",
) -> dict:
    """
    Returns:
        {
            "total_pages": int,
            "passed": int,
            "failed": int,
            "results": [
                {
                    "page": str,
                    "screenshot": str,
                    "status": "pass" | "fail",
                    "error": str | None,
                }
            ],
        }
    """
```

### 5. `promote_to_production`

Ship from develop to main: CI, Rhea gate, merge, deploy, verify.

```python
def promote_to_production(
    pr_number: int,           # PR against main
    skip_smoke: bool = False, # Skip post-deploy smoke test
) -> dict:
    """
    Returns:
        {
            "ci_status": str,
            "rhea_approved": bool,
            "merged": bool,
            "deploy_url": str,
            "smoke_test": dict | None,
        }
    """
```

Orchestration: cerebro-github `check_ci` -> `merge_pr` (triggers Rhea gate for main) -> railguey `railguey_deployments` (poll) -> optionally `smoke_test` on production.

### 6. `login`

Automated login with TOTP. Returns session info for reuse.

```python
def login(
    environment: str = "staging",
    role: str = "viewer",
) -> dict:
    """
    Returns:
        {
            "session_id": str,        # Browserbase session ID
            "context_id": str | None, # Persistent context ID if reused
            "logged_in": bool,
            "screenshot": str,        # Post-login screenshot path
        }
    """
```

### 7. `test_overlay`

Navigate to a preview page and verify the preview overlay behavior.

```python
def test_overlay(
    page_slug: str,              # Page slug from page-registry
    environment: str = "staging",
) -> dict:
    """
    Returns:
        {
            "overlay_present": bool,
            "overlay_vendor": str | None,
            "overlay_progress": str | None,
            "dismissed": bool,
            "content_visible_after_dismiss": bool,
            "screenshot_with_overlay": str,
            "screenshot_after_dismiss": str,
        }
    """
```

### 8. `deploy_status`

Check Railway deployment status for a given environment.

```python
def deploy_status(
    environment: str = "staging",
) -> dict:
    """
    Returns:
        {
            "service": str,
            "status": str,        # "deployed", "building", "failed", etc.
            "commit": str,        # SHA of deployed commit
            "deployed_at": str,   # ISO timestamp
            "url": str,           # Live URL
        }
    """
```

Delegates to railguey `railguey_deployments` with the appropriate account.

## Dependencies

```toml
[project]
name = "cerebro-web-builder"
version = "0.1.0"
description = "Web deployment pipeline MCP — encoded knowledge for Cerebro ship/verify/promote"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "pyotp>=2.9.0",         # TOTP generation (RFC 6238)
    "httpx>=0.27.0",        # Browserbase API calls
]
```

- `pyotp` -- standard TOTP library. Replaces hand-rolled HMAC. Generates 6-digit codes from base32 secrets with 30s period.
- `httpx` -- async HTTP client for Browserbase REST API (create session, connect, screenshots).
- `mcp` -- FastMCP framework, same as cerebro-builder.

No Playwright or Selenium. Browser automation runs through Browserbase's cloud API + the agent-browser CLI (`tools/agent-browser/ab`) for page interaction. Browserbase provides the remote browser; `ab` drives it.

## Integration with other MCPs

### cerebro-github (ship + merge ceremony)

- `create_work` -- create issue for the shipping PR
- `open_pr` -- open PR against develop or main
- `check_ci` -- poll CI status until terminal
- `merge_pr` -- merge PR (triggers Rhea gate when target is main)

### cerebro-builder (session context)

- `get_topology` -- cross-reference deploy topology
- `convene` / `adjourn` -- web-builder tools can be called within a builder session

### railguey (Railway deploys)

- `railguey_account_default` -- switch between `develop` and `production` accounts
- `railguey_deployments` -- check deploy status, poll for completion
- `railguey_logs` -- fetch deploy logs on failure

### cerebro-verifier (evidence)

- `take_evidence` -- store screenshots as verification evidence
- `verify_page` -- web-builder's verify_page can feed results into verifier fixtures

## Implementation notes

1. **Knowledge, not logic.** The value is in the encoded facts. Tool implementations are thin orchestration layers that compose knowledge with child MCP calls. Keep tool bodies under 50 lines.

2. **Browserbase sessions.** Each verification tool creates a Browserbase session, drives it via `ab`, and tears it down. Persistent contexts can skip re-login for the same role/environment pair.

3. **TOTP timing.** `pyotp.TOTP(secret).now()` handles the 30-second window. No need for custom HMAC code.

4. **Page registry parsing.** Read `lib/page-registry.ts` from the cerebro repo (local clone or GitHub API) and parse the exported object to get the list of pages, their slugs, live/preview status, and tool associations.

5. **Error model.** Every tool returns a dict. Failures include an `"error"` key with a human-readable message. No exceptions cross the MCP boundary.

6. **No secrets in code.** Browserbase API key and test account credentials live in `knowledge.py` as constants (they are test-only credentials, not production secrets). If this changes, move to env vars.
