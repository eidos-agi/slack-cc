---
id: "ADR-001"
type: "decision"
title: "Docs layer on cerebro-mcp follows Di\u00e1taxis; reference content is auto-generated, not authored"
status: "active"
date: "2026-04-15"
---

# Decision: Docs layer on cerebro-mcp follows Diátaxis; reference content is auto-generated, not authored

## Context

Session 29 (2026-04-15). Daniel proposed "Cerebro Training" — a progressive-reveal onboarding system with 10 training-specific tools. On reflection we reframed: training is one content type within a broader docs layer. A rhea_debate was run to choose architecture.

Current cerebro-mcp has 9 tools that map cleanly onto the Diátaxis framework:
- **Reference**: list_metrics, get_metric, list_categories, list_periods, list_entities, about (6 tools)
- **Explanation**: explain_why_this_works, list_mcp_gotchas (2 tools)
- **Live data** (not docs): get_entity_pnl (1 tool)
- **Tutorial**: missing
- **How-to**: missing

The gap is two of the four Diátaxis quadrants. Training is specifically the tutorial subset of that gap.

## Decision

Build a docs layer on cerebro-mcp with exactly three generic tools — `docs_search`, `docs_read`, `docs_list` — covering all four Diátaxis content types via frontmatter `type` field. Seed content is auto-generated from the existing structured data (metrics-registry.ts), not hand-authored where avoidable.

Concretely:
- Three tools, no more, no less, for v1
- Markdown files in repo with YAML frontmatter
- Reference content: 44 auto-generated stubs from `src/metrics-registry.ts` via a prebuild script
- Tutorial content: 3 handwritten seed lessons
- Explanation content: ported from existing `WHY_THIS_WORKS` and `GOTCHAS` in-code constants
- How-to content: zero files — deferred until real demand

## Explicitly rejected alternatives

| Alternative | Reason for rejection |
|---|---|
| Adaptive training engine (state machine on telemetry) | Recommendation engine for three executives with no demand signal. Killed by rhea Doubter. |
| 10 training-specific tools | Over-specialized. Training is a content type, not a product line. |
| Wrapping existing tools (list_metrics, etc.) as docs_read proxies | Structured JSON tools serve tool pipelines; converting to markdown loses fidelity. Keep parallel, not beneath. |
| Supabase-backed content store | Premature. Markdown in repo is the simpler thing; move only if a real constraint appears (cross-service sharing, edit-without-deploy, etc.). |
| PDF reprocessing (Alex's Greenmark_Metrics PDF) | Defer until demand. Registry stubs cover the same ground. |
| HOW-TO recipe system | Defer until demand. Build when the first real task-oriented question lands. |

## Consequences

**Positive:**
- Two missing Diátaxis quadrants get coverage with minimal new surface area (3 tools vs 10).
- Existing tool contracts stay intact. Zero churn on the 9 shipped tools.
- Content scales linearly with authorship effort; reference content doesn't require authorship at all (codegen).
- Telemetry already logs every tool call — `docs_*` calls are automatically instrumented via the existing `register()` wrapper. We can query "did anyone read docs this month" at any time.

**Negative:**
- Claude (the LLM) now has two overlapping retrieval shapes for metrics: structured `get_metric` and narrative `docs_read`. Mitigated by sharper tool descriptions — `get_metric` for programmatic/computational use, `docs_read` for human-readable explanation.
- Content bootstrap is a one-time load (codegen script + 3 tutorial files + 2 explanation files). After that, ongoing authorship burden exists for any new tutorial or how-to.
- Supply-side reasoning risk: no specific stakeholder has asked "how do I use Cerebro, teach me" yet. Monitored via telemetry — if docs_read count is zero after 30 days, pause.

## References

- `cerebro-mcp/decisions/ADR-0002-docs-layer-diataxis.md` — full engineering ADR in the repo that implements this
- `.ike/tasks/TASK-0056 - cerebro-mcp-docs-layer-3-tools-docs-search-read-li.md` — execution task
- rhea_debate transcript from session 29, 2026-04-15 — architectural decision log (not stored; summarized in ADR)
- Diátaxis framework: https://diataxis.fr — the taxonomy driving the content-type schema
- cerebro-mcp commit log — the existing 9-tool surface this layer parallels
