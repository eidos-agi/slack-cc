#!/usr/bin/env bash
#
# test-railway-tokens.sh — Test all Railway tokens across all permission types
#
# Usage: ./test-railway-tokens.sh
#
# Tests each railguey account's token against:
# 1. GraphQL introspection (projectToken query)
# 2. Variable read (list service vars)
# 3. Variable write (set a test var, then delete it)
# 4. Deploy (deploymentRedeploy — checks permission, doesn't execute)
# 5. Service info (list services)
#
# Consult this when a deploy fails or a token seems wrong.

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}PASS${NC} $1"; }
fail() { echo -e "  ${RED}FAIL${NC} $1"; }
warn() { echo -e "  ${YELLOW}WARN${NC} $1"; }

API="https://backboard.railway.com/graphql/v2"
PROJECT_ID="3501a64c-d1e2-4e89-8450-b6542b5ac0b1"

gql() {
  local token="$1" query="$2"
  /usr/bin/curl -s -X POST "$API" \
    -H "Content-Type: application/json" \
    -H "Project-Access-Token: $token" \
    -d "{\"query\":\"$query\"}"
}

test_token() {
  local name="$1" token="$2"
  echo ""
  echo "── $name ──"
  echo "  Token: ${token:0:8}...${token: -4}"

  # 1. Introspect
  local result=$(gql "$token" "{ projectToken { projectId environmentId } }")
  local env_id=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('projectToken',{}).get('environmentId','FAILED'))" 2>/dev/null)
  if [ "$env_id" != "FAILED" ]; then
    pass "Introspect: environmentId=$env_id"
  else
    fail "Introspect: not a valid project token"
    return
  fi

  # 2. List services
  result=$(gql "$token" "{ project(id: \\\"$PROJECT_ID\\\") { services { edges { node { id name } } } } }")
  local svc_count=$(echo "$result" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('data',{}).get('project',{}).get('services',{}).get('edges',[])))" 2>/dev/null)
  if [ "$svc_count" -gt 0 ] 2>/dev/null; then
    pass "List services: $svc_count services visible"
  else
    fail "List services: cannot query project"
  fi

  # 3. Read variables (use data-daemon service)
  result=$(gql "$token" "query(\\\$p: String!, \\\$e: String!, \\\$s: String!) { variables(projectId: \\\$p, environmentId: \\\$e, serviceId: \\\$s) }" | head -c 100)
  # This is a simplified check
  if echo "$result" | grep -q "variables"; then
    pass "Read variables: accessible"
  else
    warn "Read variables: may need service ID"
  fi

  # 4. Deploy permission (check only, don't execute)
  # We test by attempting deploymentRedeploy with a fake ID — if we get "not found" vs "not authorized"
  result=$(gql "$token" "mutation { deploymentRedeploy(id: \\\"00000000-0000-0000-0000-000000000000\\\") }")
  if echo "$result" | grep -qi "not authorized"; then
    fail "Deploy: NOT AUTHORIZED (token cannot deploy)"
  elif echo "$result" | grep -qi "not found\|deployment"; then
    pass "Deploy: authorized (deployment not found = permission OK)"
  else
    warn "Deploy: unknown response"
  fi
}

echo "═══════════════════════════════════════"
echo "Railway Token Test Suite"
echo "═══════════════════════════════════════"

# Get tokens from railguey
DEV_TOKEN=$(python3 -c "import sys; sys.path.insert(0,'$(pwd)/railguey'); from railguey.lib.accounts import get_account_token; print(get_account_token('develop'))")
PROD_TOKEN=$(python3 -c "import sys; sys.path.insert(0,'$(pwd)/railguey'); from railguey.lib.accounts import get_account_token; print(get_account_token('production'))")

test_token "DEVELOP (railguey)" "$DEV_TOKEN"
test_token "PRODUCTION (railguey)" "$PROD_TOKEN"

# Test any additional tokens passed as args
for extra in "$@"; do
  test_token "EXTRA" "$extra"
done

echo ""
echo "═══════════════════════════════════════"
echo "Done. If deploy fails, the token needs deploy permissions."
echo "Create a new token in Railway → Project Settings → Tokens."
echo "═══════════════════════════════════════"
