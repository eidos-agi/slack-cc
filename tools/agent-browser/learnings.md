# Agent Browser Learnings

Flywheel file. After every browser automation session, add what worked, what broke, and what to do differently next time. This compounds — the more sessions logged, the better future sessions go.

---

## HubSpot Login (2026-02-28)

**Target:** `https://app.hubspot.com/login`
**Account:** `it@greenmarkwaste.com`

### What Worked
- `snapshot` gives clean accessibility tree with `@ref` IDs — reliable for finding form fields
- `fill @<ref> <email>` works for the email field
- Login flow: email → "Sign in a different way" → "Sign in with password" → password field appears
- After password + 2FA, landed on HubSpot account chooser with both portals visible (Greenmark Dev + Greenmark Waste Solutions)
- Direct navigation to settings pages works: `goto https://app-na2.hubspot.com/settings/244562652/users`

### What Broke
- Tried `dshanklin@aicholdings.com` first → "No account found". Use `it@greenmarkwaste.com`.
- `wait --load networkidle` sometimes hangs on HubSpot's heavy JS. After ~60s got "Resource temporarily unavailable (os error 35)". Workaround: use `screenshot` instead of `wait` when page is visually loaded.
- `click text=Access` matched 2 elements. Fix: use `snapshot` to get the specific `@ref`, don't use text selectors when ambiguous.

### Login Flow (Step by Step)
1. `open https://app.hubspot.com/login`
2. `fill @e4 it@greenmarkwaste.com` (email field)
3. `click @e5` (Continue button)
4. `wait --load networkidle`
5. Page shows passkey/alternate options → `click` "Sign in a different way"
6. Options appear → `click` "Sign in with password"
7. Password field appears at `@e8` → **STOP: Daniel pastes from LastPass**
8. Daniel enters Duo 2FA on phone
9. Lands on account chooser → `click` "Greenmark Waste Solutions" link
10. Redirects to dashboard

### Timing Notes
- HubSpot login takes 2-3 seconds between steps
- Account chooser loads fast
- Settings pages are heavy — can take 5-10 seconds

---

## Railway Login (2026-03-02)

**Target:** `https://railway.app`
**Account:** `dshanklin@greenmarkwaste.com` (NOT `it@greenmarkwaste.com` — that didn't receive the magic link)
**Workspace:** Greenmark Waste Pro (2 projects: greenmark-waste-solutions, cerebro-qa)

### What Worked
- Railway uses **Magic.link** email verification — no password, just a 6-digit code sent to email
- `headed` mode was required — Daniel needed to see the browser to enter the code and 2FA
- After login, landed on workspace with both projects visible
- Settings → Tokens → created `cli-automation` project token for API/CLI access
- Service renaming works: created empty service, renamed from auto-generated name to `vault-simple`

### What Broke
- `it@greenmarkwaste.com` was tried first — magic link never arrived. Switched to `dshanklin@greenmarkwaste.com`
- Headless mode doesn't work for login flows requiring user to enter codes — must use `headed`
- Agent incorrectly assumed workspace was empty after login — it had 2 projects. Always `snapshot` and read carefully.
- `@e11` syntax caused CSS selector parse errors in some contexts — sometimes need `e11` without `@`

### Login Flow (Step by Step)
1. Open `https://railway.app` in **headed** mode
2. Click "Login" → redirects to login page
3. `fill` email field with `dshanklin@greenmarkwaste.com`
4. Click "Login with Email"
5. **STOP: Daniel enters 6-digit code from email**
6. May get 2FA prompt — **STOP: Daniel handles**
7. Lands on workspace selector → "Greenmark Waste Pro"
8. `snapshot` to see projects

### Project Token Creation
1. Navigate to project → Settings (gear icon)
2. Settings → Tokens tab
3. Click "Create Token"
4. Name: `cli-automation`
5. **STOP: Daniel enters 2FA**
6. Token appears — copy immediately
7. Use as `RAILWAY_TOKEN` env var for CLI access

### CLI with Project Token
```bash
RAILWAY_TOKEN=<token> railway status        # works
RAILWAY_TOKEN=<token> railway variables --json --service <name>  # works
RAILWAY_TOKEN=<token> railway variables --set "KEY=VAL" --service <name>  # works
```

### Timing Notes
- Magic link takes 5-10 seconds to arrive
- Railway pages load fast compared to HubSpot
- Token creation requires 2FA — adds ~15s for Daniel

---

## Claude.ai MCP Connector Setup (2026-04-15, session 29)

**Target:** `https://claude.ai` — configure cerebro-mcp as MCP connector
**Account:** `dshanklin@aicholdings.com`

### What Worked
- `ab -p browserbase open` successfully opened cerebro login page and claude.ai
- GitHub SSO click worked via `ab click`
- `ab screenshot` reliably captured state after navigation
- Live View handoff to Daniel for MFA + connector configuration steps
- `ab eval` with JavaScript to type prompts into Claude's input field
- Connector worked — 5 tool calls confirmed via cerebro-telemetry

### What Broke
- Multi-step flows across `ab` invocations: refs go stale, pages navigate to `about:blank`
- Navigating to `/settings/connectors` after login hit `about:blank` on second `ab open`
- Had to hand off to Daniel via Live View for: GitHub auth completion, adding connector

### Login Flow
1. `ab open https://cerebro.greenmark.jettaintelligence.com/login` → cerebro login
2. `ab snapshot` → find GitHub SSO button → `ab click @ref`
3. **HANDOFF:** Live View URL to Daniel for GitHub auth + MFA
4. Navigate to `https://claude.ai/login`
5. `ab fill @ref dshanklin@aicholdings.com`
6. Daniel provides verification code
7. **HANDOFF:** Live View for connector setup in `/settings/connectors`
8. Daniel adds connector (URL: `https://cerebro-mcp.dshanklin.workers.dev/mcp`)
9. `ab eval` to type prompt invoking the connector

### Key Insight
For multi-step auth flows: use `ab` for navigation + form filling, hand off to human via Live View for auth steps, use `ab eval` for post-auth actions. Single-command operations work reliably in Browserbase — the limitation is state persistence across multiple invocations.

---

## General Patterns

### Reliable
- `snapshot -i` for interactive elements only — less noise
- `screenshot --annotate` for visual debugging — adds numbered labels
- `fill` over `type` — fill clears first, prevents doubled text
- Named sessions (`--session-name`) for multi-step flows

### Unreliable
- `wait --load networkidle` on heavy SPAs (HubSpot, etc.) — can timeout
- `text=` selectors when page has duplicate text — always prefer `@ref`
- Long sessions without screenshots — if daemon gets busy, `snapshot` can fail

### Rules
1. Always `snapshot` before interacting — never guess at refs
2. Stop for password/2FA — never try to automate credential entry
3. Screenshot after key actions — creates visual audit trail
4. Log failures here so the next session avoids them
