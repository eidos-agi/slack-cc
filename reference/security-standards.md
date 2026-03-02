# Greenmark Security Standards

How Greenmark protects credentials, identities, and data across all systems.

---

## Three Layers — Don't Confuse Them

| Layer | Question It Answers | Greenmark Solution | Owner |
|-------|--------------------|--------------------|-------|
| **Identity** | Who are you? | Microsoft Entra ID (via M365) | Michael / IT |
| **Authentication** | Prove it | Entra ID SSO + Microsoft Authenticator MFA | Michael / IT |
| **Secrets** | Where do API keys and tokens live? | Azure Key Vault (service) + Entra ID (human) | Daniel / IT |

These are three different problems. "Microsoft auth" covers the first two. Azure Key Vault covers the third. All Microsoft, one bill, one ecosystem.

---

## Layer 1: Identity — Microsoft Entra ID

**What it does:** Single source of truth for "who works at Greenmark" and "what can they access."

**Why it matters:** Right now, every vendor system has its own login. HubSpot uses `it@greenmarkwaste.com`. Sage uses individual accounts. Fleetio uses who-knows-what. There's no central directory that says "Daniel left, revoke everything."

**What Entra ID gives you:**
- One directory of all Greenmark users
- Single sign-on (SSO) into HubSpot, Sage, Cerebro, and any app that supports SAML/OIDC
- When someone leaves → disable one account → locked out of everything
- Audit trail: who logged into what, when

**Setup:**
- [ ] Confirm M365 plan includes Entra ID P1 (most Business Premium plans do)
- [ ] Register Greenmark users in Entra ID (if not already there from M365)
- [ ] Enable SSO for HubSpot (HubSpot Enterprise supports SAML SSO)
- [ ] Enable SSO for Cerebro (Daniel builds OIDC login against Entra ID)
- [ ] Document which systems support SSO and which don't

**Systems that support Entra ID SSO:**
| System | SSO Support | Notes |
|--------|------------|-------|
| HubSpot | SAML 2.0 | Enterprise plan required |
| Sage Intacct | SAML 2.0 | Supported on all plans |
| Cerebro | OIDC | Daniel builds this (Phase 2) |
| Railway | GitHub SSO | Indirect — GitHub org linked to Entra ID |
| Supabase | SAML | Team plan required |
| Fleetio | SAML 2.0 | Supported |
| Paylocity | SAML 2.0 | Supported |

---

## Layer 2: Authentication — MFA Everywhere

**What it does:** Even if a password leaks, attackers can't get in without a second factor.

**Current state:** Duo MFA on some accounts, nothing on others. Shared `it@greenmarkwaste.com` account with a shared Duo seed — this is the weakest link.

**Target state:**
- Microsoft Authenticator on every user account (comes free with Entra ID)
- Conditional Access policies: require MFA for all logins outside the office network
- No shared accounts — every person has their own identity

**Immediate actions:**
- [ ] Enable MFA on all Entra ID accounts (if not already)
- [ ] Replace Duo with Microsoft Authenticator (one fewer vendor, same security)
- [ ] Create individual accounts for Daniel, Michael, Alex, Robert
- [ ] Retire `it@greenmarkwaste.com` as a login — convert to a distribution list

**Why retire the shared `it@` account:**
The `it@greenmarkwaste.com` account is currently used to log into HubSpot, Railway, Supabase, GitHub, and LastPass. If that password leaks from any one of those services, an attacker has the keys to everything. Individual accounts + SSO fixes this.

---

## Layer 3: Secrets — Azure Key Vault

**What it does:** Stores API keys, tokens, and service credentials where code can access them but humans don't have to copy-paste them.

**Current state:**
| Secret | Where It Lives Now | Problem |
|--------|-------------------|---------|
| HubSpot PAK | Knox (AIC-owned) | Greenmark doesn't control Knox |
| Sage API key | Not yet created | — |
| Supabase DB password | Railway env vars | Acceptable for now |
| Railway API token | Not yet needed | — |

**Target state:** All service secrets in Azure Key Vault, accessed by data-daemon and Cerebro at runtime.

