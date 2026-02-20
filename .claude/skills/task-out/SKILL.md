---
name: task-out
description: "Route action items from a meeting README into project checklists, the Waiting On table, and follow-up assignments. Use after running diarize on a meeting transcript — takes the extracted action items and makes sure every one lands in the right place with the right owner. Triggers: '/task-out', 'route these action items', 'task this out', 'where do these go', or after diarize produces a README. Also use for weekly reconciliation: '/task-out --reconcile' to check all open items across meetings and projects for staleness, duplicates, and progress."
---

# Task-Out — Action Item Router

Take action items from a meeting README and route every one to the right project checklist, the right owner, and the right follow-up. Then verify nothing fell through the cracks.

## Why this exists

After a 45-minute call, there might be 14 action items. Each needs to:
- Land in the correct project checklist (or get a new one)
- Have a clear owner (not "someone")
- Show dependencies ("blocked on #1")
- Not duplicate something already tracked elsewhere
- Get flagged for follow-up if it requires an email or access request

A human doing this manually will miss items, create duplicates, and lose track of which meeting spawned which task. This skill makes it exhaustive and auditable.

## Two modes

### Route mode (default)
Point at a meeting README → route all action items.

### Reconcile mode
Scan ALL open items across all meetings and project checklists → find stale items, duplicates, fulfilled items still marked pending, and items with no home.

---

## Route Mode Workflow

### 1. Load context

Load these files:
```
reference/glossary/people.md       — who owns what systems, decision authority
reference/glossary/systems.md      — which systems map to which projects
README.md                          — main dashboard, Waiting On table, project list
```

### 2. Read the meeting README

Accept a file path or find the most recent meeting README:
```
meetings/YYYY-MM-DD-*/README.md
```

Extract the action items table. For each item, capture: number, description, owner, status, dependencies.

### 3. Inventory all project checklists

Scan every checklist in `projects/`:
```
projects/*/checklist.md
projects/*/README.md
```

Build a map: project name → existing checklist items (text + status). This is the "already tracked" inventory.

**Note:** Glob may not find files in `projects/` due to directory permissions. Fall back to `find` via Bash if Glob returns empty.

Also load prior meeting READMEs for cross-meeting detection (step 4b).

### 4. Route each action item

**First pass: separate completed from open.** Completed items need no routing — categorize them quickly and move on. On the Feb 11 kickoff, 4 of 8 items were already done. Don't waste time routing completed work.

For each OPEN action item, determine:

**a) Does it already exist in a project checklist?**
- Search for keyword overlap (not exact match — "Provision Daniel Sage account" matches "Alex to provision Daniel a Sage Intacct user account")
- If found: compare statuses. If the meeting says "In progress" but the project says "Planning", flag the discrepancy.
- If found and statuses match: skip (already tracked)

**b) Does it appear in another meeting's action items? (Cross-meeting carry-over)**
Check prior meeting READMEs for the same item. Signs of carry-over:
- Same action with same or similar wording in an earlier meeting
- Same owner, still pending
- Example: "Get Claude set up for Greenmark" (Feb 11 #5) = "Provision Daniel a seat on Greenmark Claude Team" (Feb 19 #3) — same item, 9 days apart, still pending

Cross-meeting carry-overs are significant because:
- Being raised twice means it's important and not moving
- The age should be counted from the FIRST meeting, not the most recent
- Flag these prominently even if under the 2-week stale threshold

Also check for **umbrella decomposition**: a broad item from an earlier meeting that got broken into specific items in a later meeting. Example: "Get system access/credentials" (Feb 11 #8) → "Sage account" (Feb 19 #1), "HubSpot access" (Feb 19 #4), etc. When this happens, the umbrella item is superseded — track the specifics, not the umbrella.

**c) Which project does it belong to?**
- Match by topic/system using the glossary:
  - Sage, HubSpot, API keys, user accounts, GitHub, Railway, billing → `tech-org-setup`
  - SEO, PageSpeed, Webflow, website → `seo-improvement`
  - Dashboards, mockups, charts, map page → `data-mockups`
  - Recording, Fireflies, transcripts, diarize → `recording-solution`
  - Data warehouse, pipeline, connectors, vendor research → `data-integration`
  - Physical warehouse, yard, facility → `warehouse-strategy`
- If no project matches: check if the item is **covered by an existing process** (e.g., "keep a feature list" is covered by the diarize pipeline capturing Feature Requests from every meeting). If covered, note it. If genuinely homeless, flag it.

**d) Is it a "Waiting On" item?**
Items where Daniel is blocked on someone else's action go on the main README's Waiting On table. Signs:
- Owner is NOT Daniel but Daniel needs the result
- Status is "Pending" or "Blocked on #N"
- Involves access provisioning, account creation, or approval
- **Joint actions count** — if an item needs both Daniel and someone else, and the other person hasn't done their part yet (e.g., Michael creates a Railway account before Daniel can transfer the project), it's a Waiting On.

