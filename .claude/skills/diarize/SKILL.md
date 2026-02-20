---
name: diarize
description: "Process meeting transcripts into structured project artifacts. Use when the user has a meeting transcript (Fireflies export, Teams VTT, SRT, plain text, or any diarized format) and wants to extract decisions, action items, feature requests, and key quotes into a standardized meeting README. Triggers: '/diarize', 'process this transcript', 'extract meeting notes', 'what did we decide on that call', or when a transcript file is dropped into a meetings/ folder."
---

# Diarize — Meeting Transcript Processor

Extract structured intelligence from meeting transcripts: decisions, action items, feature requests, and key quotes. Output follows the greenmark-planning meeting convention.

## Workflow

### 1. Locate the transcript

Accept a file path argument or look for the most recent unprocessed transcript:
```
meetings/YYYY-MM-DD-*/transcript.{txt,srt,vtt,md}
```

If no README.md exists alongside the transcript, it's unprocessed.

### 2. Load speaker context

Read the cheat sheet before processing:
```
reference/stakeholders/diarize-cheatsheet.md
```

This provides name variants, decision authority, systems owned, and entity context. Use it to:
- Resolve ambiguous speaker names ("Michael" → Michael D. Nguyen, President)
- Validate decisions (does this speaker have authority over this topic?)
- Route action items (who typically owns this system?)

### 3. Detect transcript format

Check file extension and content patterns:

| Pattern | Format | Parser |
|---------|--------|--------|
| `.srt` extension or numbered blocks + `HH:MM:SS,mmm --> HH:MM:SS,mmm` | SRT | Strip sequence numbers and timestamps, join speaker turns |
| `.vtt` extension or `WEBVTT` header + `HH:MM:SS.mmm --> HH:MM:SS.mmm` | VTT | Strip header and timestamps, join speaker turns |
| `Speaker Name` paragraph prefix pattern | Fireflies plain text | Split on speaker name changes |
| `Speaker Name:` prefix per line | Generic diarized text | Split on colon-delimited speaker tags |
| No speaker attribution | Raw text | Flag for user — ask who was speaking |

Confirm detected format with user before proceeding.

### 4. Audit speaker attribution

Before extracting content, scan for attribution problems. Fireflies and other tools often misattribute speakers when multiple people share similar audio profiles.

**Check for:**
- Fewer unique speaker labels than known attendees (e.g., 2 labels but 3 people on the call)
- Finance/accounting statements attributed to a non-finance person
- Statements that contradict a speaker's known role or authority

**If attribution is suspect:**
1. Add a `**Speaker attribution warning**` block after Attendees in the output
2. Use the decision authority matrix from the cheat sheet to infer likely speakers
3. Annotate inferred attributions with *(line N, attributed to X but Y topic = likely Z)*
4. Present the inferred attributions to the user for confirmation before finalizing

This is critical — a misattributed decision changes who owns it.

### 5. Collect metadata

Infer or ask for these fields:
- **Date** — from folder name (`YYYY-MM-DD`) or transcript timestamps
- **Platform** — from transcript content or ask user (Teams, Zoom, etc.)
- **Title** — from folder name or first topic discussed
- **Attendees** — extract unique speaker names from transcript, cross-reference cheat sheet for roles
- **Duration** — estimate from timestamp range or transcript length (~150 words/minute of conversation)
- **Recording source** — ask if not obvious

### 6. Extract structured content

Process the full transcript and extract four categories. See `references/extraction-guide.md` for signal words, quality checks, and examples. When speaker attribution was flagged in step 4, use inferred attributions during extraction but annotate them.

**Categories:**
1. **Decisions** — commitments made with consensus. Need: title, who decided, exact quote, implications.
2. **Action items** — specific tasks with owners. Need: description, owner, status, dependencies.
3. **Feature requests** — aspirational ideas, not committed work. Need: name, description, requester.
4. **Key quotes** — memorable lines that capture priorities or sentiment. Max 5-7.

### 7. Check existing project state

Before generating, scan `projects/` checklists to enrich action item statuses:
- If an extracted action item already appears in a project checklist, inherit its current status (e.g., "In progress" not "Pending")
- If a project already exists for a topic discussed, link to it
- This prevents the README from showing stale statuses when work has already begun

### 8. Generate README.md

Use the template in `references/output-template.md`. Write to the same folder as the transcript:
```
meetings/YYYY-MM-DD-title/README.md
```

### 9. Gather external context

The transcript only captures what was said on the call. Ask the user:

> "Is there anything from outside this transcript I should add? Examples:
> - Email chains or follow-up decisions after the call
> - How the transcript was obtained (chain of custody)
> - Process improvements for future recordings
> - Context only you would know (e.g., 'similar code already exists at AIC')"

Add responses to the appropriate sections:
- Chain of custody → "How We Got This Transcript" section (add if provided)
- Follow-up action items → append to action items table
- Process improvements → checklist items under transcript status
- Institutional context → inline notes on relevant decisions or features

### 10. Review with user

Present a summary of what was extracted:
- "Found X decisions, Y action items, Z feature requests, W key quotes"
- Highlight any low-confidence extractions (especially inferred speaker attributions)
- List any action items whose status was updated from project checklists
- Ask if anything was missed

### 11. Route action items (optional)

Scan existing project checklists in `projects/` for keyword matches. Present proposed updates:
```
Suggested checklist updates:
- projects/tech-org-setup/checklist.md: Add "Provision Daniel HubSpot access"
- projects/seo-improvement/README.md: Update blocker status
```

Only update after user approval. Never auto-update project checklists.

## Key Rules

- **Exact quotes only** — decisions and key quotes use the speaker's actual words, not paraphrases
- **Clear ownership** — every action item needs an owner. If unclear, mark "Owner: TBD"
- **Decisions need consensus** — one person saying "we should" isn't a decision. Two agreeing or one authority deciding is.
- **Features vs. actions** — "wouldn't it be cool" = feature request. "I'll do X by Friday" = action item.
- **Flag uncertainty** — if speaker attribution is ambiguous, say so. Don't guess.
- **Preserve the transcript** — never modify the source file. Only create the README alongside it.
