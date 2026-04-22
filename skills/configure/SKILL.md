---
name: configure
description: Set up the Slack channel — save the bot and app tokens. Use when the user pastes Slack tokens, asks to configure Slack, or wants to check channel status.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Bash(ls *)
  - Bash(mkdir *)
---

# /slack-cc:configure

Configure the Slack channel with your bot token and app-level token.

## Usage

```
/slack-cc:configure <xoxb-bot-token> <xapp-app-token>
```

## Instructions

1. Parse the two arguments from `$ARGUMENTS`:
   - First token must start with `xoxb-` (Bot User OAuth Token)
   - Second token must start with `xapp-` (App-Level Token)

2. If either token is missing or has the wrong prefix, show this error and stop:
   ```
   Error: Two tokens required.
     - Bot token (starts with xoxb-) from OAuth & Permissions
     - App token (starts with xapp-) from Socket Mode settings

   Usage: /slack-cc:configure xoxb-... xapp-...
   ```

3. Create the state directory if it doesn't exist:
   ```
   ~/.claude/channels/slack/
   ```

4. Write the `.env` file at `~/.claude/channels/slack/.env`:
   ```
   SLACK_BOT_TOKEN=<bot-token>
   SLACK_APP_TOKEN=<app-token>
   ```

5. Set file permissions to owner-only:
   ```bash
   chmod 600 ~/.claude/channels/slack/.env
   ```

6. Confirm success:
   ```
   Slack channel configured.

   Start Claude with the Slack channel:
     claude --plugin-dir ~/repos/slack-cc --dangerously-load-development-channels server:slack
   ```

## Security

- Never echo the tokens back in the confirmation message
- Never log tokens to stdout or any file other than `.env`
- Always set 0o600 permissions on the `.env` file
