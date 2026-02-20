---
name: diarize
description: "Process meeting transcripts into structured project artifacts. Use when the user has a meeting transcript (Fireflies export, Teams VTT, SRT, plain text, or any diarized format) and wants to extract decisions, action items, feature requests, and key quotes into a standardized meeting README. Triggers: '/diarize', 'process this transcript', 'extract meeting notes', 'what did we decide on that call', or when a transcript file is dropped into a meetings/ folder."
---

# Diarize — Meeting Transcript Processor

Extract structured intelligence from meeting transcripts: decisions, action items, feature requests, and key quotes. Output follows the greenmark-planning meeting convention.

## Autonomous by default

This skill runs end-to-end without stopping unless it hits genuine ambiguity. Infer what you can from the transcript, cheat sheet, folder name, and project state. Generate the full README, then present a summary at the end. Only ask the user when:
- Speaker attribution is suspect and you need confirmation on reattributions
- The transcript has no speaker labels at all
- You truly cannot determine who was on the call

Do NOT stop to confirm: format detection, platform, duration, or other metadata you can infer.

## Workflow

### 1. Locate and load

Accept a file path argument or find the most recent unprocessed transcript:
```
meetings/YYYY-MM-DD-*/transcript.{txt,srt,vtt,md}
```

A transcript is unprocessed if no `README.md` exists alongside it.

**If a README already exists:** Do not overwrite. Instead:
- If the user explicitly asked to re-diarize, write to `README-rediarized.md` and note differences
- If the transcript is a corrected version (e.g., `transcript-corrected.srt`), validate the existing README against it and update metadata only
- If unsure, ask the user: overwrite, create a draft, or validate?

Load these references before doing anything else:
```
reference/stakeholders/diarize-cheatsheet.md    — speaker names, roles, authority
reference/glossary/transcription-corrections.md — Fireflies mishearings → correct terms
references/extraction-guide.md                  — signal words, quality checks, edge cases
references/output-template.md                   — README template
```

Apply transcription corrections when generating the README: use canonical spellings in quotes and text, but never modify the original transcript file.

### 2. Detect format and parse

Check file extension and content patterns:

| Pattern | Format | How to parse |
|---------|--------|-------------|
| `.srt` or numbered blocks + `HH:MM:SS,mmm --> HH:MM:SS,mmm` | SRT | Group consecutive blocks by same speaker into turns. Duration = last timestamp minus first. |
| `.vtt` or `WEBVTT` header + `HH:MM:SS.mmm --> HH:MM:SS.mmm` | VTT | Same as SRT after stripping the WEBVTT header. |
| `Speaker Name` paragraph prefix | Fireflies plain text | Split on speaker name changes. Each paragraph = one turn. |
| `Speaker Name:` per line | Generic diarized | Split on colon-delimited speaker tags. |
| No speaker attribution | Raw text | Stop — ask user who was speaking. Cannot proceed without attribution. |

**Long transcripts (>3000 lines):** Read in chunks. For SRT/VTT, you can grep for speaker names first to get a count and distribution, then read sections focused on decision-heavy portions (typically mid-call, after introductions and before wrap-up). Always read the first 200 and last 200 lines for metadata and wrap-up action items.

### 3. Collect metadata and identify attendees

Infer these fields — only ask if truly unknowable:
- **Date** — from folder name (`YYYY-MM-DD`) or transcript header/timestamps
- **Platform** — Greenmark uses Teams. Default to "Microsoft Teams" unless transcript says otherwise.
- **Title** — from folder name. Strip the date prefix.
- **Attendees** — extract unique speaker labels, normalize to canonical names via cheat sheet. Cross-reference: does the cheat sheet list someone who should be on this call but has no speaker label?
- **Duration** — for SRT/VTT: last timestamp minus first. For plain text: estimate at ~150 words/minute.
- **Recording source** — default "Fireflies" unless stated otherwise. Note whose account if known.

### 4. Audit speaker attribution

Now that you know who the attendees are (step 3), check whether everyone is accounted for.

**Red flags:**
- Fewer speaker labels than expected attendees
- Someone mentioned as present ("I got Lannis sitting here with me") but no label for them
- One label covers both financial AND operational topics
- Finance vocabulary ("de minimis", "journal entries", "GL") under a non-finance label

**If attribution is suspect:**
1. Count the gap (e.g., "3 known attendees, 2 labels — who's missing?")
2. Scan for strong reattribution signals (see `references/extraction-guide.md` edge cases)
3. If you find strong signals, note the corrections and proceed
4. If the evidence is ambiguous, stop and ask the user — show the suspect blocks with context
5. Add a **Speaker attribution warning** block in the output

### 5. Extract structured content

Process the full transcript. See `references/extraction-guide.md` for signal words, quality checks, and examples.

**Categories:**
1. **Decisions** — commitments with consensus. Need: title, who decided, exact quote, implications.
2. **Action items** — specific tasks with owners. Need: description, owner, status, dependencies.
3. **Feature requests** — aspirational ideas, not committed. Need: name, description, requester.
4. **Key quotes** — memorable lines revealing priorities or sentiment. Aim for 5-7, fewer is fine for short meetings.

### 6. Enrich from project state and prior meetings

Before generating, scan two sources:

**Project checklists** (`projects/`):
- If an action item already exists in a checklist, inherit its current status
- Link to existing projects where relevant

**Prior meeting READMEs** (`meetings/`):
- Check for earlier meetings with overlapping attendees
- Mark action items that were resolved or superseded by this call
- Link for continuity: "Completed — covered in [Feb 19 call](../2026-02-19-stakeholder-call/README.md)"

### 7. Generate README.md

Use the template in `references/output-template.md`. Write to:
```
meetings/YYYY-MM-DD-title/README.md
```

### 8. Route action items to project checklists

Scan `projects/` checklists for keyword matches. Present proposed updates:
```
Suggested checklist updates:
- projects/tech-org-setup/checklist.md: Add "Provision Daniel HubSpot access"
- projects/seo-improvement/README.md: Update blocker status
```

Always present suggestions. Only apply after user approval.

### 9. Present summary and gather additions

Combine the review step and external context prompt into one:

```
Diarized: X decisions, Y action items, Z feature requests, W key quotes.
[List any low-confidence extractions or inferred attributions]
[List any action items updated from project state]
[List suggested checklist routes from step 8]

Anything to add from outside this transcript? (email follow-ups, chain
of custody, process improvements, context only you'd know)
```

This is the ONE checkpoint. Everything before this runs autonomously.

## Key Rules

- **Exact quotes only** — decisions and key quotes use the speaker's actual words, not paraphrases
- **Clear ownership** — every action item needs an owner. If unclear, mark "Owner: TBD"
- **Decisions need consensus** — one person saying "we should" isn't a decision. Two agreeing or one authority deciding is.
- **Features vs. actions** — "wouldn't it be cool" = feature request. "I'll do X by Friday" = action item.
- **Flag uncertainty** — if speaker attribution is ambiguous, say so. Don't guess.
- **Preserve the transcript** — never modify the source file. Only create the README alongside it.
