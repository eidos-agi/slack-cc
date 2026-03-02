# SEO Improvement Project

**Status:** Active
**Owner:** Daniel Shanklin
**Requested by:** Stakeholder call, Feb 19, 2026 — [meeting notes](../../meetings/2026-02-19-stakeholder-call/README.md)
**Target:** Improve SEO scores for both Greenmark websites

## Sites

| Site | Brand | Market | Focus |
|------|-------|--------|-------|
| [greenmarkwaste.com](greenmarkwaste.com/seo-plan.md) | Greenmark Waste Solutions | North Texas + Indiana | B2B: commercial hauling, construction, roll-off dumpsters |
| [htdisposal.com](htdisposal.com/seo-plan.md) | Hometown Disposal | Indiana | B2C: residential curbside, bulk pickup, dumpster rental |

Same parent company, separate brands, different markets. SEO strategies are parallel but tailored to each audience.

## Shared 90-Day Timeline

### Phase 1: Foundation (Days 1-30)
- [x] Run PageSpeed baseline on greenmarkwaste.com — Mobile: 47, Desktop: 85, LCP: 17.5s (2026-02-28)
- [ ] Run full baseline audits on both sites (Screaming Frog, Ahrefs/Semrush)
- [ ] Set up GA4 + Google Search Console for both domains
- [ ] Record baseline metrics (DA, keyword rankings, organic traffic, Core Web Vitals)
- [ ] Implement schema markup (LocalBusiness + Service) on both sites
- [ ] Optimize title tags and meta descriptions on both sites
- [ ] Fully optimize Google Business Profile listings for both brands
- [ ] Set up call tracking (CallRail or similar)

### Phase 2: Content (Days 31-60)
- [ ] Create dedicated service pages for each site (see individual plans)
- [ ] Create service area pages for top 5-10 cities per brand
- [ ] NAP audit and citation cleanup for both brands
- [ ] Publish first 2 blog posts per site

### Phase 3: Authority (Days 61-90)
- [ ] Join Chambers of Commerce in key service areas
- [ ] List in industry directories (waste management, construction, local)
- [ ] Launch partner outreach (contractors for Greenmark, realtors/HOAs for Hometown)
- [ ] Implement automated review request system for both brands
- [ ] Establish blog cadence (1-2 posts/month per site)
- [ ] First quarterly performance review against baseline

## Tools

| Tool | Purpose |
|------|---------|
| Google Analytics (GA4) | Traffic, conversions, user behavior |
| Google Search Console | Indexing, impressions, clicks, keyword data |
| Screaming Frog | Technical crawl audit |
| Ahrefs or Semrush | Keyword rankings, domain authority, backlinks, competitors |
| Google PageSpeed Insights | Core Web Vitals (LCP, INP, CLS) |
| CallRail (or similar) | Phone call tracking attribution |
| BrightLocal or Whitespark | NAP audit, citation building |

## KPIs

| Metric | Frequency | Tool |
|--------|-----------|------|
| GSC impressions + clicks | Weekly | Google Search Console |
| Top 10 keyword ranking changes | Weekly | Ahrefs/Semrush |
| Organic sessions + users | Monthly | GA4 |
| Leads from organic (forms + calls) | Monthly | GA4 + CallRail |
| GBP map views, website clicks, calls | Monthly | GBP Dashboard |
| Keywords in top 3 / top 10 / top 20 | Monthly | Ahrefs/Semrush |
| Domain authority / domain rating | Monthly | Ahrefs |

## Key Detail from Feb 19 Call
- Both sites built on **Webflow** (confirmed by Michael)
- AIC's website also on Webflow
- Claude sidebar can log into Webflow and make changes directly
- Michael: "This is low hanging fruit. That shouldn't take too long. That should be kind of at the top of the list."

## Change Log

| Date | Site | Change | Impact | Details |
|------|------|--------|--------|---------|
| 2026-02-28 | greenmarkwaste.com | Hero slider: lazy loading + responsive srcset | Mobile perf 47→49, LCP 17.5→12.5s, CLS regressed 0.176→0.203 | [Full changelog](greenmarkwaste.com/changelog.md) |

## Blockers

- [ ] Need access to existing GA/GSC accounts (if any) — ask Alex
- [x] Need Webflow login for both sites — have access via designer
- [ ] Need GBP login credentials for both brands
