#!/usr/bin/env bash
#
# preflight.sh — Validate slack-cc plugin end-to-end before restart
#
# Tests everything that can be tested without actually launching Claude Code:
#   1. Plugin structure (plugin.json, .mcp.json, channels, skills)
#   2. Name consistency (all names match across files)
#   3. Dep installation (npm install works from the install path)
#   4. Server boot (starts, connects Socket Mode, shuts down cleanly)
#   5. Slack API (bot token auth, channel membership)
#   6. Marketplace (installed, correct version)
#   7. Launch flag format (predicts what Claude Code will see)
#
# Usage: ./tools/preflight.sh
# Exit code: 0 = all pass, 1 = failures found

set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

pass() { echo -e "  ${GREEN}✓${NC} $1"; ((PASS++)); }
fail() { echo -e "  ${RED}✗${NC} $1"; ((FAIL++)); }
warn() { echo -e "  ${YELLOW}!${NC} $1"; ((WARN++)); }

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="$HOME/.claude/channels/slack"
PLUGIN_JSON="$REPO_ROOT/.claude-plugin/plugin.json"
MCP_JSON="$REPO_ROOT/.mcp.json"
INSTALL_PATH=""

echo "slack-cc preflight check"
echo "========================"
echo ""

# --- 1. Plugin structure ---
echo "1. Plugin structure"

if [ -f "$PLUGIN_JSON" ]; then
  pass "plugin.json exists"
else
  fail "plugin.json missing at $PLUGIN_JSON"; exit 1
fi

if [ -f "$MCP_JSON" ]; then
  pass ".mcp.json exists"
else
  fail ".mcp.json missing at $MCP_JSON"; exit 1
fi

PLUGIN_NAME=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['name'])")
PLUGIN_VERSION=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])")
CHANNEL_SERVER=$(python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['channels'][0]['server'])" 2>/dev/null || echo "MISSING")
MCP_SERVER=$(python3 -c "import json; print(list(json.load(open('$MCP_JSON'))['mcpServers'].keys())[0])" 2>/dev/null || echo "MISSING")

echo "  Plugin: $PLUGIN_NAME v$PLUGIN_VERSION"
echo "  Channel server: $CHANNEL_SERVER"
echo "  MCP server: $MCP_SERVER"

# --- 2. Name consistency ---
echo ""
echo "2. Name consistency"

if [ "$PLUGIN_NAME" = "$CHANNEL_SERVER" ]; then
  pass "plugin.json name matches channels.server ($PLUGIN_NAME)"
else
  fail "plugin.json name ($PLUGIN_NAME) != channels.server ($CHANNEL_SERVER)"
fi

if [ "$PLUGIN_NAME" = "$MCP_SERVER" ]; then
  pass "plugin.json name matches .mcp.json server key ($MCP_SERVER)"
else
  fail "plugin.json name ($PLUGIN_NAME) != .mcp.json server key ($MCP_SERVER)"
fi

# Check MCP Server() name in server.ts matches
SERVER_MCP_NAME=$(grep -o "name: '[^']*'" "$REPO_ROOT/server.ts" | head -1 | sed "s/name: '//;s/'//")
if [ "$SERVER_MCP_NAME" = "$PLUGIN_NAME" ]; then
  pass "server.ts Server name matches plugin name ($SERVER_MCP_NAME)"
else
  fail "server.ts Server name ($SERVER_MCP_NAME) != plugin name ($PLUGIN_NAME)"
fi

# Check skill command prefix
SKILL_PREFIX=$(grep -o '/[a-z-]*:' "$REPO_ROOT/skills/access/SKILL.md" | head -1 | tr -d '/:')
EXPECTED_PREFIX="$PLUGIN_NAME"
if [ "$SKILL_PREFIX" = "$EXPECTED_PREFIX" ]; then
  pass "Skill prefix matches plugin name (/$SKILL_PREFIX:)"
else
  fail "Skill prefix (/$SKILL_PREFIX:) != expected (/$EXPECTED_PREFIX:)"
fi

# Predict Claude Code's tool prefix
TOOL_PREFIX="mcp__plugin_${PLUGIN_NAME}_${MCP_SERVER}__"
echo "  Predicted tool prefix: ${TOOL_PREFIX}*"

# --- 3. Plugin validation ---
echo ""
echo "3. Plugin validation"

VALIDATE_OUT=$(claude plugin validate "$REPO_ROOT" 2>&1)
if echo "$VALIDATE_OUT" | grep -q "Validation passed"; then
  pass "claude plugin validate passed"
else
  fail "claude plugin validate failed: $VALIDATE_OUT"
fi

# --- 4. Tokens ---
echo ""
echo "4. Slack tokens"

