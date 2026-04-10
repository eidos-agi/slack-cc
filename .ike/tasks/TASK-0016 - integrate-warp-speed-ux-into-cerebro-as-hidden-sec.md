---
id: TASK-0016
title: Migrate Warp Speed into Cerebro — replace /ask with real Agent SDK experience
status: To Do
created: '2026-04-09'
priority: high
tags:
  - cerebro
  - ux
  - refactor-forge
  - agent-sdk
acceptance-criteria:
  - 'Phase 1: /dashboard/ask renders the real Agent SDK chat (not canned responses)'
  - 'Phase 1: Single sidebar entry ''Ask Cerebro'' — no ''Warp Speed'' entry'
  - 'Phase 2: All 4 tool plugins pass refactor-verify with golden fixtures'
  - 'Phase 2: Streaming works in Next.js API route on Railway'
  - 'Phase 3: Python service retired only after 5 business days parallel run with zero
  incidents'
  - 'Phase 3: cerebro-warp-speed repo archived, not deleted'
updated: '2026-04-09'
---
Replace the canned-response /dashboard/ask page with the real Warp Speed agent experience. Port the Python FastAPI + Agent SDK backend to TypeScript using @anthropic-ai/agent-sdk and refactor-forge for behavioral parity.

Current state:
- /dashboard/ask = fake AI (canned responses, fuzzy keyword matching)
- /dashboard/warp-speed = real Agent SDK (WebSocket to Python backend, 4 tool plugins, session resume)
- Both are in the sidebar already

Migration uses refactor-forge (eidos-agi/refactor-forge) — golden fixtures prove identical behavior.

Phase 1 — Frontend swap (30 min, zero backend risk):
1. Replace /dashboard/ask/page.tsx with warp-speed's page.tsx
2. Remove /dashboard/warp-speed route
3. Update sidebar: one "Ask Cerebro" entry, remove "Warp Speed"
4. Keep NEXT_PUBLIC_WARP_SPEED_URL pointing at Python service

Phase 2 — Backend port (2-3 days, uses refactor-forge):
1. /refactor-capture on cerebro-warp-speed — record golden fixtures for all 4 plugin suites
2. /refactor-port each plugin: hubspot, sage, identity, insights → TypeScript
3. /refactor-verify — replay fixtures, assert identical output
4. Port agent.py → app/api/ask/route.ts (Agent SDK TypeScript)
5. 1-day streaming spike: prove WebSocket/SSE works in Next.js on Railway
6. Point React component at /api/ask instead of external URL

Phase 3 — Cutover (after 5 business days parallel run):
1. Run both services in parallel for 5 business days — hard gate from Rhea review
2. Archive cerebro-warp-speed repo (keep for reference)
3. Remove NEXT_PUBLIC_WARP_SPEED_URL env var
4. Retire separate Railway service

Rhea ruling: Phase 1 is no-brainer. Phase 2 only if 1-day streaming spike passes. Don't archive Python repo until TS version runs 5 days in prod without incident.
