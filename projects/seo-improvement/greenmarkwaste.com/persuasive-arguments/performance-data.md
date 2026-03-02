# Performance Data: How AI Changed What's Possible

## The Story

When the Webflow site was built, its performance was typical for the platform — and Webflow was a reasonable choice. Since then, Google tightened its mobile speed requirements (Core Web Vitals became a direct ranking signal in 2021), and AI tools made it possible to build sites at a performance level that previously required a specialized web agency.

## Source

All data from Google PageSpeed Insights (Lighthouse). Tests run during the SEO improvement project (Feb 2026). Tests run against:
- **Webflow:** greenmarkwaste.com (live production)
- **Astro:** gmw-dot-com-production.up.railway.app (deployed replacement)

## The Numbers

| Metric | Webflow (Current) | Astro (Replacement) | Change |
|--------|-------------------|---------------------|--------|
| **Mobile Speed Score** | 47 / 100 (Poor) | 92 / 100 (Good) | +96% improvement |
| **Desktop Speed Score** | ~70 / 100 | 99 / 100 | +41% improvement |
| **Largest Contentful Paint (LCP)** | 17.5 seconds | 2.7 seconds | 6.5x faster |
| **Cumulative Layout Shift (CLS)** | Unknown (high) | 0.001 (excellent) | Near-zero layout shift |
| **Total Blocking Time (TBT)** | Unknown | 0 ms (perfect) | No JavaScript blocking |

## What These Metrics Mean

### Mobile Speed Score (47 → 92)
Google assigns a score from 0–100 based on real-world mobile user experience. Scores are categorized:
- **0–49: Poor** (red) — Google penalizes rankings
- **50–89: Needs Improvement** (orange)
- **90–100: Good** (green) — Google rewards rankings

Greenmark's Webflow site is in the **Poor** category. The Astro replacement is in the **Good** category. This is a direct input to Google's ranking algorithm.

### Largest Contentful Paint / LCP (17.5s → 2.7s)
LCP measures how long it takes for the main content to appear on screen. Google's thresholds:
- **Good:** under 2.5 seconds
- **Needs Improvement:** 2.5–4.0 seconds
- **Poor:** over 4.0 seconds

The Webflow site takes **17.5 seconds** — nearly 4.5x over the "Poor" threshold. The Astro site loads in **2.7 seconds**, just above the "Good" threshold.

At 17.5 seconds, most visitors have already left. Industry data shows:
- 53% of mobile visits are abandoned if a page takes over 3 seconds to load (Google, 2018)
- Bounce rate increases 32% as page load time goes from 1s to 3s (Google)
- At 10+ seconds, the probability of bounce increases by 123%

### Why Webflow's Speed Can't Be Fixed (It's the Platform, Not the Design)
Webflow generates its own HTML, CSS, and JavaScript. This was fine when speed expectations were lower. The site owner has no control over:
- How many CSS/JS files are loaded
- The render-blocking behavior of those files
- Image optimization and lazy loading strategies
- The HTML structure and DOM size

This is a **platform limitation**, not a design flaw. Whoever built the Webflow site made a good-looking, functional website. The speed gap is about the platform's architecture, not the designer's work.

### Why Astro Is Fast (and Why This Wasn't Accessible Before)
Astro generates static HTML at build time — no JavaScript framework runs in the browser by default. Pages are pre-rendered HTML + CSS files served directly by the CDN. This is the fastest possible delivery method for a website.

Building this way used to require a dedicated frontend developer. AI tools changed that — they can generate, modify, and maintain Astro components at a level that makes the "hire an agency" step unnecessary for a team like Greenmark's.

## How to Verify These Numbers

Anyone can check:
1. Go to https://pagespeed.web.dev/
2. Enter `greenmarkwaste.com` → see Webflow scores
3. Enter `gmw-dot-com-production.up.railway.app` → see Astro scores
4. Compare

The data speaks for itself.
