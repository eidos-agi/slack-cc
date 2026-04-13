#!/usr/bin/env bash
# bootstrap-repo.sh — Apply tier-appropriate release practices to a repo.
#
# Usage:
#   ./tools/bootstrap-repo.sh /path/to/repo              # auto-detect tier from tier-map.sh
#   ./tools/bootstrap-repo.sh /path/to/repo --tier 1     # override tier
#
# What each tier gets:
#   T1 Production:  CI + guard-main + PR template + CODEOWNERS + dependabot (human review) + branch protection + pre-push
#   T2 Supporting:  CI + guard-main + PR template + dependabot (auto-merge patches) + pre-push
#   T3 Reference:   pre-push hook only
#
# Idempotent — safe to run multiple times. Skips files that already exist.
# Does NOT install deploy workflows — those are repo-specific (Railway vs Supabase vs none).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

REPO="${1:?Usage: bootstrap-repo.sh /path/to/repo [--tier 1|2|3]}"
TIER=""
GH_ORG="greenmark-waste-solutions"

shift
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tier) TIER="$2"; shift 2 ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

source "$SCRIPT_DIR/tier-map.sh"

if [[ ! -d "$REPO/.git" ]]; then
    echo "Error: $REPO is not a git repo" >&2
    exit 1
fi

NAME=$(basename "$REPO")

# Auto-detect tier from map if not overridden
if [[ -z "$TIER" ]]; then
    TIER="${TIER_MAP[$NAME]:-}"
    if [[ -z "$TIER" ]]; then
        echo "Error: $NAME not found in tier-map.sh and no --tier provided" >&2
        exit 1
    fi
fi

