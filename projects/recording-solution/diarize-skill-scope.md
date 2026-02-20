# Diarize Skill — Scope Document

**Status:** Scoping
**Owner:** Daniel Shanklin
**Origin:** Feb 19 session — "I'd LOVE a diarizing skill of some kind we can work on together"

## Problem

Meeting transcripts arrive in various formats (Fireflies export, Teams VTT, raw text). Processing them into useful project artifacts is manual and inconsistent. The Feb 19 stakeholder call took ~45 minutes of Claude time to fully extract decisions, action items, feature requests, and key quotes. A reusable skill would make this repeatable and consistent.

## What "Diarize" Means Here

Not just speaker attribution (the traditional meaning of "diarization") — this is **full meeting intelligence extraction**:

1. **Parse** any transcript format into normalized speaker-attributed text
2. **Extract** structured information: decisions, action items, feature requests, key quotes
3. **Generate** a standardized meeting README following our convention
4. **Route** action items to existing project checklists (optional, human-approved)

## Reference Implementation

The gold standard is `meetings/2026-02-19-stakeholder-call/README.md` — produced manually during the Feb 19 session. That output format is the target.

---

## Input Formats to Support

### Priority 1 (what Greenmark actually uses)

| Format | Source | Extension | Speaker Attribution |
|--------|--------|-----------|-------------------|
| Fireflies plain text | Fireflies export → text | `.txt` | `Speaker Name` prefix per paragraph |
| Fireflies SRT | Fireflies export | `.srt` | `Speaker Name:` prefix, timestamped blocks |
| Teams VTT | Microsoft Teams recording | `.vtt` | Speaker labels, `HH:MM:SS.mmm` timestamps |

### Priority 2 (for broader reuse)

| Format | Source | Extension | Speaker Attribution |
|--------|--------|-----------|-------------------|
| Otter.ai TXT/SRT | Otter export | `.txt`, `.srt` | `Speaker:` prefix |
| Zoom VTT/TXT | Zoom recording | `.vtt`, `.txt` | Speaker labels (VTT) or `Speaker:` prefix (TXT) |
| Google Meet | Google Docs export | `.txt`, `.docx` | Varies |
| Generic SRT | Any source | `.srt` | `Speaker Name:` prefix in subtitle text |

### Format Detection Strategy

1. Check file extension first (`.srt`, `.vtt`, `.txt`, `.docx`)
2. For ambiguous `.txt` files: inspect first 20 lines for patterns
   - SRT-like numbering + timestamps → treat as SRT
   - `Speaker Name:` pattern → Fireflies/Otter plain text
   - `WEBVTT` header → VTT misnamed as .txt
   - Freeform text → raw transcript (no speaker attribution)

---

## Output Format

### Primary Output: `README.md`

Follows the convention established in CLAUDE.md:

```markdown
# Meeting Title — Date

**Date:** YYYY-MM-DD
**Platform:** [Teams/Zoom/etc.]
**Recording:** [source]
**Duration:** ~XX min

## Attendees
- Name (Org — role)

## Transcript Status
- [x] Transcript received
- [x] Converted to standard format
- [x] Decisions extracted
- [x] Action items logged

## Decisions Made

### 1. [Decision title]
- [Speaker]: "[exact quote]"
- [Context and implications]

## Action Items

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | [action] | [name] | Pending |

## Feature Requests / Future Ideas
- **[Feature name]** — [description with speaker attribution]

## Key Quotes
> **[Speaker] on [topic]:** "[memorable quote]"
```

### Secondary Output: Action Item Routing (optional)

After generating the README, suggest updates to existing project checklists:
- Match action items to existing projects by keyword
- Present proposed updates for human approval
- Never auto-update — show diff, let user confirm

---

## Extraction Categories

### Speaker Context
The skill loads `reference/stakeholders/diarize-cheatsheet.md` before processing. This provides:
- Name variants for speaker matching (e.g., "Michael D Nguyen" → Michael D. Nguyen, President)
- Decision authority matrix — who can actually decide what
- Systems owned by each person — for context on technical discussions
- Entity context — NTX vs Hometown vs Memphis references
- Speaker resolution rules for ambiguous labels

### Decisions
**Signal words:** "let's do", "agreed", "confirmed", "that makes sense", "we should", "go with"
**Required fields:** title, who decided, exact quote showing consensus, implications
**Quality check:** A decision needs at least two people agreeing or one person with authority deciding

### Action Items
**Signal words:** "I'll", "can you", "we need to", "let's get", "action item", "next step", "follow up"
**Required fields:** action description, owner, status, dependencies (if any)
**Quality check:** Must have a clear owner. "We should look into X" without an owner is a discussion point, not an action item.

### Feature Requests / Future Ideas
**Signal words:** "wouldn't it be cool if", "in the future", "eventually", "phase 2", "down the road", "what if we"
**Required fields:** feature name, description, who requested it, data source needed
**Quality check:** Distinguish from action items — features are aspirational, action items are committed.

