# SRT Diarization Process

A repeatable process for converting raw .srt recordings into useful, attributed meeting transcripts.

## Inputs Required
1. **Raw .srt file(s)** from the recording (Fireflies, Teams, etc.)
2. **Meeting .ics file** (provides attendee list, time, organizer)
3. **Any pre-meeting correspondence** (.eml, Slack) for additional context

## Step 1: Merge Split Recordings
Recordings often get split into multiple .srt files (e.g., Fireflies segments). Merge them by:
- Checking the "Meeting created at" timestamp in each file header
- Ordering files chronologically
- Adjusting timestamp offsets so the second file continues where the first left off
- Deduplicating any overlapping segments (common at split boundaries)

## Step 2: Identify Speakers
SRT files use anonymous labels ("Speaker 1", "Speaker 2"). Resolve them using:

1. **Self-introductions** - Scan for phrases like "I'm [name]", "this is [name]", "my name is"
2. **Cross-references** - When Speaker X says "Daniel, what do you think?" and Speaker Y responds, Y = Daniel
3. **Role context** - Match what speakers say about their role to the .ics attendee list
4. **Speech patterns** - Organizer typically does most housekeeping ("let me let you introduce yourself")

### Speaker Resolution Template
```
Speaker 1 → [Name] | Evidence: "[quote that identifies them]"
Speaker 2 → [Name] | Evidence: "[quote that identifies them]"
...
```

## Step 3: Produce Clean Transcript
- Replace all "Speaker N" labels with real names
- Merge consecutive lines from the same speaker into paragraphs
- Clean up transcription artifacts (false starts, "um", "uh", repeated words)
- Preserve timestamps at paragraph boundaries for reference
- Flag any segments where speaker attribution is uncertain with [?]

## Step 4: Extract Meeting Intelligence
From the clean transcript, produce:

### Summary (2-3 paragraphs)
High-level overview of what was discussed and decided.

### Attendees & Roles
Table of who was present and their role in the meeting.

### Decisions Made
Bulleted list of decisions with who made them.

### Action Items
| Owner | Action | Deadline | Source Quote |
|-------|--------|----------|-------------|

### Key Quotes
Notable statements worth preserving verbatim (with speaker and timestamp).

### Topics for Follow-Up
Things mentioned but not resolved.

## Step 5: Update Meeting README
Add the diarized outputs to the meeting folder's README.md alongside the raw artifacts.

## Notes
- Always keep the raw .srt files - they're the source of truth
- The diarized transcript is a derived artifact, clearly labeled as AI-processed
- When in doubt about speaker identity, mark as [unidentified] rather than guess wrong
- This process works with any SRT source (Fireflies, Otter, Teams, Whisper, etc.)
