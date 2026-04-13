---
title: Board Staleness
tags: [project-board, stale, close, ceremony, visibility, progress]
---

# Board Staleness

The board lies when closing is manual but opening is enforced.

## The problem

The ceremony enforces `create_work()` before writing code — every issue lands on the board. But closing is manual. Nobody calls `close_work()` when the PR merges, the deploy lands, and the feature is verified.

Result: M-03 was 25% on the board when it was 100% in reality. The board became a liar. Daniel opens the board and sees stale progress.

## Session 25 cleanup

Closed 10 issues in one batch after auditing the board against reality:
- M-03: 4 sub-issues all done (connector written, YAML configured, extraction running)
- M-04: 3 sub-issues all done (silver + gold views deployed in migration)
- M-05: 2 sub-issues done (fixtures exported, parity script written)
- Duplicate issue closed as "not planned"
- Jam.dev issue closed (already deployed)

## Rules

1. **Close issues when the work is verified, not when the PR merges.** The PR closing the issue is step 5. Verification is step 10. If you close at step 5, the board says "done" but production might be broken.
2. **Audit the board regularly.** During convene, check if the board matches reality. Stale boards erode trust.
3. **The builder should prompt for closures.** After verify_milestone passes, the builder should suggest which issues to close. Don't wait for the human to notice.

## What should change

The adjourn ceremony (A-04) checks "PRs are opened for completed work." It should also check: "Issues are closed for completed work." Open issues for done work are just as invisible as code without PRs.
