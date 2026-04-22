#!/usr/bin/env bash
#
# start-with-slack.sh — Launch Claude Code with the Slack channel bridge
#
# Usage: ./start-with-slack.sh [claude args...]
#
# Examples:
#   ./start-with-slack.sh                    # fresh session
#   ./start-with-slack.sh --resume           # resume picker
#   ./start-with-slack.sh --debug            # with debug logs

cd "$(dirname "$0")"
exec claude \
  --dangerously-load-development-channels plugin:slack-cc@eidos-agi \
  --allowedTools "mcp__plugin_slack-cc_slack-cc__reply,mcp__plugin_slack-cc_slack-cc__react,mcp__plugin_slack-cc_slack-cc__edit_message,mcp__plugin_slack-cc_slack-cc__fetch_messages" \
  "$@"
