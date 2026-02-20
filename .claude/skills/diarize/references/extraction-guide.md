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

**Example from Feb 19 call:**
```markdown
### 1. Sage Intacct + HubSpot are the first two data sources
- Michael: "Sage makes sense, right, Alex?" — confirmed
- Alex agreed (HubSpot second)
- Michael explicitly said **don't worry about WAM**
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

**Output format:**
```markdown
| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | Provision Daniel a Sage Intacct user account | Alex Kaye | Pending |
| 2 | Create read-only API key in Sage | Daniel | Blocked on #1 |
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

**Example:**
```markdown
- **Customer + prospect map in Cerebro** — separate page, shows HubSpot customers
  and prospects on a map, color-coded by deal pipeline stage.
  Michael: "The sales guys drive around a lot."
  Alex: "Plan my week for me, yo."
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
- Max 5-7 quotes per meeting. Be selective.
- Not every sentence — just the ones that capture the spirit
- Prefer quotes that would be useful in future planning ("this is what Michael cares about")

**Example:**
```markdown
> **Michael on WAM:** "I think it's still living in the 80s. It's like a DOS interface."
> **Alex on AI future:** "Plan my week for me, yo."
```

## Edge Cases

### Fireflies misattributes multiple speakers to one label
This is common when two speakers have similar audio profiles or when Fireflies can't distinguish remote participants. Signs:
- Only 2 speaker labels but 3+ known attendees
- One label covers both financial AND operational topics (likely two different people)

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

### Action items from outside the transcript
Some action items arise from email chains, follow-up conversations, or institutional knowledge that isn't in the transcript. The skill's "Gather external context" step (step 9) catches these. Mark them distinctly so reviewers know the source.

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
