# Approval-flow redesign — Block Kit + interactive components

**Status:** Design proposal (not yet implemented)
**Date:** 2026-04-28
**Audience:** slack-cc maintainers, future implementers
**Triggered by:** Daniel's feedback that the current approval flow is poor and that production Slack apps (Linear, GitHub, Datadog, Sentry, PagerDuty, Vercel) handle this much better.

## Problem — what's poor about the current flow

Today (`server.ts:377–395`), a permission request looks like:

```
:closed_lock_with_key: *Permission request* `pqqew`
*Tool:* Bash
*Action:* Create issue via REST

Reply `yes pqqew` or `no pqqew`
```

Plain text. Cookie-token reply. No buttons. No context beyond a tool name and a verb. Reply parsing is a regex (`PERMISSION_RE` at `lib.ts:178`: `^\s*(y|yes|n|no)\s+([a-z0-9]{5})\s*$`).

What's wrong:

1. **Token-typing on a phone is tedious and error-prone.** `yes pqqew` has to be typed exactly, including the cookie. Auto-correct breaks it. One typo = ignored.
2. **No context.** "Bash: Create issue via REST" doesn't tell you what command, against what repo, with what blast radius.
3. **No in-place resolution.** After replying, the original message stays unchanged in the channel — no audit trail visible at a glance.
4. **No nuance.** Approve or deny only. Can't say "approve but skip step X" or "deny because Y" without dropping a separate text reply with no correlation.
5. **Existing `interactive` handler is a TODO stub** (`server.ts:453–456`). Manifest disables interactivity (`cerebro-development-slack/manifest.json:38`). Block Kit type definitions exist via the npm SDK but are unused.

The current flow is the first thing that worked. It was never the design. Six months of usage has surfaced what production Slack apps figured out years ago.

## UX principles — what production apps do

From a study of GitHub, PagerDuty, Datadog, Sentry, Linear, and Vercel Slack integrations:

1. **Context-rich card, not a token.** Title, who/what/why, snapshot or excerpt, deep-link back to the resource — never an opaque ID.
2. **Buttons are the verbs, not text replies.** Primary actions are Block Kit buttons; destructive ones get a confirm dialog or modal.
3. **Mutate the original message.** Post-action, the card re-renders with actor + timestamp ("Approved by Daniel · 9:42am"). Audit trail lives where the request did.
4. **Modals capture nuance.** Reasons, durations, assignees, conditional approvals — open a modal rather than parse free-text replies.
5. **Thread = audit log.** Subsequent state changes, related events, and bot follow-ups append to the same thread, keeping one canonical surface per decision.

## Proposed message structure

### The approval card (Block Kit)

```json
{
  "blocks": [
    {
      "type": "header",
      "text": {"type": "plain_text", "text": "Permission request"}
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Tool*\nBash"},
        {"type": "mrkdwn", "text": "*Action*\nCreate issue via REST"},
        {"type": "mrkdwn", "text": "*Repo*\ndata-daemon-v4"},
        {"type": "mrkdwn", "text": "*Branch*\nmain"}
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "```gh issue create --title 'pagination' --body '...'```"
      }
    },
    {
      "type": "context",
      "elements": [
        {"type": "mrkdwn", "text": "ID `pqqew` · expires in 5m · session `abc123`"}
      ]
    },
    {
      "type": "actions",
      "block_id": "pqqew",
      "elements": [
        {
          "type": "button",
          "action_id": "approve",
          "style": "primary",
          "text": {"type": "plain_text", "text": "Approve"},
          "value": "pqqew"
        },
        {
          "type": "button",
          "action_id": "approve_with_note",
          "text": {"type": "plain_text", "text": "Approve with note"},
          "value": "pqqew"
        },
        {
          "type": "button",
          "action_id": "deny",
          "style": "danger",
          "text": {"type": "plain_text", "text": "Deny"},
          "value": "pqqew",
          "confirm": {
            "title": {"type": "plain_text", "text": "Deny this request?"},
            "text": {"type": "plain_text", "text": "Claude will be told you said no."},
            "confirm": {"type": "plain_text", "text": "Deny"},
            "deny": {"type": "plain_text", "text": "Cancel"}
          }
        }
      ]
    }
  ]
}
```

