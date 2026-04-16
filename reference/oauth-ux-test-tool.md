# OAuth UX Test Tool

A one-click smoke test for Cerebro's OAuth login + consent flow. Simulates being a DCR-registered OAuth client (like Claude) so you can exercise the real flow on staging without needing to go through claude.ai/settings/connectors.

**Why this exists**: PR #68 introduced the contained-frame banner on `/login` and unified `/oauth/consent`. Unit tests + Playwright covered the code paths, but the only way to see how real Supabase data flows through our resolver is with a real OAuth authorization. This test tool gives us that with one click.

Per rhea's call (2026-04-16 debate): register **one** persistent test DCR client, document it here, reuse forever. Don't build a harness into the cerebro repo.

## Test client details

Registered on staging Supabase OAuth Server:

| Field | Value |
|---|---|
| `client_id` | `2a20b62f-1d41-4c61-aff2-e46a2dda9a87` |
| `client_name` | `Cerebro OAuth UX Tester` |
| `client_uri` | `https://example.com` (→ rendered as "External" in banner) |
| `redirect_uri` | `https://example.com/oauth-test-callback` |
| `scope` | `openid profile email mcp:read` |
| `token_endpoint_auth_method` | `none` (public client; PKCE required) |

## How to use

1. **Regenerate a fresh PKCE + state** (code_verifier is one-time-use):

   ```bash
   python3 -c "
   import secrets, hashlib, base64, urllib.parse
   verifier = secrets.token_urlsafe(64)
   challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
   state = secrets.token_urlsafe(16)
   base = 'https://wwmcgtyngnziepeynccz.supabase.co/auth/v1/authorize'
   params = {
     'response_type': 'code',
     'client_id': '2a20b62f-1d41-4c61-aff2-e46a2dda9a87',
     'redirect_uri': 'https://example.com/oauth-test-callback',
     'scope': 'openid profile email mcp:read',
     'state': state,
     'code_challenge': challenge,
     'code_challenge_method': 'S256',
   }
   print(base + '?' + urllib.parse.urlencode(params))
   "
   ```

2. **Paste the URL into a browser** while signed out of Cerebro. Supabase redirects you to `https://staging-cerebro-greenmark.jettaintelligence.com/login?next=/oauth/consent?authorization_id=...`. This is exactly what Claude's flow does.

3. **Sign in** — you should see the OAuth flow banner (neutral "EXTERNAL APPLICATION REQUESTING ACCESS" frame, shield icon, "Cerebro OAuth UX Tester" app name, "example.com" redirect host, "Didn't start this?" escape hatch). Verify the Sign-in button is above the fold.

4. **Complete MFA** if prompted. (Known UX gap: banner disappears here — rhea-accepted tradeoff.)

5. **Land on `/oauth/consent`** — you should see the same banner at the top of the consent page (continuity thread preserved), scope list, and Allow / Cancel buttons.

6. **Click Allow**. Supabase redirects you to `https://example.com/oauth-test-callback?code=...&state=...`. The code is visible in the URL bar — no server needed on example.com. The presence of the code means the full round-trip worked.

## First-party variant (optional)

To test the emerald-tinted first-party banner, register a second client with `client_uri` set to a host in `OAUTH_FIRST_PARTY_HOSTS` (currently `cerebro.greenmark.jettaintelligence.com`, `staging-cerebro-greenmark.jettaintelligence.com`). Not needed for the primary smoke test.

```bash
curl -X POST "$SUPABASE_URL/auth/v1/admin/oauth/clients" \
  -H "apikey: $SERVICE_KEY" \
  -H "Authorization: Bearer $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Cerebro First-Party Tester",
    "client_uri": "https://cerebro.greenmark.jettaintelligence.com",
    "redirect_uris": ["https://example.com/first-party-callback"],
    "grant_types": ["authorization_code"],
    "response_types": ["code"],
    "token_endpoint_auth_method": "none",
    "scope": "openid"
  }'
```

## Cleanup (if ever needed)

The test clients are persistent. If you want to remove them:

```bash
curl -X DELETE "$SUPABASE_URL/auth/v1/admin/oauth/clients/2a20b62f-1d41-4c61-aff2-e46a2dda9a87" \
  -H "apikey: $SERVICE_KEY" \
  -H "Authorization: Bearer $SERVICE_KEY"
```

## Troubleshooting

- **"invalid_client"**: client_id wrong, or client was deleted. Re-register.
- **"invalid_redirect_uri"**: `redirect_uri` in the authorize URL doesn't exactly match `redirect_uris` in the client registration. Re-check for trailing slashes.
- **"invalid_grant" after Allow**: PKCE `code_verifier` doesn't match the `code_challenge` you sent. You re-used an old one — generate fresh.
- **Authorization expires**: Supabase authorization IDs are short-lived (~5 min). Regenerate the authorize URL if the consent page 404s.
