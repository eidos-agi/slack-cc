# Agent Browser — Greenmark Cockpit

Headless browser automation for vendor logins, dashboard access, and credential workflows. This is the cockpit's only browser tool. Do NOT use Claude-in-Chrome, Helios, or any other browser MCP.

## Quick Start

```bash
# From greenmark-cockpit root:
AB="./tools/agent-browser/ab"

# Navigate
$AB open https://railway.app

# See what's on the page (AI-friendly accessibility tree)
$AB snapshot

# Interact by ref (refs come from snapshot output)
$AB fill @e4 it@greenmarkwaste.com
$AB click @e5

# Screenshot for human review
$AB screenshot /tmp/screenshot.png
$AB screenshot --annotate /tmp/labeled.png   # numbered labels

# Wait for page loads
$AB wait --load networkidle
```

## Auth Pattern (Greenmark Vendor Logins)

All Greenmark vendor accounts use `it@greenmarkwaste.com` with passwords in LastPass.

```
1. $AB open <login-url>
2. $AB snapshot                          # find the email field ref
3. $AB fill @<ref> it@greenmarkwaste.com
4. $AB click @<submit-ref>
5. $AB wait --load networkidle
6. $AB snapshot                          # check for password field
7. → STOP: Tell Daniel to paste password from LastPass
8. → STOP: Daniel enters Duo 2FA
9. $AB wait --load networkidle
10. $AB snapshot                         # confirm logged in
```

## Key Commands

| Command | What |
|---------|------|
| `open <url>` | Navigate to URL |
| `snapshot` | Get page as accessibility tree with `@ref` IDs |
| `snapshot -i` | Interactive elements only (buttons, inputs, links) |
| `click @<ref>` | Click element |
| `fill @<ref> <text>` | Clear field and type |
| `type @<ref> <text>` | Append text (no clear) |
| `press Enter` | Press a key |
| `screenshot [path]` | Screenshot (default: /tmp) |
| `screenshot --annotate [path]` | Labeled screenshot with numbered legend |
| `wait --load networkidle` | Wait for page to finish loading |
| `get text @<ref>` | Extract text from element |
| `get url` | Current page URL |
| `eval <js>` | Run JavaScript on page |
| `tab list` | List open tabs |
| `tab new` | New tab |

## Session Persistence

```bash
# Named sessions auto-save cookies + localStorage
$AB --session-name railway open https://railway.app
# Next time, session state is restored automatically
```

## Workflow: Agent Uses This

The `ab` wrapper logs every command and output to `logs/YYYY-MM-DD.log`. This creates an audit trail of all browser interactions — what was clicked, what was seen, what failed.

After each browser session, update `learnings.md` with:
- What worked
- What broke
- Login flow changes (vendors update UIs)
- Timing gotchas (elements that need extra waits)

## File Structure

```
tools/agent-browser/
├── ab                  ← wrapper script (adds logging)
├── README.md           ← you are here
├── learnings.md        ← flywheel: what works, what doesn't
├── package.json        ← agent-browser dependency
├── node_modules/       ← installed
└── logs/               ← daily command logs (gitignored)
```
