# SEO Changelog — greenmarkwaste.com

All SEO-related changes to the Greenmark Waste Solutions website, with before/after data and reasoning.

---

## 2026-02-28: Hero Slider Performance Fix

### Baseline (PageSpeed Insights, pre-fix)

| Category | Mobile | Desktop |
|----------|--------|---------|
| Performance | **47** (red) | 85 (orange) |
| Accessibility | 100 | 100 |
| Best Practices | 81 | 81 |
| SEO | 100 | 100 |

Key mobile issues:
- **LCP: 17.5s** (Google wants < 2.5s) — hero slider images
- Render-blocking requests — est savings 3,360 ms
- Unused JavaScript — est savings 410 KiB
- Image delivery — est savings 239 KiB
- CLS: 0.176 (should be < 0.1)
- Font display — est savings 70 ms

Desktop LCP was 2.2s (passable). Google uses **mobile-first indexing**, so the 47 mobile score is what hurts rankings.

### Changes Made (in Webflow Designer)

**1. Lazy Loading on Slides 2–5**
- Changed loading from Eager → Lazy on RollOff, Front Load 2, Portable, MiniBins slider images
- Slide 1 (Front Load Services / "Commercial Dumpsters") stays Eager — it's the first visible content
- Eliminates ~800 KB of unnecessary image downloads on initial page load

**2. Enabled Responsive Images on All 5 Slides**
- Unchecked "Disable responsiveness" on all 5 slider images
- Before: full 3000x1000px source served to every device (including 375px phones)
- After: Webflow generates `srcset` with versions at ~500px, 800px, 1080px, 1600px, 2000px
- Mobile devices download the smallest version that fits the screen

### Post-Publish Results (PageSpeed, Feb 27 6:57 PM CST)

| Category | Before | After | Change |
|----------|--------|-------|--------|
| Performance | 47 | **49** | +2 |
| Accessibility | 100 | 100 | — |
| Best Practices | 81 | 81 | — |
| SEO | 100 | 100 | — |

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **LCP** | 17.5s | **12.5s** | **-5.0s** |
| FCP | — | 5.8s | — |
| CLS | 0.176 | **0.203** | +0.027 (worse) |
| TBT | — | 150ms | — |
| Speed Index | — | 5.8s | — |
| Render-blocking | 3,360ms | **1,950ms** | -1,410ms |

**Assessment:** LCP improved 5 seconds but still 10s above Google's 2.5s target. Score barely moved (47→49). CLS got worse — responsive images without explicit width/height cause layout shifts. The hero slider optimization alone isn't enough. Deeper fixes needed.

### Remaining Issues (from post-publish audit)

| Issue | Savings | Priority |
|-------|---------|----------|
| **Render-blocking requests** | 1,950 ms | High — biggest remaining LCP blocker |
| **Image elements missing width/height** | CLS fix | High — causing the CLS regression (0.176→0.203) |
| **Unused JavaScript** | 411 KiB | Medium |
| **Font display** | 110 ms | Medium |
| **Image delivery** | 239 KiB | Medium |
| **Unused CSS** | 37 KiB | Low |
| **Deprecated APIs** | 1 warning | Low |
| **Long main-thread tasks** | 4 found | Low |

### Hero Slider Image Audit (live CDN, 2026-02-28)

All images are already AVIF format (Webflow auto-converts). Actual CDN sizes:

| Slide | Filename | CDN Size | CSS Class |
|-------|----------|----------|-----------|
| 0 | Front Load Services.avif | 282 KB | dtfl |
| 1 | Roll Off Services 2.avif | 197 KB | ro |
| 2 | Front-Load-Services-2.avif | 149 KB | — |
| 3 | Portable Services.avif | — | pp |
| 4 | mini Dumpsters Hero Image.avif | — | _15y |

All 5 are 3000x1000px. The 1971 KB figure from PageSpeed was the decoded/uncompressed memory size, not the transfer size. AVIF compression is already effective.

### What Was Considered But Not Needed
- Re-compressing the RollOff image — CDN already serves it at 197 KB (AVIF). No recompression needed.

