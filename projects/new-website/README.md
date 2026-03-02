# New Website — greenmarkwaste.com

## Overview

Replace the current Webflow site with a high-performance Astro build, centralize domain and hosting accounts under `it@greenmarkwaste.com`, and eliminate third-party designer dependency.

## Current State

| Item | Status |
|------|--------|
| **Webflow site** | Live at greenmarkwaste.com. Mobile score 47/100, LCP 17.5s. Last published Feb 28, 2026 |
| **Astro replacement** | Homepage built and deployed on Railway. Mobile 92/100, LCP 2.7s. Repo: `gmw-dot-com-astro` |
| **GoDaddy (registrar)** | Domain registered, account owner unknown. Expires Aug 1, 2026 |
| **Webflow (hosting)** | Daniel has editor access (Task-46). Workspace ownership unknown |
| **Cloudflare** | Not yet set up. Planned as DNS/CDN layer between GoDaddy and Railway |

## Goals

1. **Centralize accounts** — GoDaddy, Webflow, and a new Cloudflare account all owned by `it@greenmarkwaste.com`, billing to `accounting@greenmarkwaste.com`
2. **Complete Astro build** — Remaining pages: about, services, FAQs, contact, service-area city pages
3. **Cut over DNS** — GoDaddy nameservers → Cloudflare → Railway (Astro)
4. **Wind down Webflow** — Cancel subscription once Astro is live, verified, and Michael approves

## Key Dates

- **Aug 1, 2026** — greenmarkwaste.com domain expires at GoDaddy. Must ensure auto-renewal is on.
- **Astro cutover** — Target TBD, depends on remaining page build + Michael's approval

## Deliverables in This Folder

| File | What It Is |
|------|-----------|
| [account-transfer-checklist.md](account-transfer-checklist.md) | Step-by-step transfer plan for GoDaddy + Webflow + Cloudflare |
| [discovery-questions.md](discovery-questions.md) | Questions for Michael about Webflow history and GoDaddy access |
| [email-draft.md](email-draft.md) | Ready-to-send email to Michael requesting access and answers |

## Related Work

- **SEO improvement project** — [projects/seo-improvement/](../seo-improvement/) — 90-day SEO plans for both sites
- **Astro site repo** — [gmw-dot-com-astro](https://github.com/greenmark-waste-solutions/gmw-dot-com-astro)
- **Account ownership policy** — [Task-92](../../backlog/tasks/task-92%20-%20Enforce-account-ownership-policy-across-all-vendors.md) — approved by Alex Kaye, Feb 27, 2026
- **Previous transfer tasks** — Tasks 78–81 (Railway, Supabase, GitHub ownership transfers)

## Checklist

- [ ] Send email to Michael with discovery questions
- [ ] Get answers: GoDaddy owner, Webflow workspace owner, designer/agency info
- [ ] Transfer GoDaddy account to `it@greenmarkwaste.com`
- [ ] Transfer Webflow workspace to `it@greenmarkwaste.com`
- [ ] Set up Cloudflare account under `it@greenmarkwaste.com`
- [ ] Complete Astro pages (about, services, FAQs, contact)
- [ ] Build service-area city pages for DFW metro
- [ ] Set up GA4 + Google Search Console on Astro site
- [ ] DNS cutover: GoDaddy NS → Cloudflare → Railway
- [ ] Verify Astro site live at greenmarkwaste.com
- [ ] Wind down Webflow subscription (after Michael confirms he's happy with new site)
