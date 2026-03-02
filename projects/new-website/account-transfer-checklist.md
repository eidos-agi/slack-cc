# Account Transfer Checklist — Domain & Hosting

All accounts should be owned by `it@greenmarkwaste.com` with billing sent to `accounting@greenmarkwaste.com`. This follows the same pattern used for Railway, Supabase, and GitHub (Tasks 78–81).

---

## GoDaddy (Registrar + DNS)

greenmarkwaste.com is registered at GoDaddy. Domain expires **Aug 1, 2026**.

| # | Action | Who | Depends On | Done |
|---|--------|-----|------------|------|
| 1 | Identify who owns the GoDaddy account (email on file) | Michael | — | [ ] |
| 2 | Add `it@greenmarkwaste.com` as delegate/admin on the GoDaddy account | Current owner | Step 1 | [ ] |
| 3 | Transfer full account ownership to `it@greenmarkwaste.com` | Current owner + Daniel | Step 2 | [ ] |
| 4 | Update billing to `accounting@greenmarkwaste.com` | Daniel | Step 3 | [ ] |
| 5 | Verify Daniel can manage DNS records (A, CNAME, NS records) | Daniel | Step 2 | [ ] |
| 6 | Verify domain auto-renewal is ON | Daniel | Step 2 | [ ] |
| 7 | Check if htdisposal.com is on the same account — if so, include in transfer | Daniel | Step 2 | [ ] |

**Risk:** If domain expires Aug 2026 without renewal, the website goes down. Priority is getting access and confirming auto-renewal is enabled.

---

## Webflow (Hosting + CMS)

greenmarkwaste.com is currently hosted on Webflow. Daniel has editor access (Task-46, credentials in LastPass).

| # | Action | Who | Depends On | Done |
|---|--------|-----|------------|------|
| 1 | Identify the Webflow workspace owner (check LastPass or ask Michael) | Daniel | — | [ ] |
| 2 | Change workspace owner email to `it@greenmarkwaste.com` | Current owner | Step 1 | [ ] |
| 3 | Update billing to `accounting@greenmarkwaste.com` | Daniel | Step 2 | [ ] |
| 4 | Audit who else has access (editors, designers, agencies) | Daniel | Step 2 | [ ] |
| 5 | Document Webflow plan tier and monthly cost | Daniel | Step 2 | [ ] |
| 6 | Check if htdisposal.com uses the same workspace or a separate one | Daniel | Step 2 | [ ] |

**Note:** Webflow stays live until the Astro replacement is fully deployed and verified at greenmarkwaste.com. Do not cancel the Webflow subscription until cutover is complete.

---

## Cloudflare (New — DNS/CDN Layer)

Cloudflare sits between GoDaddy (registrar) and Railway (hosting). It gives us DNS management, CDN caching, SSL, and DDoS protection — all free tier.

| # | Action | Who | Depends On | Done |
|---|--------|-----|------------|------|
| 1 | Create Cloudflare account under `it@greenmarkwaste.com` | Daniel | — | [ ] |
| 2 | Add greenmarkwaste.com to Cloudflare | Daniel | Step 1 | [ ] |
| 3 | Change GoDaddy nameservers to Cloudflare's assigned NS records | Daniel | GoDaddy Step 5 + Step 2 | [ ] |
| 4 | Configure DNS: initially point to Webflow (no downtime) | Daniel | Step 3 | [ ] |
| 5 | When Astro is ready: update DNS to point to Railway | Daniel | Step 4 + Astro build complete | [ ] |
| 6 | Update billing to `accounting@greenmarkwaste.com` (if upgrading from free) | Daniel | Step 1 | [ ] |
| 7 | Add htdisposal.com to Cloudflare (if applicable) | Daniel | Step 1 | [ ] |

**Why Cloudflare?** Free DNS management is faster and more reliable than GoDaddy's. Also gives us CDN, SSL certificates, and the ability to switch hosting targets (Webflow → Railway) with a single DNS record change instead of touching GoDaddy each time.

---

## Cutover Sequence (When Astro Is Ready)

This is the order of operations for the final switch:

1. All Astro pages built and verified on Railway staging URL
2. GA4 and Google Search Console configured on Astro site
3. SSL certificate provisioned for greenmarkwaste.com on Railway
4. Update Cloudflare DNS: CNAME `greenmarkwaste.com` → Railway endpoint
5. Verify site loads correctly at greenmarkwaste.com (check all pages, forms, redirects)
6. Monitor for 48 hours — watch for broken links, SEO ranking changes, form submissions
7. Michael confirms he's happy with the new site
8. Cancel Webflow subscription

**Rollback plan:** If issues arise after cutover, change Cloudflare DNS back to Webflow's IP. Takes effect within minutes (Cloudflare's TTL is low by default). Webflow site stays intact and available as a safety net until everyone is confident in the new site.
