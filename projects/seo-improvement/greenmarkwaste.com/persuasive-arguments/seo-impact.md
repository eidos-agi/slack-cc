# SEO Impact: Why the Rules Changed and What It Means for Greenmark

## Google Raised the Bar — and It Keeps Going Up

When the Webflow site was built, mobile speed was a secondary consideration. That changed. Google has made page speed a progressively more important ranking factor:

- **2018:** Google's "Speed Update" made mobile page speed a ranking factor for mobile search results
- **2021:** Core Web Vitals (LCP, CLS, FID/INP) became direct ranking signals
- **2024+:** Google continues to weight Core Web Vitals, with LCP being the most impactful metric

Greenmark's Webflow site was built before these thresholds became this strict. It now falls short on the most important metric:

| Core Web Vital | Google's "Good" Threshold | Greenmark Webflow | Greenmark Astro |
|---------------|---------------------------|-------------------|-----------------|
| LCP (loading) | Under 2.5 seconds | **17.5 seconds** (7x over) | 2.7 seconds |
| CLS (stability) | Under 0.1 | Unknown (high) | 0.001 |
| INP (interactivity) | Under 200ms | Unknown | Near 0ms |

## What This Means for Greenmark's Business

### Local Search Is How Customers Find Waste Services

When a business in Dallas needs waste services, they search:
- "commercial waste services Dallas"
- "dumpster rental DFW"
- "waste management companies near me"
- "roll off container Dallas TX"

Google returns results ranked by relevance, authority, and **user experience** (which includes page speed). A site with a 47/100 mobile score is actively suppressed in these results.

### The Bounce Rate Problem

Google's own research shows:
- **53% of mobile visits are abandoned** if a page takes over 3 seconds to load
- Bounce rate increases **32%** as page load time goes from 1s to 3s
- At **5 seconds**, the probability of bounce increases by **90%**
- At **10+ seconds**, the probability of bounce increases by **123%**

Greenmark's page loads in **17.5 seconds**. The vast majority of mobile visitors leave before seeing any content.

### The Competitive Advantage (AI Creates the Opening)

Moving from 47/100 to 92/100 is not a marginal improvement — it's a category change:
- **47/100 = "Poor"** — Google penalizes
- **92/100 = "Good"** — Google rewards

Most competitors in the DFW waste services space likely haven't optimized for mobile speed either — they're in the same Webflow/Squarespace/WordPress boat. AI tools give Greenmark the ability to leapfrog them without the cost of hiring an agency to do it. This is a first-mover advantage that won't last forever.

## Beyond Speed: What Astro Enables for SEO

### Service-Area City Pages (AI Makes This Scalable)
In Webflow, each city page requires manual creation in the visual editor. AI tools can generate 30+ city pages from a template in minutes. Astro lets us create dedicated pages for every city in the DFW metro:
- "Waste Services in Plano, TX"
- "Dumpster Rental in Frisco, TX"
- "Commercial Waste Solutions in Arlington, TX"

Each page targets location-specific searches. This is a proven local SEO strategy that Webflow makes difficult (each page costs editorial effort in the drag-and-drop editor; in Astro, they can be templated).

### Structured Data (JSON-LD Schema)
Astro gives us full control over structured data that tells Google:
- What services Greenmark offers (LocalBusiness schema)
- What areas Greenmark serves (ServiceArea schema)
- FAQs in a format Google can show directly in search results (FAQPage schema)
- Reviews and ratings (Review schema)

Webflow's generated HTML makes adding custom schema difficult and fragile.

### AI-Optimized Content (AIO)
AI-powered search (Google AI Overviews, Bing Copilot, ChatGPT search) is becoming a primary way people find businesses. These systems favor:
- Clean semantic HTML (Astro produces this; Webflow adds unnecessary wrapper divs)
- Structured data they can parse (JSON-LD schema)
- Fast, accessible pages

Astro is built for this. Webflow's generated HTML is not optimized for AI consumption.

## Revenue Impact Estimate

| Scenario | New Leads/Month | Avg Account Value/Year | Annual Revenue Impact |
|----------|----------------|------------------------|----------------------|
| Conservative | 1 additional lead | $5,000 | $5,000/year |
| Moderate | 2 additional leads | $10,000 | $20,000/year |
| Optimistic | 5 additional leads | $15,000 | $75,000/year |

These are rough estimates, but the point is clear: **the revenue impact of better search rankings far exceeds any subscription savings.** A single additional commercial waste account pays for the entire technology engagement.

## How We'll Measure Success

1. **Google Search Console** — Track impressions, clicks, and average position for target keywords
2. **Google Analytics 4** — Track organic traffic, bounce rate, and conversion events (form submissions)
3. **PageSpeed Insights** — Monthly monitoring of Core Web Vitals scores
4. **Keyword rankings** — Track position changes for "waste services Dallas" and related terms

All of these tools are free. We set them up before cutover so we have baseline data from day one.
