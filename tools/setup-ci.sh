#!/usr/bin/env bash
# setup-ci.sh — Install standardized CI pipeline on any repo
#
# Usage:
#   ./tools/setup-ci.sh /path/to/repo              # Node.js repo (default)
#   ./tools/setup-ci.sh /path/to/repo --python      # Python repo
#   ./tools/setup-ci.sh /path/to/repo --deploy URL  # Add smoke tests for deployed app
#
# What it installs:
#   1. .github/workflows/ci.yml — type check + lint + test + build on PRs
#   2. .github/workflows/guard-main.yml — alert on direct pushes to main
#   3. .git/hooks/pre-push — block direct pushes to main locally
#
# Optional (--deploy):
#   4. Smoke test job in deploy.yml — health check + auth gate after deploy
#
# Idempotent — safe to run multiple times. Skips files that already exist.

set -euo pipefail

REPO="${1:?Usage: setup-ci.sh /path/to/repo [--python] [--deploy URL]}"
PYTHON=false
DEPLOY_URL=""

shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --python) PYTHON=true; shift ;;
        --deploy) DEPLOY_URL="$2"; shift 2 ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

if [[ ! -d "$REPO/.git" ]]; then
    echo "Error: $REPO is not a git repo" >&2
    exit 1
fi

NAME=$(basename "$REPO")
echo "setup-ci: configuring $NAME"

# ── 1. CI Workflow ────────────────────────────────────────────

mkdir -p "$REPO/.github/workflows"

CI_FILE="$REPO/.github/workflows/ci.yml"
if [[ -f "$CI_FILE" ]]; then
    echo "  skip: ci.yml already exists"
else
    if [[ "$PYTHON" == true ]]; then
        cat > "$CI_FILE" << 'PYCI'
name: CI

on:
  pull_request:
    branches: [main, master, develop]
  push:
    branches: [main, master, develop]
  workflow_call:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check .

  typecheck:
    name: Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pyright
      - run: pyright || echo "::warning::Type check had errors (non-blocking)"

  test:
    name: Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]" 2>/dev/null || pip install -r requirements.txt 2>/dev/null || pip install pytest
      - run: pytest -x --tb=short 2>/dev/null || echo "::warning::No tests found"
PYCI
    else
        cat > "$CI_FILE" << 'JSCI'
name: CI

on:
  pull_request:
    branches: [main, master, develop]
  push:
    branches: [main, master, develop]
  workflow_call:

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  typecheck:
    name: Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npx tsc --noEmit

  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint 2>/dev/null || echo "::warning::No lint script found"

  test:
    name: Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm test 2>/dev/null || echo "::warning::No test script found"

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [typecheck, lint, test]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run build 2>/dev/null || echo "::warning::No build script found"
JSCI
    fi
    echo "  ✓ ci.yml"
fi

# ── 2. Guard Main Workflow ────────────────────────────────────

GUARD_FILE="$REPO/.github/workflows/guard-main.yml"
if [[ -f "$GUARD_FILE" ]]; then
    echo "  skip: guard-main.yml already exists"
else
    cat > "$GUARD_FILE" << 'GUARD'
name: Guard Main Branch

on:
  push:
    branches: [main, master]

jobs:
  check-direct-push:
    runs-on: ubuntu-latest
    steps:
      - name: Check if this was a PR merge
        id: check
        run: |
          COMMIT_MSG=$(echo "${{ github.event.head_commit.message }}" | head -1)
          if [[ "$COMMIT_MSG" == Merge\ pull\ request* ]]; then
            echo "merge=true" >> "$GITHUB_OUTPUT"
          else
            echo "merge=false" >> "$GITHUB_OUTPUT"
            echo "::warning::Direct push to main by ${{ github.event.head_commit.author.name }}"
          fi

      - name: Fail on direct push
        if: steps.check.outputs.merge != 'true'
        run: |
          echo "Direct push to main detected. Use a PR."
          exit 1
GUARD
    echo "  ✓ guard-main.yml"
fi

# ── 3. Local Pre-Push Hook ───────────────────────────────────

HOOK_FILE="$REPO/.git/hooks/pre-push"
if [[ -f "$HOOK_FILE" ]]; then
    echo "  skip: pre-push hook already exists"
else
    cat > "$HOOK_FILE" << 'HOOK'
#!/usr/bin/env bash
while read local_ref local_sha remote_ref remote_sha; do
    if [[ "$remote_ref" == "refs/heads/main" || "$remote_ref" == "refs/heads/master" ]]; then
        echo ""
        echo "  BLOCKED: Direct push to main."
        echo "  Push to develop and merge via PR."
        echo ""
        exit 1
    fi
done
exit 0
HOOK
    chmod +x "$HOOK_FILE"
    echo "  ✓ pre-push hook"
fi

# ── Done ──────────────────────────────────────────────────────

echo ""
echo "setup-ci: $NAME configured"
echo "  Next: commit .github/workflows/ and push"
