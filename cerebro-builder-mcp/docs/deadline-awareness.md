---
title: Deadline Awareness
tags: [deadline, rhea, monday, urgency, mission, runway, ceremony]
---

# Deadline Awareness

Rhea and the ceremony don't know what day it is.

## The problem

The mission says `deadline_context: "Monday morning review — every week."` But Rhea doesn't see this. In session 25, Rhea ruled "wait 16 hours" on a Sunday before a Monday deadline because it optimized for ceremony safety. Daniel pushed back — Sunday is the only runway before the deadline.

## The fix

When the builder invokes Rhea for a gate check, the context should include:
- Current day/time
- Next deadline
- Hours of runway remaining
- What's blocked if we wait

"Is this safe to merge?" is a different question on a Tuesday morning (72 hours of runway) vs a Sunday afternoon (16 hours, and the cron fires at 6 AM).

## Rules

1. **Sunday before Monday deadline is runway, not downtime.** Every hour is learning time. Failing at 3 PM Sunday means you can fix by 6 PM. Failing at 6 AM Monday means you can't.
2. **Ceremony protects correctness. Correctness includes time to iterate.** Waiting is not cautious when waiting burns the margin for recovery.
3. **Rhea should know the deadline.** The challenge prompt should include: "The next deadline is Monday morning. It is currently Sunday afternoon. There are N hours of runway."
4. **"Expected green" with CI pending is still a valid merge on the critical path** if: (a) tests pass locally, (b) the fix is under 10 lines, (c) waiting means missing the deadline. Document the risk in the merge comment.
