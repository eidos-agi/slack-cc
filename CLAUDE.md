# CLAUDE.md — Greenmark Cockpit

AI Cockpit for Greenmark Waste Solutions. Orchestrates technology leadership, vendor integration, and project delivery. Built from [rhea-impact/ai-cockpit-template](https://github.com/rhea-impact/ai-cockpit-template).

This is NOT a code repo. It contains projects, decisions, meeting records, reference material, and the session lifecycle for the Greenmark engagement.

## Who's Who

### Greenmark Leadership
- **Michael D. Nguyen** — President. Initiated Project Cerebro. Owns Navusoft, WAM, 3rd Eye vendor relationships. mnguyen@greenmarkwaste.com
- **Alex Kaye, CFA** — CFO. Owns Sage Intacct, HubSpot, Paylocity credentials. Knows which systems flow through Sage. akaye@greenmarkwaste.com
- **Lannis Nicholson** — CRO (Partner). Sales strategy, revenue operations. Previously at LRS and Ramco.
- **Robert Heath** — General Manager. Owns Fleetio credentials. Fleet and field operations.

### AIC Holdings (Technology Partner)
- **Daniel Shanklin** — Director of AI & Technology. Tech lead for Project Cerebro. Writes the code, runs the agents.
- **William Holloway** — Partner & COO. Strategic advisor.
- **Collin Bird** — Managing Director. Project sponsor.

### Audience for This Repo
Michael, Alex, and Robert browse this in GitHub's web UI. Keep files readable as rendered markdown. Don't assume git/CLI knowledge.

## Glossary

| Term | Meaning |
|------|---------|
| **Cerebro** | Project Cerebro — the executive dashboard and data warehouse initiative |
| **NTX** | North Texas entity — operates as Greenmark Waste Solutions |
| **Hometown** | Indiana entity — operates as Hometown Disposal (htdisposal.com) |
| **Entity** | A business unit. Greenmark has 3: NTX, Hometown, and Memphis (nascent) |
| **Bronze schema** | Raw data landing zone in the warehouse — one schema per vendor (e.g., sage_bronze, navusoft_bronze) |
| **data-daemon** | The extraction pipeline that pulls vendor data into the warehouse |
| **Medallion architecture** | Bronze (raw) → Silver (cleaned) → Gold (business metrics) data layers |
| **2+2+2** | Integration strategy: connect 2 vendor systems at a time, ordered by business value |
| **Elephant Carpaccio** | Thin-slicing delivery so stakeholders approve each increment before proceeding |

## Cockpit Primitives

This workspace is an **AI Cockpit** — built from [rhea-impact/ai-cockpit-template](https://github.com/rhea-impact/ai-cockpit-template).

| Skill | When | What |
|-------|------|------|
| `/takeoff` | Start of session | Boot sequence: bookmark → drift check → priorities → wait for orders |
| `/land` | End of session | Capture outcomes → write bookmark → clean exit |
| `/cockpit-status` | Anytime | Active workstreams, blockers, ages, who owes what |

### Session Protocol
1. Every session starts with `/takeoff`
2. Work using domain-specific skills (see below)
3. Every session ends with `/land`
4. If a session crashes without `/land`, the next `/takeoff` detects drift and flags it

### Domain Skills
| Skill | What It Does |
|-------|-------------|
| `/diarize` | Process meeting transcripts into structured README with decisions + action items |
| `/task-out` | Route action items from meetings to project checklists and the Waiting On table |
| `/weekly-update` | 7-stage subagent pipeline: collect → analyze → interview → synthesize |
| `/take-notes` | Clipboard capture (pbpaste) for raw notes processing |
| `/vendor-research` | Deep research on vendor APIs → structured api-data-model.md |
| `/hubspot-explore` | CRM data exploration via REST API wrapper |

### State Files
- **`state.json`** — Watermarks, counters, last-run timestamps. Skills read/write this.
- **Bookmarks** — Written to `~/.claude/bookmarks/` by `/land`. Read by `/takeoff`. Bridge between sessions.

## Repo Structure

```
greenmark-cockpit/
├── CLAUDE.md              ← you are here
├── README.md              ← dashboard: active projects, status, links
├── state.json             ← cockpit state: watermarks, counters
├── projects/              ← active work with checklists and deliverables
│   ├── seo-improvement/   ← SEO plans for both websites
│   ├── data-mockups/      ← 3 HTML dashboard prototypes
│   ├── data-integration/  ← (future: 2+2+2 integration tracking)
│   ├── recording-solution/
│   ├── tech-org-setup/
│   └── warehouse-strategy/
├── meetings/              ← meeting folders: transcripts, notes, action items
│   └── YYYY-MM-DD-short-description/
├── decisions/             ← decision log (pending and resolved)
├── reference/             ← living reference material
│   ├── stakeholders/      ← org chart, contact info
│   └── research/          ← design docs, gap analysis, processes
└── archive/               ← completed/superseded material
    └── kickoff-2026-02/   ← original engagement kickoff (Feb 2026)
```

## Meeting Conventions

Each meeting gets a folder: `meetings/YYYY-MM-DD-short-description/`

A meeting folder should contain:
- **transcript.md** — diarized transcript with speaker names (or raw .srt if unprocessed)
- **README.md** — attendees, key decisions, action items, links to artifacts
- **Source files** — .ics, .eml, .docx, .pdf, .srt as received

After processing a transcript, extract:
1. **Decisions made** — add to `decisions/` if significant
2. **Action items** — update relevant project checklists
3. **New information** — update reference docs or project plans

## Related Repos (Where the Code Lives)

| Repo | What It Is | Who Works In It |
|------|-----------|-----------------|
| [data-daemon](https://github.com/greenmark-waste-solutions/data-daemon) | Extraction pipeline — YAML-driven, Postgres job queue, 82 tests | Daniel |
| [cerebro](https://github.com/greenmark-waste-solutions/cerebro) | Next.js dashboard app — hosted on Railway | Daniel |
| [cerebro-mcp](https://github.com/greenmark-waste-solutions/cerebro-mcp) | Remote MCP server — Cloudflare Worker, 9 tools, Supabase OAuth + RLS. Live at `cerebro-mcp.dshanklin.workers.dev` | Daniel |
| [cerebro-telemetry](https://github.com/greenmark-waste-solutions/cerebro-telemetry) | Dedicated telemetry service — Node + Hono + SQLite on a Railway volume. One endpoint every Greenmark service writes to. Live at `cerebro-telemetry-develop.up.railway.app` | Daniel |
| [infra](https://github.com/greenmark-waste-solutions/infra) | Vendor API research, data dictionary, integration specs | Daniel |
| [weekly-updates](https://github.com/greenmark-waste-solutions/weekly-updates) | Automated engineering reports from GitHub commits | Daniel |
| [cerebro-qa](https://github.com/greenmark-waste-solutions/cerebro-qa) | QA dashboard — data quality monitoring | Daniel |

## Release Practices (Tier System)

All 13 repos are classified into tiers with appropriate release ceremony. See [ADR-2026-02](decisions/ADR-2026-02.md) for the original decision and [ADR-2026-03](decisions/ADR-2026-03-repo-governance-as-code.md) for the current source-of-truth model (Probot/Settings).

**Source of truth**: each repo's `.github/settings.yml`. The `repository.topics` field carries `tier-t1` / `tier-t2` / `tier-t3` as queryable metadata. Reconciled by the Probot/Settings GitHub App.

Tier contract:

- **T1 Production**: deploy risk is real. PR required on main, required status checks (Type Check / Lint / Unit Tests / Build), CODEOWNERS, dependabot.
- **T2 Supporting**: has CI, lower blast radius. PR required, required checks.
- **T3 Reference**: docs + tools, no deploy risk. Direct-to-main OK, pre-push hooks only.

Migration status (2026-04-16, session 30):

- **Migrated** (settings.yml committed, PR open or merged):
  greenmark-cockpit, cerebro, cerebro-mcp (new), cerebro-telemetry (new),
  cerebro-migrations, cerebro-qa, cerebro-ai-services, cerebro-bot-farm,
  cerebro-warp-speed, cerebro-warp-speed-excel, cerebro-excel, infra
- **Deferred**: data-daemon — pre-commit hook runs full pytest, blocks landing
  from CI environment. Needs Daniel's local env to land the file.
- **Removed from scope**: cerebro-vault — not in the GitHub org (local-only clone). Retired from tier-map.

Continuous enforcement: `.github/workflows/settings-yml-audit.yml` polls every
migrated repo every 6h, fetches `.github/settings.yml`, validates against the
tier contract. Fails + auto-files a drift issue if any repo regresses.

Per-repo self-check: `.github/workflows/settings-yml-check.yml` is a reusable
workflow any Greenmark repo can call from its own CI to validate the file on
every PR.

Validator: `.github/scripts/validate-settings-yml.py` — enforces schema (tier
topic, greenmark topic, private:true, branch protection per tier). Runs in CI
and locally.

Legacy: `tools/tier-map.sh` is mostly emptied. Only `data-daemon` remains
(deferred above). When data-daemon migrates, delete `tier-map.sh` entirely.

## Current State (as of 2026-04-13)

### What's Active
- **Sage Medallion LIVE (M-04 through M-06 done)**: Full bronze→silver→gold pipeline live. 1.38M GL entries in sage_bronze, 7 silver materialized views, 3 gold views (entity_pnl, gl_summary, ap_aging). `sage_gold.refresh_all()` wired into data-daemon executor. Financial + Executive dashboard pages fetch live data from sage_gold via PostgREST, with mock fallback. Dec 2025 revenue matches Alex's Greenmark_Metrics to the penny (HTN $872,850.23, NTX $75,246.02). Parity: FULL (10,056 rows, 0 failures). Deployed to staging + production 2026-04-13.
- **cerebro-builder MCP**: 12 tools for session orchestration. Serendipity learning system: Ariadne surfaces docs while working, adapts from engagement (read/graduation signals). Adaptive serendipity rate (0.10-0.50). 13 docs in knowledge base. Rhea 3-model debate for high-stakes decisions.
- **cerebro-github MCP**: 14 tools encoding engineering ceremony — create_work, open_pr, check_ci, merge_pr, bulk_merge, dashboard, health_check, changelog, stale, onboard, why, retro, learn. Persistent incident ledger (7 entries). Rhea token-gate pattern for T1 production merges.
- **Release practices**: Tiered system applied across all 13 repos (ADR-2026-02). 13/13 compliant. Pre-push hooks, CI, PR templates, CODEOWNERS, dependabot — all tier-appropriate.
- **Jam.dev bug reporter**: Deployed to staging on cerebro. One-click screen capture for Michael/Alex/Robert. Gated on NEXT_PUBLIC_JAM_TEAM_ID env var.
- **Vendor research**: 6 of 15 systems deeply researched (Sage, Navusoft, HubSpot, Fleetio, Paylocity, WAM). 65 bronze tables proposed.
- **data-daemon**: v1.4 + SageIntacctConnector. Pipeline live against real Sage API. Executor refreshes gold views after each extraction.
- **Warp-speed Excel**: Local-first Sage data intelligence. 1.38M GL entries in SQLite. Proved the dimensionality that sage_bronze was built from.

### What's Blocked
- **HubSpot**: Deprioritized per Michael (2026-04-06). Sage is priority #1.
- **3rd Eye**: Complete unknown — no API docs, no vendor contact, can't even evaluate.
- **WAM**: Confirmed no API. Michael says Hometown transitioning to Navusoft "over the next couple months" — may not need WAM integration.

### Decisions Made (Feb 19 call)
1. **Sage Intacct is the system of record.** Cerebro reads from it but never writes to it. Other systems (Expensify, potentially Comerica) flow through Sage rather than directly into the warehouse. Alex: "If Sage can be our Rosetta Stone for most things, I'd rather just flow it through Sage." Daniel: "Your auditors will love it. Sage is the system of record. Cerebro just happens to look at it."
2. **First two data sources: Sage Intacct + HubSpot** — confirmed by Michael and Alex
3. **Michael is de facto tech lead** at Greenmark — manages IT and software
4. **Expensify already flows through Sage** — no separate connector needed. **Comerica does NOT** — decision tabled, Alex leaning toward flowing through Sage
4. **Greenmark billing fully separate from AIC** — Railway, GitHub, all infrastructure
5. **API keys are read-only** — no agent writes to Sage. Human-in-the-loop for all entries.
6. **Communication via email + Teams** — not Wrike
7. **Both websites built on Webflow** — SEO is "low hanging fruit, top of the list"

## Vendor Systems at a Glance

15 total systems across 3 priority tiers:

| Tier | Systems | Status |
|------|---------|--------|
| **P1 Core** | Sage Intacct, Navusoft, HubSpot | Deep research complete |
| **P2 Operational** | Fleetio, Paylocity, 3rd Eye, WAM | Deep research complete (except 3rd Eye — unknown) |
| **P3 Supporting** | LB Technologies, Comerica, Expensify, AssureHire, Samba Safety, Wrike, Egnyte, Vested Network | Cataloged, not yet researched. Several may flow through Sage. |

Full details: [infra/vendor-status.md](https://github.com/greenmark-waste-solutions/infra/blob/main/vendor-status.md)

## Rules

- **Soft deletes only** — never hard-delete records from any database. Use `deleted_at` timestamps.
- **No secrets in repos** — credentials go in Railway env vars (Greenmark's secrets manager) or LastPass, never in git. Do NOT use Knox (that's AIC's vault, not Greenmark's).
- **Commit messages explain why** — not just what changed.
- **Keep files under 2700 lines** — break up large documents.
- **Meeting folders are self-contained** — all artifacts for a meeting live in one folder.

## Browser Automation — MANDATORY

**Use `tools/agent-browser/` for ALL browser automation. No exceptions.**

- **DO NOT** use `mcp__claude-in-chrome__*` tools
- **DO NOT** use `mcp__helios__*` tools
- **DO NOT** use any other browser MCP

**How to use it:**
```bash
AB="./tools/agent-browser/ab"
$AB open <url>           # navigate
$AB snapshot             # see the page (AI-friendly tree with @refs)
$AB fill @<ref> <text>   # fill a field
$AB click @<ref>         # click something
$AB screenshot /tmp/x.png # visual proof
```

**After every browser session**, update `tools/agent-browser/learnings.md` with what worked, what broke, and what to do differently. This compounds.

**Auth pattern:** Drive to login page, fill email (`it@greenmarkwaste.com`), then STOP for Daniel to paste password from LastPass and handle Duo 2FA.

Full docs: [tools/agent-browser/README.md](tools/agent-browser/README.md)

## Software adoption policy — MANDATORY

**Before installing, adopting, or proposing ANY new third-party software** — library, SaaS, GitHub App, CLI, Cloudflare add-on, Railway add-on, browser extension, anything — an agent must consult:

- [`GR-TOOLING-001`](.visionlog/guardrails/GUARD-003-gr-tooling-001-new-software-requires-a-rulebook-check-and.md) — the rulebook (scripture)
- [`policies/software-approved.md`](policies/software-approved.md) — the approved list

"Free tier" does **not** exempt. Sentry free, PostHog free, Axiom free, Cloudflare R2 free — all create accounts, credentials, and almost always grow into spend. The Greenmark stakeholders default to "no" on software cost because they do not yet internalize that AI creates leverage proportional to tooling spend. Frame any spend proposal as "collapses X hours of recurring human work into Y minutes," not "this is production-grade."

**Red-flag phrases that require an immediate stop-and-consult:**
- "Production-grade systems have this"
- "Industry best practice is to…"
- "While we're at it, let's also add…"
- "Free tier should be enough for now"
- "We can always add it back later" (if yes, default to NOT having it today)

Anything not on the approved list requires explicit Daniel approval before install.

<!-- BACKLOG.MD MCP GUIDELINES START -->

<CRITICAL_INSTRUCTION>

## BACKLOG WORKFLOW INSTRUCTIONS

This project uses Backlog.md MCP for all task and project management activities.

**CRITICAL GUIDANCE**

- If your client supports MCP resources, read `backlog://workflow/overview` to understand when and how to use Backlog for this project.
- If your client only supports tools or the above request fails, call `backlog.get_workflow_overview()` tool to load the tool-oriented overview (it lists the matching guide tools).

- **First time working here?** Read the overview resource IMMEDIATELY to learn the workflow
- **Already familiar?** You should have the overview cached ("## Backlog.md Overview (MCP)")
- **When to read it**: BEFORE creating tasks, or when you're unsure whether to track work

These guides cover:
- Decision framework for when to create tasks
- Search-first workflow to avoid duplicates
- Links to detailed guides for task creation, execution, and finalization
- MCP tools reference

You MUST read the overview resource to understand the complete workflow. The information is NOT summarized here.

</CRITICAL_INSTRUCTION>

<!-- BACKLOG.MD MCP GUIDELINES END -->
