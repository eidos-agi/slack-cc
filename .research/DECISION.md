# Decision

**Date:** 2026-04-21
**Status:** Decided

## Decision

Adopt BOTH: Create an eidos-agi private marketplace for immediate distribution, and simultaneously submit to anthropics/claude-plugins-official for broader reach. The private marketplace is Phase 1 (ships today), official submission is Phase 2 (async, Anthropic-gated).

## Rationale

Scored 97 weighted vs next-best 88 (private-only). The dual approach captures every advantage: immediate shipping via private marketplace, maximum reach via official, and — critically — builds the Eidos ecosystem distribution channel that every future plugin (railguey, research.md, ike.md, visionlog, rhea) will use. The only cost is creating a marketplace repo, which is a one-time ~30 min investment. The private marketplace also eliminates the --dangerously-load-development-channels flag, fixes the dual-start problem at the root, and makes installation a single command.
