---
id: MS-0004
title: 'M-04: Operator ergonomics'
status: open
created: '2026-04-28'
---
Make slack-cc trivial to install on a fresh operator machine and trivial to launch with the right flags. Marketplace path now works (MS-0002 done) but a fresh second machine is still a manual recipe and launching requires remembering `--dangerously-load-development-channels plugin:slack-cc@eidos-agi --allowedTools "..."`. This milestone closes both gaps: documented second-machine install + a `claude-slack` wrapper that hides the flags.
