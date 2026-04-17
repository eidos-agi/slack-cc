---
id: "ADR-002"
type: "decision"
title: "cerebro-mcp docs retrieval \u2014 static frontmatter graph now, RRF at trigger"
status: "accepted"
date: "2026-04-15"
source_research_id: "5e236fa8-db20-49e1-ab70-cf1f0f71a92c"
---

## Context

Session 29 added a Diátaxis docs layer to cerebro-mcp (3 tools: `docs_search`, `docs_read`, `docs_list`; 52 bundled docs, ADR-001). Daniel then raised two architectural concerns in the same session: (1) the docs layer ships naive weighted-substring retrieval, but ADR-2026-36 in greenmark-docs already decided hybrid RRF retrieval (tsvector + pgvector fused at k=60) for cerebro-ai-services /v1/ask; (2) the interesting question isn't single-shot retrieval quality but multi-turn traversal quality — "just think about recursive loops that answer questions through tool calls."

Two research projects were run:
- v1 (c63d6891…): five candidates, nine weighted criteria — decided Candidate C
- v2 (5e236fa8…): Rhea-triggered after adversarial review identified a missing candidate (F: docs_suggest_next as a dynamic tool) and a missing criterion (operational routing risk on non-docs tools)

## Decision

Adopt cerebro-mcp ADR-0004. Phase 1 ships now:
1. Extend Doc frontmatter with `suggests_tools` and `questions_this_raises`
2. Author the graph on ~14 hand-authored docs (3 tutorials, 2 explanations, 3 entity references, 6 new strategic docs)
3. Rewrite 12 tool descriptions so each appears in the descriptions of semantically adjacent tools
4. Ship EXP-010 through EXP-015 explanation docs progressively revealing Greenmark's AI-engineering thesis
5. Extend docs_read response to surface the new frontmatter fields

Phase 2 (RRF migration per ADR-2026-36) triggers at 100 docs OR 2026-10-15, whichever fires first. The trigger is decoupled from cerebro-ai-services commitment — we migrate when docs-side demand justifies it, not when someone else needs it.

## v2 weighted scores

| Candidate | Score |
|---|---|
| **C — static frontmatter now, RRF at trigger** | **194** (chosen) |
| D — RRF first, graph second | 189 |
| A — retrieval-first RRF now | 188 |
| E — hold and monitor | 182 (fallback) |
| F — dynamic docs_suggest_next tool | 169 |
| B — static frontmatter, defer RRF indefinitely | 147 |

## Consequences

**Positive:** Best agent-traversal quality. Maintains ADR-2026-36 conformance via phasing. Phase-2 trigger decoupled from external dependency. Frontmatter extension is backward-compatible.

**Negative:** Small authorship tax on hand-authored docs. Tool-description rewrites carry operational risk for non-docs routing (monitored via cerebro-telemetry). Phase 2 is deferred work.

## References

- cerebro-mcp/decisions/ADR-0004-agentic-docs-graph-then-rrf.md
- .research/agentic-docs-retrieval-v2/ (authoritative)
- .research/agentic-docs-retrieval/ (superseded v1)
- ADR-2026-36 in greenmark-docs — the upstream retrieval decision this ADR conforms to via phasing
- ADR-001 (this visionlog) — the docs layer this ADR extends

