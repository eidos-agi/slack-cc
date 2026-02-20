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

{IF_SPEAKER_ATTRIBUTION_SUSPECT}
**Speaker attribution warning:** {DESCRIBE_THE_PROBLEM}. Statements attributed to {INFERRED_SPEAKER} below are inferred from context using the decision authority matrix. Verify with attendees.
{END_IF}

## Transcript Status
- [x] Transcript received
- [x] Format detected: {FORMAT_NAME}
- [x] Speaker attribution audited {IF_ISSUES: "— N reattributions inferred, see warning above"}
- [x] Decisions extracted
- [x] Action items logged to project checklists

{IF_CHAIN_OF_CUSTODY_PROVIDED}
## How We Got This Transcript
1. {STEP_1}
2. {STEP_2}
3. {STEP_N}

### Process Improvements Needed
{FOR_EACH_IMPROVEMENT}
- [ ] {IMPROVEMENT}
{END_FOR}
{END_IF}

## Artifacts
- `{TRANSCRIPT_FILENAME}` — {DESCRIPTION}
{ANY_OTHER_SOURCE_FILES}

---

## Decisions Made

{FOR_EACH_DECISION}
### {N}. {DECISION_TITLE}
- {SPEAKER}: "{EXACT_QUOTE}" — {CONTEXT}
  {IF_INFERRED_ATTRIBUTION: "*(line N, attributed to X but Y topic = likely Z per authority matrix)*"}
- {SUPPORTING_DETAILS}
- {IMPLICATIONS_OR_NOTES}
{END_FOR}

## Action Items

| # | Action | Owner | Status |
|---|--------|-------|--------|
{FOR_EACH_ACTION}
| {N} | {ACTION_DESCRIPTION} | {OWNER_NAME} | {STATUS_FROM_PROJECT_CHECKLIST_OR_DEFAULT} |
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

1. **Section order is fixed** — Metadata, Attendees, (Attribution Warning), Status, (Chain of Custody), Artifacts, Decisions, Action Items, Features, Quotes
2. **Decisions are numbered** — use `### N.` format with descriptive titles
3. **Action items are a table** — columns: #, Action, Owner, Status
4. **Status values:** Pending, Blocked on #N, In progress, Completed, Noted. Inherit from existing project checklists when available (step 7).
5. **Quotes use blockquote** — `> **Speaker on topic:** "quote"`
6. **Links to project checklists** — action items that map to existing projects should link: `[plans created](../../projects/project-name/README.md)`
7. **Attendee roles from cheat sheet** — use org and title from `people.md`
8. **Partial attendance noted** — italicized parenthetical: `*(joined briefly)*`
9. **Inferred attributions annotated** — when speaker was reattributed in step 4, add *(line N, attributed to X but Y topic = likely Z)* after the quote
10. **Chain of custody is optional** — only include "How We Got This Transcript" if user provides this context in step 9
11. **External action items marked** — action items added from outside the transcript (step 9) should note their source
