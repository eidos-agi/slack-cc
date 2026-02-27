---
id: TASK-34
title: >-
  Cerebro AI sidebar — OpenAI Realtime API conversational drawer with orb
  trigger
status: To Do
assignee: []
created_date: '2026-02-27 00:31'
updated_date: '2026-02-27 00:43'
labels:
  - cerebro
  - ai
  - ux
  - feature
  - openai-realtime
dependencies: []
references:
  - cerebro/components/layout/header.tsx
  - cerebro/components/claude-drawer.tsx
  - Reeves-Web orb implementation
  - 'https://platform.openai.com/docs/guides/realtime'
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a full-height AI conversation drawer to Cerebro, accessible from a button/orb in the top header bar. Powered by **OpenAI Realtime API** for low-latency, streaming conversational interaction.

**Backend approach (updated):**
- Use OpenAI Realtime API key for the conversational backend
- This sidesteps the "no Anthropic SDK" constraint entirely — OpenAI Realtime provides streaming, low-latency responses natively
- WebSocket connection from client or via Next.js API route to OpenAI Realtime endpoint
- Supports voice + text modalities if we want voice later

**Key behaviors:**
- Trigger button/orb lives in the top Header bar (components/layout/header.tsx)
- Full-height drawer from the right edge, distinct from DetailPanel
- Conversational UI — chat-style messages with streaming responses
- Context-aware: passes page context snapshot with each message (route, filters, visible KPIs, widgets)
- Persists across page navigation within /dashboard (mounted in layout.tsx)
- DashboardContextProvider collects current route + filters + visible widget summaries

**MVP build sequence:**
1. UI first — orb trigger, right drawer, chat transcript + input, suggested prompts by route
2. Context snapshot plumbing — global provider collecting route + filters + KPI summaries
3. OpenAI Realtime WebSocket adapter — streaming responses, timeout + error handling
4. Optional: conversation storage in Supabase for audit/history
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AI orb/button visible in the top header bar on all dashboard pages
- [ ] #2 Clicking opens a full-height conversational drawer from the right
- [ ] #3 Drawer is taller/wider than the detail panel — distinct visual treatment
- [ ] #4 Chat-style message interface with streaming responses via OpenAI Realtime API
- [ ] #5 Drawer persists across page navigation within /dashboard
- [ ] #6 Page context (route, filters, KPIs) passed with each message
- [ ] #7 Study Reeves-Web orb for interaction patterns and apply similar UX
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Feb 27: Architecture decision — switched from `claude -p` subprocess to OpenAI Realtime API key per user direction. GPT-5.2 second opinion originally recommended mock UI + claude -p, but OpenAI Realtime provides native streaming, lower latency, and avoids the Railway CLI installation complexity. WebSocket-based connection gives real-time feel.
<!-- SECTION:NOTES:END -->
