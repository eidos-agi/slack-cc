---
title: Hotfix Fast Lane
tags: [hotfix, ceremony, fast-lane, tier, critical-path, ci, merge]
---

# Hotfix Fast Lane

Three-line fixes on the critical path shouldn't need full ceremony.

## The problem

Session 25 shipped three hotfixes to data-daemon (T1 repo). Each went through: create issue → create branch → commit → push → create PR → wait for CI → merge → redeploy. For a 3-line fix that's blocking the pipeline.

The ceremony is right for features — you want the issue, the review, the CI gate. But for a hotfix where:
- The pipeline is broken right now
- The fix is under 10 lines
- CI passes (or the change is trivially correct)
- There's a deadline

...the full ceremony costs 10-15 minutes per fix. Three fixes = 45 minutes of ceremony for 9 lines of code.

## Fast lane criteria

A fix qualifies for the fast lane if ALL of these are true:
1. **On the critical path** — something is broken or blocked right now
2. **Under 10 lines changed** — auditable by reading, not by running
3. **CI green** (or trivially correct — e.g., adding a conn.commit())
4. **Idempotent** — re-running doesn't cause harm
5. **Observable** — you can verify it worked from logs within minutes

## Fast lane process

```
1. Fix on branch
2. Push + create PR (issue optional — create after if needed)
3. CI green? Merge immediately.
4. Redeploy + trigger + observe
5. Create the issue retroactively and link it
```

The issue-before-PR rule exists so work is visible. For hotfixes, the PR IS the visibility. The issue can follow.

## What doesn't qualify

- Schema changes (even small ones — migrations are not hotfixes)
- New features disguised as hotfixes
- Anything touching auth, RLS, or credentials
- Fixes where you're not sure why it works

## T1 Rhea gate

For T1 repos, Rhea quick (not full challenge) is sufficient for hotfixes. The question isn't "should we do this?" — the pipeline is broken. The question is "is this fix correct?"
