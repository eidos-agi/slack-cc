# Podcast Styles — Weekly Update Audio Generation

This file defines podcast styles for NotebookLM audio generation. Each style produces a different `-notebooklm.md` file with tailored instructions and context emphasis.

## How It Works

1. The `/weekly-update` skill generates the weekly report (Stages 1-7) as usual
2. At Stage 8, Daniel chooses a podcast style (or gets the default)
3. The skill writes `YYYY-WNN-notebooklm.md` with the style's instructions + full context
4. Daniel uploads to NotebookLM and generates audio

**Style selection:** Daniel says `/weekly-update` (default style) or `/weekly-update --podcast boardroom` (specific style). If no style specified, use `boardroom`.

---

## Style: `boardroom` (DEFAULT)

**Duration:** ~3 minutes
**Audience:** Greenmark leadership (Michael, Alex, Robert) + AIC (William, Collin)
**Tone:** Professional but approachable. Like a Monday morning briefing over coffee.
**Format:** Two hosts — one plays the strategic lead, the other asks clarifying questions

### NotebookLM Instructions (paste into front-matter)

```
Generate a 3-minute audio overview. Two hosts discuss the weekly progress of a technology project at a waste management company.

Host 1 is the informed narrator — they know the details and tell the story. Host 2 is the engaged questioner — they represent the executive audience, asking "wait, what does that mean?" and "why does that matter?" when things get technical.

Structure:
1. Open with the headline: what's the single biggest thing that happened this week? (15s)
2. Where we were — what was the starting position? What was blocked? (30s)
3. Where we are now — walk through the progress, lead with outcomes not code (60s)
4. Where we're going — next priorities, what the audience should expect (45s)
5. Blockers — who needs to do what, by when? Name names. (30s)
6. Close with: task tracking is in GitHub for now, moving to Wrike or Cerebro as the project matures. (10s)

Rules:
- Never say "API" without briefly explaining what it means in context
- Use analogies for technical concepts (e.g., "think of it like a read-only security camera on the CRM")
- Name real people — this is a small company update, not a generic report
- If something is blocked, say who can unblock it and what the timeline is
- Sound like two people who care about the project, not news anchors
```

