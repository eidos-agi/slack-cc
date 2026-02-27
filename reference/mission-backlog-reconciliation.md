# Mission Control ↔ Backlog Reconciliation

Generated: 2026-02-27

## Summary

- **33 MC missions** across 18 initiatives and 9 areas
- **57 backlog tasks** (27 Done, 29 To Do, 1 In Progress)
- **Mapped**: 17 missions have matching backlog tasks
- **Unmapped MC missions**: 16 missions have no backlog task
- **Orphan backlog tasks**: 28 tasks don't map to any MC mission (ad-hoc execution work)
- **Status conflicts**: 6 cases where MC and backlog disagree

---

## 1. Mission → Backlog Mapping

### Platform & AI Tools Area

| MC Mission | MC Status | Backlog Task(s) | BL Status | Conflict? |
|------------|-----------|-----------------|-----------|-----------|
| m-db-1: Evaluate warehouse options | queued | — | — | No task |
| m-db-2: Provision database instance | queued | — | — | No task |
| m-dash-1: Build 8 dashboard mockups | complete | TASK-19 (spike) | Done | OK |
| m-dash-2: Get feedback on mockups | queued | TASK-8 | To Do | OK (both say pending) |
| m-infra-1: Document 15 systems | complete | TASK-21 | Done | OK |
| m-infra-2: Deploy Cerebro site | complete | — | — | No task (was done inline) |
| m-dq-1: Design validation framework | queued | TASK-12, TASK-36 | To Do | OK |
| m-dq-2: Build audit trail | queued | — | — | No task |
| m-claude-1: Email Alex re Claude Teams | in_progress | — | — | **STALE** — this was done Feb 12 |
| m-claude-2: Setup call with Alex | queued | — | — | **STALE** — Claude Teams set up |
| m-claude-3: Add domains + invite members | queued | — | — | **STALE** — likely done |
| m-claude-4: Demo Claude sidebar | queued | TASK-34 (AI sidebar) | To Do | Partial match |
| m-gov-1: Draft AI governance policy | queued | — | — | No task |
| m-aicost: Benchmark AI cost vs human | queued | — | — | No task — AI Costs page exists |

### Finance Area (Sage Intacct)

| MC Mission | MC Status | Backlog Task(s) | BL Status | Conflict? |
|------------|-----------|-----------------|-----------|-----------|
| m-sage-1: Research Sage API | complete | TASK-3 (parent) | To Do | **CONFLICT** — MC says done, BL still open |
| m-sage-2: Get Web Services creds | blocked | TASK-3 (includes this) | To Do | OK (both say blocked) |
| m-sage-3: Build GL → bronze pipeline | queued | TASK-9, TASK-10 | To Do | OK |
| m-walk-1: Schedule walkthrough w/ Alex | queued | — | — | No task |
| m-walk-2: Map Excel model to warehouse | queued | TASK-14 | To Do | OK |
| m-walk-3: Document metric calculations | queued | TASK-18 | To Do | OK |
| m-expense: Invoice scanning | queued | — | — | No task (Doc §8 — future) |

### Sales Area (HubSpot)

| MC Mission | MC Status | Backlog Task(s) | BL Status | Conflict? |
|------------|-----------|-----------------|-----------|-----------|
| (init-hub: Connect HubSpot) | not_started | TASK-1 family (18 tasks!) | 16 Done, 2 To Do | **CONFLICT** — MC says not started, BL is mostly done |
| (init-hub2nav: HubSpot→Navusoft bridge) | not_started | — | — | No task (future) |

### Customers Area (Navusoft)

| MC Mission | MC Status | Backlog Task(s) | BL Status | Conflict? |
|------------|-----------|-----------------|-----------|-----------|
| m-nav-1: Research Navusoft API | complete | — | — | No task (was done inline) |
| m-nav-2: Get vendor contact | blocked | — | — | No task |
| m-nav-3: Design customer schema | queued | — | — | No task |
| m-nav-4: Build customer ETL | queued | — | — | No task |

### Fleet Area (FleetIO)

| MC Mission | MC Status | Backlog Task(s) | BL Status | Conflict? |
|------------|-----------|-----------------|-----------|-----------|
| m-fleet-1: Research FleetIO API | complete | — | — | No task (was done inline) |
| m-fleet-2: Get API key from Robert | blocked | — | — | No task |
| m-fleet-3: Map R&M cost categories | queued | — | — | No task |

### Drivers Area (3rd Eye, LB Tech, Samba)

| MC Mission | MC Status | Backlog Task(s) | BL Status | Conflict? |
|------------|-----------|-----------------|-----------|-----------|
| m-3eye-1: Identify vendor + API status | blocked | — | — | No task |

### People Area (Paylocity)

No MC missions have backlog tasks. init-pay, init-timekeep are all "not_started" with no backlog coverage.

### Operations Area (WAM)

No MC missions have backlog tasks. init-wam is "not_started" with no backlog coverage.

---

## 2. Status Conflicts (6 total)