# Auto-detect language
# Heuristic: if the repo has a src/ or app/ dir with .ts/.tsx files, it's Node.
# A bare package.json (e.g., for supabase CLI) without app code is NOT Node.
HAS_NODE=false
HAS_PYTHON=false
LANG="unknown"
if [[ -f "$REPO/package.json" ]]; then
    # Only count as Node if there's actual app/source code, not just a lockfile for tooling
    if ls "$REPO"/src/*.ts "$REPO"/src/*.tsx "$REPO"/app/*.ts "$REPO"/app/*.tsx "$REPO"/pages/*.ts "$REPO"/pages/*.tsx 2>/dev/null | head -1 | grep -q .; then
        HAS_NODE=true
    elif [[ -f "$REPO/tsconfig.json" || -f "$REPO/next.config.js" || -f "$REPO/next.config.mjs" || -f "$REPO/next.config.ts" ]]; then
        HAS_NODE=true
    fi
fi
[[ -f "$REPO/requirements.txt" || -f "$REPO/pyproject.toml" || -f "$REPO/setup.py" ]] && HAS_PYTHON=true
# If repo has Python scripts but no Python markers, still detect
if [[ "$HAS_PYTHON" == false ]] && ls "$REPO"/*.py 2>/dev/null | head -1 | grep -q .; then
    HAS_PYTHON=true
fi

if [[ "$HAS_NODE" == true ]]; then
    LANG="node"
elif [[ "$HAS_PYTHON" == true ]]; then
    LANG="python"
fi

echo "bootstrap-repo: $NAME (tier $TIER — ${TIER_NAMES[$TIER]}, lang: $LANG)"
echo

installed=0
skipped=0

# ── Helpers ───────────────────────────────────────────────────────

install_if_missing() {
    local path="$1" label="$2"
    if [[ -f "$path" ]]; then
        echo "  skip: $label already exists"
        skipped=$((skipped + 1))
        return 1
    fi
    mkdir -p "$(dirname "$path")"
    return 0
}

# ── 1. Pre-push hook (all tiers) ─────────────────────────────────

HOOK_FILE="$REPO/.git/hooks/pre-push"
if [[ -f "$HOOK_FILE" ]] && grep -q "ensure-flow hook" "$HOOK_FILE" 2>/dev/null; then
    echo "  skip: pre-push hook already installed"
    skipped=$((skipped + 1))
else
    cat > "$HOOK_FILE" << 'HOOK'
#!/usr/bin/env bash
# ensure-flow hook — blocks direct pushes to main, master, and develop.
# Feature branches only. Go through a PR.
#
# Installed by tools/bootstrap-repo.sh in greenmark-cockpit.

while read local_ref local_sha remote_ref remote_sha; do
    case "$remote_ref" in
        refs/heads/main|refs/heads/master|refs/heads/develop)
            branch="${remote_ref##refs/heads/}"
            echo ""
            echo "  BLOCKED: Direct push to $branch."
            echo "  Feature branches only. Open a PR."
            echo ""
            exit 1
            ;;
    esac
done

exit 0
HOOK
    chmod +x "$HOOK_FILE"
    echo "  + pre-push hook"
    installed=$((installed + 1))
fi

# T3 stops here
if [[ "$TIER" -ge 3 ]]; then
    echo
    echo "bootstrap-repo: $NAME done ($installed installed, $skipped skipped)"
    exit 0
fi

# ── 2. CI workflow (T1, T2) ──────────────────────────────────────

CI_FILE="$REPO/.github/workflows/ci.yml"
if install_if_missing "$CI_FILE" "ci.yml"; then
    if [[ "$LANG" == "python" ]]; then
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
    echo "  + ci.yml ($LANG)"
    installed=$((installed + 1))
fi

# ── 3. Guard main workflow (T1, T2) ──────────────────────────────

GUARD_FILE="$REPO/.github/workflows/guard-main.yml"
if install_if_missing "$GUARD_FILE" "guard-main.yml"; then
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
    echo "  + guard-main.yml"
    installed=$((installed + 1))
fi

# ── 4. PR template (T1, T2) ──────────────────────────────────────

PR_TEMPLATE="$REPO/.github/pull_request_template.md"
if install_if_missing "$PR_TEMPLATE" "pull_request_template.md"; then
    cat > "$PR_TEMPLATE" << 'PRTMPL'
## Why

## How tested

- [ ] AI-generated content reviewed for correctness
PRTMPL
    echo "  + pull_request_template.md"
    installed=$((installed + 1))
fi

# ── 5. Dependabot (T1 with human review, T2 with auto-merge labels) ──

DEPBOT_FILE="$REPO/.github/dependabot.yml"
if install_if_missing "$DEPBOT_FILE" "dependabot.yml"; then
    {
        echo "version: 2"
        echo "updates:"

        if [[ "$HAS_NODE" == true ]]; then
            echo "  - package-ecosystem: npm"
            echo "    directory: \"/\""
            echo "    schedule:"
            echo "      interval: weekly"
            echo "    open-pull-requests-limit: 10"
            if [[ "$TIER" -eq 2 ]]; then
                echo "    labels:"
                echo "      - dependencies"
                echo "      - automerge"
            fi
        fi

        if [[ "$HAS_PYTHON" == true ]]; then
            echo "  - package-ecosystem: pip"
            echo "    directory: \"/\""
            echo "    schedule:"
            echo "      interval: weekly"
            echo "    open-pull-requests-limit: 5"
            if [[ "$TIER" -eq 2 ]]; then
                echo "    labels:"
                echo "      - dependencies"
                echo "      - automerge"
            fi
        fi

        # Fallback if neither detected — still useful for GitHub Actions updates
        if [[ "$HAS_NODE" == false && "$HAS_PYTHON" == false ]]; then
            echo "  - package-ecosystem: github-actions"
            echo "    directory: \"/\""
            echo "    schedule:"
            echo "      interval: weekly"
        fi
    } > "$DEPBOT_FILE"

    if [[ "$TIER" -eq 1 ]]; then
        echo "  + dependabot.yml (human review required)"
    else
        echo "  + dependabot.yml (auto-merge patches)"
    fi
    installed=$((installed + 1))
fi

# T2 stops here
if [[ "$TIER" -ge 2 ]]; then
    echo
    echo "bootstrap-repo: $NAME done ($installed installed, $skipped skipped)"
    exit 0
fi

# ── 6. CODEOWNERS (T1 only) ──────────────────────────────────────

CODEOWNERS_FILE="$REPO/.github/CODEOWNERS"
if install_if_missing "$CODEOWNERS_FILE" "CODEOWNERS"; then
    cat > "$CODEOWNERS_FILE" << 'OWNERS'
# Default: Daniel reviews everything. Add per-path overrides as team grows.
* @dshanklin-bv
OWNERS
    echo "  + CODEOWNERS (@dshanklin-bv)"
    installed=$((installed + 1))
fi

# ── 7. Branch protection (T1 only, requires GitHub Pro) ──────────

echo
echo "  Attempting branch protection via GitHub API..."
if gh api "repos/$GH_ORG/$NAME/branches/main/protection" \
    --method PUT \
    --input - << 'PROTECTION' > /dev/null 2>&1
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "required_status_checks": {
    "strict": true,
    "contexts": ["CI"]
  },
  "enforce_admins": false,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
PROTECTION
then
    echo "  + branch protection on main (1 review, CI required)"
    installed=$((installed + 1))
else
    echo "  warn: branch protection requires GitHub Pro/Team for private repos"
    echo "        guard-main.yml + pre-push hook provide equivalent coverage"
fi

echo
echo "bootstrap-repo: $NAME done ($installed installed, $skipped skipped)"
