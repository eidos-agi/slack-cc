#!/usr/bin/env bash
#
# pre-bash-railway-guard — Block direct Railway CLI usage, redirect to railguey
#
# Prevents: railway up, railway deploy, railway whoami, npx @railway/cli, etc.
# Suggests: railguey MCP tools instead

COMMAND="$CLAUDE_BASH_COMMAND"

if echo "$COMMAND" | grep -qiE '(^|\s|/)(railway|npx.*@railway)(\s|$)'; then
  echo "BLOCKED: Do not use the Railway CLI directly." >&2
  echo "" >&2
  echo "Use railguey MCP tools instead:" >&2
  echo "  railguey_deploy     — deploy a service" >&2
  echo "  railguey_redeploy   — rebuild from source" >&2
  echo "  railguey_restart    — restart without rebuild" >&2
  echo "  railguey_variables  — list env vars" >&2
  echo "  railguey_variable_set — set an env var" >&2
  echo "  railguey_service_info — check deploy status" >&2
  echo "  railguey_doctor     — full workspace audit" >&2
  echo "" >&2
  echo "For GitHub Actions deploys:" >&2
  echo "  gh workflow run deploy.yml --repo <repo> --ref <branch>" >&2
  exit 2
fi
