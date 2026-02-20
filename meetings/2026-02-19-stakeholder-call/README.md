# Stakeholder Call — Feb 19, 2026

**Date:** 2026-02-19
**Platform:** Microsoft Teams
**Recording:** Collin Bird's Fireflies account
**Transcript source:** Winnie Makama exported from Fireflies → Pages file → plain text
**Duration:** ~45 min (estimated from transcript length)

## Attendees
- Daniel Shanklin (AIC — presenting, screen sharing)
- Michael D. Nguyen (Greenmark — President)
- Alex Kaye (Greenmark — CFO)
- *(Collin Bird joined briefly but stepped out)*

## Transcript Status
- [x] Recording requested from Winnie Makama — 2026-02-20
- [x] Transcript received (Pages format from Fireflies)
- [x] Converted to plain text
- [x] Decisions extracted
- [x] Action items logged to project checklists

## How We Got This Transcript
1. Call recorded to **Collin Bird's Fireflies account** (not Daniel's)
2. Daniel emailed **Winnie Makama** requesting a copy
3. Winnie exported as `Project-Cerebro transcript.pages` (Apple Pages format)
4. Collin Bird approved adding Daniel (dshanklin@aicholdings.com) to AIC Fireflies team

### Process Improvements Needed
- [x] **Get Daniel a Fireflies account** (dshanklin@aicholdings.com) and add to AIC company team — ✓ Winnie sent invite, Daniel confirmed access
- **Export as plain text or markdown** — Pages format required AppleScript conversion
- **Standardize transcript format** — Fireflies does speaker attribution, but format varies by export type

## Artifacts
- `Project-Cerebro transcript.pages` — original file from Winnie
- `transcript.txt` — plain text conversion (320 lines, ~85KB)

---

## Decisions Made

### 1. Sage Intacct + HubSpot are the first two data sources
- Michael: "Sage makes sense, right, Alex?" — confirmed
- Alex agreed (HubSpot second)
- Michael explicitly said **don't worry about WAM** — Hometown transitioning to Navusoft "over the next couple months"
- Michael on WAM: "That thing's still living in the 80s. It's like a DOS interface."

### 2. Greenmark billing should be fully separate from AIC
- Michael: "The way we set up Greenmark was like it was in a separate control group from Jetta and AIC... all this should be separate."
- Applies to: Railway, GitHub (already done), all tech infrastructure
- Railway transfer: Pro account ($20/mo), Daniel to transfer the project
- Michael: "Whatever info that we need can flow from this instance kind of into AIC to kind of feed AIC's databases."

### 3. Michael is the de facto tech lead at Greenmark
- Michael: "At very best and it's weak, that would be me. I manage most of the IT stuff and the software."
- They also have a managed service provider for other IT
- Travis (AIC/Jetta) dabbles on broader org-hosted stuff

### 4. Sage Intacct is the system of record — Cerebro reads, never writes
- Alex: "If Sage can be kind of our Rosetta Stone for most things, I'd rather just kind of flow it through Sage."
- Daniel: "Your auditors will love it... Sage is the system of record. Cerebro just happens to look at it."
- **Architectural principle:** Other systems should flow through Sage where possible, not directly into the warehouse.
- Expensify already flows through Sage — no separate connector needed.
- Comerica does NOT — decision **tabled**, Alex leaning toward flowing through Sage.

### 5. Daniel gets a Sage Intacct user account
- Not just an API key — a full user account so Daniel can create/manage API keys himself
- Alex confirmed cost is "de minimis" for an extra seat
- API key should be **read-only** — no ability to make journal entries
- Daniel: "My recommendation would be that it be a read only key. It should not have the ability to make entries." Alex agreed.

### 6. Daniel gets a seat on Greenmark's Claude Team plan
- Michael: "We still have one seat open. You can have it."
- Email: dshanklin@aicholdings.com
- Enables shared Claude projects between Daniel and Greenmark team
- Note: May need a greenmarkwaste.com email alias — Claude Team requires matching domain

### 7. SEO improvement is a priority — "low hanging fruit"
- Michael: "We need to make these changes to the websites, both Hometown and Greenmark's. That's low hanging fruit. That shouldn't take too long. That should be kind of at the top of the list."
- Both sites built on **Webflow**
- Daniel demo'd PageSpeed Insights live on the call

