---
id: TASK-0009
title: Reproduce install on a second Mac (greenmark parity)
status: To Do
created: '2026-04-28'
priority: high
milestone: MS-0004
dependencies:
  - TASK-0008
definition-of-done:
  - Documented end-to-end install procedure on a fresh Mac that does NOT yet have slack-cc, derived from whatever sequence got the working ("greenmark") machine into shape — captured as a runbook (preferably extending `skills/doctor/skill.md` + `tools/preflight.sh`, or a new `skills/install/skill.md`).
  - Procedure executed on Daniel's cockpit Mac; `claude plugin list` shows `slack-cc@eidos-agi`; `claude --dangerously-load-development-channels plugin:slack-cc@eidos-agi` boots with the channel listener registered.
  - Bot Token + signing secret + workspace context handled via the documented secrets surface (eidos-vault keys called out by name in the runbook), not ad-hoc env vars.
  - Inbound (Slack → session) and outbound (`reply` / `react`) verified end-to-end on the cockpit Mac, mirroring the TASK-0008 acceptance.
  - Anything the greenmark machine had pre-configured that the cockpit Mac didn't (Node version, npm scope, `claude` CLI version, marketplace add) is enumerated in the runbook so the third machine is push-button.
---
"Greenmark" = whichever Mac currently has slack-cc working end-to-end. The marketplace path landed in TASK-0008 but the install steps still live in heads + the README's quickstart. Treat the cockpit Mac as the test fixture: if a fresh agent can't install slack-cc by following the runbook alone, the runbook isn't done. The `doctor` skill + `preflight.sh` from the 9-attempt saga are the natural home for the verification half — extend them rather than inventing a parallel checker.
