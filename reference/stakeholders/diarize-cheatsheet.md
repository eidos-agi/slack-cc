# Diarize Cheat Sheet — Known Meeting Participants

Used by the `/diarize` skill as context when processing transcripts. Helps with speaker attribution, decision authority, and action item routing.

For full org details: [greenmark-org.md](greenmark-org.md)

---

## Greenmark Leadership

### Michael D. Nguyen
- **Title:** President, Greenmark Waste Solutions
- **Also:** Director - Private Equity, AIC Holdings
- **Name variants:** "Michael D Nguyen", "Michael Nguyen", "Michael", "Mike"
- **Email:** mnguyen@greenmarkwaste.com / mnguyen@aicholdings.com
- **Decision authority:** Operations, IT/software, vendor relationships (Navusoft, WAM, 3rd Eye), hiring, business strategy
- **Systems owned:** Navusoft, WAM, 3rd Eye, Wrike, Webflow (both sites)
- **Common topics:** Operations, fleet, drivers, sales team needs, technology adoption, Navusoft transition
- **Meeting behavior:** Asks clarifying questions, confirms with Alex on financial items, often says "that makes sense"
- **Key context:** De facto tech lead at Greenmark. Manages IT and software. Initiated Project Cerebro.

### Alex Kaye, CFA
- **Title:** CFO, Greenmark Waste Solutions
- **Name variants:** "Alex Kaye", "Alex"
- **Email:** akaye@greenmarkwaste.com
- **Decision authority:** Finance, accounting systems, budget approval, system access provisioning (Sage, HubSpot, Paylocity)
- **Systems owned:** Sage Intacct, HubSpot, Paylocity, Expensify, Comerica, AssureHire
- **Common topics:** GL structure, journal entries, cost allocation, entity-level financials, auditor requirements
- **Meeting behavior:** Detail-oriented, thinks about audit implications, wants things flowing through Sage
- **Key context:** "If Sage can be our Rosetta Stone for most things, I'd rather just flow it through Sage."

### Lannis Nicholson
- **Title:** CRO (Partner), Greenmark Waste Solutions
- **Name variants:** "Lannis Nicholson", "Lannis", "Lance" (Fireflies mishearing), "Lana" (Fireflies mishearing)
- **Decision authority:** Sales strategy, revenue operations, pricing
- **Common topics:** Sales pipeline, revenue targets, market expansion, customer acquisition
- **Meeting behavior:** Tends to listen more than speak. On Feb 11 kickoff, introduced herself but was otherwise a passive participant.
- **Key context:** Started career at Waste Management (the company) out of Arkansas. Started own waste company with "one truck and one container," grew it, sold to a mid-market waste company. Previously at LRS and Ramco. Joined AIC/Greenmark ~6 months before Daniel.
- **Attribution note:** Often in-room with Michael, sharing a mic. Fireflies will merge her speech with Michael's. Her Fireflies name varies: "Lana", "Lance" — always check for these misspellings.

### Robert Heath
- **Title:** General Manager, Greenmark Waste Solutions
- **Name variants:** "Robert Heath", "Robert", "Rob"
- **Decision authority:** Fleet operations, field operations, driver management
- **Systems owned:** Fleetio
- **Common topics:** Fleet status, driver productivity, routes, maintenance, daily operations
- **Key context:** Boots-on-the-ground operations leader. Fleetio is his primary system.

---

## AIC Holdings Team

### Daniel Shanklin
- **Title:** Director of AI & Technology, AIC Holdings
- **Name variants:** "Daniel Shanklin", "Daniel", "Dan"
- **Email:** dshanklin@aicholdings.com
- **Role in meetings:** Usually presenting, screen sharing, explaining technical architecture
- **Decision authority:** Technology architecture, data warehouse design, API integrations, code
- **Common topics:** Data pipelines, API access, bronze/silver/gold schemas, Cerebro features, SEO
- **Meeting behavior:** Explains technical concepts in business terms, asks for access/credentials, proposes architecture
- **Key context:** Writes the code, runs the agents. Tech lead for Project Cerebro.

### William Holloway
- **Title:** Partner & COO, AIC Holdings
- **Name variants:** "William Holloway", "William", "Will", "Bill"
- **Role in meetings:** Strategic advisor, typically brief appearances
- **Decision authority:** AIC-level strategy, resource allocation, engagement scope

### Collin Bird
- **Title:** Managing Director, AIC Holdings
- **Name variants:** "Collin Bird", "Collin", "Collin Bird - AIC" (Fireflies label with org suffix)
- **Role in meetings:** Project sponsor, may join briefly
- **Decision authority:** Project approval, budget, AIC team resources
- **Key context:** Owns the Fireflies account where meetings are recorded.

### Luke Huntley
- **Title:** Engineer, AIC Holdings
- **Name variants:** "Luke Huntley", "Luke"
- **Role in meetings:** Technical contributor, joined remotely on Feb 11 kickoff
- **Common topics:** Data warehouse architecture, frontend dashboards, Supabase, connectors
- **Key context:** Worked with Daniel at a startup in North Carolina. Moved to Fort Worth area Sep 2025. Built Sable and Meridian dashboards for AIC (~9 months). Specializes in frontend work — "incredibly good at front end type work" per Daniel.

---

## Support Staff (may appear in email chains / correspondence)

### Winnie Makama
- **Name variants:** "Winnie Makama", "Winnie"
- **Role:** AIC support staff
- **Context:** Handles transcript exports from Fireflies, email correspondence

### Travis
- **Name variants:** "Travis"
- **Role:** AIC/Jetta IT
- **Context:** Dabbles on broader org-hosted IT stuff. Not a regular meeting attendee.

---

## Speaker Resolution Rules

When the transcript has ambiguous speaker labels:

1. **"Speaker 1", "Speaker 2"** — Match by topic. If discussing Sage/financials → likely Alex. If discussing operations/Navusoft → likely Michael. If explaining technical architecture → likely Daniel.
2. **First name only ("Michael")** — Match to the person with that first name in the attendee list.
3. **Misspelled names** — Fireflies sometimes misspells. "Micheal" = Michael. "Daneil" = Daniel. "Lana" or "Lance" = Lannis.
4. **Inconsistent format across meetings** — The same person may appear as "Michael Nguyen" on one call and "Michael D Nguyen" on another. "Collin Bird - AIC" with an org suffix on one, "Collin Bird" on another. Always normalize to canonical names above.
5. **"Unknown Speaker"** — Flag for human review. Don't guess.

## Decision Authority Matrix

Use this to validate whether a decision was actually *decided* or just *discussed*:

| Topic | Who can decide | Who must agree |
|-------|---------------|----------------|
| Financial systems (Sage, Paylocity) | Alex | — |
| Operational systems (Navusoft, WAM, Fleetio) | Michael | — |
| Technology architecture | Daniel | Michael (as tech lead) |
| Budget / spending | Alex + Michael | — |
| Vendor contracts | Michael | Alex (if financial) |
| Hiring / staffing | Michael | — |
| Sales strategy | Lannis | Michael |
| AIC engagement scope | William / Collin | — |
| Data access / API keys | Alex (provisioning) + Daniel (technical) | — |

## Entity Context

Greenmark operates multiple entities. Speakers may reference them differently:

| Entity | Also called | Market |
|--------|------------|--------|
| NTX | "Greenmark", "Dallas", "North Texas" | DFW commercial waste |
| Hometown | "Hometown Disposal", "Indiana", "htdisposal" | Indiana residential waste |
| Memphis | "Memphis" | Nascent — not yet operational |
