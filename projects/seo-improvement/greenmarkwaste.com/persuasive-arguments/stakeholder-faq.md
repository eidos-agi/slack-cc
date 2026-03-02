# Stakeholder FAQ: 25 Questions Answered

Questions that investors, the CEO, CFO, and CRO would ask — with direct answers.

---

## Cost & ROI

### 1. "What does Webflow cost us today?"
We don't know yet — that's a discovery question. Webflow plans range from $14–$39/month per site. If both sites are on it, that's $28–$78/month. The Astro replacement runs on Railway infrastructure we already pay for ($0 incremental cost).

### 2. "What does Cloudflare cost?"
Free tier. Zero. DNS management, CDN, and SSL are all included at no charge.

### 3. "What's the total cost of this migration?"
Daniel's time (already budgeted as part of the Cerebro engagement). No new vendor costs. Net effect is *eliminating* a recurring Webflow subscription. GoDaddy stays as-is (we're just centralizing the account, not moving the domain).

### 4. "What's the ROI?"
Eliminate Webflow subscription + eliminate designer/agency dependency + 2x improvement in Google search visibility (mobile score 47→92 directly affects rankings). For a waste services company, even 1 additional lead/month from better SEO pays for the entire project.

### 5. "Why not just fix the speed problem inside Webflow?"
We can't. Webflow generates its own HTML/CSS/JS — we don't control it. The 17.5s load time is inherent to how the platform works, not a design flaw. This wasn't a problem when the site was built — Google's speed requirements got stricter, and AI tools now let us build at a performance level that wasn't accessible without an agency before.

---

## Risk

### 6. "What if the migration breaks something?"
The Cloudflare layer gives us instant rollback. If anything goes wrong after cutover, we change one DNS record and greenmarkwaste.com points back to Webflow within minutes. The old site stays intact until we explicitly cancel it.

### 7. "What about the domain expiring?"
greenmarkwaste.com expires Aug 1, 2026. Step one of the GoDaddy transfer is confirming auto-renewal is on. This is why we need access now — not because we're in a rush, but because 5 months isn't a comfortable margin if we discover a problem with the account.

### 8. "What happens if Daniel gets hit by a bus?"
That's exactly why we're centralizing accounts under `it@greenmarkwaste.com` — it's a shared IT login, not a personal account. Any IT person can access GoDaddy, Webflow, Cloudflare, Railway with that one credential. This migration *reduces* bus-factor risk.

### 9. "Is there downtime during the switch?"
Zero. The sequence is: (1) Cloudflare manages DNS while pointing to Webflow (no change for visitors), (2) when Astro is ready, update one record in Cloudflare to point to Railway. DNS propagation happens in the background. Visitors don't notice.

### 10. "What if the designer/agency has concerns about the ownership change?"
This isn't about removing anyone — it's about making sure Greenmark has a front door key to its own house. The designer keeps editor access and can continue working as before. We're adding Greenmark as owner, not cutting anyone out. If there's an active support contract, that relationship continues until Greenmark decides otherwise.

---

## Strategic

### 11. "Why now? The website was fine before."
It was — when it was built. Two things changed: Google raised the bar on mobile speed (now a direct ranking penalty), and AI tools made it possible to build a faster replacement without hiring an agency. The opportunity didn't exist a year ago. Every month we wait, potential customers searching "waste services Dallas" see competitors first.

### 12. "Isn't this scope creep from Cerebro?"
No. Cerebro's mandate includes technology leadership for Greenmark. Account centralization was explicitly approved by Alex (Feb 27 policy). The SEO/website work was called out by Michael and Alex as "low hanging fruit, top of the list" in the Feb 19 call.

### 13. "How does this help us win more deals?" (CRO question)
Three ways: (1) Better Google rankings = more inbound leads, (2) Faster site = lower bounce rate (visitors who wait 17s leave), (3) Service-area city pages (coming next) let us rank for "waste services [city name]" across the entire DFW metro.

### 14. "What about htdisposal.com?"
Same playbook. We're discovering whether it shares the same GoDaddy/Webflow accounts. If so, we centralize both in one pass. The Astro approach works for both sites.

### 15. "Why Astro specifically? What if Astro disappears?"
Astro generates static HTML — the output is just HTML/CSS/JS files. If Astro disappeared tomorrow, the site would keep running. We could rebuild with any static site generator. There's zero vendor lock-in, unlike Webflow where your content is trapped in their CMS.

---

## Operations

### 16. "Who updates the site after the switch? What if AIC's engagement ends?"
Initially, Daniel using AI tools — same workflow as Cerebro. But the site is built so Greenmark isn't locked in. A headless CMS (like Decap or Tina — both free) can be added so a marketing hire or admin can edit content in a browser without touching code. The architecture supports self-service; we'll set it up when the team is ready. Nobody should be permanently locked into needing a specific person or agency to update their own website.

### 17. "How do we handle content changes in the meantime?"
Webflow stays live until cutover. Any content changes made in Webflow before the switch just need to be reflected in the Astro build. We're not ripping out Webflow tomorrow — this is a controlled transition.

### 18. "What's the timeline?"
Account centralization: 1–2 weeks once Michael provides GoDaddy access. Astro build (remaining pages): depends on prioritization vs. other Cerebro work. Cutover: same day once pages are built and Michael approves. No hard deadline.

### 19. "Do we need to re-do SEO when we switch?"
No. We keep the same URLs, same page titles, same meta descriptions. Google sees the same site, just faster. We'll set up 301 redirects for any URL structure changes. Search rankings should *improve* immediately because of the speed boost.

### 20. "What about forms? We need those leads."
Discovery question #17 asks exactly this. Any forms currently on the Webflow site (contact, quote requests) will be rebuilt in Astro pointing to the same backend (likely HubSpot). No leads get lost.

---

## Governance & Compliance

### 21. "Is this consistent with how we handle other vendor accounts?"
Yes. Identical pattern to Tasks 78–81 (Railway, Supabase, GitHub). Same policy (Task-92), same target owner (`it@greenmarkwaste.com`), same billing (`accounting@greenmarkwaste.com`). Alex already approved this framework.

### 22. "Who has access to what after the transfer?"
`it@greenmarkwaste.com` is the owner of everything. Daniel administers day-to-day. Michael retains visibility. Designers/agencies can be given limited access as needed. All access is documented and auditable.

### 23. "What if we decide to go back to Webflow later?"
The Webflow site isn't being deleted — we just stop paying for hosting once Astro is live. All the Webflow project data persists on their free tier. Going back would mean resubscribing. But given the 2x speed improvement, there's no technical reason to go back.

### 24. "Are we creating any security exposure?"
The opposite. Right now, we don't know who controls the GoDaddy account. An unknown party has the ability to transfer our domain, change DNS, or let it expire. Centralizing under `it@greenmarkwaste.com` *closes* a security gap.

### 25. "What does Alex (CFO) need to approve?"
Nothing new. The account ownership policy (Task-92) already covers this. Alex may want to see the Webflow subscription cost when we discover it. The email is CC'd to Alex for visibility. The net financial impact is positive (eliminate a subscription).
