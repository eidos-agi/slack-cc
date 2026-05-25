---
id: TASK-0010
title: claude-slack CLI wrapper
status: To Do
created: '2026-04-28'
priority: high
milestone: MS-0004
dependencies:
  - TASK-0009
definition-of-done:
  - Executable named `claude-slack` available on PATH after install (e.g. shipped as `bin/claude-slack` and symlinked, or installed via npm `bin` field, or documented manual symlink — implementer's call).
  - Default invocation runs `claude --dangerously-load-development-channels plugin:slack-cc@eidos-agi --dangerously-skip-permissions "$@"` — both flags, in that order, with all extra args passed through.
  - `--allowedTools` defaults to the slack-cc reply/react surface from README:61 so the wrapper works even if `--dangerously-skip-permissions` is later removed; can be overridden by passing `--allowedTools` explicitly.
  - `claude-slack --help` prints what the wrapper does, what flags it injects, and how to override them. Does NOT swallow `claude --help` — pass `claude-slack -- --help` (or similar) to reach the underlying CLI's help.
  - Exit code is `claude`'s exit code; Ctrl-C forwards cleanly (no zombie node processes).
  - README gets a "Quick launch" section pointing at `claude-slack` and explaining the security tradeoff of `--dangerously-skip-permissions` (the slack-cc permission relay is bypassed when it's set — useful for fully autonomous Slack-driven sessions, dangerous for everything else).
  - Explicit note in the wrapper's help text: this combines TWO distinct dangerously-flags (`-load-development-channels` to load a private-marketplace plugin, and `-skip-permissions` to bypass approval prompts) — they are unrelated security gates and the wrapper is opinionated about turning both off.
---
Daniel's framing: "give me a command line called claude-slack I can use to run it with dangerously skip permissions." The wrapper exists so operators don't have to remember the two flags. Implementer must NOT silently drop `--dangerously-load-development-channels` — without it the channel listener doesn't register and slack-cc looks broken (see README:127, the #1 support issue). Both flags, every time.
