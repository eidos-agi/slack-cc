# HubSpot Integration Security Audit

**Date:** 2026-02-28
**Auditor:** Daniel Shanklin, Director of AI & Technology (AIC Holdings)
**Classification:** Internal — Greenmark Waste Solutions
**Scope:** Private App "data-daemon-production" on HubSpot portal 244562652

---

## Executive Summary

Greenmark's HubSpot integration uses a Private App Key (PAK) bearer token with 4 read-only scopes, stored in Knox (secret management), to pull CRM data into a Supabase data warehouse via the data-daemon extraction pipeline. The integration is **read-only by design** — no writes to HubSpot, ever.

The current setup is **reasonably secure for a company of Greenmark's size**, but has three material weaknesses:

1. **Shared IT account** (`it@greenmarkwaste.com`) as the Private App owner — no individual accountability
2. **Long-lived bearer token** with no automatic expiry or rotation enforcement
3. **No IP restriction on API calls** — HubSpot does not support IP allowlisting for Private App tokens

This audit documents each risk, rates it, and provides practical hardening steps that work within HubSpot's actual feature set.

---

## 1. Authentication Model Analysis

### How Private App Keys Work

HubSpot Private Apps use a **static bearer token** for authentication. Every API request includes:

```
Authorization: Bearer pat-na1-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

Key characteristics of this authentication model:

| Property | Value |
|----------|-------|
| Token type | Bearer token (opaque string) |
| Token lifetime | **Indefinite** — does not expire unless manually rotated or app deleted |
| Scope binding | Fixed at app creation; modifiable by editing the Private App |
| User binding | Owned by the HubSpot user who created the app |
| Transport security | HTTPS (TLS 1.2+) required; HubSpot rejects HTTP |
| Rate limiting | 190 requests per 10 seconds (burst); 650,000/day (Professional tier) |
| Token format | Prefixed `pat-na1-` — detectable by secret scanners |

### What Happens If the Token Leaks

If the PAK is exposed (e.g., committed to a public repository, logged in plaintext, or exfiltrated from a compromised system):

1. **Immediate risk:** Anyone with the token can read all CRM data within the granted scopes — contacts (PII: names, emails, phone numbers), companies, deals (revenue data), and owner assignments. No additional authentication required.

2. **Blast radius is limited by scopes:** The 4 read-only scopes mean an attacker **cannot** modify, delete, or create records in HubSpot. They can only read.

3. **No geographic or IP restriction:** HubSpot does not support IP allowlisting for Private App API calls. A leaked token is usable from anywhere in the world.

4. **GitHub secret scanning:** HubSpot partnered with GitHub for [automatic deactivation of exposed tokens](https://developers.hubspot.com/changelog/public-beta-automatic-deactivation-of-exposed-tokens). If the PAK is committed to a public GitHub repo, HubSpot will detect the `pat-na1-` prefix and automatically deactivate the token. This is enforced as of April 2025.

5. **Revocation options:** The token can be immediately revoked via:
   - **"Expire now"** — instant deactivation
   - **"Rotate and expire later"** — generates a new token, old one remains valid for 7 days (grace period for updating integrations)
   - **Delete the Private App entirely** — kills the token permanently

### Rate Limiting as a Safety Net

HubSpot enforces rate limits that provide partial protection against abuse:

| Limit | Value | Scope |
|-------|-------|-------|
| Burst limit | 190 requests / 10 seconds | Per Private App |
| Daily limit | 650,000 requests / day (Professional) | Shared across ALL apps in the account |
| 429 response | Retry-After header included | Automatic backoff signal |

These limits constrain the speed of data exfiltration but do not prevent it. An attacker reading contacts at 190 req/10s could extract the entire CRM in minutes.

---

## 2. Weak Points Identified

### 2.1 Shared IT Account as App Owner

**Current state:** The Private App "data-daemon-production" was created under the `it@greenmarkwaste.com` HubSpot account. This is a shared IT account — both Michael Nguyen and Daniel Shanklin have credentials (via LastPass) and 2FA access (via Duo).

**Why this is a problem:**
- **No individual accountability.** HubSpot audit logs show actions as `it@greenmarkwaste.com` — there is no way to distinguish whether Michael or Daniel (or a future IT team member) performed an action.
- **Credential sprawl.** The password lives in LastPass. If the LastPass vault is shared or if additional users are added to the distribution list, the blast radius expands silently.
- **2FA shared seed.** Both users enrolled in Duo 2FA for the same account. If Daniel's engagement ends, his Duo enrollment persists unless explicitly removed.
- **Key person risk in reverse.** If the `it@` account is disabled or the password is changed without coordination, the Private App remains active (tokens are independent of login credentials), but the app cannot be managed — no scope changes, no rotation, no monitoring.

**HubSpot's actual capability:** HubSpot supports individual user accounts with role-based permissions. A Super Admin can create a dedicated service-role user or assign Private App management permissions to a named individual.

### 2.2 Long-Lived Token with No Forced Expiry

**Current state:** The PAK token was generated when the Private App was created. It does not expire. HubSpot sends reminder emails to Super Admins every 180 days suggesting rotation, but does not enforce it.

**Why this is a problem:**
- **No automatic credential rotation.** If the token is compromised silently (e.g., extracted from a compromised server, read from memory, intercepted by a rogue process), it remains valid indefinitely until someone notices and manually rotates.
- **Rotation reminders go to Super Admins.** If the Super Admin is the shared `it@` account, and nobody is actively monitoring that inbox for HubSpot security emails, reminders are missed.
- **Knox storage mitigates but doesn't eliminate.** Storing the token in Knox (AIC's secret manager) is correct — it prevents plaintext storage in code or config files. However, Knox itself becomes a single point of trust. If Knox is compromised, all secrets (including this PAK) are exposed.

**HubSpot's actual capability:** HubSpot provides a "Rotate" button on the Private App settings page. Two options: "Rotate and expire later" (7-day grace period) or "Expire now" (immediate). There is no auto-rotation API. Rotation is a manual process.

### 2.3 No IP Allowlisting for API Calls

**Current state:** HubSpot supports [IP allowlisting for portal logins](https://knowledge.hubspot.com/account-security/limit-logins-to-trusted-ip-addresses) (i.e., restricting which IPs can log into the HubSpot web UI). However, this restriction **does not apply to API calls** made with Private App tokens.

**Why this is a problem:**
- A stolen token can be used from any IP address, any network, any country.
- There is no way to restrict API access to, say, only Railway's egress IPs (where data-daemon runs) or Daniel's office IP.
- This is a known gap that HubSpot users have [requested](https://www.scopiousdigital.com/faq/restrict-hubspot-api-access-by-allowlisting-ip-addresses) but HubSpot has not implemented.

**HubSpot's actual capability:** IP restriction exists only for web UI login, not for API authentication. This is a platform limitation, not a configuration oversight.

### 2.4 Bearer Token in Transit

**Current state:** All HubSpot API calls use HTTPS (TLS 1.2 or 1.3). HubSpot enforces encrypted transport and does not accept plaintext HTTP connections.

**Risk assessment:** This is a **low risk** in practice. TLS protects the token in transit. The realistic attack surface is:
- Token exposure in server-side logs (if the `Authorization` header is logged)
- Token exposure in error reporting tools (Sentry, LogRocket, etc.)
- Token readable in process memory on a compromised host

HubSpot's encryption at rest uses AES-256 for stored data, and TLS 1.2+ for data in transit. This meets industry standards.

---

## 3. Hardening Recommendations

### 3.1 Scope Minimization — Are All 4 Scopes Necessary?

| Scope | data-daemon Needs It? | Justification |
|-------|-----------------------|---------------|
| `crm.objects.contacts.read` | **Yes** | Contacts are a primary CRM entity for Cerebro dashboards |
| `crm.objects.companies.read` | **Yes** | Companies link to Navusoft customers via entity resolution |
| `crm.objects.deals.read` | **Yes** | Deal pipeline data drives revenue reporting in Cerebro |
| `crm.objects.owners.read` | **Yes** | Required to resolve owner IDs to human-readable names on contacts/deals |

**Verdict:** All 4 scopes are justified and are the minimum required for the data-daemon's function. No scope reduction is possible without losing critical dashboard functionality.

**Not requested (correctly):**
- No `*.write` scopes — enforces the read-only principle
- No `tickets` scope — not needed for current dashboards
- No `forms`, `workflows`, or `marketing` scopes — out of scope for Cerebro
- No `account-info.security.read` — not needed for data extraction

### 3.2 API Call Logging and Monitoring

**HubSpot provides built-in monitoring:**
- **API Call Logs:** Available in HubSpot Settings > Integrations > Private Apps > [App Name] > Logs tab. Shows all API calls for the past 30 days with method, endpoint, response code, and timestamp.
- **Export capability:** Logs can be exported as CSV for external analysis.
- **Security tab:** Shows token viewing events, rotation events, and scope changes.

**Recommended actions:**
1. **Weekly spot-check** (5 minutes): Open the Private App Logs tab and scan for anomalies — unexpected endpoints, unusual call volumes, 4xx errors indicating scope probing.
2. **Monthly CSV export:** Download the API call log monthly and archive it. This provides an audit trail beyond HubSpot's 30-day window.
3. **data-daemon-side logging:** The data-daemon pipeline should log every HubSpot API call with timestamp, endpoint, record count, and response code. These logs should be stored in Supabase (the `debug_logs` table or a dedicated `api_audit_log` table) for cross-referencing.
4. **Alert on anomalous volume:** If data-daemon runs on a known schedule (e.g., nightly sync), any API calls outside that window are suspicious. HubSpot does not offer alerting on this natively — implement it in data-daemon's logging layer.

### 3.3 Token Rotation Schedule

**Recommended cadence:** Every 90 days (quarterly).

HubSpot's default reminder is 180 days. For a production integration handling CRM PII, 90 days is more appropriate. The rotation process:

1. Go to HubSpot Settings > Integrations > Private Apps > "data-daemon-production"
2. Click **"Rotate and expire later"** — this generates a new token and gives 7 days before the old one dies
3. Update the token in Knox immediately
4. Verify data-daemon connects successfully with the new token
5. Confirm the old token is deactivated after the 7-day grace period
6. Document the rotation in the devlog

**Calendar reminder:** Set a recurring quarterly reminder for the 1st of the month (March, June, September, December).

**Rotation runbook:** Should be documented in the infra repo so any future engineer can perform it without tribal knowledge.

### 3.4 Network Restrictions

**What HubSpot supports:**
- IP allowlisting for web UI login (Settings > Account > Security > Login) -- **recommended to enable**
- Does NOT support IP allowlisting for API calls

**What we can do at the infrastructure level:**
- **Railway egress IPs are not static** by default, so IP-based restriction at the HubSpot side is not feasible even if HubSpot supported it.
- **Knox access control:** Ensure only the data-daemon Railway service can read the HubSpot PAK from Knox. No other service or user should have Knox access to this secret.
- **Environment variable isolation:** The PAK should exist only in the Railway service environment for data-daemon-production. It should not be in any other service's env vars, not in CI/CD logs, not in developer `.env` files.

**Recommended action:** Enable HubSpot IP allowlisting for web UI logins. Restrict login to Greenmark's office IPs and Daniel's known IPs. This does not protect the API, but it protects the management plane (the portal where scopes and tokens are managed).

### 3.5 Service Account vs. Shared IT Account

**Current state:** Private App owned by `it@greenmarkwaste.com` (shared).

**Recommended migration path:**

1. **Create a dedicated HubSpot user** for service ownership: `integrations@greenmarkwaste.com` or `cerebro-svc@greenmarkwaste.com`. This should be a functional account whose sole purpose is owning integration Private Apps.
2. **Assign Super Admin permissions** to this service account (required to manage Private Apps).
3. **Transfer Private App ownership** by recreating the app under the service account. (HubSpot does not support transferring ownership of existing Private Apps — the app must be recreated and a new token generated.)
4. **Remove `it@greenmarkwaste.com` as the app owner.** The it@ account should remain for IT administration but should not own production integrations.
5. **Store the service account credentials** in LastPass with restricted access — only Daniel and Michael should have access.

**Why this matters for Greenmark specifically:** When Daniel's AIC engagement ends, Greenmark needs to own and manage these integrations independently. If the Private App is owned by a personal account or a shared account that Daniel has access to, the handover is messy. A dedicated service account makes ownership transfer clean.

### 3.6 Available HubSpot Audit Logs

HubSpot provides three categories of audit data (available in Settings > Account > Audit Logs):

| Log Type | Retention | Contents | API Access |
|----------|-----------|----------|------------|
| **Account Activity** | 30 days | CRM record changes, setting modifications, import/export events | Enterprise only |
| **Login History** | 90 days | Timestamp, email, success/failure, IP address, location, user agent | Enterprise only |
| **Security Activity** | 1 year | Token rotations, permission changes, 2FA changes, app installations | Enterprise only |

**Important limitation:** The [Account Activity API](https://developers.hubspot.com/docs/api-reference/account-audit-logs-v3/guide) is **Enterprise-only**. If Greenmark is on a Professional plan, audit log access is limited to the web UI and CSV exports. Programmatic audit log ingestion is not available.

**Recommended action:** Regardless of plan tier, a Super Admin should enable **audit log email notifications** for security events (token rotations, new Private App creation, scope changes).

---

## 4. Risk Matrix

| # | Threat | Likelihood | Impact | Risk Level | Current Mitigation | Residual Risk |
|---|--------|-----------|--------|------------|-------------------|---------------|
| T1 | **Token leaked via code commit** | Low | High — full CRM read access from anywhere | **Medium** | Knox storage (not in code); `.gitignore`; GitHub auto-deactivation | Low — GitHub scanning provides backstop |
| T2 | **Token leaked via compromised server** | Low | High — attacker reads all CRM PII | **Medium** | Railway environment isolation; Knox access control | Medium — no IP restriction on API calls means token is usable from anywhere |
| T3 | **Token leaked via logs/monitoring tools** | Medium | High — token in Authorization header could appear in debug logs | **High** | data-daemon should redact auth headers in logs | Medium — depends on log hygiene discipline |
| T4 | **Shared account compromise (it@)** | Medium | Critical — attacker gains portal access: can modify scopes, create write-enabled apps, export all data | **High** | LastPass + Duo 2FA | Medium — shared credentials increase attack surface |
| T5 | **Scope escalation by insider** | Low | High — someone adds write scopes to the Private App, enabling CRM modification | **Medium** | Only Super Admins can edit Private Apps; audit log captures scope changes | Low — requires deliberate action by authorized user |
| T6 | **Stale token remains valid after personnel change** | Medium | Medium — former team member retains knowledge of the token value | **Medium** | Knox access can be revoked; token can be rotated | Low — if rotation happens promptly at offboarding |
| T7 | **Rate limit abuse / data exfiltration** | Low | Medium — attacker bulk-downloads CRM data | **Low** | 190 req/10s burst limit; read-only scopes | Low — rate limits slow but don't prevent exfiltration |
| T8 | **Man-in-the-middle on API calls** | Very Low | High — token and data intercepted | **Low** | TLS 1.2+ enforced by HubSpot | Very Low — standard TLS protection |
| T9 | **Knox compromise exposes all secrets** | Very Low | Critical — PAK plus all other managed secrets exposed | **Low** | Knox access controls; encryption at rest | Low — single point of trust, but well-protected |

### Risk Heat Map

```
              Low Impact    Medium Impact    High Impact    Critical Impact
