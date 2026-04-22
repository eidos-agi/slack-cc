# How slack-cc Got Published to the Eidos Marketplace

**Date:** 2026-04-21/22
**Session:** 33
**Duration:** ~4 hours across multiple restarts

## The Goal

Publish the Slack channel bridge as a marketplace plugin so anyone can install it with:
```bash
claude plugin marketplace add eidos-agi/claude-plugins
claude plugin install slack-cc@eidos-agi
claude --dangerously-load-development-channels plugin:slack-cc@eidos-agi
```

## What We Started With

A development plugin that required:
```bash
claude --plugin-dir ~/repos/cc-channel-slack-eidos \
       --dangerously-load-development-channels server:slack
```

This had problems:
- Dual-start: `--plugin-dir` started one server instance, workspace `.mcp.json` started another
- Both competed for Socket Mode's single connection slot
- The plugin name was `slack-channel`, the workspace entry was `slack`, nothing matched
- Tests re-implemented all logic as shadow copies (could silently diverge)
- No CI, no lint, no CLAUDE.md

## The Journey (8 restarts to get it right)

### Attempt 1: Understand the Telegram plugin

Investigated how the official Telegram plugin works. Key finding: it uses the **exact same MCP tool architecture** as our Slack bridge. No secret native transport. Both expose `reply` as an MCP tool that Claude calls.

### Attempt 2: Fix the dual-start

Removed `channels` from `plugin.json` so `--plugin-dir` only loads skills, not a competing server. The workspace `.mcp.json` `slack` entry became the single server. This worked — inbound started delivering.

### Attempt 3: Extract lib.ts

The biggest refactor. Moved all pure logic (gate, access, dedup, chunking, pairing, env parsing) into `lib.ts`. Both `server.ts` and `server.test.ts` import from the same source. Tests went from testing shadow copies to testing real code.

### Attempt 4: Research → Decision → Execute (the trilogy)

Used research.md to evaluate 4 distribution strategies:
1. Private Eidos marketplace + official submission (scored 97/105)
2. Private marketplace only (88)
3. Official only (61)
4. Stay as dev plugin (47)

Recorded ADR-001 in visionlog. Created milestones and tasks in ike.md.

### Attempt 5: Make it marketplace-ready

Fixed `.mcp.json` to use `${CLAUDE_PLUGIN_ROOT}` variable. Re-added `channels` to `plugin.json`. Added YAML frontmatter to skills. Added LICENSE. Renamed from `slack-channel` to `slack-eidos`. Passed `claude plugin validate`.

### Attempt 6: Create the Eidos marketplace

Created `eidos-agi/claude-plugins` repo with `marketplace.json`. Plugin installed successfully. But the install path was empty — **marketplace installs don't run `npm install`**.

**Fix:** Changed `package.json` start script to `npm install --silent && tsx server.ts`. Changed `.mcp.json` to use `npm start --prefix ${CLAUDE_PLUGIN_ROOT}`. Same pattern as Telegram's `bun install && bun server.ts`.

### Attempt 7: The naming gauntlet

Renamed 4 times in total:
- `cc-channel-slack-eidos` → `slack-eidos` → `slack-eidos-cc` → `slack-cc`

Each rename required updating 5 synchronized names:
1. `.claude-plugin/plugin.json` → `name`
2. `.claude-plugin/plugin.json` → `channels[0].server`
3. `.mcp.json` → server key
4. `server.ts` → `new Server({ name: '...' })`
5. `skills/*/SKILL.md` → `/<name>:access`

Plus: skill references in all docs, tool prefix in `--allowedTools`, marketplace entry, workspace `.mcp.json` debug entry, `settings.local.json` allow list.

### Attempt 8: The --channels vs --dangerously discovery

Launched with `--channels plugin:slack-cc@eidos-agi`. Everything looked like it worked — tools loaded, skills appeared, bot reacted with 👀, `deliver.ok` fired. But no `<channel>` tag arrived in the session.

Debug log revealed:
```
plugin slack-cc@eidos-agi is not on the approved channels allowlist
(use --dangerously-load-development-channels for local dev)
```

**`--channels` only works for Anthropic-approved plugins.** Private marketplace plugins require `--dangerously-load-development-channels plugin:<name>@<marketplace>`. This is the single most important thing in this entire devlog.

### Attempt 9: The tool prefix discovery

`--allowedTools "mcp__slack-cc__reply"` didn't match. Still prompted for approval.

The deferred tools list showed the actual name: `mcp__plugin_slack-cc_slack-cc__reply`. Claude Code names marketplace plugin tools as `mcp__plugin_<pluginName>_<serverName>__<toolName>`.

### Final: It works

```bash
./start-with-slack.sh --debug
```

Output:
```
Listening for channel messages from: plugin:slack-cc@eidos-agi

← slack-cc · Daniel Shanklin: hey
```

Inbound delivered. Outbound replied. Full marketplace pipeline live.

## What Made It Work (the final configuration)

### plugin.json
```json
{
  "name": "slack-cc",
  "version": "0.2.1",
  "channels": [{ "server": "slack-cc" }]
}
```

### .mcp.json
```json
{
  "mcpServers": {
    "slack-cc": {
      "command": "npm",
      "args": ["start", "--prefix", "${CLAUDE_PLUGIN_ROOT}"]
    }
  }
}
```

### package.json start script
```json
"start": "npm install --no-fund --no-audit --silent && tsx server.ts"
```

### server.ts
```typescript
const mcp = new Server({ name: 'slack-cc', version: '0.2.1' }, { ... })
```

### Launch command
```bash
claude \
  --dangerously-load-development-channels plugin:slack-cc@eidos-agi \
  --allowedTools "mcp__plugin_slack-cc_slack-cc__reply,mcp__plugin_slack-cc_slack-cc__react,mcp__plugin_slack-cc_slack-cc__edit_message,mcp__plugin_slack-cc_slack-cc__fetch_messages"
```

### Workspace .mcp.json
No `slack` or `slack-cc` entry. The marketplace plugin is the only server. Only `slack-cc-debug` remains (separate diagnostic server).

## Lessons Encoded

All lessons written to `tools/learnings.md` and checked by `tools/preflight.sh` (16 checks) and `/slack-cc:doctor` skill (self-diagnosing loop).

## What's Left

- Submit to official marketplace via clau.de/plugin-directory-submission (M-03)
- When accepted, `--channels` replaces `--dangerously-load-development-channels`
- Port the marketplace pattern to other Eidos tools (railguey, research.md, etc.)
