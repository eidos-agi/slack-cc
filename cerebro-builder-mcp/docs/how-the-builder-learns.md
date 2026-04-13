---
title: How the Builder Learns
tags: [learning, serendipity, ariadne, feedback-loop, graduation, knowledge, violin-model]
---

# How the Builder Learns

The builder has three ways of knowing things, and they work together the way human knowledge does.

## Pattern memory — the flinch

When something breaks, the lesson gets saved to Ariadne's pattern memory with trigger words. Next time those words appear in a task, Ariadne warns you before you make the same mistake. This is fast, automatic, and grows over time. It's the "I burned my hand on that stove" layer.

Example: L003 says "JSONB path extraction at query time doesn't scale." Anytime someone writes a task mentioning `jsonb` or `raw_data`, Ariadne flags it.

## Serendipity — the stumble

Every time Ariadne challenges an approach, she also checks the docs knowledge base. If a doc's tags overlap with what you're working on, she surfaces it — "by the way, you might want to read this." Sometimes she also surfaces a random doc you didn't ask for. Like browsing a shelf and noticing something adjacent.

This is how new knowledge enters the builder's awareness. Without it, the builder only knows what it's already been taught. Serendipity starts new threads.

## The feedback loop — learning from browsing

The system watches what happens after a doc is surfaced:

- **Read**: If the agent later calls `docs()` and that doc appears in the results, it's marked as read. The nudge worked.
- **Graduated**: If the agent calls `ariadne_learn()` and the source mentions the doc, the insight moved from the doc into pattern memory. The doc taught the agent something permanent.
- **Ignored**: The agent didn't engage. That's fine — most browsing doesn't lead anywhere.

At the end of each session, these signals get written to the session log. At the start of the next session, the system reads the history and adjusts:

- If the agent reads random docs often → surface more (up to 50%).
- If the agent ignores them → surface less (down to 10%).
- No history → 30% (the starting point).

The rate self-tunes. No configuration needed.

## Graduation — knowledge that moves on

When a doc's insight becomes a pattern memory learning, that doc is "graduated." It doesn't get deleted — it gets deprioritized. The learning now handles the fast path. The doc is still there for deep reference.

But graduation is context-sensitive. A doc that graduated in one context (say, JSONB performance) can resurface in a different context (say, deployment configuration) if the original learning isn't relevant to the new task. Knowledge can have a second life.

## The violin model

Think of each piece of knowledge as a horizontal shape over time — wide where it's actively used, narrow where it's not. New knowledge starts narrow (just surfaced), gets wide as it's used and reinforced, and tapers as it gets superseded or stops being exercised.

Some knowledge stays wide for years. Some is briefly useful and tapers fast. Some gets wide again later when a skill you thought you'd moved past becomes relevant in a new context.

The builder's capability at any moment isn't everything it's ever learned. It's the cross-section of all these shapes at the current time — some wide, some tapering, some just starting. Serendipity starts new ones. Graduation widens them. Decay lets them taper gracefully.

## In practice

None of this requires the agent to do anything special. It works by working:

1. `convene()` — session starts, serendipity stats from last session are reported
2. `ariadne()` — before a task, patterns fire + docs surface + Rhea reasons
3. `docs()` — agent reads what looks useful (implicit read signal)
4. `ariadne_learn()` — agent saves what it learned (implicit graduation signal)
5. `adjourn()` — session closes, signals written to the log, existing learnings surfaced for reflection

The builder doesn't study. It learns by doing.