**e) Is it self-unblockable?**
Items owned by Daniel (or the person running task-out) with NO dependencies on anyone else. These are the most actionable findings — things that can be done TODAY. Signs:
- Owner is Daniel
- No "Blocked on #N" status
- No dependency on access, credentials, or someone else's action
- Example: "Make Michael admin in GitHub org" — Daniel has admin access, Michael has an account. 30-second operation.

**f) Does it need a follow-up communication?**
- If the owner is external to Daniel (Alex, Michael, Robert) AND the item is still pending → flag for follow-up email
- If it was discussed on the call, the owner heard it — but a written follow-up confirms and creates a record
- **Cross-meeting carry-overs get priority** — an item raised in two meetings with no action needs a more direct follow-up
- **Group by person** — one email per person listing all their pending items, not one email per item

### 5. Generate the routing plan

Present a clear plan before making any changes. Categories in priority order:

```
ROUTING PLAN — [Meeting Name] ([N] action items)

✅ Completed (no routing needed):
  ✅ #1 Build infrastructure map — Completed
  ✅ #2 Build prototype dashboards — Completed

🔓 Self-unblockable (do these TODAY):
  🔓 #7  Make Michael admin in GitHub org — Daniel has admin, Michael has account

🔁 Cross-meeting carry-over (raised before, still open):
  🔁 #5  Claude Team seat — originated Feb 11, re-raised Feb 19, still pending (9 days)
         Owner: Michael. Raised in 2 meetings with no action.

📧 Follow-up needed (group by person):
  📧 Alex (3 items): Sage account (#1), HubSpot access (#4), GitHub account (#8)
  📧 Michael (2 items): Claude Team seat (#3) ← RAISED TWICE, Railway account (#6)

⚠ Status discrepancies:
  ⚠ #5  SEO: meeting says "In progress", project says "Planning" — Planning is accurate

⏳ Add to Waiting On:
  ⏳ #6  Railway account — waiting on Michael to create Greenmark Railway account

+ Add to project checklists:
  + #10 Customer map page → data-mockups/checklist.md [NEW]

✓ Already tracked (no changes needed):
  ✓ #1  Sage account → tech-org-setup/checklist.md [Pending]
  ...

🔀 Superseded (umbrella decomposed into specifics):
  🔀 Feb 11 #8 "Get system access" → split into Feb 19 #1 (Sage), #4 (HubSpot), etc.

🔄 Covered by process:
  🔄 #14 "Bells and whistles list" — diarize captures Feature Requests every meeting
```

**Why this order:** Completed items first to clear them out. Self-unblockable second because they're immediately actionable. Cross-meeting carry-overs third because they signal stuck work. Follow-ups fourth to drive others. Already-tracked items last because they need no action.

### 6. Apply with approval