### The post-action update (chat.update)

When Daniel taps Approve, the card re-renders to:

```json
{
  "blocks": [
    {"type": "header", "text": {"type": "plain_text", "text": "Permission request"}},
    {"type": "section", "fields": [
      {"type": "mrkdwn", "text": "*Tool*\nBash"},
      {"type": "mrkdwn", "text": "*Action*\nCreate issue via REST"}
    ]},
    {"type": "context", "elements": [
      {"type": "mrkdwn", "text": ":white_check_mark: Approved by <@U0ADVV3RKHN> · 9:42am"}
    ]}
  ]
}
```

The buttons disappear. The decision is durable in the channel. No double-clicks, no second guesses.

### The "approve with note" / "deny with reason" modal

`trigger_id` from the action payload (3-second TTL, single-use) → `views.open`:

```json
{
  "type": "modal",
  "callback_id": "approval_reason",
  "private_metadata": "{\"requestId\":\"pqqew\",\"verdict\":\"approve\"}",
  "title": {"type": "plain_text", "text": "Approve with note"},
  "submit": {"type": "plain_text", "text": "Approve"},
  "blocks": [
    {
      "type": "input",
      "block_id": "note",
      "label": {"type": "plain_text", "text": "Note for Claude"},
      "element": {
        "type": "plain_text_input",
        "action_id": "text",
        "multiline": true,
        "placeholder": {"type": "plain_text", "text": "e.g. \"yes but skip the migration\""}
      }
    }
  ]
}
```

The `view_submission` payload returns Daniel's note alongside the original `requestId`. Bridge forwards it to Claude as additional context attached to the approval.

## Interaction handler contract

Slack POSTs interactive payloads to either an HTTPS request_url (manifest-configured) or — in the bridge's case — over Socket Mode. The audit identified an `interactive` event handler stub at `server.ts:453–456`. It needs to dispatch on `payload.type`:

| Payload type | Handler | What it does |
|---|---|---|
| `block_actions` (action_id=`approve`) | `handleApprove(requestId, userId)` | `chat.update` with approved-state blocks; emit `notifications/claude/channel/permission` with verdict=allow |
| `block_actions` (action_id=`deny`) | `handleDeny(requestId, userId)` | `chat.update` with denied-state blocks; emit `notifications/claude/channel/permission` with verdict=deny |
| `block_actions` (action_id=`approve_with_note`) | `openModal(trigger_id, requestId, "approve")` | `views.open` with the reason modal |
| `view_submission` (callback_id=`approval_reason`) | `handleApprovalWithNote(requestId, verdict, note, userId)` | Same as approve/deny + propagate note to Claude |

