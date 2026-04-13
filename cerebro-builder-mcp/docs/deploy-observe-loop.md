---
title: Deploy-Observe-Diagnose Loop
tags: [deploy, observe, diagnose, hotfix, logs, railway, production, debugging]
---

# Deploy-Observe-Diagnose Loop

After deploying, you are not done. You are watching.

```
Deploy → Trigger → Watch logs → Pass or Fail
                                  |
                              Diagnose → Fix → Redeploy → Trigger again
```

## The pattern

1. **Deploy** — merge + redeploy (or auto-deploy from branch)
2. **Trigger** — fire the thing you changed (POST /trigger, manual test, cron)
3. **Observe** — watch logs until the operation completes or fails. Not "check back later." Watch.
4. **Pass** — if it works, move on
5. **Fail** — read the error, form a hypothesis, fix, redeploy, trigger again

This loop can repeat multiple times. Session 25 ran it three times on Sage:
- Attempt 1: periodic commits → failed (connection dead before load started)
- Attempt 2: found PgBouncer kills idle connections → reconnect before load
- Attempt 3: reconnect fix deployed

## Rules

1. **Don't move on after deploy.** A deploy without observation is a hope, not a verification.
2. **Watch the actual logs, not the deploy status.** "Deploy SUCCESS" means the container started. It doesn't mean your code works.
3. **Each failure teaches something.** The fix for attempt 1 was wrong, but the observation from attempt 2 revealed the real root cause.
4. **Sunday is runway, not downtime.** If Monday morning is the deadline, every hour on Sunday is learning time. Waiting is gambling.

## Tools for this loop

- `railguey_redeploy` → deploy
- `POST /trigger/{service}` → trigger
- `railguey_logs(filter="error")` → observe failures
- `railguey_logs(filter="checkpoint")` → observe progress