### Where
Webflow Designer: [greenmark-waste.design.webflow.com](https://greenmark-waste.design.webflow.com/?workflow=canvas)

---

## 2026-02-28: Astro Rebuild — Deployed to Railway

### Why

Webflow's performance ceiling was too low. After optimizing everything available in Webflow Designer (lazy loading, responsive images), mobile performance only reached 49. The hero slider JS, render-blocking resources (1,950ms), unused JavaScript (411 KiB), and CLS issues were all baked into the Webflow runtime — unfixable without leaving the platform.

### What We Built

Rebuilt the homepage from scratch using **Astro + Tailwind v4**, deployed on **Railway** via nginx Docker container.

Architecture decisions:
- **CSS-only hero crossfade** — zero JS slider. `@keyframes heroFade` rotates 5 slides.
- **Static hero on mobile** — single image, no animation. Fastest possible mobile FCP.
- **All images AVIF** — extracted from Webflow export, resized and recompressed.
- **Async Google Fonts** — `media="print" onload="this.media='all'"` pattern eliminates render-blocking.
- **nginx serving static files** — multi-stage Docker build (Node builds, nginx serves).
- **Explicit width/height on every image** — CLS 0.001.

### v1 Results (first deploy, PageSpeed Mobile)

| Category | Webflow | Astro v1 | Change |
|----------|---------|----------|--------|
| Performance | 47 | **87** | **+40** |
| Accessibility | 100 | 98 | -2 |
| Best Practices | 81 | 96 | +15 |
| SEO | 100 | 92 | -8 |

| Metric | Webflow | Astro v1 | Change |
|--------|---------|----------|--------|
| LCP | 17.5s | **3.5s** | **-14.0s** |
| FCP | 5.8s | **2.7s** | **-3.1s** |
| CLS | 0.176 | **0.001** | **-0.175** |
| TBT | 150ms | **0ms** | **-150ms** |
| Speed Index | 5.8s | **2.7s** | **-3.1s** |

v1 issues flagged by PageSpeed:
- Image delivery: 221 KiB savings possible (hero images were 3000px wide, only need 1600px)
- Render-blocking: 1,790ms (Astro CSS 150ms + Google Fonts 750ms)
- Missing `<main>` landmark
- robots.txt errors
- Incorrect aspect ratios on service card images (HTML said 600x400, images were 800x267)

### v2 Optimizations (same session)

Changes deployed:
1. **Async Google Fonts** — render-blocking fonts eliminated (750ms saved)
2. **Hero images resized** 3000px → 1600px and recompressed at q=55:
   - hero-front-load: 282 KB → 101 KB (64% smaller)
   - hero-rolloff: 197 KB → 53 KB
   - hero-commercial: 149 KB → 71 KB
   - hero-mini: 285 KB → 136 KB
3. **Service images recompressed** at q=55 (20-40% smaller)
4. **Aspect ratios fixed** — service card width/height matches actual 800x267
5. **`<main>` landmark** added for accessibility
6. **robots.txt** added
7. **Texas map** converted PNG → AVIF (10 KB → 6 KB)

v2 critical path: **2 requests, 199ms, 11 KiB total** — HTML + one CSS file. Nothing else blocks render.

### v3 Optimizations — Inline CSS (same session)

- Set `build.inlineStylesheets: 'always'` in astro.config.mjs
- CSS inlined into HTML `<style>` tag — no external CSS file at all
- Critical path: **1 request (HTML only)**
- FCP improved 2.7s → 1.6s

### v4 Optimizations — LCP Push (same session)

- Hero image recompressed q=55 → q=35 (101KB → 45KB) — behind 50% opacity overlay, invisible quality difference
- Added `<link rel="preload" as="image" type="image/avif" href="/images/hero-front-load.avif">` in `<head>`
- Browser starts fetching hero before parsing body HTML

### Final Results (PageSpeed, Feb 27 ~7:45 PM CST, multiple runs)

Scores stabilized at **95-96 mobile** with normal PageSpeed variance (±2 points per run).

| Metric | Webflow (baseline) | Astro final | Change |
|--------|-------------------|-------------|--------|
| LCP | 17.5s | **~2.8s** | **-14.7s** |
| FCP | 5.8s | **1.5s** | **-4.3s** |
| CLS | 0.176 | **0.001** | **-0.175** |
| TBT | 150ms | **0ms** | **-150ms** |
| Speed Index | 5.8s | **1.5s** | **-4.3s** |

LCP is the only metric not green (<2.5s). On simulated Slow 4G, any photo-based hero will hover around 2.7-2.9s. Would need CSS gradient or solid color hero to reliably hit <2.5s — not worth the design tradeoff.

### v2 Results (PageSpeed, Feb 27 7:35 PM CST)

**Mobile:**

| Category | Webflow | Astro v1 | Astro v2 | Change (from Webflow) |
|----------|---------|----------|----------|----------------------|
| Performance | 47 | 87 | **92** | **+45** |
| Accessibility | 100 | 98 | **100** | — |
| Best Practices | 81 | 96 | 96 | +15 |
| SEO | 100 | 92 | **100** | — |

| Metric | Webflow | Astro v1 | Astro v2 | Change |
|--------|---------|----------|----------|--------|
| LCP | 17.5s | 3.5s | **2.7s** | **-14.8s** |
| FCP | 5.8s | 2.7s | **2.7s** | **-3.1s** |
| CLS | 0.176 | 0.001 | **0.001** | **-0.175** |
| TBT | 150ms | 0ms | **0ms** | **-150ms** |
| Speed Index | 5.8s | 2.7s | **2.7s** | **-3.1s** |

**Desktop:**

| Category | Score |
|----------|-------|
| Performance | **99** |
| Accessibility | **100** |
| Best Practices | 96 |
| SEO | **100** |

| Metric | Desktop |
|--------|---------|
| LCP | **0.9s** |
| FCP | **0.7s** |
| CLS | 0.004 |
| TBT | 0ms |
| Speed Index | 0.7s |

Only render-blocking item: one 5.5 KiB CSS file (170ms). Google Fonts fully async. Remaining flag: "images with incorrect aspect ratio" (Best Practices deduction) — likely the service cards in their CSS aspect-ratio containers.

### Deployment

- **Repo:** `greenmark-waste-solutions/gmw-dot-com-astro` (private)
- **Railway service:** `gmw-dot-com` in Greenmark Waste project
- **Railway domain:** https://gmw-dot-com-production.up.railway.app
- **Custom domain:** `gm2026.jettaintelligence.com` (pending DNS CNAME: `gm2026` → `3kvk2aoh.up.railway.app`)
- **Stack:** Astro 5.17 + Tailwind 4.2 + nginx:alpine

### What's Not Built Yet

Only the homepage is built. The Webflow export contains HTML for all pages:
- about-us, roll-off-dumpsters, commercial-dumpsters, portable-restrooms, mini-dumpsters
- faqs, contact-us, request-services, residential
- holiday-schedule, recycling-schedule, checkout

These would need to be built as Astro pages to fully replace Webflow.

---

## Next Actions (Performance)

To get from 49 → 80+ on mobile, the next fixes in priority order:

1. **Add explicit width/height to all slider images** — fixes the CLS regression. In Webflow, set dimensions on each image element.
2. **Reduce render-blocking resources** — 1,950ms of blocking. Defer non-critical CSS/JS. May need Webflow custom code or a plugin.
3. **Reduce unused JavaScript** — 411 KiB. Audit which Webflow interactions/third-party scripts are loading but not needed.
4. **Font loading** — add `font-display: swap` via Webflow custom code head.
5. **Consider replacing the slider with a static hero on mobile** — sliders are inherently heavy. A single static image on mobile would massively reduce LCP.

---

## SEO Context

### Why This Matters
- Google uses mobile-first indexing — the 49 mobile score directly hurts search rankings
- SEO score is 100/100 on both mobile and desktop — Webflow setup is solid, the problem is purely performance
- For a DFW service business, local SEO signals + page speed are the two biggest levers

### Timeline Expectations
- Ranking changes from a new Webflow build typically take ~90 days (Google's Rank Transition Algorithm)
- Meaningful traffic gains for local businesses: 3–6+ months on competitive terms (waste, dumpsters, roll-off in DFW)

### Next Steps (from SEO plan)
- [x] Publish Webflow changes and rerun PageSpeed — done, 47→49, LCP 17.5→12.5s
- [ ] Fix CLS regression (add image dimensions)
- [ ] Address render-blocking resources
- [ ] Set up GA4 + Google Search Console for both domains
- [ ] Run baseline audit (Screaming Frog, Ahrefs/Semrush)
- [ ] Implement schema markup (LocalBusiness + Service)
- [ ] Optimize title tags and meta descriptions
- [ ] Fully optimize Google Business Profile