All handlers must verify request signature (Slack's signing secret, X-Slack-Signature header) — Bolt-js does this automatically; raw socket-mode events are pre-authenticated by the websocket connection.

## State machine

```
                     ┌────────────────┐
                     │ pendingPermissions[id] = {channel, ts, expires} │
                     └────────────────┘
                              │
                              ▼
       Claude → MCP → bridge → chat.postMessage(blocks) → channel
                              │
                              ▼
                    Daniel sees card on phone
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
              [Approve]   [Note]        [Deny]
                │             │             │
                │             ▼             │
                │       views.open(modal)   │
                │             │             │
                │       Daniel types reason │
                │             │             │
                │       view_submission     │
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                  chat.update(blocks → resolved-state)
                  notifications/claude/channel/permission
                              │
                              ▼
                    Claude resumes (or doesn't)
```

## Backwards compatibility

The existing text-based regex parser (`PERMISSION_RE` in `lib.ts:178`) should remain active during transition. Three reasons:

1. Legacy clients (already-deployed bridges that haven't redeployed)
2. Mobile users who type `yes pqqew` from muscle memory
3. Audit replay: old permission threads should still be readable

Strategy: when a permission request is posted, send Block Kit blocks AND keep the text fallback in the same message (the `text` field is required by Slack anyway, used for notifications and accessibility). Reply parser keeps working. The interactive handler runs in addition, not instead.

## Manifest changes required

`cerebro-development-slack/manifest.json` (and any other deployed app manifest) needs:

```json
{
  "settings": {
    "interactivity": {
      "is_enabled": true
    },
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": ["message.channels", "message.im", "app_mention"]
    }
  }
}
```

The bridge already runs Socket Mode; only `interactivity.is_enabled` flips. Slack will deliver `block_actions` and `view_submission` events over the same socket connection.

## Implementation plan — file-level deltas

| File | Change |
|---|---|
| `cerebro-development-slack/manifest.json` | `interactivity.is_enabled: true` |
| `slack-cc/server.ts:377–395` | Permission post → Block Kit blocks payload (preserve `text` fallback) |
| `slack-cc/server.ts:453–456` | Replace TODO stub with `block_actions` + `view_submission` dispatcher |
| `slack-cc/lib.ts` | Add `buildApprovalCard()`, `buildResolvedCard()`, `buildReasonModal()` builders |
| `slack-cc/server.ts` | New: `handleApprove`, `handleDeny`, `handleApprovalWithNote`, `openReasonModal` |
| `slack-cc/server.test.ts` | Block Kit shape tests; in-place update assertions; modal trigger_id flow |

Estimated effort: 1–2 focused sessions. The audit confirmed the foundation is in place (Socket Mode connection, MCP notification round-trip, request correlation map). What's missing is the Block Kit serialization + the dispatcher.

## Open questions for whoever implements

1. **Where does the Block Kit JSON live?** Inline strings in `lib.ts` are quick but brittle; importing per-shape builders from a dedicated `blocks/` directory scales better past three or four message types. Recommend the latter once there's more than one card.
2. **Bundle/batch approvals.** When N requests pile up, does the bridge collapse them into a single multi-select card? UX is great but adds state-machine complexity. Defer until there's evidence of pile-up.
3. **Expiration policy.** Slack doesn't expire buttons natively. Bridge needs a sweeper that updates expired cards with "⏱ Expired — request was abandoned." TTL: 5–15 minutes feels right.
4. **Persistence.** Today `pendingPermissions` is in-process Map; bridge restart loses correlation. SQLite-backed map (one row per request, soft-delete on resolution) would survive restarts. Probably worth doing alongside the redesign.

## References

- Block Kit overview: https://docs.slack.dev/block-kit/
- Blocks reference: https://docs.slack.dev/reference/block-kit/blocks
- Handling interactivity: https://docs.slack.dev/interactivity/handling-user-interaction
- Bolt-js: https://github.com/slackapi/bolt-js
- Bolt-js examples: https://github.com/slackapi/bolt-js/tree/main/examples
- Block Kit Builder (live JSON sandbox): https://app.slack.com/block-kit-builder
- `chat.update`: https://docs.slack.dev/reference/methods/chat.update
- `views.open`: https://docs.slack.dev/reference/methods/views.open
- Slack approval blueprints: https://api.slack.com/best-practices/blueprints/approval-workflows
- PagerDuty Slack: https://support.pagerduty.com/main/docs/slack-user-guide
- Sentry Slack: https://docs.sentry.io/organization/integrations/notification-incidents/slack/
- Linear Slack: https://linear.app/docs/slack
- Vercel deploys from Slack: https://vercel.com/kb/guide/run-and-track-deploys-from-slack

## Why this matters

Daniel's stated reason for not leaving Claude Code: approval prompts slow him down. The current flow makes that worse — typing `yes pqqew` on a phone is a tax that compounds over a session. A button is one tap. A modal-with-reason is one tap and a sentence. Multiplied over hundreds of approvals per week, the time saving is real, and the UX gain (context, audit trail, modify-while-approving) is what makes the bridge feel like a tool rather than a hostage situation.