### Key Quotes
**Criteria:** Memorable, reveals priorities/sentiment, useful for future context
**Required fields:** speaker, topic, exact quote
**Quality check:** Max 5-7 quotes. Not every sentence — just the ones that capture the spirit of the meeting.

---

## Skill Interface

### Invocation

```
/diarize [path-to-transcript]
```

Or with metadata:

```
/diarize [path-to-transcript] --date 2026-02-19 --platform "Microsoft Teams" --title "Stakeholder Call"
```

### Interactive Flow

1. **Input:** User provides transcript file path
2. **Detect:** Skill identifies format, shows detected format for confirmation
3. **Metadata:** Skill asks for missing metadata (date, platform, title, attendees) — or infers from transcript content
4. **Extract:** Process transcript through LLM extraction
5. **Review:** Present extracted decisions, action items, features, quotes in draft form
6. **Save:** Write README.md to `meetings/YYYY-MM-DD-short-description/`
7. **Route:** (Optional) Suggest action item updates to project checklists

### What the Skill Does NOT Do

- Does not record meetings (that's Fireflies/Teams)
- Does not convert audio to text (that's speech-to-text)
- Does not auto-update project checklists without approval
- Does not summarize — it extracts structured data with exact quotes

---

## Technical Approach

### Approach: Repo-Local Skill in greenmark-planning

The skill lives in the greenmark-planning repo itself — available to anyone with a Claude sidebar open on this repo.

**Location:** `greenmark-planning/.claude/skills/diarize.md`

**How it works:**
1. User drops a transcript file into `meetings/YYYY-MM-DD-title/`
2. User invokes `/diarize meetings/YYYY-MM-DD-title/transcript.txt`
3. Skill reads the transcript, detects format, normalizes
4. Extracts decisions, action items, feature requests, key quotes
5. Generates `README.md` in the same meeting folder
6. Optionally suggests action item routing to project checklists

**Why repo-local:**
- Anyone on the Greenmark Claude Team can use it (Michael, Alex, Daniel)
- Skills travel with the repo — no separate installation
- Version-controlled alongside the meeting conventions in CLAUDE.md
- Can be promoted to a taskr skillflow later if it proves valuable across repos

---

## Implementation Phases

### Phase 1: Core Extraction (MVP)

- [ ] Create skill definition in `greenmark-planning/.claude/skills/diarize.md`
- [ ] Support Fireflies plain text format (our primary input)
- [ ] Extract: decisions, action items, feature requests, key quotes
- [ ] Generate README.md following the Feb 19 gold standard template
- [ ] Test against the Feb 19 transcript (known-good baseline)

### Phase 2: Multi-Format Support

- [ ] Add SRT parser (Fireflies SRT, generic SRT)
- [ ] Add VTT parser (Teams, Zoom)
- [ ] Add format auto-detection
- [ ] Test against a second real transcript (next stakeholder call)

### Phase 3: Action Item Routing

- [ ] Scan existing project checklists for keyword matches
- [ ] Present suggested checklist updates for human approval
- [ ] Update CLAUDE.md with the skill's conventions
- [ ] Consider promoting to taskr skillflow

### Phase 4: Quality & Learning

- [ ] Compare skill output to manual extraction (Feb 19) — measure recall
- [ ] Add confidence scoring for extractions ("high/medium/low confidence this is a decision")
- [ ] Build feedback loop: user edits README → skill learns what it missed
- [ ] Devlog the methodology as a reusable pattern

---

## Success Criteria

1. **Processing a 45-minute transcript takes < 5 minutes** (vs. ~45 min manual)
2. **Captures >= 90% of decisions** found by manual extraction
3. **Action items have correct owners** >= 80% of the time
4. **Output requires minimal editing** — human reviews and tweaks, not rewrites
5. **Works on the Feb 19 transcript** as a regression test (compare to existing README)

## Risks

| Risk | Mitigation |
|------|-----------|
| LLM misattributes decisions to wrong speaker | Include exact quotes — human reviewer catches misattribution |
| Transcript format varies even within same tool | Format detection heuristics + fallback to "ask user" |
| Action items without clear owners | Flag as "Owner: TBD" rather than guessing |
| Feature requests confused with action items | Use signal words + context (aspirational vs. committed) |
| Long transcripts exceed context window | Chunk by speaker turns, process in sections, merge results |

---

## Open Questions

1. ~~Where does the skill definition live?~~ **Resolved: `greenmark-planning/.claude/skills/diarize.md`**
2. **Should it auto-create the meeting folder?** Or expect the user to create `meetings/YYYY-MM-DD-title/` first?
3. **How do we handle transcripts with bad speaker attribution?** (e.g., "Speaker 1" instead of real names)
4. **Should the skill also produce a `transcript.md`** (cleaned/normalized version of the input)?
5. **Do we want a "quick mode"** that just extracts action items without the full README?
