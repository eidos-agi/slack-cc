---
id: TASK-0056
title: cerebro-mcp docs layer — 3 tools (docs_search/read/list), auto-seeded from
  metrics-registry
status: Done
created: '2026-04-15'
priority: high
tags:
  - cerebro-mcp
  - docs
  - content
  - diataxis
  - rhea-approved
definition-of-done:
  - docs/ tree created with reference/, tutorial/, explanation/ subdirectories
  - scripts/generate-docs.ts emits content.generated.ts from metrics-registry.ts + markdown
  files
  - '3 tools registered on cerebro-mcp: docs_search, docs_read, docs_list'
  - 44 metric reference stubs auto-generated and indexable via docs_search
  - 3 handwritten tutorial files in docs/tutorial/
  - 2 explanation files (ported from existing in-code content)
  - ADR-0002 in cerebro-mcp/decisions/ capturing Rhea decision
  - Type-check clean, 34/34 test suite still passes
  - Deployed to cerebro-mcp Worker
  - docs_search('revenue') via curl with valid JWT returns ranked results
  - Ike task references the ADR
updated: '2026-04-15'
---
Add a minimal docs layer to cerebro-mcp covering the TUTORIAL and EXPLANATION quadrants of Diátaxis that the current tool set doesn't serve. Live data tools (list_metrics, get_metric, get_entity_pnl, etc.) stay exactly as they are — docs tools are parallel, not underneath them.

Decision driver: rhea_debate (session 29, 2026-04-15) ruled to build ONLY the reference-docs MVP with 3 generic tools, not the adaptive training engine / HOW-TO recipe system / supabase-backed content store I initially proposed. Strip to the smallest thing that covers the real gap.

Tools:
- docs_search(query, type?, limit?) — full-text ranked search across all markdown content
- docs_read(id) — fetch one doc by id, returns markdown
- docs_list(type?) — table of contents, optionally filtered by content type

Content (seeded):
- 44 auto-generated reference stubs from src/metrics-registry.ts (script-driven, not authorship)
- 3 entity references (ntx, hometown, consolidated) — handwritten, small
- 3 tutorial lessons — handwritten by Daniel or AI-drafted for review
- 2 explanation documents — port existing WHY_THIS_WORKS and GOTCHAS content from src/index.ts

Storage: Markdown files in docs/ with YAML frontmatter. Prebuild script generates content.generated.ts that the Worker imports. No Supabase, no external service, no database.

Telemetry: Every docs_* tool call auto-emits via the existing register() wrapper. Query cerebro-telemetry in 30 days — if docs_read count is zero, it's a signal to pause and reconsider.

Scope limits (explicit):
- NO tutorial sequencing engine / state machine
- NO progression tracking beyond raw telemetry
- NO HOW-TO recipe system
- NO wrappers over existing tools (list_metrics, about, explain_why_this_works stay as-is)
- NO Supabase move
- NO PDF reprocessing of Alex's Greenmark_Metrics_2.11.26.pdf (defer until there's real demand)

ADR: decisions/ADR-0002-docs-layer-diataxis.md in cerebro-mcp will capture the architectural choice + Rhea's reasoning + the defer-list.

Shipped 2026-04-15. PR cerebro-mcp#2 merged to main. Live at cerebro-mcp.dshanklin.workers.dev with docs_search / docs_read / docs_list. 52 docs bundled (44 auto-generated metric stubs + 3 entity refs + 3 tutorials + 2 explanations). Bundle delta 2645 to 2738 KiB. Worker startup unchanged at 68ms. Test suite 34/34 green. ADR-0002 in cerebro-mcp captures rationale. visionlog ADR-001 filed at cockpit level. Deferred per rhea: HOW-TO recipes (zero v1), Supabase content store, PDF reprocessing. Monitor: 30-day telemetry check for docs_read usage.
