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

### 4. Route each action item

For each action item from the meeting, determine:

**a) Does it already exist in a project checklist?**
- Search for keyword overlap (not exact match — "Provision Daniel Sage account" matches "Alex to provision Daniel a Sage Intacct user account")
- If found: compare statuses. If the meeting says "Pending" but the checklist says "Complete", flag the discrepancy.
- If found and statuses match: skip (already tracked)

**b) Which project does it belong to?**
- Match by topic/system using the glossary:
  - Sage, HubSpot, API keys, user accounts → `tech-org-setup`
  - SEO, PageSpeed, Webflow → `seo-improvement`
  - Dashboards, mockups, charts → `data-mockups`
  - Recording, Fireflies, transcripts → `recording-solution`
  - Database, warehouse, schemas → `warehouse-strategy`
  - GitHub, Railway, billing separation → `tech-org-setup`
- If no project matches: flag as "needs a home" — suggest creating a new project or adding to an existing one

**c) Is it a "Waiting On" item?**
Items where Daniel is blocked on someone else's action (Alex provisioning access, Michael creating an account) go on the main README's Waiting On table. Signs:
- Owner is NOT Daniel but Daniel needs the result
- Status is "Pending" or "Blocked on #N"
- Involves access provisioning, account creation, or approval

**d) Does it need a follow-up communication?**
- If the owner is external to Daniel (Alex, Michael, Robert) AND the item hasn't been communicated → flag for follow-up email
- If it was discussed on the call, the owner heard it — but a written follow-up confirms

### 5. Generate the routing plan

Present a clear plan before making any changes:

```
ROUTING PLAN — Feb 19 Stakeholder Call (14 action items)

Already tracked (no changes needed):
  ✓ #9 Add Daniel to Fireflies — already in recording-solution/checklist.md [Complete]

Route to existing checklists:
  → #1 Provision Daniel Sage account → tech-org-setup/checklist.md (already there, status matches)
  → #5 SEO improvement → seo-improvement/README.md (already there, update status: Planning → In progress)

Add to existing checklists:
  + #4 Get Daniel HubSpot API access → tech-org-setup/checklist.md [NEW ITEM]
  + #10 Build customer map page → data-mockups/checklist.md [NEW ITEM]

Add to Waiting On (main README):
  ⏳ #1 Sage account — waiting on Alex
  ⏳ #3 Claude Team seat — waiting on Michael
  ⏳ #4 HubSpot access — waiting on Alex/Michael

Needs a home:
  ? #14 Keep running bells and whistles list — no matching project

Follow-up needed:
  📧 Alex: Sage account (#1), HubSpot access (#4), GitHub account (#8)
  📧 Michael: Claude Team seat (#3), GitHub admin (#7)

Status discrepancies:
  ⚠ #9 Meeting says "Pending" but checklist says "Complete" — update meeting README
```

### 6. Apply with approval

Only make changes after the user confirms. For each approved change:
- Add items to project checklists
- Update the main README Waiting On table
- Fix status discrepancies
- Note which items need follow-up emails (but don't send them)

### 7. Log what was routed

Append a routing log to the bottom of the meeting README:

```markdown
## Routing Log
*Routed by task-out on YYYY-MM-DD*
- 8 items already tracked in project checklists
- 3 new items added to checklists
- 3 items added to Waiting On table
- 1 item needs a home (bells and whistles list)
- 2 follow-up emails flagged (Alex, Michael)
```

---

## Reconcile Mode Workflow

Run with `--reconcile` or "reconcile all tasks" to audit across everything.

### 1. Gather all open items

Scan:
- All meeting READMEs → action items tables
- All project checklists → unchecked items
- Main README → Waiting On table

### 2. Build the master list

Deduplicate: same item may appear in a meeting README, a project checklist, and the Waiting On table. Group by canonical description.

### 3. Check each item

For each unique item:
- **Stale?** — Is it still "Pending" after 2+ weeks with no progress?
- **Duplicate?** — Does it appear in multiple places with different statuses?
- **Fulfilled?** — Is it marked "Pending" somewhere but "Complete" elsewhere?
- **Orphaned?** — Is it in a meeting README but NOT in any project checklist?
- **Owner clear?** — Does it have a real name, not "TBD"?

### 4. Present the reconciliation report

```
RECONCILIATION REPORT — Feb 20, 2026

Open items across all sources: 23
Unique items (deduplicated): 17

🟢 On track (6):
  - SEO improvement — In progress, Daniel
  - ...

🟡 Stale — no progress in 7+ days (4):
  - Provision Daniel Sage account — Pending since Feb 19, owner: Alex
  - ...

🔴 Status conflicts (2):
  - Add Daniel to Fireflies — "Pending" in Feb 19 README, "Complete" in recording-solution checklist
  - ...

👻 Orphaned — in meeting but no project (1):
  - Keep running bells and whistles list

📧 Follow-up suggested (3):
  - Alex: Sage account, HubSpot access
  - Michael: Claude Team seat
```

---

## Key Rules

- **Never auto-update** — always present the plan, apply only with approval
- **Keyword matching, not exact match** — "Provision Daniel Sage" and "Alex to provision Daniel a Sage Intacct user account" are the same item
- **Preserve source attribution** — every routed item traces back to its meeting (date + item number)
- **One item, one canonical location** — the project checklist is the source of truth for status. Meeting READMEs are the historical record.
- **Flag, don't fix** — if something looks wrong (stale, duplicate, conflicting), report it. Let the human decide.
