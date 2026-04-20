#!/usr/bin/env bash
#
# test-railway-token.sh — Diagnose Railway API token issues
#
# Usage:
#   ./test-railway-token.sh <token>
#   ./test-railway-token.sh              # uses $RAILWAY_TOKEN from env
#
# Tests:
#   1. Is the token non-empty?
#   2. Can it query `me`? (account-scoped tokens only)
#   3. Can it list projects? (account-scoped tokens only)
#   4. Can it query variables for the Greenmark project? (project-scoped OK)
#   5. Can it upsert a test variable? (project-scoped OK)
#
# cerebro-vault needs: test 4 + 5 passing (read + write service vars)
# A project-scoped token should work for vault. An account token works for everything.

set -euo pipefail

TOKEN="${1:-${RAILWAY_TOKEN:-}}"
PROJECT_ID="${RAILWAY_PROJECT_ID:-3501a64c-d1e2-4e89-8450-b6542b5ac0b1}"
ENV_ID="${RAILWAY_ENVIRONMENT_ID:-}"
SERVICE_ID="${RAILWAY_SERVICE_ID:-}"
API="https://backboard.railway.com/graphql/v2"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}PASS${NC} $1"; }
fail() { echo -e "  ${RED}FAIL${NC} $1"; }
warn() { echo -e "  ${YELLOW}WARN${NC} $1"; }

gql() {
  # Project-scoped tokens use Project-Access-Token, account tokens use Bearer.
  # Try Project-Access-Token first (safer, recommended).
  /usr/bin/curl -s -X POST "$API" \
    -H "Content-Type: application/json" \
    -H "Project-Access-Token: $TOKEN" \
    -d "{\"query\":\"$1\"$([ -n "${2:-}" ] && echo ",\"variables\":$2" || echo "")}"
}

gql_bearer() {
  /usr/bin/curl -s -X POST "$API" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"query\":\"$1\"$([ -n "${2:-}" ] && echo ",\"variables\":$2" || echo "")}"
}

echo "── Railway Token Diagnostic ──────────────────────"
echo ""

# Test 0: Token exists
if [ -z "$TOKEN" ]; then
  fail "No token provided. Pass as arg or set RAILWAY_TOKEN."
  exit 1
fi
echo "  Token: ${TOKEN:0:8}...${TOKEN: -4} (${#TOKEN} chars)"
echo "  Project: $PROJECT_ID"
echo "  Env ID: ${ENV_ID:-(not set)}"
echo "  Service ID: ${SERVICE_ID:-(not set)}"
echo ""

# Test 1: Introspect token (project-scoped tokens)
echo "Test 1: Introspect token (Project-Access-Token header)"
RESULT=$(/usr/bin/curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "Project-Access-Token: $TOKEN" \
  -d '{"query":"{ projectToken { projectId environmentId } }"}')
PROJ_FROM_TOKEN=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['projectToken']['projectId'])" 2>/dev/null || echo "")
ENV_FROM_TOKEN=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['projectToken']['environmentId'])" 2>/dev/null || echo "")
if [ -n "$PROJ_FROM_TOKEN" ]; then
  pass "Project-scoped token — projectId=$PROJ_FROM_TOKEN envId=$ENV_FROM_TOKEN"
  SCOPE="project"
  # Use introspected values if not set
  [ -z "$ENV_ID" ] && ENV_ID="$ENV_FROM_TOKEN"
else
  # Fall back to Bearer (account-scoped)
  RESULT=$(gql '{ me { email } }')
  if echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['me']['email'])" 2>/dev/null; then
    pass "Account-scoped token (Bearer) — full access"
    SCOPE="account"
  else
    fail "Token not recognized as project-scoped or account-scoped"
    SCOPE="unknown"
  fi
fi
echo ""

# Test 2: List projects (account-scoped only)
echo "Test 2: List projects (account-scoped only)"
RESULT=$(gql '{ projects { edges { node { id name } } } }')
if echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f\"  {n['node']['name']}\") for n in d['data']['projects']['edges']]" 2>/dev/null; then
  pass "Can list projects"
else
  warn "Cannot list projects (expected for project-scoped tokens)"
fi
echo ""

# Test 3: Query project by ID
echo "Test 3: Query project by ID"
RESULT=$(gql "{ project(id: \\\"$PROJECT_ID\\\") { name } }")
PNAME=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['project']['name'])" 2>/dev/null || echo "")
if [ -n "$PNAME" ]; then
  pass "Project: $PNAME"
else
  fail "Cannot query project $PROJECT_ID"
  echo "  Raw: $(echo "$RESULT" | head -c 200)"
fi
echo ""

# Test 4: Read service variables (what vault needs)
echo "Test 4: Read service variables (vault read)"
if [ -z "$ENV_ID" ] || [ -z "$SERVICE_ID" ]; then
  warn "RAILWAY_ENVIRONMENT_ID or RAILWAY_SERVICE_ID not set — skipping"
else
  QUERY="query(\$p: String!, \$e: String!, \$s: String!) { variables(projectId: \$p, environmentId: \$e, serviceId: \$s) }"
  VARS="{\"p\":\"$PROJECT_ID\",\"e\":\"$ENV_ID\",\"s\":\"$SERVICE_ID\"}"
  RESULT=$(gql "$QUERY" "$VARS")
  if echo "$RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
v=d['data']['variables']
secrets=[k for k in v if k.startswith('SECRET_')]
print(f'  {len(v)} vars total, {len(secrets)} secrets (SECRET_* prefix)')
" 2>/dev/null; then
    pass "Can read service variables"
  else
    fail "Cannot read service variables"
    echo "  Raw: $(echo "$RESULT" | head -c 300)"
  fi
fi
echo ""

# Test 5: Upsert test variable (vault write)
echo "Test 5: Upsert test variable (vault write)"
if [ -z "$ENV_ID" ] || [ -z "$SERVICE_ID" ]; then
  warn "RAILWAY_ENVIRONMENT_ID or RAILWAY_SERVICE_ID not set — skipping"
else
  QUERY="mutation(\$p: String!, \$e: String!, \$s: String!, \$n: String!, \$v: String!) { variableUpsert(input: { projectId: \$p, environmentId: \$e, serviceId: \$s, name: \$n, value: \$v }) }"
  VARS="{\"p\":\"$PROJECT_ID\",\"e\":\"$ENV_ID\",\"s\":\"$SERVICE_ID\",\"n\":\"SECRET_TEST_PING\",\"v\":\"$(date -Iseconds)\"}"
  RESULT=$(gql "$QUERY" "$VARS")
  if echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['data']['variableUpsert'] is True" 2>/dev/null; then
    pass "Can write service variables"
  else
    fail "Cannot write service variables"
    echo "  Raw: $(echo "$RESULT" | head -c 300)"
  fi
fi
echo ""

# Summary
echo "── Summary ─────────────────────────────────────────"
if [ "$SCOPE" = "account" ]; then
  pass "Account-scoped token — works for everything"
elif [ "$SCOPE" = "project" ]; then
  echo "  Project-scoped token. Tests 4+5 must pass for vault to work."
  echo "  If they failed, the token may not have variable read/write permissions."
else
  fail "Token does not appear to be valid"
fi
echo ""
echo "  To use this token with cerebro-vault:"
echo "    export RAILWAY_TOKEN=$TOKEN"
echo "  Or update .mcp.json to inject it."
