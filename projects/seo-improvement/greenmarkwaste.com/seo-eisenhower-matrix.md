# SEO Eisenhower Matrix — greenmarkwaste.com

*Created 2026-02-28. Covers on-site, off-site, and external actions.*

**Counterfactual framing:** For each factor, ask: "If a competitor does this and we don't, what do we lose?" The factors that cost us the most by omission go in Q1.

---

## Q1: Urgent + Important (Do First)

These are active liabilities — every day without them costs rankings, visibility, or data.

### 1. GA4 + Google Search Console Setup
- **Status:** Missing
- **Counterfactual:** Every day without tracking = lost baseline data. When we eventually rank, we won't know what drove it. Can't measure ROI of any SEO work. Can't see crawl errors, indexing issues, or search queries.
- **Blocked on:** Alex providing access / confirming if accounts exist
- **Effort:** Small (once unblocked)
- **Backlog:** TASK-47

### 2. Google Business Profile Optimization
- **Status:** Partial (listing exists, not optimized)
- **Counterfactual:** Competitors with optimized GBP show up in the Maps 3-pack for "dumpster rental Dallas." We don't. The 3-pack appears ABOVE organic results — this is where phone calls come from. A competitor with 50+ reviews, full service catalog, weekly posts, and 20 photos will bury us regardless of website speed.
- **What's needed:** Complete every field, add all services as "Products" with photos, upload 20+ job site photos, populate Q&A with the 28 FAQs, respond to all reviews, start weekly GBP posts
- **Blocked on:** GBP login credentials from Alex/Michael
- **Effort:** Medium (once unblocked, then ongoing)
- **Backlog:** TASK-48

### 3. Build Interior Pages (Astro)
- **Status:** Only homepage exists. 8+ footer/nav links go to 404s.
- **Counterfactual:** Google can't rank pages that don't exist. A competitor with dedicated /roll-off-dumpsters, /commercial-dumpsters, /portable-restrooms pages will rank for those service keywords. We literally cannot compete on any non-brand query without pages.
- **What's needed:** Port Webflow content to Astro pages: 4 service pages, FAQ, about, contact, request-services
- **Effort:** Large
- **Backlog:** None yet

### 4. Structured Data / JSON-LD Schema
- **Status:** Missing on Astro site
- **Counterfactual:** Competitors with LocalBusiness + Service + FAQPage schema get rich snippets — expandable FAQs, star ratings, business hours, service catalogs directly in search results. Higher CTR on the same ranking position. We show up as a plain blue link.
- **What's needed:** LocalBusiness (or WasteManagementService), Organization, Service per service type, FAQPage on FAQ content
- **Effort:** Medium
- **Backlog:** None yet

### 5. Canonical Tags
- **Status:** Missing
- **Counterfactual:** Three URLs serve overlapping content right now (greenmarkwaste.com via Webflow, gmw-dot-com-production.up.railway.app, and soon gm2026.jettaintelligence.com). Without canonicals, Google may index the wrong one or dilute authority across all three.
- **What's needed:** `<link rel="canonical" href="https://www.greenmarkwaste.com/{path}" />` in Layout.astro
- **Effort:** Small (5 min)

### 6. XML Sitemap
- **Status:** robots.txt references a sitemap that doesn't exist (404)
- **Counterfactual:** Google crawls blind. New pages take longer to get indexed. A 404 sitemap reference is worse than no robots.txt at all — it signals a broken site.
- **What's needed:** `@astrojs/sitemap` integration (5-min install)
- **Effort:** Small
- **Backlog:** None yet

---

## Q2: Not Urgent + Important (Schedule)

These compound over time. A competitor who starts these today will have an advantage 90 days from now.