### 8. Communication preference: email and Teams, not Wrike
- Daniel: "If you want to just do email, I would appreciate that."
- Michael agreed to keep task lists to "five or six big block things"
- Daniel's experience: "Wrike... people don't update it. The tool itself became the thing we were managing."

### 9. Monthly in-person at Greenmark office
- Michael: "In a couple weeks we'll have our new office spaces... that makes sense to kind of meet in person."
- Daniel already suggested to William: "at least a monthly, Daniel works out of Greenmark all day"

### 10. Michael and Alex to create GitHub accounts
- Michael already created his (greenmarkwaste.com email)
- Michael to be made **admin** in the org (same privilege as Daniel)
- Daniel: "If I get hit by a bus, you'll own the code."

### 11. No agentic AI for writes — human approval always
- Daniel: "We don't employ it as an agent yet to do complex work... there is no test for sending an email to the wrong client."
- AI makes entries via sidebar (human-in-the-loop), not autonomously
- Alex's future vision: AI processes PDF invoices → summarizes → creates journal entry → human clicks approve

## Action Items

| # | Action | Owner | Status |
|---|--------|-------|--------|
| 1 | Provision Daniel a Sage Intacct user account (dshanklin@aicholdings.com) | Alex Kaye | Pending |
| 2 | Create read-only API key in Sage (Daniel to do once he has account, with Alex approval on permissions) | Daniel | Blocked on #1 |
| 3 | Provision Daniel a seat on Greenmark Claude Team (dshanklin@aicholdings.com) | Michael | Pending — may need greenmark email alias |
| 4 | Get Daniel HubSpot API access | Alex/Michael | Pending |
| 5 | SEO improvement for greenmarkwaste.com + htdisposal.com | Daniel | In progress — [plans created](../../projects/seo-improvement/README.md) |
| 6 | Transfer Railway project to Greenmark billing (Pro account, $20/mo) | Daniel + Michael | Pending — needs Greenmark Railway account |
| 7 | Make Michael admin in GitHub org | Daniel | Pending — Michael just created account |
| 8 | Alex to create GitHub account | Alex | Pending |
| 9 | Add Daniel to AIC Fireflies team | Winnie/Collin | Complete — Winnie sent invite, Daniel confirmed access |
| 10 | Build customer + prospect map page in Cerebro (from HubSpot data) | Daniel | Noted — after HubSpot connected |
| 11 | Document what's shared vs. Greenmark-only billing (diagram for Alex as CFO) | Daniel | Pending |
| 12 | Get permissions/access matrix from Michael ("who gets permission to what") | Daniel | Pending |
| 13 | Monthly in-person at Greenmark office | Daniel + Michael | Pending — new office opening in ~2 weeks |
| 14 | Keep running "bells and whistles" list for future AI features | All | Ongoing |

## Feature Requests / Future Ideas (from call)

- **Customer + prospect map in Cerebro** — separate page, shows HubSpot customers and prospects on a map, color-coded by deal pipeline stage. Michael: "The sales guys drive around a lot." Alex: "Plan my week for me, yo."
- **Route optimization** — Michael brought up Navusoft's route tool but noted "one accident changes everything." Daniel noted this is an NP-hard problem. Future item.
- **AI-powered invoice processing** — Alex described workflow: scan PDF invoices → summarize in table → allocate by business line/department → create journal entry → human approves in Sage. AIC has similar code already (document summarization + number extraction).
- **AI filling out HubSpot** — Daniel: take a photo of a business, say "go fill out my HubSpot." Could improve CRM data quality (known industry-wide problem).
- **Cerebro MCP** — direct AI-to-data connection via Claude, not just sidebar. "Build a Cerebro MCP directly into Claude."
- **Mobile app** — Michael asked about mobile. Currently mobile-responsive web. Could do PWA (pin to home screen) or actual App Store app ($200/yr Apple developer account). App enables camera features (receipt scanning, etc.).

## Key Quotes

> **Michael on WAM:** "I think it's still living in the 80s. It's like a DOS interface... you're pressing the F keys a lot."

> **Alex on AI future:** "Plan my week for me, yo."

> **Michael on Greenmark separation:** "We wanted the flexibility to be able to peel things off."

> **Daniel on agentic AI:** "There is no test for 'you sent the email to the wrong client.'"

> **Michael on AI at AIC:** "We're actually doing more work because it's dropping the cost of executing on things."

> **Alex on journal entries:** "Scanning a certain email address, scraping in those PDFs, doing everything behind the scenes and then plugging a journal entry into Sage."
