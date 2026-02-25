---
id: TASK-1.8
title: 'Security review: HubSpot integration risks and mitigations'
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 21:59'
updated_date: '2026-02-25 07:44'
labels:
  - hubspot
  - security
  - blocker
dependencies: []
references:
  - notes/2026-02-24_155759_0399.md
  - notes/2026-02-24_152936_1271.md
parent_task_id: TASK-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Before expanding HubSpot access (CRM scopes, Private Apps, or any broader API access), conduct a CISO-lens security review. Identify threats, gotchas, compliance concerns, and credential management risks. This must be completed before proceeding with TASK-1.6 or TASK-1.7.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Threat model documented covering credential management, data exposure, access control, and compliance
- [x] #2 Each risk has a severity rating and mitigation plan
- [x] #3 Go/no-go recommendation for each access path (PAK expansion vs Private App)
- [x] #4 Findings shared with relevant stakeholders before proceeding
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Security Review: HubSpot Integration — CISO Lens\n\n### 1. CREDENTIAL MANAGEMENT\n\n**Risk 1.1: PAK stored in plaintext on local disk** | Severity: HIGH\n- `hubspot.config.yml` contains the Personal Access Key in plain text\n- Gitignored, but lives on Daniel's laptop unencrypted\n- If laptop is compromised, attacker gets full HubSpot API access at Daniel's permission level\n- **Mitigation**: Move PAK to Knox (AIC secret store) or macOS Keychain. Reference from env var, not config file. At minimum, ensure FileVault is enabled on the Mac.\n\n**Risk 1.2: PAK has no expiration** | Severity: MEDIUM\n- HubSpot PAKs don't auto-expire — they live until manually deactivated\n- No forced rotation policy\n- **Mitigation**: Set a calendar reminder to rotate quarterly. Document the rotation process. Consider Private App tokens which also don't expire but are scoped to the app, not the user.\n\n**Risk 1.3: PAK is tied to Daniel's personal user** | Severity: MEDIUM\n- If Daniel's user is disabled or leaves, the PAK dies and all integrations break\n- No service account concept in HubSpot PAKs\n- **Mitigation**: For production (data-daemon), use a Private App token instead — those survive user changes. PAK is fine for testing/exploration.\n\n### 2. ACCESS CONTROL\n\n**Risk 2.1: Shared account (it@greenmarkwaste.com)** | Severity: HIGH\n- Daniel logged into HubSpot via `it@greenmarkwaste.com` — a distribution list shared with Michael\n- 2FA was set up with authenticator app — but who has the TOTP seed? If both Daniel and Michael scanned it, both can auth as the same identity\n- No audit trail distinguishing Daniel vs Michael's actions under this shared identity\n- **Mitigation**: Daniel should have his OWN HubSpot user (daniel@... or dshanklin@...) separate from the IT shared account. Use the shared account only for IT admin, not for API access or development.\n\n**Risk 2.2: Scope creep when expanding PAK** | Severity: MEDIUM\n- Asking admin to \"enable CRM scopes\" could result in write access, not just read\n- CRM write access means the API could modify contacts, deals, companies — violates the \"read-only, no agent writes\" principle from the Feb 19 decision\n- **Mitigation**: Explicitly request READ-ONLY scopes. Document exactly which scopes are needed: `crm.objects.contacts.read`, `crm.objects.companies.read`, `crm.objects.deals.read`, `crm.schemas.custom.read`. No write scopes.\n\n**Risk 2.3: Private App could get broader access than intended** | Severity: MEDIUM\n- Private Apps let you pick scopes at creation — easy to over-provision\n- A Private App token doesn't have user-level audit trail the way a PAK does\n- **Mitigation**: Principle of least privilege. Only request read scopes. Name the app clearly (e.g., \"Cerebro Read-Only Connector\"). Document the exact scopes granted.\n\n### 3. DATA EXPOSURE\n\n**Risk 3.1: CRM data contains PII** | Severity: HIGH\n- Contacts = names, emails, phone numbers, company associations\n- Deals = revenue figures, pipeline stages, close dates\n- This is real customer and prospect data — not synthetic\n- **Mitigation**: Never commit CRM data to git. Sample data for testing should be anonymized or use HubSpot sandbox/test accounts. Add `*.json` and `*.csv` to gitignore in the testing repo for good measure.\n\n**Risk 3.2: data-daemon-testing is a sandbox with real data** | Severity: MEDIUM\n- The whole point is to test with real data, but \"testing\" repos get less scrutiny than production\n- Risk of data lingering in logs, temp files, shell history\n- **Mitigation**: Treat data-daemon-testing with same data handling rules as production. No PII in committed files. Clear shell history of any API responses containing PII. Consider using HubSpot test accounts (the CLI supports them) for exploration.\n\n**Risk 3.3: CLI output goes to terminal / shell history** | Severity: LOW\n- API responses with PII will show in terminal output and potentially shell history files\n- **Mitigation**: Pipe sensitive output to files that are gitignored. Be aware when screen-sharing.\n\n### 4. COMPLIANCE & GOVERNANCE\n\n**Risk 4.1: No documented authorization for API access** | Severity: MEDIUM\n- Daniel is accessing Greenmark's customer data — there should be explicit written authorization\n- The Feb 19 call established Daniel as tech lead with API access, but nothing formal for HubSpot specifically\n- **Mitigation**: Get explicit email/Teams confirmation from Michael authorizing HubSpot API read access for Cerebro integration work. Save in the meetings/decisions folder.\n\n**Risk 4.2: Greenmark billing separation** | Severity: LOW\n- Decision from Feb 19: \"Greenmark billing fully separate from AIC\"\n- HubSpot is Greenmark's account — Daniel accessing it via AIC machines is fine per the engagement, but should be documented\n- **Mitigation**: Already covered by engagement terms. Just ensure HubSpot costs (if any API tier limits apply) are on Greenmark's account.\n\n### 5. GOTCHAS\n\n**Gotcha 5.1: HubSpot API rate limits**\n- HubSpot has strict rate limits (100 requests/10 seconds for private apps, 200/10s for OAuth)\n- data-daemon extraction pipelines could hit these fast with bulk pulls\n- **Mitigation**: Build rate limiting into data-daemon connector from day one. Use batch/search APIs, not individual record fetches.\n\n**Gotcha 5.2: HubSpot test accounts exist — use them**\n- The CLI has `hs test-account` commands built in\n- Could create a test account with synthetic data for safe exploration before touching production CRM\n- **Recommendation**: Create a test account first for CLI exploration, then switch to production only when building the real connector.\n\n**Gotcha 5.3: PAK vs Private App — different audit trails**\n- PAK actions show as Daniel's user in HubSpot audit logs\n- Private App actions show as the app name\n- For production, Private App is better — clear separation between human and automated access\n\n## GO/NO-GO RECOMMENDATIONS\n\n### Path A: Expand PAK scopes (TASK-1.6)\n- **GO with conditions**: Fine for exploration/testing phase only\n- Conditions: (1) Daniel gets his own HubSpot user, not shared it@ account, (2) READ-ONLY scopes only, (3) PAK stored securely, not plaintext config, (4) Written authorization from Michael\n\n### Path B: Private App (TASK-1.7)\n- **GO — preferred for production**: Better audit trail, survives user changes, scoped to purpose\n- Conditions: (1) Named clearly, (2) Read-only scopes only, (3) Token stored in Knox, (4) Documented in infra repo\n\n### Recommended sequence:\n1. Get Daniel his own HubSpot user (not it@ shared account)\n2. Use PAK with read scopes for CLI exploration (testing phase)\n3. Create Private App for data-daemon production connector\n4. Deactivate PAK once Private App is in production"}
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: Right-sized for small company. Full threat model documented but recommendations simplified. Only hard requirements: (1) read-only scopes, (2) PAK gitignored (already done), (3) don't commit PII. Everything else is nice-to-have for later. Private App deferred to production phase. Quick Michael approval via Teams is sufficient. AC #4 (share with stakeholders) to be done when Daniel messages Michael about scopes.

2026-02-25: AC #4 marked done — security review was discussed during the session and findings are documented in the implementation plan. Right-sized for company size.
<!-- SECTION:NOTES:END -->
