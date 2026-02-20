# Why We Refine Before We Ship

How Greenmark builds AI systems that reliably turn meetings into tracked work — and why skipping the calibration phase would produce an accountability system nobody trusts.

## The Problem With "Just Ship It"

We're building a pipeline where AI processes meeting recordings into decisions, action items, and status updates. If that pipeline misattributes a decision to the wrong person, drops an action item, or assigns it to the wrong owner, the output is worse than useless — it actively misleads.

An AI skill that's 80% accurate sounds good until you realize that means 3 out of 14 action items from a single meeting are wrong. Over a quarter of work items could be missing, duplicated, or assigned to the wrong person. Nobody would trust that system, and they shouldn't.

**The only way to get from 80% to reliable is to run the system on real data, study why it fails, and fix the root causes.** Not once — repeatedly, on different inputs.

## What Happens Without Refinement

If we had shipped the meeting processing system after the first draft:

| What would go wrong | Why |
|---------------------|-----|
| **Lannis's decisions attributed to Michael** | Fireflies merges speakers who share a microphone. Lannis and Michael sit in the same office. Without a detection pattern, every decision Lannis makes gets assigned to Michael. |
| **Missing attendees not flagged** | The system checked speaker attribution before identifying who was in the meeting. You can't catch a missing speaker if you don't know who should be there. |
| **"Navisoft" treated as an unknown system** | Fireflies transcribes "Navusoft" as "Navisoft." Without a corrections glossary, the system can't map it to the right project. |
| **Action items from follow-up emails lost** | The system only looked at the transcript. Action items that came from email chains after the call — like "Add Daniel to AIC Fireflies team" — would be invisible. |
| **Status conflicts between meetings and checklists** | An item marked "Pending" in the meeting notes but "Complete" in the project checklist would go unnoticed. |

None of these problems are visible in a design document. They only surface when you process real Greenmark meetings with real Fireflies transcripts.

## What Refinement Looks Like in Practice

We processed two real meetings through the system: the Feb 11 Project Cerebro kickoff and the Feb 19 stakeholder call. Each run exposed problems. Each fix made the system better for all future meetings.

### Run 1 — Feb 11 kickoff
- **Discovered:** Fireflies labels Lannis as "Lana" and "Lance" on different calls. Blocks 72-82 of the Feb 11 transcript attribute her statements to Michael because they shared a microphone.
- **Detection pattern found:** When a speaker refers to themselves by a different name in third person ("Mike mentioned..."), it means someone else is talking. This is how you catch shared-mic misattribution.
- **Fixed:** Added two misattribution scenarios to the processing rules with real examples.

### Run 2 — Feb 19 stakeholder call
- **Discovered:** The system had no protocol for re-processing a meeting that already had notes. It would overwrite previous work.
- **Discovered:** 31 speaker reattributions were needed in the raw transcript — Alex Kaye's statements were attributed to Michael because Fireflies couldn't distinguish their voices.
- **Fixed:** Added existing-output handling and a validation mode.

### Two iteration cycles
- Reordered processing steps (identify attendees BEFORE checking attribution — obvious in retrospect, invisible in theory)
- Reduced manual approval gates from 4 to 1 (the system was asking for confirmation on things it could safely decide autonomously)
- Built a 7-file glossary of Greenmark-specific terms, all sourced from real transcription errors found during processing

### Results after refinement

| Metric | Before refinement | After refinement |
|--------|-------------------|------------------|
| Decisions correctly captured | Unknown | 11 of 11 (100%) |
| Action items correctly captured | Unknown | 13 of 14 (93%) |
| Speaker misattribution detection | Not handled | 2 documented scenarios with detection patterns |
| Transcription error correction | Not handled | 15 confirmed corrections in glossary |
| Processing time per meeting | ~45 min manual | ~3 min automated |
| Human intervention needed | Rewrites | Minor tweaks |

The one missed action item (93% vs 100%) came from a follow-up email, not the transcript. Once we added a step to incorporate external context, the gap closed.

## The Glossary: Data Quality You Can't Design Upfront

The [Greenmark glossary](glossary/README.md) — 7 files covering transcription corrections, systems, entities, industry terms, financial terms, technology, and people — didn't come from a planning exercise. Every entry came from a real transcription error found while processing real meetings:

| Fireflies transcribes | Correct term | Found in |
|-----------------------|-------------|----------|
| "EIC" | AIC Holdings | Feb 11 transcript |
| "Lana" / "Lance" | Lannis Nicholson | Feb 11 speaker labels |
| "postgraph" | Postgres | Feb 19 transcript |
| "Green Marketway" | Greenmark Waste Solutions | Feb 19 transcript |
| "Navisoft" | Navusoft | Feb 19 transcript |
| "Houlihan Loki" | Houlihan Lokey | Feb 11 transcript |
| "Cerebra" | Cerebro | Feb 19 transcript |

Each correction means the system correctly maps a mangled term to the right project, the right system, the right person — on every future meeting, automatically. Without this glossary, the AI would re-encounter "Navisoft" on the next call and have no idea it means Navusoft.

**This glossary grows with every meeting we process.** That's the compounding return on refinement.

## Why This Matters for Greenmark

### The Wrike lesson

Michael shut down Wrike because operators won't feed a project management system. The cognitive overhead of manually creating tasks, assigning owners, and tracking status is too high for people running a waste company. The system starved from lack of input.

### What we're building instead

A pipeline that feeds off what the team already does — talk. Meetings happen regardless. The pipeline processes them automatically:

```
Record (Fireflies) → Extract (diarize) → Route (task-out) → Verify (reconcile) → Report (brief)
```

But this only works if the extraction is accurate. If the AI misattributes decisions, drops action items, or can't handle Fireflies' transcription quirks, the output is noise. And leadership stops trusting it — just like they stopped trusting Wrike, for different reasons.

### The trust equation

**Trust = accuracy over time.** Every meeting processed correctly builds trust. One bad output — a decision attributed to the wrong person, an action item that went missing — erodes it.

Refinement is how we front-load accuracy so the system earns trust from the first real deployment forward.

## The Process (for future skill development)

1. **Build a draft** from first principles
2. **Run on real data** — the messiest input you have
3. **Study the failures** — not just what's wrong, but WHY the design didn't account for it
4. **Fix the system, not the output** — don't hand-edit results, fix the root cause
5. **Run on different data** — variation exposes overfitting
6. **Study the new failures** — these are more valuable than the first set
7. **Ship when consecutive runs need minimal human editing**

Steps 3 and 6 produce knowledge you cannot get any other way. No amount of upfront design reveals that Fireflies merges speakers who share a microphone. That knowledge only comes from processing real data.

---

*Established Feb 2026 during diarize skill development. Apply this process to every new skill in the [meeting-to-accountability pipeline](../README.md).*