**Why Azure Key Vault:**
- Already included in M365 / Azure subscription
- Cost: ~$0.03 per 10,000 operations (essentially free)
- REST API — data-daemon can pull secrets at startup
- RBAC — Daniel gets write access, services get read-only
- Audit log — every access is logged
- Rotation support — Key Vault can auto-rotate secrets on a schedule

**Migration plan:**

| Phase | Action | Timeline |
|-------|--------|----------|
| **Now** | Move HubSpot PAK from Knox → Railway env var (Greenmark-owned) | Today |
| **Phase 1** | Provision Azure Key Vault under Greenmark Azure tenant | Week 1 |
| **Phase 1** | Move all service secrets into Key Vault | Week 1-2 |
| **Phase 2** | Configure data-daemon to pull secrets from Key Vault at startup | Week 2-3 |
| **Phase 2** | Set up 90-day rotation policy for all API keys | Week 3-4 |

**Interim (before Key Vault):**
Railway environment variables are acceptable for service secrets. Greenmark owns the Railway project, env vars are encrypted at rest, and access is limited to project members. This is not a security gap — it's a reasonable bridge.

---

## What Changes For Each Person

### Michael (President / IT)
- You get a single pane of glass for who has access to what
- When someone leaves, you disable one Entra ID account and they're locked out everywhere
- You approve access requests — "Does Daniel need Sage read access?" Yes/no in Entra ID
- Audit trail for compliance: who accessed what, when

### Alex (CFO)
- Your Sage login goes through Microsoft SSO — same Microsoft account you use for email
- MFA protects financial data even if a password is compromised
- API keys for Cerebro's Sage connection are in Key Vault, not floating in emails or spreadsheets
- SOC 2 alignment if Greenmark ever needs it for enterprise clients

### Daniel (Technology)
- Service secrets live in Key Vault, pulled at runtime — no hardcoded keys
- Cerebro login via Entra ID OIDC — no custom auth to maintain
- Individual account with scoped permissions — not a shared admin

### Robert (Operations)
- Same Microsoft login for Fleetio, Cerebro, and anything else that supports SSO
- Microsoft Authenticator on your phone — one app for all MFA

---

## Security Rules (Non-Negotiable)

1. **No shared accounts for login.** Every person gets their own Entra ID identity.
2. **MFA on everything.** No exceptions. Microsoft Authenticator is free.
3. **API keys are read-only by default.** Write access requires explicit justification.
4. **Secrets never in code.** Not in git, not in environment files checked into repos, not in Slack/Teams messages.
5. **90-day rotation for all API keys.** Calendar reminder + documented runbook.
6. **Offboarding = immediate revocation.** Disable Entra ID account within 24 hours of departure.
7. **Audit quarterly.** Review who has access to what. Remove stale permissions.

---

## Cost

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| Entra ID P1 | $6/user/mo | May already be included in M365 Business Premium |
| Azure Key Vault | ~$1/mo | Usage-based, negligible at Greenmark's scale |
| Microsoft Authenticator | Free | Included with Entra ID |
| **Total** | **~$25-50/mo** | For 4-8 users |

This replaces: LastPass ($4/user/mo) + Duo ($3/user/mo) = similar cost, but now it's one ecosystem instead of three.

---

## Timeline

| Week | What Happens |
|------|-------------|
| **This week** | Move HubSpot PAK to Railway env var. Document current secrets inventory. |
| **Week 1** | Confirm M365 plan, provision Key Vault, enable MFA if not already on. |
| **Week 2** | Create individual Entra ID accounts for Daniel, Michael, Alex, Robert. |
| **Week 3** | Migrate service secrets to Key Vault. Configure data-daemon. |
| **Week 4** | Enable SSO for HubSpot + Sage (if Enterprise plans allow). |
| **Ongoing** | 90-day key rotation. Quarterly access review. |

---

## Questions For Michael

1. What M365 plan is Greenmark on? (Business Basic / Standard / Premium?) — determines Entra ID tier
2. Is there an existing Azure tenant, or do we need to create one?
3. Who should be the Entra ID Global Admin? (Recommend: Michael as primary, one backup)
4. Are there other employees beyond leadership who need system access?
