---
id: TASK-0048
title: First dogfood run on staging Cerebro
status: To Do
created: '2026-04-13'
priority: high
milestone: 'M-08: cerebro-verifier — Learning QA System'
tags:
  - verifier
  - dogfood
  - exploration
dependencies:
  - Prove auth flow works end-to-end in browser
acceptance-criteria:
  - dogfood skill runs against staging
  - Structured report with screenshots produced
  - Issues categorized by severity
  - Financial and Executive pages explored with data verification
updated: '2026-04-17'
---
Run agent-browser dogfood skill against staging Cerebro. Explore the dashboard pages, capture screenshots, find issues. This is the first exploratory pass — the raw material that the learning layer will crystallize into regression checks.


**Session 32 partial progress (2026-04-18):**

Ran agent-browser against staging. Confirmed:
- ✅ Staging is up and rendering (STAGING — DEV, BUILT 6H AGO)
- ✅ lucide-react 1.8.0 deployed correctly — GitHub icon on SSO button renders fine
- ✅ Login page functional: email/password form, GitHub SSO, Microsoft SSO (disabled)
- ✅ "15 INTERCONNECTED SYSTEMS" counter visible
- ✅ Screenshots saved to tools/agent-browser/sessions/dogfood-001/
- ❌ Cannot get past login — no test account creds available
- ❌ Persistent Browserbase context (870a8efe) is for production, not staging, and may be expired

**Still blocked on:** Daniel setting up a test viewer account or sharing staging creds.