Very Low      |             |                | T8           |
Low           |             | T7             | T1, T5       |
Medium        |             | T6             | T3           | T4
High          |             |                |              |
```

**Top 3 risks requiring action:**
1. **T4 — Shared account compromise** (Medium likelihood, Critical impact)
2. **T3 — Token in logs** (Medium likelihood, High impact)
3. **T6 — Stale token after personnel change** (Medium likelihood, Medium impact)

---

## 5. SOC 2 Compliance Comparison

SOC 2 Type II compliance evaluates controls across five Trust Service Criteria. Here is how this integration compares:

### 5.1 Security (Common Criteria)

| SOC 2 Requirement | Current State | Gap |
|-------------------|---------------|-----|
| **Unique user identification** | FAIL — shared `it@` account owns the Private App | Remediate: create dedicated service account |
| **Least-privilege access** | PASS — 4 read-only scopes, minimum necessary | None |
| **Credential encryption at rest** | PASS — token in Knox (encrypted secret store) | None |
| **Credential encryption in transit** | PASS — TLS 1.2+ enforced by HubSpot | None |
| **Access review process** | PARTIAL — no documented periodic review of who has access | Remediate: quarterly access review |
| **Credential rotation** | FAIL — no rotation schedule in place; token is indefinite | Remediate: implement 90-day rotation |
| **Network segmentation** | FAIL — no IP restriction on API calls (platform limitation) | Accept: HubSpot does not support this; document as accepted risk |

### 5.2 Availability

| SOC 2 Requirement | Current State | Gap |
|-------------------|---------------|-----|
| **Service continuity** | PASS — data-daemon handles HubSpot outages gracefully (retry logic, job queue) | None |
| **Rate limit handling** | PASS — data-daemon implements backoff on 429 responses | None |

### 5.3 Processing Integrity

| SOC 2 Requirement | Current State | Gap |
|-------------------|---------------|-----|
| **Data validation** | PASS — data-daemon validates API responses before warehouse insert | None |
| **Audit trail for data changes** | PASS — bronze schema preserves raw data; medallion architecture provides lineage | None |

### 5.4 Confidentiality

| SOC 2 Requirement | Current State | Gap |
|-------------------|---------------|-----|
| **PII classification** | PARTIAL — CRM data contains PII (names, emails, phone numbers) but no formal data classification exists | Remediate: document PII fields in data dictionary |
| **PII handling in logs** | PARTIAL — data-daemon should redact PII from debug logs | Remediate: implement log redaction |
| **Data access logging** | PASS — HubSpot API call logs + data-daemon application logs | None |

### 5.5 Privacy

| SOC 2 Requirement | Current State | Gap |
|-------------------|---------------|-----|
| **Data minimization** | PASS — only 4 CRM object types accessed; no marketing/engagement data | None |
| **Retention policy** | PARTIAL — bronze data retained indefinitely in Supabase; no formal retention policy documented | Document: define retention periods |

### Overall SOC 2 Assessment

**If Greenmark were undergoing a SOC 2 audit today, this integration would have 4 findings:**

1. **Finding:** Shared account for integration ownership (Security CC6.1 — logical access)
2. **Finding:** No credential rotation policy (Security CC6.1 — credential management)
3. **Finding:** No IP-based network restriction on API access (Security CC6.6 — network controls; document as accepted risk with compensating controls)
4. **Finding:** No formal PII classification for CRM data flowing to warehouse (Confidentiality C1.1)

None of these are "stop-ship" findings. They are remediation items that would need a corrective action plan with target dates.

---

## 6. Prioritized Action Items

| Priority | Action | Effort | Owner | Target Date |
|----------|--------|--------|-------|-------------|
| **P1** | Implement 90-day token rotation schedule + calendar reminder | 15 min | Daniel | Week of 2026-03-03 |
| **P1** | Audit data-daemon logs to confirm PAK is never logged in plaintext | 30 min | Daniel | Week of 2026-03-03 |
| **P2** | Enable HubSpot login IP allowlisting for portal access | 15 min | Michael / Daniel | Week of 2026-03-10 |
| **P2** | Enable HubSpot audit log email notifications for security events | 10 min | Daniel (Super Admin) | Week of 2026-03-10 |
| **P3** | Create dedicated service account for Private App ownership | 30 min | Michael + Daniel | Before Q2 2026 |
| **P3** | Document PII fields in HubSpot data dictionary (infra repo) | 1 hour | Daniel | Before Q2 2026 |
| **P4** | Write token rotation runbook in infra repo | 30 min | Daniel | Before Q2 2026 |
| **P4** | Formal access review: who has Knox access to the HubSpot PAK? | 15 min | Daniel | Quarterly |

---

## 7. What Daniel Told Michael (Context)

Daniel told Michael that "login security is weak" and he is "red-teaming security." Here is what that means in plain language:

**"Login security is weak"** refers to the shared `it@greenmarkwaste.com` account. This is a distribution list (Microsoft 365) that both Daniel and Michael use to log into HubSpot. When two people share one login, you lose the ability to know who did what. If the password leaks, both people are compromised. This is the single biggest security gap — and the easiest to fix (create separate user accounts).

**"Red-teaming security"** means Daniel is deliberately looking for weaknesses before a bad actor finds them. This audit is the output of that exercise. The good news: because the integration is read-only with minimal scopes, the worst-case scenario is data exposure (someone reads your CRM data), not data corruption (someone changes or deletes your CRM data). The recommendations above close the most likely attack paths.

---

## Sources

- [HubSpot Private Apps Documentation](https://developers.hubspot.com/docs/apps/legacy-apps/private-apps/overview)
- [HubSpot API Usage Guidelines and Limits](https://developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines)
- [HubSpot API Usage Details](https://developers.hubspot.com/docs/guides/apps/api-usage/usage-details)
- [HubSpot: Automatic Deactivation of Exposed Tokens](https://developers.hubspot.com/changelog/public-beta-automatic-deactivation-of-exposed-tokens)
- [HubSpot: Limit Logins to Trusted IP Addresses](https://knowledge.hubspot.com/account-security/limit-logins-to-trusted-ip-addresses)
- [HubSpot: View and Export Account Activity History](https://knowledge.hubspot.com/account-management/view-and-export-account-activity-history)
- [HubSpot Account Activity API](https://developers.hubspot.com/docs/api-reference/account-audit-logs-v3/guide)
- [HubSpot Security Program](https://legal.hubspot.com/security)
- [HubSpot Trust Center](https://trust.hubspot.com/)
- [HubSpot Community: Token Rotation Feature Request](https://community.hubspot.com/t5/HubSpot-Ideas/Eliminate-automate-private-app-access-token-rotation/idi-p/1100014)
- [HubSpot: IP Allowlisting for API Access (Not Supported)](https://www.scopiousdigital.com/faq/restrict-hubspot-api-access-by-allowlisting-ip-addresses)
- [HubSpot Scopes Reference](https://developers.hubspot.com/docs/apps/legacy-apps/authentication/scopes)
- [Private App Token Rotation Guide](https://impulsecreative.com/product-support/private-app-refresh)
- [SOC 2 Compliance with HubSpot](https://community.hubspot.com/t5/Tips-Tricks-Best-Practices/Solution-Strengthen-Your-SOC-2-Compliance-Posture-While-Using/td-p/1225347)
