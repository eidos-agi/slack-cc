# Task Register

Central view of all cross-project work items. Each task has its own file with full history and comments. Updated by [task-out](../.claude/skills/task-out/SKILL.md) after each meeting.

*Last updated: 2026-02-20*

## Self-unblockable — do these now (1)

| ID | Task | Owner | Effort |
|----|------|-------|--------|
| 007 | [Make Michael GitHub admin](007-github-admin-michael.md) | Daniel | 30 seconds |

## Blocked — waiting on another task (2)

| ID | Task | Owner | Since | Blocker |
|----|------|-------|-------|---------|
| 002 | [Create read-only Sage API key](002-sage-api-key.md) | Daniel | Feb 19 | [001 Sage account](001-sage-account.md) |
| 010 | [Transfer Railway project](010-railway-transfer.md) | Daniel | Feb 19 | [009 Railway account](009-railway-account.md) |

## Pending — waiting on Alex (4)

| ID | Task | Since | Follow-up |
|----|------|-------|-----------|
| 001 | [Sage Intacct user account](001-sage-account.md) | Feb 19 | Emailed Feb 20 |
| 004 | [HubSpot API access](004-hubspot-api-access.md) | Feb 19 | Emailed Feb 20 |
| 006 | [GA4 / Google Search Console access](006-ga4-gsc-access.md) | Feb 19 | Emailed Michael Feb 20 |
| 008 | [GitHub account](008-github-account-alex.md) | Feb 19 | Emailed Feb 20 |

## Pending — waiting on Michael (4)

| ID | Task | Since | Follow-up |
|----|------|-------|-----------|
| 003 | [Claude Team seat](003-claude-team-seat.md) | **Feb 11** | RAISED TWICE — emailed Feb 20. Invite received, accepting. |
| 005 | [Webflow login](005-webflow-login.md) | Feb 19 | Not yet emailed |
| 009 | [Railway account](009-railway-account.md) | Feb 19 | Emailed Feb 20 |
| 011 | [Google Business Profile login](011-google-business-profile.md) | Feb 19 | Not yet emailed |

## Pending — waiting on Michael + Alex (1)

| ID | Task | Since | Follow-up |
|----|------|-------|-----------|
| 012 | [Dashboard mockup feedback](012-dashboard-feedback.md) | **Feb 11** | RAISED TWICE — not yet emailed |

## Completed

_(none yet — completed tasks move to [archive/](archive/))_

---

## Summary

| Person | Open tasks | Oldest |
|--------|-----------|--------|
| **Alex Kaye** | 4 | Feb 19 (1 day) |
| **Michael Nguyen** | 4 | Feb 11 (9 days) |
| **Daniel Shanklin** | 3 (1 self-unblockable, 2 blocked) | Feb 19 |
| **Michael + Alex** | 1 | Feb 11 (9 days) |
| **Total** | **12** | |

## How this works

- **task-out** creates task files when routing meeting action items
- **task-out --reconcile** scans all tasks and updates this index
- Each task file has full history and comments — click through for details
- Completed tasks move to `archive/` to keep this list focused on open work
- Source attribution links every task back to the meeting that created it
