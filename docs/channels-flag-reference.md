# Claude Code Channels — Flag Reference

Source: https://code.claude.com/docs/en/channels and https://code.claude.com/docs/en/channels-reference

## --dangerously-load-development-channels

Bypasses the channel allowlist for specific entries during the research preview. Two entry formats:

```bash
# For a bare .mcp.json server (no plugin wrapper)
claude --dangerously-load-development-channels server:<name>
# <name> must match a server entry in .mcp.json

# For a plugin-provided channel
claude --dangerously-load-development-channels plugin:<name>@<marketplace>
```

### server:<name> format
- Looks for `<name>` in the workspace or user `.mcp.json`
- Example: `server:webhook` matches `"webhook": { ... }` in `.mcp.json`
- The server must declare `claude/channel` capability to register as a channel

### plugin:<name>@<marketplace> format
- References an installed marketplace plugin
- Example: `plugin:telegram@claude-plugins-official`
- Install first with `/plugin install <name>@<marketplace>`

## --channels (production)
Same format as above but only allows plugins from the approved allowlist (Anthropic-curated or org-configured via `allowedChannelPlugins`).

## Key Gotcha: --plugin-dir vs server:<name>

When using `--plugin-dir`, the plugin's MCP server registers with the internal name `plugin:<pluginName>:<serverName>`. This format is NOT accepted by `--dangerously-load-development-channels`.

**Workaround**: Add the server to the workspace `.mcp.json` and use `server:<name>` instead. If also using `--plugin-dir` for skills, remove the server from the plugin's `.mcp.json` to avoid duplicate instances.

## Channel Capability

A server must declare `claude/channel` in its capabilities for Claude Code to register the notification listener:

```typescript
capabilities: {
  experimental: { 'claude/channel': {} },
  tools: {},  // omit for one-way channels
}
```

Without this, the server connects as a normal MCP server (tools work) but channel notifications are silently dropped.
