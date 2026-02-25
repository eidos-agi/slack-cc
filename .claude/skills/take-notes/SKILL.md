---
name: take-notes
description: "Capture and process raw notes about Greenmark activity. Use when Daniel says 'take notes', 'process notes', 'note this', or '/take-notes'. Offers clipboard capture (pbpaste) for guaranteed fidelity, or can process an existing file from notes/."
---

# Take Notes — Raw Capture + Processing

Capture raw notes with guaranteed fidelity, then extract actionable intelligence.

## Workflow

### 1. Ask how to capture

When triggered, prompt Daniel with `AskUserQuestion`:

```
Question: "How are your notes coming in?"
Options:
  - "Grab from clipboard" — I copied my notes already, grab them with pbpaste (recommended)
  - "Already saved a file" — I dropped a file in notes/ manually, just process it
  - "I'll paste in chat" — I'll type/paste right here (note: LLM sits between input and file, minor fidelity risk)
```

### 2a. Clipboard capture (recommended path)

Generate the filename via Bash:
```bash
pbpaste > "notes/$(date +%Y-%m-%d_%H%M%S)_$(printf '%04d' $((RANDOM % 10000))).md"
```

Format: `YYYY-MM-DD_HHMMSS_XXXX.md` where XXXX is a 4-digit random number. This avoids collisions and sorts chronologically.

This writes clipboard contents directly to disk. No LLM in the path. Every character preserved.

Then read the file back to confirm it saved and show Daniel a preview (first ~10 lines) so he can verify it looks right before processing.

### 2b. Existing file path

Look for the most recent unprocessed file in `notes/`:
```
notes/YYYY-MM-DD_*.md
```

A notes file is **unprocessed** if it does NOT contain a `## Processed` section at the bottom.

If no unprocessed file exists, tell Daniel and suggest clipboard capture instead.

### 2c. Chat paste fallback

If Daniel pastes in chat, save to `notes/YYYY-MM-DD_HHMMSS_XXXX.md` with a header noting the capture method:

```markdown
<!-- Captured via chat paste — minor fidelity risk vs. direct file write -->
```

Then proceed to processing.

### 3. Read the raw notes

Read the file. Never modify the original content above the processing separator.

### 4. Process and extract

From the notes, extract:

1. **Status updates** — what happened, what changed
2. **Decisions made** — anything committed to
3. **Action items** — tasks with owners if identifiable
4. **Blockers or risks** — anything stalled or at risk
5. **New information** — contacts, credentials provisioned, vendor updates, timeline changes

### 5. Append processing results

Append a `## Processed` section to the bottom of the notes file (below the raw content):

```markdown

---

## Processed

**Processed by:** Claude
**Date:** YYYY-MM-DD

### Status Updates
- ...

### Decisions
- ...

### Action Items
- [ ] ...

### Blockers / Risks
- ...

### New Information
- ...
```

This marks the file as processed and keeps raw + extracted together.

### 6. Route extracted items

Check these locations for updates needed:

- **`decisions/`** — if any significant decisions were captured
- **`projects/`** — if action items map to active project checklists
- **`reference/`** — if new reference info was learned (contacts, systems, etc.)
- **`backlog/`** — if tasks should be tracked

Present a summary:
```
Processed: notes/YYYY-MM-DD-NNN.md

Extracted:
- X status updates
- Y action items
- Z decisions

Suggested routes:
- [list where items should go, with specifics]

Want me to apply these updates?
```

### 7. Apply updates (only after approval)

Only update project files, decisions, or backlogs after Daniel confirms.

## Key Rules

- **Raw notes are sacred** — never modify the original content Daniel wrote
- **Clipboard is the default** — `pbpaste` goes straight to disk, no LLM in the path
- **Chat paste is the fallback** — if used, note the fidelity tradeoff in the file header
- **Date everything** — every note file is dated
- **Filename format** — `YYYY-MM-DD_HHMMSS_XXXX.md` (timestamp + 4-digit random). No sequential numbering needed.
- **Don't over-extract** — if the notes are casual ("talked to Alex, he's good"), just note the status update. Not everything is an action item.
- **Append, don't overwrite** — processing results go at the bottom, raw stays at the top
- **Preview before processing** — after clipboard capture, show Daniel a preview so he can verify before extraction begins
