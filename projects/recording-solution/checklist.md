# Recording & Transcript Solution - Engineering Checklist
*Gap identified: 2026-02-11*
*Updated: 2026-02-20 — diarize skill scoped*

## Problem
Teams recordings have no transcripts. Only Collin Bird had a Fireflies account for the kickoff call. When transcripts do arrive, processing them into useful project artifacts is manual and inconsistent.

## Getting Transcripts (Infrastructure)
- [x] Get Fireflies transcript from Collin for Feb 19 call — received via Winnie Makama
- [x] Collin approved adding Daniel to AIC Fireflies team (dshanklin@aicholdings.com)
- [x] Get Daniel a Fireflies account and add to AIC company team — Winnie sent invite, Daniel confirmed access
- [ ] Evaluate transcript options for future meetings
  - [ ] Fireflies for all participants?
  - [ ] Enable Teams transcription?
  - [ ] Standardize export format (plain text or markdown, NOT Pages)
- [ ] Implement chosen solution before next meeting

## Processing Transcripts (Diarize Skill)
- [x] Build `/diarize` skill — [scope document](diarize-skill-scope.md)
  - [x] Phase 1: Core extraction (Fireflies text format, MVP) — **tested, iterated, shipped**
  - [ ] Phase 2: Multi-format support (SRT, VTT)
  - [ ] Phase 3: Action item routing to project checklists
  - [ ] Phase 4: Quality scoring and feedback loop
- [x] Test against Feb 19 transcript as regression baseline — 11/11 decisions, 13/14 action items, 6/6 features
- [x] Fix gaps: speaker attribution audit, external context prompt, project state check
