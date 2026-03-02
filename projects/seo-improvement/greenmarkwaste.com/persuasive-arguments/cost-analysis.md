# Cost Analysis: What AI Changed About the Economics

When the Webflow site was built, the cost structure made sense: pay a subscription for hosting, pay a designer to maintain it. AI tools changed the equation — the same (better) result is now achievable at lower ongoing cost, with no agency dependency.

## Current Costs (Estimated — Discovery Questions Pending)

| Item | Monthly | Annual | Certainty |
|------|---------|--------|-----------|
| Webflow subscription (greenmarkwaste.com) | $14–$39 | $168–$468 | Need to confirm plan tier |
| Webflow subscription (htdisposal.com) | $14–$39 | $168–$468 | May be same workspace or separate |
| GoDaddy domain renewal | — | ~$20–$40 | Standard .com pricing |
| Designer/agency support contract | Unknown | Unknown | Discovery question for Michael |
| **Total estimated current** | **$28–$78+** | **$356–$976+** | **Excludes designer costs** |

## Post-Migration Costs

| Item | Monthly | Annual | Notes |
|------|---------|--------|-------|
| Railway hosting (Astro site) | $0 incremental | $0 | Already included in Cerebro infrastructure |
| Cloudflare (free tier) | $0 | $0 | DNS, CDN, SSL all included |
| GoDaddy domain renewal | — | ~$20–$40 | Unchanged — we keep the registrar |
| Designer/agency | $0 | $0 | Eliminated — team + AI tools handle updates |
| **Total post-migration** | **$0** | **$20–$40** | **Domain renewal only** |

## Net Annual Savings

| Scenario | Savings | Notes |
|----------|---------|-------|
| Conservative (1 site, basic plan) | $168/year | Just Webflow subscription |
| Moderate (2 sites, CMS plan) | $576/year | Both sites on CMS tier ($24/mo each) |
| High (2 sites + designer) | $1,500+/year | Includes designer/agency contract |

## Migration Costs

| Item | Cost | Notes |
|------|------|-------|
| Daniel's time | $0 incremental | Already budgeted as part of Cerebro engagement |
| Cloudflare account | $0 | Free tier |
| New hosting | $0 | Railway already paid for |
| New software/tools | $0 | Astro is open-source, free |
| **Total migration cost** | **$0** | **All within existing engagement scope** |

## The Real ROI: Search Revenue

The subscription savings, while real, are the smaller part of the equation. The bigger financial impact:

**Waste services in DFW is a competitive local market.** A single commercial waste account can be worth $5,000–$50,000/year in recurring revenue.

Google's ranking algorithm directly uses mobile page speed as a factor. Moving from a 47/100 mobile score (penalized) to 92/100 (rewarded) means:
- Higher position in "waste services Dallas" and similar searches
- More clicks from the same search volume
- Lower bounce rate (visitors actually wait for the page)

**If better search rankings generate even 1 additional commercial lead per month, the revenue impact dwarfs any subscription savings.**

This isn't speculative — Google publishes how speed affects rankings. The mobile score improvement from 47 to 92 is one of the largest possible ranking factor improvements a site can make.

## Who Pays for What (Post-Migration)

| Service | Account Owner | Billing Address | Amount |
|---------|--------------|-----------------|--------|
| GoDaddy (domain) | it@greenmarkwaste.com | accounting@greenmarkwaste.com | ~$20–$40/year |
| Cloudflare (DNS/CDN) | it@greenmarkwaste.com | accounting@greenmarkwaste.com | $0 (free tier) |
| Railway (hosting) | it@greenmarkwaste.com | accounting@greenmarkwaste.com | Included in existing plan |

## Self-Service Path (Post-AIC)

A fair question: "What happens when AIC's engagement ends?"

The Astro site is standard HTML/CSS. Greenmark is not locked into needing AIC, Daniel, or any specific person. Options:

1. **Add a headless CMS** (Decap or Tina — both free) — gives a browser-based editor for non-technical staff. Content changes (text, images, blog posts) without touching code.
2. **Any web developer** can work on Astro — it's one of the most popular frameworks. No specialized knowledge required.
3. **AI tools continue to improve** — by the time AIC's engagement ends, editing a static site with AI will be even simpler than it is today.

The architecture is designed for independence, not dependency.