| # | Mission | MC Status | Backlog | BL Status | Resolution |
|---|---------|-----------|---------|-----------|------------|
| 1 | m-sage-1: Research Sage API | complete | TASK-3 | To Do | **MC is right** — research IS done (in infra repo). TASK-3 is broader (full connection). Split. |
| 2 | init-hub: Connect HubSpot | not_started | TASK-1 family | 16/18 Done | **BL is right** — massive HubSpot exploration done. MC needs update. |
| 3 | m-claude-1: Email Alex | in_progress | — | — | **STALE** — this was completed weeks ago. Mark complete. |
| 4 | m-claude-2: Setup call | queued | — | — | **STALE** — Claude Teams was set up. Mark complete. |
| 5 | m-claude-3: Add domains + invite | queued | — | — | **LIKELY DONE** — needs confirmation. |
| 6 | init-dash: Dashboard mockups | complete | TASK-8 (feedback) | To Do | **PARTIAL** — mockups done, feedback still pending. MC is correct. |

---

## 3. Unmapped MC Missions (need backlog tasks)

These 16 MC missions have no corresponding backlog task:

1. **m-db-1**: Evaluate warehouse options — *already decided (Supabase), need task to document*
2. **m-db-2**: Provision database instance — *already done (Supabase running), mark complete*
3. **m-infra-2**: Deploy Cerebro site — *already done, mark complete*
4. **m-nav-2**: Get vendor contact from Michael — *needs task (blocker)*
5. **m-nav-3**: Design customer + cart schema — *needs task*
6. **m-nav-4**: Build customer data ETL — *needs task (blocked on nav-2)*
7. **m-fleet-2**: Get FleetIO API key from Robert — *needs task (blocker)*
8. **m-fleet-3**: Map R&M cost categories — *needs task (blocked on fleet-2)*
9. **m-3eye-1**: Identify 3rd Eye vendor — *needs task (blocker)*
10. **m-walk-1**: Schedule walkthrough with Alex — *needs task*
11. **m-dq-2**: Build audit trail — *needs task*
12. **m-gov-1**: Draft AI governance policy — *needs task*
13. **m-expense**: Invoice scanning for anomalies — *future, defer*
14. **m-claude-2**: Setup Claude Teams — *already done, mark complete*
15. **m-claude-3**: Add domains + invite members — *verify, likely done*
16. **init-hub2nav**: HubSpot → Navusoft bridge — *future, defer*

---

## 4. Orphan Backlog Tasks (no MC mission)

These 28 tasks exist in the backlog but don't map to any MC mission. They're valid execution work — just not in the original roadmap:

**Cerebro UI/UX (13 tasks):**
- TASK-19: Prospect map spike (Done)
- TASK-20: Rename prospect map terminology (To Do)
- TASK-22: Lasso/polygon selection (To Do)
- TASK-23: Probability-to-close fields (To Do)
- TASK-24: Mobile responsive detail panel (To Do)
- TASK-25: Memphis entity across dashboards (Done)
- TASK-26: Sparkline charts (Done)
- TASK-27: Layout-level detail panel (Done)
- TASK-28: Stage icons (Done)
- TASK-29: Fix Leaflet popup (Done)
- TASK-30: Interactive legend (Done)
- TASK-31: JSON toggle (Done)
- TASK-32: Company cards grid (Done)

**Infrastructure (7 tasks):**
- TASK-6: Railway billing (Done)
- TASK-33: DetailPanel for infra map (Done)
- TASK-35: Provider cards (Done)
- TASK-37: greenmarkwaste.com registrar (To Do)
- TASK-38: htdisposal.com registrar (To Do)
- TASK-39: Railway 2FA (Done)
- TASK-41: Infra map Loom (Done)

**Process & Comms (4 tasks):**
- TASK-4: SEO baseline audits (To Do)
- TASK-5: Reply to outstanding comms (To Do)
- TASK-7: Add team to GitHub org (To Do)
- TASK-40: Prospect map Loom feedback (To Do)

**HubSpot deep-dive (3 tasks not in MC):**
- TASK-1.17: Design data-daemon HubSpot connector (To Do)
- TASK-1.18: Fix hs-api.sh associations (To Do)
- TASK-2: CRM Agent (To Do, future)

**Architecture (1 task):**
- TASK-34: AI sidebar with OpenAI Realtime (To Do)

---

## 5. Recommended MC Updates

### Missions to mark COMPLETE (were done, MC doesn't know):
- m-db-1 → complete (Supabase selected and running)
- m-db-2 → complete (Supabase provisioned, schemas created)
- m-infra-2 → complete (already was marked complete)
- m-claude-1 → complete (email sent Feb 12)
- m-claude-2 → complete (Claude Teams org created)
- m-claude-3 → complete (verify with Daniel)

### Initiatives to update status:
- init-hub → **in_progress** (TASK-1 family is 16/18 done, not "not_started")
- init-db → **complete** (Supabase running)
- init-claude → **complete** (all sub-missions done)
- init-infra → already complete (correct)

### Areas to update livePercent:
- platform: 0% → still 0% (no real data flowing yet)
- All others: remain 0% (waiting on vendor credentials)

### Activity feed: add recent entries
- Feb 26–27: Infrastructure map enhanced (daemon nodes, provider cards, DetailPanel migration)
- Feb 26–27: Training page created with 3 Loom walkthroughs
- Feb 20–26: HubSpot exploration complete (18 tasks, CLI + REST, test data seeded)
- Feb 20: Railway workspace set up (Pro plan, 2FA enforced)
