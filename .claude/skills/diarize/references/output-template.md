# Output Template — Meeting README.md

Use this template for the generated README. Replace placeholders with extracted content. Remove sections that have no content for a given meeting.

---

```markdown
# {MEETING_TITLE} — {DATE_DISPLAY}

**Date:** {YYYY-MM-DD}
**Platform:** {PLATFORM}
**Recording:** {RECORDING_SOURCE}
**Transcript source:** {HOW_TRANSCRIPT_WAS_OBTAINED}
**Duration:** ~{DURATION} min {DURATION_METHOD}

## Attendees
{FOR_EACH_ATTENDEE}
- {NAME} ({ORG} — {ROLE_OR_CONTEXT})
{END_FOR}
- *(Note any partial attendance: "joined briefly", "stepped out", etc.)*

## Transcript Status
- [x] Transcript received
- [x] Converted to standard format
- [x] Decisions extracted
- [x] Action items logged to project checklists

## Artifacts
- `{TRANSCRIPT_FILENAME}` — {DESCRIPTION}
{ANY_OTHER_SOURCE_FILES}

---

## Decisions Made

{FOR_EACH_DECISION}
### {N}. {DECISION_TITLE}
- {SPEAKER}: "{EXACT_QUOTE}" — {CONTEXT}
- {SUPPORTING_DETAILS}
- {IMPLICATIONS_OR_NOTES}
{END_FOR}

## Action Items

| # | Action | Owner | Status |
|---|--------|-------|--------|
{FOR_EACH_ACTION}
| {N} | {ACTION_DESCRIPTION} | {OWNER_NAME} | {STATUS} |
{END_FOR}

## Feature Requests / Future Ideas

{FOR_EACH_FEATURE}
- **{FEATURE_NAME}** — {DESCRIPTION}. {SPEAKER}: "{QUOTE_IF_AVAILABLE}"
{END_FOR}

## Key Quotes

{FOR_EACH_QUOTE}
> **{SPEAKER} on {TOPIC}:** "{EXACT_QUOTE}"
{END_FOR}
```

---

## Template Rules

1. **Section order is fixed** — Metadata, Attendees, Status, Artifacts, Decisions, Action Items, Features, Quotes
2. **Decisions are numbered** — use `### N.` format with descriptive titles
3. **Action items are a table** — columns: #, Action, Owner, Status
4. **Status values:** Pending, Blocked on #N, In progress, Completed, Noted
5. **Quotes use blockquote** — `> **Speaker on topic:** "quote"`
6. **Links to project checklists** — action items that map to existing projects should link: `[plans created](../../projects/project-name/README.md)`
7. **Attendee roles from cheat sheet** — use org and title from `diarize-cheatsheet.md`
8. **Partial attendance noted** — italicized parenthetical: `*(joined briefly)*`
