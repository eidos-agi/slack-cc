# CLAUDE.md — Greenmark

This is the shared planning hub for Greenmark Waste Solutions leadership. It is NOT a code repo. It contains projects, decisions, meeting records, and reference material.

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
greenmark-planning/
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
| [infra](https://github.com/greenmark-waste-solutions/infra) | Vendor API research, data dictionary, integration specs | Daniel |
| [weekly-updates](https://github.com/greenmark-waste-solutions/weekly-updates) | Automated engineering reports from GitHub commits | Daniel |
| [cerebro-qa](https://github.com/greenmark-waste-solutions/cerebro-qa) | QA dashboard — data quality monitoring | Daniel |

## Current State (as of 2026-02-20)

### What's Active
- **Vendor research**: 6 of 15 systems deeply researched (Sage, Navusoft, HubSpot, Fleetio, Paylocity, WAM). 65 bronze tables proposed.
- **data-daemon**: v1.4 complete. Pipeline works with synthetic data. Ready for real connections.
- **SEO planning**: 90-day plans written for both greenmarkwaste.com and htdisposal.com. No baseline audit done yet.

### What's Blocked
- **Sage connection**: Alex provisioning Daniel a user account → Daniel creates read-only API key
- **HubSpot connection**: Need API access from Alex/Michael
- **3rd Eye**: Complete unknown — no API docs, no vendor contact, can't even evaluate
- **WAM**: Confirmed no API, but Michael says Hometown transitioning to Navusoft "over the next couple months" — may not need WAM integration at all

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
- **No secrets in repos** — credentials go in Knox or AIC Secure Request, never in git.
- **Commit messages explain why** — not just what changed.
- **Keep files under 2700 lines** — break up large documents.
- **Meeting folders are self-contained** — all artifacts for a meeting live in one folder.

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
