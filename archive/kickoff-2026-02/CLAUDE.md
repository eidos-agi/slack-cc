# Greenmark Waste Solutions - Kickoff Feb 2026

## Project Context
This repo contains kickoff materials for the Greenmark Waste Solutions engagement (Project Cerebro) starting February 2026. It demonstrates how raw files (.ics, .eml, .docx, recordings) can be organized in a repo for AI-assisted consulting workflows.

## PARA Structure
This repo follows the PARA method (Projects, Areas, Resources, Archive):

- **projects/** - Active deliverables with engineering checklists
  - `data-mockups/` - Business monitoring dashboards promised in kickoff
  - `recording-solution/` - Fix the transcript gap
  - `tech-org-setup/` - Greenmark as separate tech org
  - `warehouse-strategy/` - Long-haul yard/warehouse planning
- **areas/** - Ongoing responsibilities
  - `meetings/` - One folder per meeting, containing ALL related artifacts (.ics, .eml, notes, recordings, transcripts)
  - `stakeholders/` - People, org charts, contact info
  - `correspondence/` - Ongoing comms not tied to a specific meeting (Slack exports, etc.)
- **resources/** - Reference material still in active use
  - `research/` - Gap analysis, infra repo design, SRT diarization process
- **archive/** - Completed/inactive items
  - `initial-research/` - Discovery-phase docs now superseded by the infra repo (company profile, deep dive, infra map)

## Meeting Folder Convention
Each meeting gets its own folder under `areas/meetings/` named `YYYY-MM-DD-short-description`. Everything related to that meeting lives together:
- Calendar invite (.ics)
- Email thread that set it up (.eml)
- Pre-read documents (.docx, .pdf)
- Recording and transcript (when available)
- README.md summarizing attendees, outcomes, and action items

## Conventions
- Raw source files (.ics, .eml, .docx, .pdf, .mp3) live alongside the context they belong to
- AI-generated analysis and summaries go in `resources/research/`
- Each project folder contains a `checklist.md` with engineering tasks
- Follow the global CLAUDE.md constraints (soft deletes, no direct Anthropic API, etc.)
