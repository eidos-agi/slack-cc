# Diarize Skill — Scope Document

**Status:** Phase 1+2 complete — tested on both SRT and plain text, iterated twice
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
The skill loads `reference/glossary/people.md` before processing. This provides:
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

### Interactive Flow (autonomous by default)

1. **Locate + load:** Find transcript, load cheat sheet and guides
2. **Parse:** Detect format automatically, parse into speaker turns. Handle long transcripts by chunking.
3. **Metadata:** Infer date, platform, attendees, duration. Only ask if truly unknowable.
4. **Attribution:** Now that attendees are known, audit for misattribution. Stop only if evidence is ambiguous.
5. **Extract:** Process transcript — decisions, action items, features, quotes
6. **Enrich:** Inherit statuses from project checklists and prior meeting READMEs
7. **Save:** Write README.md to `meetings/YYYY-MM-DD-short-description/`
8. **Route:** Suggest action item updates to project checklists
9. **Summary:** Present extraction counts + gather any additions from outside the transcript. This is the ONE checkpoint.

### What the Skill Does NOT Do

- Does not record meetings (that's Fireflies/Teams)
- Does not convert audio to text (that's speech-to-text)
- Does not auto-update project checklists without approval
- Does not summarize — it extracts structured data with exact quotes

---

## Technical Approach

### Approach: Repo-Local Skill in greenmark-planning

The skill lives in the greenmark-planning repo itself — available to anyone with a Claude sidebar open on this repo.

**Location:** `greenmark-planning/.claude/skills/diarize/SKILL.md`

**How it works (9-step workflow, autonomous by default):**
1. Locate transcript + load speaker context + extraction guide
2. Detect format and parse (SRT, VTT, Fireflies text, generic)
3. Collect metadata and identify attendees (infer, don't ask)
4. Audit speaker attribution (now AFTER attendees are known)
5. Extract decisions, action items, feature requests, key quotes
6. Enrich from project state and prior meetings
7. Generate `README.md` in the meeting folder
8. Route action items to project checklists (present suggestions, apply with approval)
9. Present summary + gather additions (the ONE checkpoint)

**Why repo-local:**
- Anyone on the Greenmark Claude Team can use it (Michael, Alex, Daniel)
- Skills travel with the repo — no separate installation
- Version-controlled alongside the meeting conventions in CLAUDE.md
- Can be promoted to a taskr skillflow later if it proves valuable across repos

---

## Implementation Phases

### Phase 1: Core Extraction (MVP) — COMPLETE

- [x] Create skill definition in `greenmark-planning/.claude/skills/diarize/SKILL.md`
- [x] Support Fireflies plain text format (our primary input)
- [x] Extract: decisions, action items, feature requests, key quotes
- [x] Generate README.md following the Feb 19 gold standard template
- [x] Test against the Feb 19 transcript (known-good baseline)
- [x] Fix gaps found in testing: speaker attribution audit, external context prompt, project state check

### Phase 2: Multi-Format Support — COMPLETE

- [x] SRT parser — tested on Feb 11 kickoff (clean attribution) and Feb 19 stakeholder call (corrected attribution)
- [x] Format auto-detection — extension + content pattern matching
- [x] Tested on both transcripts in repo
- [ ] VTT parser — not yet tested (no Teams VTT transcript available yet)

### Phase 3: Action Item Routing

- [ ] Scan existing project checklists for keyword matches
- [ ] Present suggested checklist updates for human approval
- [ ] Update CLAUDE.md with the skill's conventions
- [ ] Consider promoting to taskr skillflow

### Phase 4: Quality & Learning

- [x] Compare skill output to manual extraction (Feb 19) — measure recall (**done: see test results below**)
- [ ] Add confidence scoring for extractions ("high/medium/low confidence this is a decision")
- [ ] Build feedback loop: user edits README → skill learns what it missed
- [ ] Devlog the methodology as a reusable pattern

---

## Test Results (Feb 19 Regression Test)

Ran the skill against the Feb 19 transcript and compared output to the manually-created README.

| Category | Manual | Skill | Match |
|----------|--------|-------|-------|
| Decisions | 11 | 11 | **11/11 (100%)** |
| Action items | 14 | 13 | **13/14 (93%)** |
| Feature requests | 6 | 6 | **6/6 (100%)** |
| Key quotes | 6 | 6 | **6/6 (100%)** |

**What the skill did better than manual:**
- Elevated "Sage is the system of record" as Decision #1 automatically (manual pass initially buried it)
- Flagged the Fireflies speaker attribution problem with a warning block
- Added line-number citations for inferred speaker reattributions

**What the skill missed:**
- 1 action item ("Add Daniel to AIC Fireflies team") — came from email correspondence after the call, not the transcript → **Fixed by adding step 9: Gather external context**
- "How We Got This Transcript" section — came from human knowledge → **Fixed by step 9**
- SEO status was "In progress" not "Pending" — manual knew work had started → **Fixed by adding step 7: Check existing project state**

**Gaps fixed in iteration:**
1. Step 4: Speaker attribution audit — catches Fireflies misattribution via decision authority matrix
2. Step 7: Project state check — inherits statuses from existing checklists
3. Step 9: External context prompt — catches email follow-ups, chain of custody, institutional knowledge

---

## Success Criteria

1. **Processing a 45-minute transcript takes < 5 minutes** (vs. ~45 min manual) — **MET** (estimated ~3 min with skill)
2. **Captures >= 90% of decisions** found by manual extraction — **MET** (100%)
3. **Action items have correct owners** >= 80% of the time — **MET** (100% for transcript-sourced items)
4. **Output requires minimal editing** — human reviews and tweaks, not rewrites — **MET** (~5 min of tweaks)
5. **Works on the Feb 19 transcript** as a regression test (compare to existing README) — **MET**

## Risks

| Risk | Mitigation | Status |
|------|-----------|--------|
| LLM misattributes decisions to wrong speaker | Step 4: Speaker attribution audit using decision authority matrix + user confirmation | Addressed |
| Transcript format varies even within same tool | Format detection heuristics + fallback to "ask user" | Addressed |
| Action items without clear owners | Flag as "Owner: TBD" rather than guessing | Addressed |
| Feature requests confused with action items | Use signal words + context (aspirational vs. committed) | Addressed |
| Long transcripts exceed context window | Chunk by speaker turns, process in sections, merge results | Not yet tested |
| External context missed | Step 9: Explicit prompt for email chains, follow-ups, institutional knowledge | Addressed |

---

## Open Questions

1. ~~Where does the skill definition live?~~ **Resolved: `greenmark-planning/.claude/skills/diarize/SKILL.md`** — repo-local, travels with the repo
2. **Should it auto-create the meeting folder?** Or expect the user to create `meetings/YYYY-MM-DD-title/` first?
3. ~~How do we handle transcripts with bad speaker attribution?~~ **Resolved: Step 4 (speaker attribution audit) uses the decision authority matrix from the cheat sheet to infer corrections, annotates with line numbers, and asks user to confirm.**
4. **Should the skill also produce a `transcript.md`** (cleaned/normalized version of the input)?
5. **Do we want a "quick mode"** that just extracts action items without the full README?
