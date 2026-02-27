---
id: TASK-45
title: Video recording + feature request system in Cerebro
status: Done
assignee:
  - Daniel Shanklin
created_date: '2026-02-27 04:14'
labels:
  - cerebro
  - supabase
  - feature
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build a feedback system in Cerebro so Greenmark leadership (Michael, Alex, Robert) can record their screen + camera, describe what's wrong or what they want, and have AI auto-create a feature request.

Record page (/dashboard/feedback/record): Screen + camera recording with PiP overlay. Stop → preview → upload → transcribe → submit.

Feedback list page (/dashboard/feedback): All feature requests with status, playback, transcription text. Daniel reviews and responds.

AI transcription pipeline: Recording → Whisper API → GPT-4o extracts title/description/category/priority → auto-populates the feature request.

First Supabase integration in Cerebro — sets the pattern for all future data connections.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented full video recording + feature request system across 4 slices:

**Slice 1 — Feedback page + Supabase integration**: List page with KPI cards, new request form, detail dialog with status management. Supabase client setup (browser + server), 4 API routes (CRUD + upload + transcribe). Sidebar entry added.

**Slice 2 — Screen + camera recording**: use-media-recorder hook with getDisplayMedia + getUserMedia + canvas PiP compositing (screen as full frame, camera as circle bottom-right). Recording controls (start/stop/pause/timer). Upload to Supabase Storage via signed URLs with XHR progress tracking.

**Slice 3 — AI transcription**: Whisper API transcription + GPT-4o structured extraction (title/description/category/priority). Auto-populate submit form from recording.

**Slice 4 — Polish**: Video playback in detail dialog, status management (new/reviewing/planned/in_progress/done/won't_do), response notes, mobile detection gate.

**Infrastructure**: Supabase project greenmark-cerebro (wwmcgtyngnziepeynccz) connected. feature_requests table with 19 columns. feedback-recordings storage bucket. Migration runner (psycopg2 via Supavisor session-mode pooler). ADR-2026-03 documents migration strategy and 5 gotchas learned.

**Env vars set**: .env.local locally + Railway cerebro service (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY). OPENAI_API_KEY still needed for transcription.
<!-- SECTION:FINAL_SUMMARY:END -->