### 7. Service Area Pages (City-Specific Landing Pages)
- **Status:** Missing
- **Counterfactual:** "Dumpster rental Plano TX", "roll-off Fort Worth", "portable restrooms Arlington" — these are high-intent local searches. Competitors like American AF Dumpsters have individual pages per city per county. Without city pages, we lose every geo-modified search to whoever does have them. This is the #1 organic traffic growth lever for local service businesses.
- **What's needed:** Unique (not template-swapped) pages for top 5-8 DFW cities: Dallas, Fort Worth, Plano, Arlington, Frisco, Irving, McKinney, Garland. 500+ words unique content each.
- **Effort:** Large
- **Depends on:** Interior pages built first (#3)

### 8. FAQ Schema Markup (FAQPage)
- **Status:** 28 FAQs exist on Webflow but no schema
- **Counterfactual:** FAQ rich results are the easiest way to dominate SERP real estate. A competitor with FAQ schema takes up 3-4x the visual space in search results. Our 28 well-organized FAQs are wasted without the markup.
- **What's needed:** FAQPage JSON-LD on any page with FAQ content
- **Effort:** Small (once FAQ page is built)
- **Depends on:** Interior pages (#3)

### 9. Review Generation System
- **Status:** 5 testimonials on about page, some Yelp reviews, no systematic process
- **Counterfactual:** Reviews are a top-3 local pack ranking factor. A competitor who asks every customer for a Google review will accumulate 50+ reviews in 90 days. We won't. Reviews also build social proof that directly affects conversion rate — a prospect choosing between two dumpster companies picks the one with 4.8 stars and 87 reviews over the one with 4 reviews.
- **What's needed:** Automated post-service review request (email/SMS via HubSpot), AggregateRating + Review schema on testimonials, respond to all existing reviews
- **Effort:** Medium (schema is small; review system is ongoing)

### 10. NAP Consistency + Citation Building
- **Status:** Unaudited. Listings exist on Yelp, AAGD, ZoomInfo, RocketReach.
- **Counterfactual:** Inconsistent NAP (Name, Address, Phone) across the web confuses Google and hurts local rankings. If our Yelp says one phone number and our GBP says another, both get penalized. Competitors with clean, consistent citations across 50+ directories rank higher in local pack.
- **What's needed:** Audit with BrightLocal or Whitespark. Ensure identical NAP across: GBP, Yelp, BBB, Yellow Pages, Apple Maps, Bing Places, Facebook, NWRA, SWANA, construction directories, DFW chambers.
- **Effort:** Medium

### 11. Backlink Profile + Directory Listings
- **Status:** Minimal. Yelp + AAGD + a few data aggregators.
- **Counterfactual:** A competitor who joins Dallas Regional Chamber, Fort Worth Chamber, NWRA, SWANA, TXSWANA, BBB, Angi, HomeAdvisor, and gets partner links from 10 general contractors has dramatically higher domain authority. We're starting from near zero. Every month without building links is a month the gap widens.
- **What's needed:** Chamber memberships, industry association listings, general directories (BBB, Angi, Thumbtack), partner outreach to GCs/roofers/property managers, sponsor local cleanups
- **Effort:** Large (ongoing)

### 12. Blog / Content Marketing
- **Status:** No blog on either site
- **Counterfactual:** "What size dumpster do I need?" gets thousands of monthly searches. The company that answers it ranks for it. Informational content builds topical authority, generates backlinks, and captures top-of-funnel traffic. Competitors like Frontier Waste have resource sections. We have nothing.
- **What's needed:** Astro content collection for `/blog`, start with 2-4 high-intent articles, 1-2 posts/month cadence
- **Effort:** Large (infrastructure small, content creation ongoing)
- **SEO plan identifies starters:** "What Size Dumpster Do I Need?" and "What Can/Can't Go in a Roll-Off Dumpster"

### 13. Open Graph + Twitter Card Meta Tags
- **Status:** Missing
- **Counterfactual:** Every time someone shares the site on LinkedIn, Facebook, or Slack, it shows a broken/empty preview. For a B2B waste company, LinkedIn shares from property managers and construction PMs matter. A competitor whose link unfurls with a professional image and description looks legitimate; ours looks broken.
- **What's needed:** og:title, og:description, og:image, og:url, twitter:card tags in Layout.astro
- **Effort:** Small

---

## Q3: Urgent + Not Important (Delegate)

Quick fixes that improve hygiene but don't move the needle alone.

### 14. Security Headers (nginx)
- **Status:** Partial (X-Frame-Options and X-Content-Type-Options in nginx.conf, but missing HSTS and CSP)
- **Counterfactual:** Not a direct ranking factor. Enterprise buyers sometimes run security scans on vendors. Missing HSTS is a flag. PageSpeed Best Practices deduction (96 not 100) is partly this.
- **What's needed:** Add HSTS, CSP headers to nginx.conf
- **Effort:** Small (5 min)

### 15. Registrar / DNS Identification
- **Status:** Unknown who controls greenmarkwaste.com and htdisposal.com DNS
- **Counterfactual:** Can't point domains at new infrastructure, can't set up email authentication (DMARC/SPF/DKIM), can't add CNAME records for Railway custom domain.
- **What's needed:** Ask Alex/Michael who the registrar is
- **Effort:** Small (just a question)
- **Backlog:** TASK-37, TASK-38

---

## Q4: Not Urgent + Not Important (Deprioritize)

### 16. /seo-audit and /seo-weekly Skills
- These are automation skills (TASK-51, TASK-53) — useful for ongoing monitoring but premature until baseline audits are done and there's enough data flowing through GA4/GSC to analyze.

---

## Existing Backlog Tasks (SEO-related)

| Task | Title | Status | Quadrant |
|------|-------|--------|----------|
| TASK-46 | Get Webflow editor access | **Done** | — |
| TASK-47 | Verify GSC + GA4 setup | To Do | Q1 (#1) |
| TASK-48 | Verify Google Business Profile | To Do | Q1 (#2) |
| TASK-49 | Run baseline SEO audit — greenmarkwaste.com | To Do | Q1 (depends on TASK-47) |
| TASK-50 | Run baseline SEO audit — htdisposal.com | To Do | Q2 |
| TASK-51 | Build /seo-audit skill | To Do | Q4 |
| TASK-52 | Fix critical technical SEO issues | To Do | Q1 (depends on audits) |
| TASK-53 | Build /seo-weekly skill | To Do | Q4 |
| TASK-37 | Identify registrar — greenmarkwaste.com | To Do | Q3 |
| TASK-38 | Identify registrar — htdisposal.com | To Do | Q3 |
| TASK-4 | SEO + AIO baseline audits (both sites) | To Do | Superseded by TASK-49/50 |

---

## Execution Sequence (Recommended)

**This week (quick wins, unblock dependencies):**
1. Canonical tags + XML sitemap + Open Graph tags → one commit
2. Structured data (LocalBusiness JSON-LD) on homepage → one commit
3. Security headers → one commit
4. Email Alex: need GA4/GSC access + GBP credentials + registrar info

**Next sprint (build foundation):**
5. Build interior pages in Astro (services, FAQ, about, contact)
6. Add FAQPage schema once FAQ page exists
7. Set up GA4 + GSC (once Alex provides access)
8. Submit sitemap to GSC

**Phase 2 (content + local):**
9. Service area city pages (Dallas, Fort Worth, Plano, Arlington, Frisco...)
10. GBP full optimization (once credentials received)
11. NAP audit + citation cleanup
12. Blog infrastructure + first 2 articles

**Phase 3 (authority + ongoing):**
13. Review generation system
14. Backlink building (chambers, associations, partner outreach)
15. Content cadence (1-2 blog posts/month)
16. Weekly SEO monitoring (GA4 + GSC → eventually automate with skills)