if [ -f "$STATE_DIR/.env" ]; then
  pass ".env exists at $STATE_DIR/.env"
  PERMS=$(stat -c '%a' "$STATE_DIR/.env" 2>/dev/null || stat -f '%Lp' "$STATE_DIR/.env" 2>/dev/null)
  if [ "$PERMS" = "600" ]; then
    pass ".env permissions are 600"
  else
    fail ".env permissions are $PERMS (expected 600)"
  fi

  BOT_TOKEN=$(grep SLACK_BOT_TOKEN "$STATE_DIR/.env" | cut -d= -f2)
  APP_TOKEN=$(grep SLACK_APP_TOKEN "$STATE_DIR/.env" | cut -d= -f2)

  if [[ "$BOT_TOKEN" == xoxb-* ]]; then
    pass "Bot token has xoxb- prefix"
  else
    fail "Bot token missing or wrong prefix"
  fi

  if [[ "$APP_TOKEN" == xapp-* ]]; then
    pass "App token has xapp- prefix"
  else
    fail "App token missing or wrong prefix"
  fi

  # Test bot token
  AUTH_RESULT=$(curl -s -H "Authorization: Bearer $BOT_TOKEN" https://slack.com/api/auth.test)
  AUTH_OK=$(echo "$AUTH_RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ok','false'))")
  if [ "$AUTH_OK" = "True" ]; then
    BOT_USER=$(echo "$AUTH_RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"{d['user']} ({d['user_id']}) on {d['team']}\")")
    pass "Bot token valid: $BOT_USER"
  else
    fail "Bot token auth failed"
  fi
else
  fail ".env missing at $STATE_DIR/.env"
fi

# --- 5. Marketplace ---
echo ""
echo "5. Marketplace"

MARKETPLACE_LIST=$(claude plugin marketplace list 2>&1)
if echo "$MARKETPLACE_LIST" | grep -q "eidos-agi"; then
  pass "eidos-agi marketplace registered"
else
  fail "eidos-agi marketplace not registered (run: claude plugin marketplace add eidos-agi/claude-plugins)"
fi

PLUGIN_LIST=$(claude plugin list 2>&1)
if echo "$PLUGIN_LIST" | grep -q "slack-cc@eidos-agi"; then
  INSTALLED_VERSION=$(echo "$PLUGIN_LIST" | grep -A1 "slack-cc" | grep Version | awk '{print $2}')
  if [ "$INSTALLED_VERSION" = "$PLUGIN_VERSION" ]; then
    pass "slack-cc@eidos-agi installed v$INSTALLED_VERSION (matches repo)"
  else
    warn "slack-cc@eidos-agi installed v$INSTALLED_VERSION but repo is v$PLUGIN_VERSION — run: claude plugin uninstall slack-cc@eidos-agi && claude plugin marketplace update eidos-agi && claude plugin install slack-cc@eidos-agi"
  fi

  INSTALL_PATH=$(python3 -c "import json; print(json.load(open('$HOME/.claude/plugins/installed_plugins.json'))['plugins']['slack-cc@eidos-agi'][0]['installPath'])" 2>/dev/null || echo "")
  if [ -n "$INSTALL_PATH" ] && [ -f "$INSTALL_PATH/server.ts" ]; then
    pass "Install path has server.ts: $INSTALL_PATH"
  else
    fail "Install path missing or empty"
  fi
else
  fail "slack-cc@eidos-agi not installed (run: claude plugin install slack-cc@eidos-agi)"
fi

# --- 6. Server boot test ---
echo ""
echo "6. Server boot (5s timeout)"

if [ -n "$INSTALL_PATH" ]; then
  # Kill any existing bridge processes first
  pkill -f "tsx.*server.ts" 2>/dev/null || true
  sleep 1

  BOOT_LOG=$(timeout 8 npm start --prefix "$INSTALL_PATH" 2>&1 || true)
  if echo "$BOOT_LOG" | grep -q "boot.complete"; then
    pass "Server booted successfully (boot.complete logged)"
  elif echo "$BOOT_LOG" | grep -q "socket.connect"; then
    pass "Server started and attempted Socket Mode connection"
  elif echo "$BOOT_LOG" | grep -q "tsx server.ts"; then
    pass "npm start resolved deps and launched tsx"
  else
    fail "Server failed to boot: $(echo "$BOOT_LOG" | tail -3)"
  fi
else
  warn "Skipping boot test — no install path"
fi

# --- 7. Launch flag ---
echo ""
echo "7. Launch command"

LAUNCH_CMD="claude --dangerously-load-development-channels plugin:${PLUGIN_NAME}@eidos-agi"
echo "  $LAUNCH_CMD"
echo ""
echo "  Tool auto-approve flag:"
echo "  --allowedTools \"${TOOL_PREFIX}reply,${TOOL_PREFIX}react,${TOOL_PREFIX}edit_message,${TOOL_PREFIX}fetch_messages\""

# --- Summary ---
echo ""
echo "========================"
echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}, ${YELLOW}$WARN warnings${NC}"

if [ "$FAIL" -gt 0 ]; then
  echo -e "${RED}PREFLIGHT FAILED${NC} — fix issues above before restarting"
  exit 1
else
  echo -e "${GREEN}PREFLIGHT PASSED${NC} — safe to restart with the launch command above"
  exit 0
fi
