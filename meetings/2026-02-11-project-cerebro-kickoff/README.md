# Project Cerebro Kickoff — Feb 11, 2026

**Date:** 2026-02-11
**Platform:** Microsoft Teams
**Recording:** Collin Bird's Fireflies account
**Transcript source:** Daniel downloaded SRT from Fireflies "Greenmark Waste" channel
**Duration:** ~29 min (timestamps 00:00:15 to 00:29:11)

## Attendees
- Daniel Shanklin (AIC — Director of AI & Technology, presenting, screen sharing)
- Michael D. Nguyen (Greenmark — President)
- Alex Kaye (Greenmark — CFO)
- Lannis Nicholson (Greenmark — CRO, in-room with Michael)
- Collin Bird (AIC — Managing Director)
- Luke Huntley (AIC — Engineer, joined remotely)

**Speaker attribution warning:** Lannis Nicholson was in the same room as Michael, sharing a microphone. Fireflies attributed Lannis's self-introduction (blocks 72-82) to "Michael Nguyen." Corrected below based on third-person reference to "Mike" in block 80 — the speaker says "met Mike and William and Colin along the way," which cannot be Michael referring to himself.

## Transcript Status
- [x] Transcript received (SRT from Fireflies)
- [x] Format detected: SRT (431 blocks, 5 speaker labels)
- [x] Speaker attribution audited — 1 cluster reattributed (Lannis's intro, blocks 72-82)
- [x] Decisions extracted
- [x] Action items logged to project checklists

## Artifacts
- `transcript.srt` — Fireflies SRT export (1725 lines, 5 speakers)

---

## Decisions Made

### 1. Dashboards first, AI agent second
- Daniel: "Is a more important thing that you have like an AI agent where you could ask it questions... or is it more important that you have like a standard dashboard set with charts and graphs that are consistent, reliable, updated?"
- Michael: "That's number one... The AI agent that can answer questions is kind of like phase two of all of this. Because most people aren't really... most people aren't used to kind of finding data or getting things that way."
- Clear phase approach: dashboards are the deliverable, AI Q&A comes later.

### 2. First deliverable: infrastructure map in GitHub
- Daniel showed the AIC `infra` repo as an example and proposed: "I think probably one of the first projects I would ask us to do is to build out this infra chart based on everything that you've provided to us as Project Cerebro."
- Daniel: "That would actually be my first suggestion. Because then we could come back and have a meeting in a day or two and I could say, does this match your expectation?"
- Michael agreed.

### 3. Build prototype dashboards for quick feedback
- Daniel: "We could just build like two or three fake dashboards, like now, if you want. And then just turn around and be like, what do you like and what do you not like?"
- Michael: "Yeah."
- Collin reinforced: "Keep our eye on the task at hand... get this KPI dashboard figured out... one thing at a time and keep kind of peeling back the next opportunity to become more efficient."

### 4. Get Claude set up for Greenmark
- Michael: "I didn't mention anything kind of about Claude kind of in this, and I imagine like it would be kind of a piece of all this, so getting Claude set up for Greenmark as well."
- Daniel: "Understood."

### 5. Data quality and audit trails are core requirements
- Michael: "Having warnings kind of come up, like, if things aren't loading correctly, if there's errors... that's kind of the big piece for us is like having a good audit trail."
- Michael: "We're a kind of trust but verify type group."
- Daniel confirmed his data quality background in hospital systems and committed to building parallel validation systems.

### 6. Frequent check-ins, process-oriented delivery
- Collin: "Success is wrapping that up in some timeline... completing that and then getting an idea of what the next thing is."
- Michael: "I'm pretty process oriented and we're going to have very frequent check... we won't let you kind of run a steer astray on anything."
- Michael: "Once you wrap your head kind of around this... we'll kind of set some internal goals."

## Action Items

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | Build infrastructure map in GitHub (vendor inventory, API connectivity, costs) | Daniel | Completed — [infra repo](https://github.com/greenmark-waste-solutions/infra) |
| 2 | Build 2-3 prototype dashboards for feedback | Daniel / Luke | Completed — [3 mockups created](../../projects/data-mockups/checklist.md) |
| 3 | Send follow-up email with next steps (within the hour) | Daniel | Completed |
| 4 | Walk through detailed underlying data tables with Daniel | Alex + Michael | Completed — covered in [Feb 19 call](../2026-02-19-stakeholder-call/README.md) |
| 5 | Get Claude set up for Greenmark | Michael | Pending — Michael offered extra seat on Feb 19 call |
| 6 | Set up the data warehouse (database instance, connectors) | Daniel | In progress — [warehouse strategy](../../projects/warehouse-strategy/checklist.md) |
| 7 | Research API connectivity for each vendor system | Daniel | In progress — [vendor research](https://github.com/greenmark-waste-solutions/infra) |
| 8 | Get system access/credentials for vendor APIs | Michael + Alex | In progress — [tech-org-setup](../../projects/tech-org-setup/checklist.md) |

## Feature Requests / Future Ideas (from call)

- **AI agent for querying data** — Michael: "The AI agent that can answer questions is kind of like phase two of all of this." Deferred until dashboards are live.
- **Data quality monitoring system** — Michael wants automated warnings and audit trails. Daniel: "I'm all about building systems outside of the original system. It's a second one that's ugly, but its whole job is to check that the first one is correct." Now the [cerebro-qa](https://github.com/greenmark-waste-solutions/cerebro-qa) repo.
- **Chrome sidebar for dashboards** — Daniel: "If you have a spreadsheet open in your browser and you pull up your Chrome sidebar, you can just say, what do you see here? What are your patterns?" Visual AI analysis of live dashboards.

## Key Quotes

> **Michael on the goal:** "We have a lot of different systems that do a lot of different things and have a lot of different data. We want to take all that data and put it into kind of a single database where we can kind of build real time dashboards off of them."

> **Michael on their business:** "A lot of our business — and you'll love this, Daniel — is still face to face and shaking hands."

> **Michael on trust:** "We're a kind of trust but verify type group."

> **Collin on success:** "Keep our eye on the task at hand... one thing at a time and keep kind of peeling back the next opportunity to become more efficient."

> **Daniel on engineering:** "Code is easy. Governance is hard."

> **Alex on AI:** "I'm like an elementary school user of it. I'm like, what's two plus two? And I make sure it's worth."

> **Lannis on background:** *(attributed to Michael in transcript, corrected here)* "Started my own company with one truck and one container and built into something pretty special."
