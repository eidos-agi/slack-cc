# Extraction Guide

How to identify and extract each category from a meeting transcript.

## Decisions

**Signal words:** "let's do", "agreed", "confirmed", "that makes sense", "sounds good", "we should go with", "right?", "yes", "I think that's the way", "makes sense"

**Pattern:** Speaker A proposes → Speaker B confirms/agrees → that's a decision.

**Required fields:**
- Numbered title (### N. Title)
- Who proposed, who agreed
- Exact quote showing consensus
- Business context and implications

**Quality checks:**
- Needs at least two people agreeing OR one person with authority deciding (check decision authority matrix in cheat sheet)
- "We should look into X" is NOT a decision — it's a discussion point
- "That thing's living in the 80s" is NOT a decision — it's commentary
- "Sage makes sense, right, Alex?" + "Yes" IS a decision

**Examples:**

*System-specific decision (Feb 19):*
```markdown
### 1. Sage Intacct + HubSpot are the first two data sources
- Michael: "Sage makes sense, right, Alex?" — confirmed
- Alex agreed (HubSpot second)
- Michael explicitly said **don't worry about WAM**
```

*Strategic/phase decision (Feb 11):*
```markdown
### 1. Dashboards first, AI agent second
- Daniel asked whether dashboards or AI agent was more important
- Michael: "That's number one... The AI agent that can answer questions is kind of like phase two."
- Clear phase approach established for the project
```

## Action Items

**Signal words:** "I'll", "can you", "we need to", "let's get", "I'll take care of", "action item", "next step", "follow up on", "send me", "set up", "provision"

**Pattern:** Someone commits to doing something specific, or assigns it to someone.

**Required fields:**
- Action description (specific and concrete)
- Owner (real name, not "someone")
- Status: Pending, Blocked on #N, In progress, Completed
- Dependencies if any (Blocked on #N notation)

**Quality checks:**
- Must have a clear owner. No owner = discussion point, not action item.
- Must be actionable. "Think about X" is too vague unless it's clearly assigned.
- Look for implicit assignments: "Alex, can you..." or "Daniel to do once he has account"

**Examples:**

*Explicit commitment (Feb 19):*
```markdown
| 1 | Provision Daniel a Sage Intacct user account | Alex Kaye | Pending |
| 2 | Create read-only API key in Sage | Daniel | Blocked on #1 |
```

*Wrap-up commitment (Feb 11):*
```markdown
| 3 | Send follow-up email with next steps (within the hour) | Daniel | Completed |
| 4 | Walk through detailed underlying data tables with Daniel | Alex + Michael | Completed — [Feb 19 call](../2026-02-19-stakeholder-call/README.md) |
```

## Feature Requests / Future Ideas

**Signal words:** "wouldn't it be cool", "in the future", "eventually", "phase 2", "down the road", "what if we", "imagine if", "that would be nice", "bells and whistles"

**Pattern:** Someone describes something they'd want but nobody commits to building it now.

**Required fields:**
- Feature name (bold)
- Description with speaker attribution
- Data source needed (if applicable)

**Quality checks:**
- Distinguish from action items: features are aspirational, actions are committed
- Include enough context that someone reading this in 3 months understands the ask
- Note who brought it up — reveals priorities

**Examples:**

*Feature with quote (Feb 19):*
```markdown
- **Customer + prospect map in Cerebro** — separate page, shows HubSpot customers
  and prospects on a map, color-coded by deal pipeline stage.
  Michael: "The sales guys drive around a lot."
  Alex: "Plan my week for me, yo."
```

*Deferred capability (Feb 11):*
```markdown
- **AI agent for querying data** — Michael: "The AI agent that can answer questions
  is kind of like phase two of all of this." Deferred until dashboards are live.
```

## Key Quotes

**Criteria:**
- Memorable and revealing of priorities or sentiment
- Useful for future context (someone new reading this should understand the culture)
- Shows personality of the speaker
- Captures a strategic insight

**Required fields:**
- Speaker name (bold)
- Topic context ("on WAM", "on AI future")
- Exact quote in blockquote

**Quality checks:**
- Aim for 5-7 per meeting. Fewer is fine for short meetings. Don't pad.
- Not every sentence — just the ones that capture the spirit
- Prefer quotes useful in future planning ("this is what Michael cares about")

**Examples across meeting types:**

*System opinion (Feb 19):*
```markdown
> **Michael on WAM:** "I think it's still living in the 80s. It's like a DOS interface."
```

*Cultural insight (Feb 11):*
```markdown
> **Michael on their business:** "A lot of our business — and you'll love this, Daniel — is still face to face and shaking hands."
```

*Engineering principle (Feb 11):*
```markdown
> **Daniel on engineering:** "Code is easy. Governance is hard."
```

*Self-aware humor (Feb 11):*
```markdown
> **Alex on AI:** "I'm like an elementary school user of it. I'm like, what's two plus two? And I make sure it's worth."
```

## Edge Cases

### Fireflies misattributes multiple speakers to one label
This is common in two distinct scenarios:

**Scenario A: Same room, shared microphone.** Two people in the same physical location share one mic/speaker. Fireflies merges them into one label. This is guaranteed when someone says "I got [name] sitting here with me." All speech from that room gets one label.
- *Feb 11 example:* Michael and Lannis were in the same room. Lannis's entire self-introduction was labeled "Michael Nguyen."

**Scenario B: Similar audio profiles (remote).** Two remote participants sound similar enough that Fireflies can't distinguish them. One gets absorbed into the other's label.
- *Feb 19 example:* Alex Kaye and Michael D. Nguyen were both remote but Alex got no label — all her speech went under Michael's.

**Signs of either scenario:**
- Fewer unique speaker labels than known attendees (e.g., 2 labels but 3 people on the call)
- One label covers both financial AND operational topics (likely two different people)
- Someone mentions another person being "here with me" or "in the room" (Scenario A)

**IMPORTANT: Consecutive blocks from the same speaker label is NOT a signal of misattribution.** SRT format splits continuous speech into 3-5 second chunks. Two "Michael D Nguyen" blocks in a row usually IS the same person still talking. Do not assume that back-to-back same-label blocks mean two different people.

**Strong signals for reattribution (use these, not consecutive blocks):**
1. **Third-person references** — speaker says "Mike said it in his notes" → cannot be Michael, must be someone else referring to him
2. **Explicit name addressing** — Daniel says "Alex, question for you" and the reply is labeled "Michael D Nguyen" → that reply is Alex
3. **Cross-speaker confirmation** — Daniel later says "I love the quote from Alex just there" → the preceding quote was Alex
4. **Topic authority** — Sage provisioning, journal entries, "de minimis" = CFO language; fleet, drivers, Navusoft = operations language
5. **"He/she" pronoun references** — "He had to walk out for a second" when labeled as Michael → speaker is referring to someone else (likely Alex speaking about Michael, or vice versa)

**Weak signals (use only to corroborate strong signals):**
- Topic area (could be anyone asking about any topic)
- Speaking style or vocabulary
- Conversation flow

**Resolution:** Start with strong signals only. Use the decision authority matrix from the cheat sheet for topic-based inference, but only when corroborated by at least one strong signal. Annotate every inferred reattribution with the block number, timestamp, and reasoning.

### Long transcripts (>3000 lines)
SRT files from calls over 45 minutes can exceed 5000 lines. Don't try to load the whole thing at once.

**Strategy:**
1. Grep for speaker names to get counts and distribution
2. Read the first 200 lines (call opening, attendee check, agenda)
3. Read the last 200 lines (wrap-up, action items, next steps)
4. Grep for decision signal words ("agreed", "let's do", "makes sense", "confirmed") to find decision clusters
5. Read around each cluster (±50 lines) for full context
6. Grep for action signal words ("I'll", "can you", "provision", "set up") for action items
7. Read any remaining unvisited sections for feature requests and quotes

This is more work but prevents context overflow and focuses on the high-value content.

### Action items from outside the transcript
Some action items arise from email chains, follow-up conversations, or institutional knowledge that isn't in the transcript. The summary step (step 9) catches these. Mark them distinctly so reviewers know the source.

### Action items from a prior meeting
Check `meetings/` for earlier calls with the same attendees. If a prior README exists, scan its action items — some may have been resolved, updated, or superseded by this call. Link to the prior meeting for continuity:
- "Completed — covered in [Feb 19 call](../2026-02-19-stakeholder-call/README.md)"
- "Superseded by Decision #3 above"

This prevents the same action item from appearing as "Pending" across multiple meeting READMEs when it was actually resolved.

### Someone talks about a topic but no decision is made
Log as context under the most relevant decision, or as a discussion point in a "Notes" section. Don't force it into a decision.

### Same topic discussed multiple times in the call
Consolidate into one decision/action item. Note that it came up multiple times — that signals importance.

### Speaker is joking or being sarcastic
If the joke reveals a real preference or pain point, it can be a key quote. Don't log jokes as decisions.

### Technical details explained at length
Summarize the conclusion, not the explanation. The transcript exists for anyone who wants the full discussion.

### Attendee joins late or leaves early
Note in attendees section: "*(Collin Bird joined briefly but stepped out)*"

### Fireflies uses inconsistent speaker name formats
The same person may appear as different labels across meetings:
- "Michael Nguyen" vs "Michael D Nguyen"
- "Collin Bird - AIC" (with org suffix) vs "Collin Bird"
- "Alex Kaye" vs "Alex K"
- "Lannis Nicholson" vs "Lance" vs "Lana" (Fireflies mishearings)

Always normalize to the canonical name from the cheat sheet. Don't assume different labels mean different people.
