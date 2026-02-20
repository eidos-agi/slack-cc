# Technology Stack

Systems built or managed by Daniel / AIC engineering for Greenmark.

## Applications

### Cerebro
- **What:** Executive dashboard and data warehouse initiative. The main deliverable of Project Cerebro.
- **Correct spelling:** Cerebro (not "Cerebra" — Fireflies inconsistently transcribes this)
- **Repo:** [cerebro](https://github.com/greenmark-waste-solutions/cerebro)
- **Stack:** Next.js, hosted on Railway
- **Named by:** Michael D. Nguyen

### data-daemon
- **What:** Extraction pipeline that pulls vendor data into the warehouse.
- **Correct spelling:** data-daemon (hyphenated, lowercase)
- **Repo:** [data-daemon](https://github.com/greenmark-waste-solutions/data-daemon)
- **Stack:** YAML-driven, Postgres job queue, 82 tests
- **Key detail:** v1.4 complete. Works with synthetic data. Ready for real connections.

### cerebro-qa
- **What:** QA dashboard for data quality monitoring.
- **Repo:** [cerebro-qa](https://github.com/greenmark-waste-solutions/cerebro-qa)
- **Key detail:** Michael's "trust but verify" requirement. "Having warnings come up if things aren't loading correctly."

## Infrastructure

### Railway
- **What:** Cloud hosting platform. Manages all Greenmark services.
- **Key detail:** Pro account ($20/mo). Greenmark project needs to be transferred to Greenmark billing (currently on AIC).
- **Analogy Daniel uses:** "Like a Dr. Horton neighborhood — Railway manages the whole neighborhood of your infrastructure and the billing."

### Supabase
- **What:** Postgres database hosting. The data warehouse.
- **Correct spelling:** Supabase (not "super base" or "supa base")

### GitHub
- **What:** Code hosting and version control. Also used for non-code documentation (this repo).
- **Org:** [greenmark-waste-solutions](https://github.com/greenmark-waste-solutions)
- **Key detail:** Michael and Alex browse this in GitHub's web UI. Keep files readable as rendered markdown.

## AI

### Claude
- **What:** Anthropic's AI assistant. Used by the team for coding, analysis, and planning.
- **Correct spelling:** Claude (not "Quad" — Fireflies mangled this on Feb 11)
- **Key detail:** Greenmark has a Claude Team plan. Daniel to get a seat (may need greenmarkwaste.com email alias).

### MCP (Model Context Protocol)
- **What:** Direct AI-to-data connection via Claude.
- **Future idea:** "Build a Cerebro MCP directly into Claude" — direct data access, not just sidebar.

## Architecture Concepts

### Medallion architecture
- **What:** Bronze (raw) → Silver (cleaned) → Gold (business metrics) data layers.
- **Bronze schema:** One per vendor (e.g., sage_bronze, navusoft_bronze). Raw data landing zone.

### 2+2+2
- **What:** Integration strategy. Connect 2 vendor systems at a time, ordered by business value.
- **Current:** Sage + HubSpot are first two.

### Elephant Carpaccio
- **What:** Thin-slicing delivery so stakeholders approve each increment before proceeding.
