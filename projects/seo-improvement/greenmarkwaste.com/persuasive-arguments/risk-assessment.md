# Risk Assessment: Website Modernization

Every risk identified, rated, and mitigated — including the risk of standing still while the goalposts move.

## Risk Matrix

| # | Risk | Likelihood | Impact | Mitigation | Residual Risk |
|---|------|-----------|--------|------------|---------------|
| 1 | Domain expires before we get access (Aug 2026) | Low | Critical | Step 1 of discovery: confirm auto-renewal. 5 months of runway. | Very Low |
| 2 | Unknown party controls GoDaddy, refuses transfer | Very Low | High | Greenmark is the domain registrant. Legal recourse exists. Michael can compel cooperation. | Negligible |
| 3 | Designer/agency has questions about ownership change | Low | Low | This is a standard account centralization — not removing anyone. Designer keeps editor access. We're adding Greenmark as owner, not taking away their tools. | Negligible |
| 4 | DNS migration causes brief downtime | Very Low | Medium | Cloudflare migration is zero-downtime by design. DNS points to Webflow first, then switches. | Very Low |
| 5 | Astro site has issues after cutover | Low | Medium | Instant rollback: change one Cloudflare DNS record back to Webflow. Takes effect in minutes. | Low |
| 6 | Forms break during migration (leads lost) | Medium | High | Discovery: identify all forms and backends before cutover. Rebuild in Astro. Test before DNS switch. | Low |
| 7 | htdisposal.com is on a different platform entirely | Medium | Low | If separate, handle as a follow-on. Doesn't block greenmarkwaste.com. | Low |
| 8 | Michael is too busy to answer discovery questions | Medium | Medium | Email is async. 15-min call offered. Most answers are quick lookups ("who owns this account?"). | Low |
| 9 | Google rankings temporarily dip during cutover | Low | Medium | Same URLs, same content, faster speed. Google typically rewards speed improvements within days. Add 301 redirects for any URL changes. | Low |
| 10 | Astro requires technical skills that Greenmark staff don't have | Low | Low | Updates are done by Daniel + AI tools. If Greenmark wants self-service later, a headless CMS can be added without changing the architecture. | Very Low |

## The Biggest Risk: Doing Nothing

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Unknown party controls domain, could transfer or let expire | **Certain** (true today) | Critical | Centralize accounts — this plan |
| Mobile speed penalty continues suppressing search rankings | **Certain** (true today) | High | Replace Webflow with Astro — this plan |
| Competitors with faster sites rank above Greenmark | **High** | High | Performance improvement — this plan |
| No visibility into designer/agency relationship (cost, contract terms) | **High** | Medium | Discovery questions + account centralization — this plan |
| No visibility into what's happening with the domain or hosting | **Certain** (true today) | Medium | Account centralization — this plan |

**The status quo is not a safe default.** The Webflow site served Greenmark well, but the landscape has shifted. Standing still now means:
- An unknown party controls Greenmark's primary web domain
- Google's speed requirements keep tightening — the penalty gets worse, not better
- Every month, potential customers find competitors first
- The domain could lapse in August 2026 if nobody monitors it
- AI tools have made a better option accessible — the opportunity cost of not using them grows over time

## Rollback Plan

If anything goes wrong at any stage:

| Phase | Rollback Action | Time to Recover |
|-------|----------------|-----------------|
| DNS migration (Webflow → Cloudflare → Webflow) | Revert GoDaddy nameservers | 1–24 hours (DNS propagation) |
| Cutover (Cloudflare → Railway) | Change one CNAME record in Cloudflare back to Webflow | Minutes (Cloudflare's low TTL) |
| Post-cutover issues | Same — one DNS record change | Minutes |

The Webflow site is never deleted during this process. It remains intact and available as a fallback until explicitly decommissioned in Phase 6, which only happens after 2+ weeks of stable Astro operation.

## Insurance Measures

1. **Cloudflare as intermediary** — Gives us instant DNS switching without touching the registrar
2. **Webflow stays live** — Not cancelled until Astro is proven stable
3. **GA4 + Search Console** — Monitoring from day one catches ranking issues immediately
4. **Phase-gated approach** — Each phase requires the previous to be complete and verified
5. **Michael approval gate** — The cutover doesn't happen until Michael reviews and approves the new site
