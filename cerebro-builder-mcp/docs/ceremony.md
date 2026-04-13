---
title: Engineering Ceremony
tags: [ceremony, create-work, open-pr, merge, ci, issue-before-pr, tier]
---

# Engineering Ceremony

The ceremony is the contract that makes work visible and safe. Every code change follows this flow.

## The flow

```
1. create_work()      Issue + project board + milestone link
2. Write code          Feature branch, tests, commit explains why
3. open_pr()           PR with "Closes #N", CI triggered
4. check_ci()          Wait for green (Lint, Tests, Type Check)
5. merge_pr()          Squash merge to develop
6. Verify staging      Deploy landed, health check passes
7. If DB change        Verify migration applied on staging Supabase
8. Promote             Merge develop -> main (production)
9. Verify production   Deploy landed, health check passes
10. Update Wrike       Executive-level summary in Daniel's voice
11. Close milestone    If all sub-issues done on the board
```

## Iron rules

**Issue before PR.** Every PR must reference an issue with "Closes #N". No orphan PRs. The project board shows empty "Linked pull requests" if you skip this. Daniel caught 9 orphan PRs in Session 22.

**CI must be green.** Always check CI status before moving on. Don't fire and forget.

**Tier determines ceremony level:**

| Tier | Repos | What's required |
|------|-------|----------------|
| T1 Production | cerebro, cerebro-migrations, data-daemon | Full ceremony: CI, Rhea gate, PR template, CODEOWNERS |
| T2 Supporting | cerebro-qa, warp-speed, ai-services, bot-farm | CI, PR template, dependabot |
| T3 Reference | infra, greenmark-cockpit, cerebro-mcp, cerebro-vault | Pre-push hooks only, merge freely |

**T1 repos need Rhea.** Before merging to production on T1 repos, run rhea_challenge for adversarial review. This is the token gate.
