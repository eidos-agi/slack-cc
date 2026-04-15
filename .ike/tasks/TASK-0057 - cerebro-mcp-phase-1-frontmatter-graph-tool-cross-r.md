---
id: TASK-0057
title: 'cerebro-mcp phase 1: frontmatter graph + tool cross-refs + EXP-010–015'
status: Done
created: '2026-04-15'
updated: '2026-04-15'
completed: '2026-04-15'
priority: High
tags:
  - cerebro-mcp
  - docs
  - adr-0004
  - phase-1
acceptance-criteria:
  - Frontmatter schema extended with suggests_tools and questions_this_raises; type-check
  passes
  - 14 hand-authored docs carry populated suggests_tools and questions_this_raises arrays
  - 12 tool descriptions rewritten; each semantically adjacent tool appears in at least
  one other tool's description
  - EXP-010 through EXP-015 exist under docs/explanation/ with well-formed frontmatter
  - content.generated.ts regenerates cleanly via npm run generate-docs
  - tests/run.sh passes locally (34 tests)
  - docs_read response includes suggests_tools and questions_this_raises fields when
  present
definition-of-done:
  - All acceptance criteria met
  - ADR-0004 cross-referenced in commit message
  - Changes deployed to cerebro-mcp.dshanklin.workers.dev
  - 'Smoke test: call docs_read on TUT-001 via claude.ai and verify graph fields present'
  - Phase-2 monitoring reminder added to cockpit state.json (check 2026-10-15 or at
  100 docs)
---
Execute phase 1 of cerebro-mcp ADR-0004 (visionlog ADR-002, research 5e236fa8). Adds agentic graph primitives on top of the existing Diátaxis docs layer (TASK-0056).

## Scope

1. **Extend docs frontmatter schema** (src/docs/types.ts, scripts/generate-docs.ts): add optional `suggests_tools: string[]` and `questions_this_raises: string[]` fields. Thread into ParsedDoc → content.generated.ts → docs_read response.

2. **Author the graph** on 14 hand-authored docs: TUT-001/002/003, EXP-001/002, REF-ENTITY-ntx/hometown/consolidated, plus the six new EXP-010 through EXP-015 shipped in step 4.

3. **Rewrite 12 tool descriptions** in src/index.ts and src/docs/tools.ts. Each tool's description mentions semantically adjacent tools. Examples:
   - get_metric mentions docs_read (REF-METRIC-*) for narrative definition
   - docs_search mentions get_metric / get_entity_pnl for structured follow-ups
   - get_entity_pnl mentions list_periods for discovery, docs_read REF-ENTITY-* for context
   - about mentions docs_list as the full inventory

4. **Ship EXP-010 through EXP-015** under docs/explanation/. Progressive-reveal of Greenmark's AI-engineering thesis. Each one links forward to the next via related / questions_this_raises.

5. **Rebuild docs bundle**: `npm run generate-docs` regenerates content.generated.ts.

6. **Run tests**: `tests/run.sh` — must stay green, especially `all_tools_have_descriptions` and `type_check_passes`.

## Out of scope (phase 2)

RRF migration to shared Supabase doc_chunks — triggered at 100 docs OR 2026-10-15, whichever first. Do NOT build this in phase 1.

## Monitoring hooks (post-ship)

- cerebro-telemetry: check for routing-quality regression on non-docs tools after description rewrites land
- docs_read call frequency on the new EXP docs — validates the graph is being traversed
- Corpus growth counter — phase-2 trigger at 100 docs

## Completion log (2026-04-15, session 29)

All acceptance criteria met. All DoD items met. Deployed live.

- Frontmatter schema extended in `src/docs/types.ts` (added `suggests_tools: string[]` and `questions_this_raises: string[]` as optional fields). Threaded through `ParsedDoc` → `content.generated.ts` → `docs_read` response.
- 14 hand-authored docs tagged with populated graph arrays: TUT-001/002/003, EXP-001/002, REF-ENTITY-ntx/hometown/consolidated, EXP-010..015.
- All 12 tool descriptions rewritten with cross-references:
  - 9 in `src/index.ts`: list_metrics, get_metric, list_categories, get_entity_pnl, list_periods, list_entities, about, explain_why_this_works, list_mcp_gotchas
  - 3 in `src/docs/tools.ts`: docs_search, docs_read, docs_list
- EXP-010..015 shipped under `docs/explanation/`: why-dashboards-arent-the-product, agentic-delivery, contracts-not-skills, brief-as-delivery-unit, trust-scaffolding, ai-engineers.
- `content.generated.ts` regenerated — 58 docs bundled (44 auto-generated metric stubs + 14 handwritten).
- `npm run type-check` clean.
- `./tests/run.sh` → 34/34 PASSED.
- Deployed via `wrangler deploy` → cerebro-mcp.dshanklin.workers.dev, version `ddba126d-cf3d-4340-af6d-1ec0cd39711a`.
- Commit: `6de06c0 feat: agentic docs graph (phase 1 of ADR-0004)` on main. Cherry-picked cleanly onto squash-merged origin/main.

Research audit trail confirms decision: Candidate C (static graph via frontmatter now, RRF at trigger) beat F (dynamic `docs_suggest_next` tool) **194 to 169 weighted points**. C wins agent-traversal-quality (8/10 vs 6/10, weight 5) and query-time latency (7/10 vs 4/10). F's only advantage was authorship cost (9/10 vs 3/10), but the actual tax turned out to be ~70 lines of YAML across 14 docs — small enough to be immaterial. See `cerebro-mcp/.research/agentic-docs-retrieval-v2/.research/DECISION.md`.

Phase-2 RRF trigger (decoupled per Rhea v2 Round 3): 100 docs OR 2026-10-15, whichever first. Out of scope for phase 1 by design.
