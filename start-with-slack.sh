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
  --plugin-dir ~/repos/cc-channel-slack-eidos \
  --dangerously-load-development-channels server:slack \
  --allowedTools "mcp__slack__reply,mcp__slack__react,mcp__slack__edit_message,mcp__slack__fetch_messages" \
  "$@"