Only make changes after the user confirms. For each approved change:
- Add items to project checklists
- Update the main README Waiting On table
- Fix status discrepancies (update the less-accurate source to match the more-accurate one)
- Note which items need follow-up emails (but don't send them)

### 7. Log what was routed

Append a routing log to the bottom of the meeting README:

```markdown
## Routing Log
*Routed by task-out on YYYY-MM-DD*
- N items completed (no routing needed)
- N items already tracked in project checklists
- N cross-meeting carry-overs flagged
- N status discrepancies fixed
- N items added to Waiting On table
- N items self-unblockable (flagged for immediate action)
- N items covered by process / superseded
- N follow-up emails flagged (names)
```

---

## Reconcile Mode Workflow

Run with `--reconcile` or "reconcile all tasks" to audit across everything.

### 1. Gather all open items

Scan:
- All meeting READMEs → action items tables
- All project checklists → unchecked items
- **All project blockers** → items listed under "Blocked On", "Blockers", or similar sections in project READMEs and checklists. These often contain Waiting On items that never came from a meeting (e.g., SEO needs Webflow login, which was identified during planning, not on a call).
- Main README → Waiting On table

### 2. Build the master list

Deduplicate: same item may appear in a meeting README, a project checklist, and the Waiting On table. Group by canonical description. Track which meeting FIRST raised each item (the origination date).

For items that appear in multiple meetings, note the carry-over pattern — this is a signal of importance and/or stuckness.

### 3. Check each item

For each unique item:
- **Stale?** — Is it still "Pending" after 2+ weeks with no progress?
- **Carry-over?** — Has it been raised in multiple meetings? Even if under 2 weeks, multi-meeting items are high-attention.
- **Duplicate?** — Does it appear in multiple places with different statuses?
- **Fulfilled?** — Is it marked "Pending" somewhere but "Complete" elsewhere?
- **Orphaned?** — Is it in a meeting README but NOT in any project checklist?
- **Superseded?** — Was a broad item decomposed into specifics in a later meeting?
- **Owner clear?** — Does it have a real name, not "TBD"?
- **Self-unblockable?** — Can the person running reconcile do it right now?
- **Missing from Waiting On?** — Is a project blocker not reflected in the main README's Waiting On table? The Waiting On table should be the single view of "what's holding us up." If a project has blockers that aren't there, they're invisible to leadership.

### 4. Present the reconciliation report

```
RECONCILIATION REPORT — [Date]

Open items across all sources: N
Unique items (deduplicated): N

🔓 Self-unblockable — do these now (N):
  - Make Michael admin in GitHub org — Daniel can do this today

🔁 Cross-meeting carry-overs — raised multiple times, still open (N):
  - Claude Team seat — Feb 11, Feb 19. Owner: Michael. 9 days, no action.

🟢 On track (N):
  - SEO improvement — Planning, Daniel
  - ...

🟡 Stale — no progress in 7+ days (N):
  - Provision Daniel Sage account — Pending since Feb 19, owner: Alex
  - ...

🔴 Status conflicts (N):
  - SEO: "In progress" in meeting, "Planning" in project
  - ...

🔀 Superseded — umbrella items decomposed (N):
  - Feb 11 #8 "Get system access" → split into Sage, HubSpot, Claude specific items

👻 Orphaned — in meeting but no project (N):
  - [item]

🔄 Covered by process (N):
  - "Bells and whistles list" — captured by diarize Feature Requests

📧 Follow-up suggested (N):
  - Alex: Sage account, HubSpot access, GitHub account
  - Michael: Claude Team seat (RAISED TWICE), Railway account
```

---

## Key Rules

- **Never auto-update** — always present the plan, apply only with approval
- **Completed items first** — clear them out before analyzing open items
- **Keyword matching, not exact match** — "Provision Daniel Sage" and "Alex to provision Daniel a Sage Intacct user account" are the same item
- **Preserve source attribution** — every routed item traces back to its meeting (date + item number)
- **One item, one canonical location** — the project checklist is the source of truth for status. Meeting READMEs are the historical record.
- **Flag, don't fix** — if something looks wrong (stale, duplicate, conflicting), report it. Let the human decide.
- **Self-unblockable items first** — the most valuable finding is "you can do this right now." Surface it prominently.
- **Cross-meeting carry-overs are high-signal** — an item raised in two meetings means it's important AND stuck. Escalate it.
- **Umbrella decomposition is normal** — broad items from early meetings get split into specifics. Mark the umbrella as superseded, track the specifics.
- **"Covered by process" is a valid resolution** — not every item needs a project. If an existing workflow handles it, say so.
- **Group follow-ups by person** — one email per person listing all their items, not one email per item.
- **Waiting On table gets a "Since" column** — makes age visible at a glance. Bold the date for items older than 1 week or carried over from prior meetings. Leadership should see which items have been stuck longest.
- **Check status consistency across ALL surfaces** — a project's status appears in the main README, the project README, and meeting READMEs. If any disagree, flag it. The project checklist is the source of truth.
- **Project blockers feed the Waiting On table** — route mode only looks at meeting action items. Reconcile mode also scans project-level blockers (e.g., "Need Webflow login" in seo-improvement). If a blocker isn't in the Waiting On table, it's invisible to leadership.