### Context Emphasis
- Lead with outcomes ("we can now read all CRM data" not "we mapped 36 OAuth scopes")
- Include the narrative arc (blocked → unblocked → what's next)
- Name all stakeholders and their roles
- Include the safety-first theme if security work happened
- Always include last week's context for "where we were"

---

## Style: `deep-dive`

**Duration:** ~8-10 minutes
**Audience:** Daniel (for review), technical stakeholders, future engineers
**Tone:** Two engineers talking through the week's work. Detailed but not dry.
**Format:** Two hosts — both are technical, one walked the path and one is catching up

### NotebookLM Instructions

```
Generate an 8-10 minute technical deep dive. Two engineers discuss the week's work on a data integration project for a waste management company.

Host 1 is the engineer who did the work — they explain what they built, what they discovered, and what tripped them up. Host 2 is a sharp peer reviewer — they ask "why did you do it that way?", "what alternatives did you consider?", and "what would break if X happened?"

Structure:
1. Context: what project is this, what are we building, why? (60s)
2. Walk through each major work item: what was the problem, what was tried, what worked (3-4 min)
3. Interesting technical discoveries — things that surprised you or changed the plan (90s)
4. Architecture and design decisions — what patterns emerged, what's the connector going to look like (90s)
5. What's the critical path? What's blocked and why? (60s)
6. If you were starting this next week from scratch, what would you do differently? (30s)

Rules:
- Use real tool and API names (HubSpot REST API, PAK, Private App, data-daemon)
- Explain gotchas in detail — these are lessons for future engineers
- When discussing security, explain the actual threat model, not just "we followed best practices"
- Reference specific numbers (36 scopes, 369 properties, 9 commands in the wrapper)
- It's okay to be nerdy — the audience chose the deep dive on purpose
```

### Context Emphasis
- Include ALL technical details from the report
- Pull from EXPLORATION.md and task implementation notes
- Include error messages, workarounds, and dead ends
- Emphasize the "what I learned" angle
- Include dependency chains and critical path analysis

---

## Style: `momentum`

**Duration:** ~2 minutes
**Audience:** The team (Daniel, William, Collin) — internal AIC
**Tone:** High energy. Celebrate wins, acknowledge blockers, set the tempo for next week.
**Format:** Single narrator — fast-paced, punchy, like a sports highlight reel

### NotebookLM Instructions

```
Generate a 2-minute high-energy progress update. Single narrator style — fast-paced, punchy, celebrating wins and calling out what's next.

Think of it like a sports highlight reel for an engineering team. Every win gets a moment. Every blocker gets called out with a "here's how we fix it." The energy should make the listener feel like the project is moving fast and the team knows what they're doing.

Structure:
1. Cold open: "This week at Greenmark..." — hit the biggest win immediately (10s)
2. Speed round: every completed task gets ONE sentence (30s)
3. The highlight play: the most impressive or surprising thing that happened, told as a mini-story (30s)
4. Blocker check: what's stuck, who's up, how long (20s)
5. Next week preview: top 3 priorities, teaser style (20s)
6. Close: one-liner that captures the week's theme (10s)

Rules:
- No jargon unless you immediately translate it
- Every task completion is a WIN — frame it that way
- Blockers aren't problems, they're "what's between us and next week's wins"
- Use contrast: "Last week we couldn't even log in. This week we've mapped every data point in the CRM."
- Keep it moving — if a sentence doesn't earn its spot, cut it
```

### Context Emphasis
- Wins list — every Done task, every milestone
- Before/after contrasts (blocked → unblocked)
- Speed metrics (8 tasks completed, hundreds of API tests)
- Next week teaser items
- Skip detailed technical explanations entirely

---

## Style: `investor`

**Duration:** ~4 minutes
**Audience:** Collin Bird (AIC MD), William Holloway (AIC COO), potential board updates
**Tone:** Measured, ROI-focused, risk-aware. Like a quarterly portfolio review but weekly.
**Format:** Two hosts — one is the project manager, one is the skeptical investor

### NotebookLM Instructions

```
Generate a 4-minute investment update. Two hosts discuss the progress of a technology engagement between AIC Holdings (the technology partner) and Greenmark Waste Solutions (the client).

Host 1 is the project lead — they present progress, milestones, and risk mitigation. Host 2 is the investment committee — they ask about ROI, timeline, burn rate, and what could go wrong.

Structure:
1. Portfolio context: what is this engagement, what's the end state, where are we in the timeline? (30s)
2. This week's milestones: what was delivered, what value does it create? (60s)
3. Risk register: what's blocked, what could go wrong, what's the mitigation? (60s)
4. Resource utilization: is the team working on the right things? Any scope creep? (30s)
5. Client relationship: how engaged is the client? Are they removing blockers? (30s)
6. 30/60/90 outlook: what should we expect in the next month, two months, three months? (30s)

Rules:
- Frame everything in terms of business value, not technical achievement
- "Connected to the CRM API" → "We can now see every customer, deal, and sales interaction"
- Quantify where possible: tasks completed, systems researched, blockers removed
- Be honest about risks — investors hate surprises more than bad news
- Reference the 2+2+2 strategy as the roadmap framework
- Note that Greenmark's president is personally engaged (reduces execution risk)
```

### Context Emphasis
- Milestone completion rate
- Client engagement level (Michael's Teams activity, Alex's responsiveness)
- Blocker aging (how long has each been open?)
- Integration strategy progress (Round 1 of 2+2+2)
- Any scope changes or surprises

---

## Style: `standup`

**Duration:** ~90 seconds
**Audience:** Daniel (self-review), quick catch-up for anyone
**Tone:** No-nonsense. Just the facts.
**Format:** Single narrator — structured as Done / Doing / Blocked

### NotebookLM Instructions

```
Generate a 90-second standup update. Single narrator, structured exactly as: what got done, what's in progress, what's blocked.

This is the shortest possible useful summary. No stories, no context-setting, no analogies. Just the signal.

Structure:
1. "Done this week:" — rapid-fire list of completed items (30s)
2. "In progress:" — what's actively being worked on (20s)
3. "Blocked on:" — what's stuck and who can unblock it (20s)
4. "Next up:" — top 3 priorities for next week (20s)

Rules:
- One sentence per item, max
- Use names: "Waiting on Michael for Sage credentials"
- Skip explanations — if the listener doesn't know what HubSpot is, this isn't for them
- Numbers over words: "8 tasks done, 10 to do, 3 blocked"
```

### Context Emphasis
- Task counts and status changes only
- Blocker owners and timelines
- Next week priorities
- Zero narrative, zero technical detail

---

## Style: `storytime`

**Duration:** ~5-6 minutes
**Audience:** Anyone — including non-technical stakeholders, new team members, or Michael sharing with his team
**Tone:** Narrative. Tell the story of the week like you're explaining it to a smart friend over dinner.
**Format:** Two hosts — one tells the story, one reacts genuinely

### NotebookLM Instructions

```
Generate a 5-6 minute narrative podcast. Two hosts discuss the week's events like they're telling a story to a friend.

Host 1 is the storyteller — they have a gift for making technical work sound interesting and relatable. Host 2 is the friend — they're smart but not technical, and they react with genuine curiosity and the occasional "wait, really?"

Tell the story of the week chronologically. Start with Monday's situation, walk through what happened, and end with where things stand on Friday. Make it a STORY with characters (Michael, Daniel, Alex), conflicts (blocked credentials, login puzzles), breakthroughs (the sandbox idea, hundreds of tests passing), and a cliffhanger (what happens next week).

Structure:
1. Set the scene: "So imagine you're running a waste management company with 15 different software systems..." (30s)
2. Monday's problem: what was blocked, what was the challenge (45s)
3. The journey: how did the team work through it? Include the surprises and pivots (2-3 min)
4. The breakthrough: what clicked, what changed, why does it matter (60s)
5. The cliffhanger: what's coming next week that the listener should care about (30s)

Rules:
- Use character names and real dialogue where possible
- "Michael said 'I can get you a Greenmark email. That's easy.'" — real quotes make it real
- Explain technical concepts through metaphor: "Think of the API like a library card — it lets you READ any book, but you can't rewrite them"
- Build tension before breakthroughs: "They'd been blocked for a week. Then Daniel had an idea..."
- End on anticipation, not summary
```

### Context Emphasis
- Chronological narrative from the report
- Real quotes from Teams/email conversations
- The human elements (Michael's helpfulness, Daniel's safety-first approach)
- Tension/resolution arcs
- Cliffhanger setup for next week

---

## Adding New Styles

To add a style:
1. Add a new `## Style: \`name\`` section to this file
2. Include: Duration, Audience, Tone, Format
3. Write the NotebookLM Instructions block (this gets pasted into the front-matter)
4. Define Context Emphasis (which parts of the report to prioritize)
5. The `/weekly-update` skill will pick it up automatically
