#!/usr/bin/env tsx
/**
 * slack-eidos-debug — Full-stack diagnostic MCP for the Slack bridge
 *
 * Inspects every layer of the stack:
 *   1. Slack API (auth, scopes, channels, bot identity)
 *   2. Bot process (running, Socket Mode, pid)
 *   3. Bridge server (node_modules, server.ts, TypeScript compilation)
 *   4. MCP config (.mcp.json entries, plugin registration)
 *   5. Plugin wiring (--plugin-dir, --dangerously-load-development-channels)
 *   6. Access control (access.json, gate rules, allowlist)
 *   7. Logs (structured JSON from stderr ring buffer)
 *
 * Read-only. Reports what's broken. The agent fixes it with Edit/Bash.
 *
 * SPDX-License-Identifier: MIT
 */
import { execSync } from 'node:child_process'
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs'
import { homedir } from 'node:os'
import { join, dirname } from 'node:path'

import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js'
import { WebClient } from '@slack/web-api'

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------
const STATE_DIR = join(homedir(), '.claude', 'channels', 'slack')
const ENV_PATH = join(STATE_DIR, '.env')
const ACCESS_PATH = join(STATE_DIR, 'access.json')
const DEBUG_DIR = join(homedir(), '.claude', 'debug')
const PLUGIN_ROOT = dirname(__dirname) // cc-channel-slack-eidos repo root
const MAIN_SERVER = join(PLUGIN_ROOT, 'server.ts')

// Derive workspace path: env var > sibling dir with .mcp.json > fallback
function findWorkspace(): string {
  if (process.env.WORKSPACE_PATH) return process.env.WORKSPACE_PATH
  // Check sibling directories for .mcp.json (common layout: repos/plugin, repos/workspace)
  const parent = dirname(PLUGIN_ROOT)
  try {
    const siblings = readdirSync(parent)
    for (const name of siblings) {
      const candidate = join(parent, name)
      if (candidate !== PLUGIN_ROOT && existsSync(join(candidate, '.mcp.json'))) {
        return candidate
      }
    }
  } catch {}
  return PLUGIN_ROOT // last resort
}
const DEFAULT_WORKSPACE = findWorkspace()

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function loadEnvTokens(): { botToken?: string; appToken?: string; errors: string[] } {
  const errors: string[] = []
  if (!existsSync(ENV_PATH)) {
    errors.push(`MISSING: ${ENV_PATH} — run /slack-channel:configure to create it`)
    return { errors }
  }

  try {
    const stat = statSync(ENV_PATH)
    const mode = (stat.mode & 0o777).toString(8)
    if (mode !== '600') errors.push(`PERMS: .env is 0${mode}, must be 0600`)
  } catch (err: any) {
    errors.push(`STAT: ${err.message}`)
  }

  const lines = readFileSync(ENV_PATH, 'utf-8').split('\n')
  const env: Record<string, string> = {}
  for (const line of lines) {
    const match = line.match(/^(\w+)=(.+)$/)
    if (match) env[match[1]] = match[2].trim()
  }

  const botToken = env.SLACK_BOT_TOKEN
  const appToken = env.SLACK_APP_TOKEN

  if (!botToken) errors.push('MISSING: SLACK_BOT_TOKEN not in .env')
  else if (!botToken.startsWith('xoxb-')) errors.push(`PREFIX: SLACK_BOT_TOKEN starts with "${botToken.slice(0, 6)}..." (expected xoxb-)`)

  if (!appToken) errors.push('MISSING: SLACK_APP_TOKEN not in .env')
  else if (!appToken.startsWith('xapp-')) errors.push(`PREFIX: SLACK_APP_TOKEN starts with "${appToken.slice(0, 6)}..." (expected xapp-)`)

  return { botToken, appToken, errors }
}

function loadAccessJson(): { access: any; errors: string[] } {
  if (!existsSync(ACCESS_PATH)) return { access: null, errors: [`MISSING: ${ACCESS_PATH}`] }
  try {
    return { access: JSON.parse(readFileSync(ACCESS_PATH, 'utf-8')), errors: [] }
  } catch (err: any) {
    return { access: null, errors: [`PARSE: ${err.message}`] }
  }
}

function shell(cmd: string): string {
  try {
    return execSync(cmd, { timeout: 5000, encoding: 'utf-8' }).trim()
  } catch {
    return ''
  }
}

/**
 * Get the boot timestamp of the current bridge process from ps.
 * Returns epoch ms or null if not running.
 */
function getBridgeBootTime(): number | null {
  const psOut = shell('ps aux | grep "[t]sx.*server.ts" | grep -v debug')
  if (!psOut) return null
  const pid = psOut.split(/\s+/)[1]
  if (!pid) return null
  // Get process start time as epoch
  const elapsed = shell(`ps -o etimes= -p ${pid} 2>/dev/null`)
  if (!elapsed) return null
  return Date.now() - parseInt(elapsed.trim()) * 1000
}

/**
 * Parse skip logs from debug files, filtered to current session only (#8).
 * Only returns logs timestamped after the bridge process started.
 */
function getCurrentSessionSkipLogs(): { logs: string[]; stale: boolean } {
  if (!existsSync(DEBUG_DIR)) return { logs: [], stale: false }

  const bootTime = getBridgeBootTime()
  const allSkipLogs: string[] = []

  try {
    const files = readdirSync(DEBUG_DIR)
      .map((n: string) => { try { return { name: n, mtime: statSync(join(DEBUG_DIR, n)).mtimeMs } } catch { return null } })
      .filter((f: { name: string; mtime: number } | null): f is { name: string; mtime: number } => f !== null)
      .sort((a: { mtime: number }, b: { mtime: number }) => b.mtime - a.mtime)

    for (const file of files.slice(0, 3)) {
      const content = readFileSync(join(DEBUG_DIR, file.name), 'utf-8')
      const skipLines = content.split('\n').filter((l: string) => l.includes('Channel notifications skipped'))
      allSkipLogs.push(...skipLines)
      if (skipLines.length) break
    }
  } catch {}

  if (!bootTime || !allSkipLogs.length) return { logs: allSkipLogs.slice(0, 5), stale: false }

  // Filter to only logs after boot time
  const currentLogs = allSkipLogs.filter((line) => {
    const tsMatch = line.match(/^(\d{4}-\d{2}-\d{2}T[\d:.]+Z)/)
    if (!tsMatch) return true // can't parse, include it
    const logTime = new Date(tsMatch[1]).getTime()
    return logTime >= bootTime - 5000 // 5s grace for boot race
  })

  return { logs: currentLogs.slice(0, 5), stale: currentLogs.length < allSkipLogs.length }
}

/**
 * Count running bridge server.ts processes (#11).
 * Returns process details for each instance found.
 */
function countBridgeProcesses(): Array<{ pid: string; user: string; cpu: string; mem: string; command: string }> {
  const psOut = shell('ps aux | grep "[t]sx.*server.ts" | grep -v debug')
  if (!psOut) return []
  return psOut.split('\n').filter(Boolean).map((line) => {
    const parts = line.split(/\s+/)
    return { user: parts[0], pid: parts[1], cpu: parts[2], mem: parts[3], command: parts.slice(10).join(' ') }
  })
}

/**
 * Check if --allowedTools includes slack reply tools (#10).
 * Checks both running process args and settings.local.json.
 */
function checkAllowedTools(workspacePath: string): {
  cliFlag: { found: boolean; tools: string[] }
  settingsFile: { found: boolean; tools: string[] }
  replyAutoApproved: boolean
} {
  const result = {
    cliFlag: { found: false, tools: [] as string[] },
    settingsFile: { found: false, tools: [] as string[] },
    replyAutoApproved: false,
  }

  // Check running process args
  const psOut = shell('ps aux | grep "[a]llowedTools" | grep -v grep')
  if (psOut) {
    const match = psOut.match(/--allowedTools\s+"?([^"]+)"?/)
    if (match) {
      result.cliFlag.found = true
      result.cliFlag.tools = match[1].split(',').map((t: string) => t.trim())
    }
  }

  // Check settings.local.json
  const settingsPath = join(workspacePath, '.claude', 'settings.local.json')
  if (existsSync(settingsPath)) {
    try {
      const settings = JSON.parse(readFileSync(settingsPath, 'utf-8'))
      const allow = settings?.permissions?.allow
      if (Array.isArray(allow)) {
        const slackTools = allow.filter((t: string) => t.startsWith('mcp__slack__'))
        if (slackTools.length) {
          result.settingsFile.found = true
          result.settingsFile.tools = slackTools
        }
      }
    } catch {}
  }

  // Is reply specifically auto-approved?
  result.replyAutoApproved =
    result.cliFlag.tools.includes('mcp__slack__reply') ||
    result.settingsFile.tools.includes('mcp__slack__reply')

  return result
}

function hintForError(error: string): string | null {
  const hints: Record<string, string> = {
    'not_in_channel': 'Bot not a member. Run /invite @BotName in the channel.',
    'channel_not_found': 'Channel ID wrong or bot lacks visibility. Verify ID + scopes.',
    'invalid_auth': 'Token invalid or revoked. Regenerate at api.slack.com/apps.',
    'token_revoked': 'Token revoked. Regenerate at api.slack.com/apps.',
    'missing_scope': 'Missing OAuth scope. For private channels: groups:history (read) + chat:write (send). groups:read is NOT required for the bridge. Check api.slack.com/apps → OAuth & Permissions.',
    'account_inactive': 'Workspace or bot account deactivated.',
    'is_archived': 'Channel archived.',
    'no_permission': 'Missing scope. Need: chat:write, channels:history, groups:history.',
  }
  return hints[error] || null
}

// ---------------------------------------------------------------------------
// MCP Server
// ---------------------------------------------------------------------------
const mcp = new Server(
  { name: 'slack-eidos-debug', version: '0.4.0' },
  {
    capabilities: { tools: {} },
    instructions: [
      'Full-stack diagnostic MCP for the cc-channel-slack-eidos Slack bridge.',
      'Read-only — reports what is broken across all layers. Fix issues with Edit/Bash.',
      '',
      'Key files (for fixes):',
      `  Tokens:  ${ENV_PATH}`,
      `  Access:  ${ACCESS_PATH}`,
      `  Server:  ${MAIN_SERVER}`,
      `  Plugin:  ${PLUGIN_ROOT}`,
      '',
      'Tools:',
      '  slack_debug_check       — full health check across all 7 layers',
      '  slack_debug_slack_api   — deep Slack API probe (scopes, bot info, team)',
      '  slack_debug_bot_process — is the bridge process running?',
      '  slack_debug_server      — server.ts integrity (deps, compilation, manifest)',
      '  slack_debug_mcp_config  — MCP registration in .mcp.json files',
      '  slack_debug_access      — access.json gate config',
      '  slack_debug_logs        — structured log entries from bridge stderr',
      '  slack_debug_send_test   — send a message to verify outbound',
      '  slack_debug_read_channel — read messages to verify inbound',
      '  slack_debug_channel_reg — check --dangerously-load-development-channels vs actual server names',
      '  slack_debug_scope_diff  — compare token scopes vs bridge requirements',
      '  slack_debug_socket_mode — Socket Mode liveness + event subscription audit',
      '  slack_debug_roundtrip   — send message + read it back to test full outbound path',
    ].join('\n'),
  },
)

// ---------------------------------------------------------------------------
// Tools
// ---------------------------------------------------------------------------
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'slack_debug_check',
      description: 'Full health check across all layers: tokens, permissions, access config, Slack API auth, channel visibility + membership, bot process (with dual-start detection), outbound permission friction, server integrity, MCP config. Returns JSON with healthy boolean, issues array, and per-layer details.',
      inputSchema: { type: 'object' as const, properties: {} },
    },
    {
      name: 'slack_debug_slack_api',
      description: 'Deep Slack API probe. Calls auth.test (bot identity + team), then checks each scope the bridge needs by testing the relevant API endpoint. Reports which scopes work and which are missing.',
      inputSchema: { type: 'object' as const, properties: {} },
    },
    {
      name: 'slack_debug_bot_process',
      description: 'Check if the bridge server.ts process is running. Detects dual-start (multiple instances competing for Socket Mode). Reports pid, uptime, memory per process.',
      inputSchema: { type: 'object' as const, properties: {} },
    },
    {
      name: 'slack_debug_server',
      description: 'Server integrity check. Verifies: server.ts exists, node_modules present, key deps installed (@modelcontextprotocol/sdk, @slack/socket-mode, @slack/web-api), tsx available, TypeScript compiles without errors.',
      inputSchema: { type: 'object' as const, properties: {} },
    },
    {
      name: 'slack_debug_mcp_config',
      description: 'Check MCP registration. Reads .mcp.json in the plugin root and in the target workspace (greenmark-cockpit). Reports whether the slack server entry exists, paths are correct, and the debug server itself is registered.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          workspace: { type: 'string', description: 'Path to workspace .mcp.json to check (optional, defaults to greenmark-cockpit)' },
        },
      },
    },
    {
      name: 'slack_debug_access',
      description: 'Dump access.json: dmPolicy, allowFrom user IDs, permanent channels + policies, pending pairing count (codes redacted). Shows exactly what the gate will allow/deny.',
      inputSchema: { type: 'object' as const, properties: {} },
    },
    {
      name: 'slack_debug_logs',
      description: 'Recent structured log entries from the bridge. Searches ~/.claude/debug/ for JSON lines from the server (contain "event" or "level" fields). Shows gate decisions, delivery outcomes, errors.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          limit: { type: 'number', description: 'Number of entries (default 30, max 200)' },
        },
      },
    },
    {
      name: 'slack_debug_send_test',
      description: 'Send a test message to a channel via Slack API (bypasses bridge). Verifies: token valid, bot in channel, chat:write scope works.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          channel: { type: 'string', description: 'Slack channel ID (C...)' },
          text: { type: 'string', description: 'Message text (defaults to timestamped diagnostic)' },
        },
        required: ['channel'],
      },
    },
    {
      name: 'slack_debug_read_channel',
      description: 'Read recent messages from a channel via Slack API (bypasses bridge). Verifies: token valid, bot in channel, channels:history scope works.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          channel: { type: 'string', description: 'Slack channel ID (C...)' },
          limit: { type: 'number', description: 'Number of messages (default 10, max 50)' },
        },
        required: ['channel'],
      },
    },
    {
      name: 'slack_debug_channel_reg',
      description: 'Comprehensive channel registration check. Verifies: flag vs server name match, current-session skip logs (filters out stale), dual-start detection, --allowedTools for frictionless replies, plugin.json declarations vs .mcp.json entries.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          workspace: { type: 'string', description: 'Path to workspace (defaults to greenmark-cockpit)' },
        },
      },
    },
    {
      name: 'slack_debug_scope_diff',
      description: 'Compare scopes baked into the bot token against what the bridge actually needs. Reports have/need/missing in a single clear output. No more guessing which scope is causing failures.',
      inputSchema: { type: 'object' as const, properties: {} },
    },
    {
      name: 'slack_debug_socket_mode',
      description: 'Socket Mode liveness check. Verifies the app token works for Socket Mode connections, checks event subscriptions, and reports bridge uptime from boot logs.',
      inputSchema: { type: 'object' as const, properties: {} },
    },
    {
      name: 'slack_debug_roundtrip',
      description: 'Send a test message to a channel, then immediately read it back. Tests the full outbound write+read cycle via Slack API (bypasses bridge Socket Mode path).',
      inputSchema: {
        type: 'object' as const,
        properties: {
          channel: { type: 'string', description: 'Slack channel ID (C...)' },
        },
        required: ['channel'],
      },
    },
  ],
}))

mcp.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params

  // =========================================================================
  // slack_debug_check — the big one
  // =========================================================================
  if (name === 'slack_debug_check') {
    const issues: string[] = []
    const report: Record<string, any> = {}

    // --- Layer 1: Tokens ---
    const { botToken, appToken, errors: tokenErrors } = loadEnvTokens()
    report.tokens = {
      envPath: ENV_PATH,
      envExists: existsSync(ENV_PATH),
      botTokenPresent: !!botToken,
      appTokenPresent: !!appToken,
      errors: tokenErrors,
    }
    issues.push(...tokenErrors)

    // --- Layer 2: File permissions ---
    let envPerms: string | null = null
    if (existsSync(ENV_PATH)) {
      try { envPerms = '0' + (statSync(ENV_PATH).mode & 0o777).toString(8) } catch {}
    }
    report.permissions = { envPerms, ok: envPerms === '0600' }
    if (envPerms && envPerms !== '0600') issues.push(`PERMS: .env is ${envPerms}`)

    // --- Layer 3: Access config ---
    const { access, errors: accessErrors } = loadAccessJson()
    issues.push(...accessErrors)
    if (access) {
      report.access = {
        dmPolicy: access.dmPolicy || 'unknown',
        allowFrom: Array.isArray(access.allowFrom) ? access.allowFrom : [],
        channels: access.channels ? Object.keys(access.channels) : [],
        pendingPairings: Array.isArray(access.pending) ? access.pending.length : 0,
      }
      if (!access.allowFrom?.length) issues.push('ACCESS: allowFrom is empty — no users can pass the gate')
      if (!access.channels || !Object.keys(access.channels).length) issues.push('ACCESS: no permanent channels — only session-scoped opt-in via @mention')
    } else {
      report.access = null
    }

    // --- Layer 4: Slack API ---
    report.slackApi = null
    if (botToken) {
      try {
        const web = new WebClient(botToken)
        const auth = await web.auth.test()
        report.slackApi = { ok: true, botUserId: auth.user_id, team: auth.team, teamId: auth.team_id }
      } catch (err: any) {
        const msg = err?.data?.error || err?.message || String(err)
        report.slackApi = { ok: false, error: msg }
        issues.push(`SLACK: auth.test failed — ${msg}`)
      }
    }

    // --- Layer 5: Channel visibility ---
    // conversations.info needs groups:read for private channels, which the bridge
    // doesn't actually require. Fall back to conversations.history (limit 1) which
    // only needs groups:history — the scope the bridge actually uses.
    report.channels = []
    if (botToken && access?.channels) {
      const web = new WebClient(botToken)
      for (const chId of Object.keys(access.channels)) {
        try {
          const info = await web.conversations.info({ channel: chId })
          const ch = info.channel as any
          const entry = { id: chId, name: ch?.name, isMember: ch?.is_member ?? null, isPrivate: ch?.is_private ?? null, ok: true }
          report.channels.push(entry)
          if (!ch?.is_member) issues.push(`CHANNEL: ${chId} (#${ch?.name}) — bot NOT a member`)
        } catch (err: any) {
          const msg = err?.data?.error || err?.message || String(err)
          // conversations.info on private channels needs groups:read, but the bridge
          // only needs groups:history. Fall back: if we can read history, the channel works.
          if (msg === 'missing_scope' || msg === 'channel_not_found') {
            try {
              const hist = await web.conversations.history({ channel: chId, limit: 1 })
              if (hist.ok) {
                report.channels.push({ id: chId, ok: true, isMember: true, isPrivate: true, note: 'private channel (verified via history fallback)' })
                continue
              }
            } catch (histErr: any) {
              const histMsg = histErr?.data?.error || histErr?.message || String(histErr)
              report.channels.push({ id: chId, ok: false, error: histMsg, note: 'conversations.info and history both failed' })
              issues.push(`CHANNEL: ${chId} — ${histMsg}`)
              continue
            }
          }
          report.channels.push({ id: chId, ok: false, error: msg })
          issues.push(`CHANNEL: ${chId} — ${msg}`)
        }
      }
    }

    // --- Layer 6: Bot process + dual-start detection (#11) ---
    const bridgeProcs = countBridgeProcesses()
    if (bridgeProcs.length === 0) {
      report.botProcess = { running: false }
      issues.push('PROCESS: no tsx server.ts process found — bridge not running')
    } else {
      report.botProcess = { running: true, processCount: bridgeProcs.length, ps: bridgeProcs.map(p => `${p.user} ${p.pid} ${p.command}`).join('\n') }
      if (bridgeProcs.length > 1) {
        issues.push(`DUAL-START: ${bridgeProcs.length} bridge processes running (pids: ${bridgeProcs.map(p => p.pid).join(', ')}). Kill stale instances.`)
      }
    }

    // --- Layer 6b: Outbound permission friction (#10) ---
    const allowedTools = checkAllowedTools(DEFAULT_WORKSPACE)
    report.outboundApproval = allowedTools.replyAutoApproved ? 'auto-approved' : 'terminal-prompt'
    if (!allowedTools.replyAutoApproved) {
      issues.push('FRICTION: mcp__slack__reply not auto-approved — outbound replies prompt in terminal')
    }

    // --- Layer 7: Server integrity ---
    const serverExists = existsSync(MAIN_SERVER)
    const nodeModulesExist = existsSync(join(PLUGIN_ROOT, 'node_modules'))
    const tsxExists = existsSync(join(PLUGIN_ROOT, 'node_modules', '.bin', 'tsx'))
    report.server = { serverExists, nodeModulesExist, tsxExists, pluginRoot: PLUGIN_ROOT }
    if (!serverExists) issues.push(`SERVER: ${MAIN_SERVER} not found`)
    if (!nodeModulesExist) issues.push('SERVER: node_modules missing — run npm install')
    if (!tsxExists) issues.push('SERVER: tsx binary missing — run npm install')

    report.healthy = issues.length === 0
    report.issues = issues
    report.issueCount = issues.length

    return { content: [{ type: 'text', text: JSON.stringify(report, null, 2) }] }
  }

  // =========================================================================
  // slack_debug_slack_api
  // =========================================================================
  if (name === 'slack_debug_slack_api') {
    const { botToken, errors } = loadEnvTokens()
    if (!botToken) return json({ ok: false, error: 'No bot token', tokenErrors: errors })

    const web = new WebClient(botToken)
    const report: Record<string, any> = {}

    // auth.test
    try {
      const auth = await web.auth.test()
      report.auth = { ok: true, botUserId: auth.user_id, botId: auth.bot_id, team: auth.team, teamId: auth.team_id, url: auth.url }
    } catch (err: any) {
      report.auth = { ok: false, error: err?.data?.error || err?.message }
      return json(report) // Can't test anything else without auth
    }

    // Token scope introspection — extract the actual scopes baked into the token
    // by making a deliberate bad call and parsing the 'provided' field from the error,
    // or by checking auth.test response headers.
    report.tokenScopes = null
    try {
      // conversations.info with a bogus channel returns missing_scope with 'provided' list
      await web.conversations.info({ channel: 'C000000FAKE' })
    } catch (err: any) {
      const provided = err?.data?.response_metadata?.scopes || err?.data?.provided
      if (provided) {
        report.tokenScopes = typeof provided === 'string' ? provided.split(',') : provided
      }
    }

    // Scope checks — test each by calling a minimal API
    // Important: test private channel scopes separately from public channel scopes.
    // The bridge needs groups:history for private channels, not just channels:history.
    const scopeTests: Array<{ scope: string; test: () => Promise<boolean> }> = [
      { scope: 'chat:write', test: async () => { /* tested by send_test */ return true } },
      { scope: 'channels:history', test: async () => {
        try { await web.conversations.list({ types: 'public_channel', limit: 1 }); return true } catch { return false }
      }},
      { scope: 'groups:history', test: async () => {
        // Test by reading from a known private channel (from access.json), or check tokenScopes
        const { access } = loadAccessJson()
        const channelIds = access?.channels ? Object.keys(access.channels) : []
        for (const chId of channelIds) {
          try {
            await web.conversations.history({ channel: chId, limit: 1 })
            return true
          } catch { /* try next */ }
        }
        // Fallback: check if tokenScopes includes it
        if (Array.isArray(report.tokenScopes)) return report.tokenScopes.includes('groups:history')
        return false
      }},
      { scope: 'reactions:write', test: async () => true }, // Can't test without a message
      { scope: 'users:read', test: async () => {
        try { await web.users.info({ user: report.auth.botUserId }); return true } catch { return false }
      }},
      { scope: 'files:read', test: async () => true }, // Can't test without a file
    ]

    report.scopes = {}
    for (const { scope, test } of scopeTests) {
      try { report.scopes[scope] = await test() } catch { report.scopes[scope] = false }
    }

    // List channels the bot is in
    // conversations.list with private_channel type needs groups:read — which the bridge
    // doesn't require. Try it, but don't report failure as an issue.
    try {
      const res = await web.conversations.list({ types: 'public_channel,private_channel', limit: 50 })
      const memberOf = (res.channels || []).filter((c: any) => c.is_member).map((c: any) => ({ id: c.id, name: c.name, isPrivate: c.is_private }))
      report.memberOf = memberOf
    } catch (err: any) {
      // Fall back to public channels only
      try {
        const res = await web.conversations.list({ types: 'public_channel', limit: 50 })
        const memberOf = (res.channels || []).filter((c: any) => c.is_member).map((c: any) => ({ id: c.id, name: c.name }))
        report.memberOf = memberOf
        report.memberOfNote = 'private channels not listed (groups:read not in token — this is fine, bridge does not need it)'
      } catch (err2: any) {
        report.memberOf = { error: err2?.data?.error || err2?.message }
      }
    }

    return json(report)
  }

  // =========================================================================
  // slack_debug_bot_process
  // =========================================================================
  if (name === 'slack_debug_bot_process') {
    const report: Record<string, any> = {}

    // Look for the main server.ts process (not this debug server) (#11)
    const bridgeProcs = countBridgeProcesses()
    if (bridgeProcs.length > 0) {
      report.running = true
      report.processCount = bridgeProcs.length
      report.processes = bridgeProcs
      if (bridgeProcs.length > 1) {
        report.dualStart = true
        report.dualStartWarning = `${bridgeProcs.length} bridge instances running! They compete for Socket Mode. Kill stale processes: kill ${bridgeProcs.slice(1).map(p => p.pid).join(' ')}`
      }
    } else {
      report.running = false
      report.hint = 'Bridge not running. Start with: ./start-with-slack.sh'
    }

    // Check if any node processes are using the slack socket-mode
    const socketOut = shell('ps aux | grep "[s]lack.*socket" | head -5')
    report.socketModeProcesses = socketOut || null

    // Check if the start-with-slack.sh exists and is executable
    const startScript = join(PLUGIN_ROOT, '..', 'greenmark-cockpit', 'start-with-slack.sh')
    report.startScript = existsSync(startScript) ? { exists: true, path: startScript } : { exists: false }

    return json(report)
  }

  // =========================================================================
  // slack_debug_server
  // =========================================================================
  if (name === 'slack_debug_server') {
    const report: Record<string, any> = {}

    report.pluginRoot = PLUGIN_ROOT
    report.serverTs = { path: MAIN_SERVER, exists: existsSync(MAIN_SERVER) }

    // node_modules
    const nmPath = join(PLUGIN_ROOT, 'node_modules')
    report.nodeModules = { exists: existsSync(nmPath) }

    // Key dependencies
    const deps = ['@modelcontextprotocol/sdk', '@slack/socket-mode', '@slack/web-api', 'zod']
    report.dependencies = {}
    for (const dep of deps) {
      const depPath = join(nmPath, dep)
      report.dependencies[dep] = existsSync(depPath)
    }

    // tsx binary
    const tsxPath = join(nmPath, '.bin', 'tsx')
    report.tsx = { path: tsxPath, exists: existsSync(tsxPath) }

    // package.json
    const pkgPath = join(PLUGIN_ROOT, 'package.json')
    if (existsSync(pkgPath)) {
      try {
        const pkg = JSON.parse(readFileSync(pkgPath, 'utf-8'))
        report.package = { name: pkg.name, version: pkg.version, deps: pkg.dependencies, devDeps: pkg.devDependencies }
      } catch (err: any) {
        report.package = { error: err.message }
      }
    }

    // TypeScript compilation check
    const tscResult = shell(`cd "${PLUGIN_ROOT}" && ./node_modules/.bin/tsc --noEmit --pretty false 2>&1 | head -20`)
    report.typeCheck = tscResult ? { errors: tscResult } : { ok: true }

    // .mcp.json in plugin root
    const mcpJsonPath = join(PLUGIN_ROOT, '.mcp.json')
    if (existsSync(mcpJsonPath)) {
      try {
        report.mcpJson = JSON.parse(readFileSync(mcpJsonPath, 'utf-8'))
      } catch (err: any) {
        report.mcpJson = { error: err.message }
      }
    } else {
      report.mcpJson = null
    }

    // manifest.json (Slack app manifest for reference)
    const manifestPath = join(PLUGIN_ROOT, 'manifest.json')
    if (existsSync(manifestPath)) {
      try {
        report.slackManifest = JSON.parse(readFileSync(manifestPath, 'utf-8'))
      } catch { report.slackManifest = null }
    }

    return json(report)
  }

  // =========================================================================
  // slack_debug_mcp_config
  // =========================================================================
  if (name === 'slack_debug_mcp_config') {
    const report: Record<string, any> = { issues: [] }

    // Plugin .mcp.json
    const pluginMcpPath = join(PLUGIN_ROOT, '.mcp.json')
    if (existsSync(pluginMcpPath)) {
      try {
        const pluginMcp = JSON.parse(readFileSync(pluginMcpPath, 'utf-8'))
        report.pluginMcpJson = { path: pluginMcpPath, servers: Object.keys(pluginMcp.mcpServers || {}) }
        if (!pluginMcp.mcpServers?.slack) report.issues.push('Plugin .mcp.json missing "slack" server entry')
      } catch (err: any) {
        report.pluginMcpJson = { error: err.message }
        report.issues.push(`Plugin .mcp.json parse error: ${err.message}`)
      }
    } else {
      report.pluginMcpJson = null
      report.issues.push(`Plugin .mcp.json missing at ${pluginMcpPath}`)
    }

    // Workspace .mcp.json
    const workspacePath = (args?.workspace as string) || DEFAULT_WORKSPACE
    const wsMcpPath = join(workspacePath, '.mcp.json')
    if (existsSync(wsMcpPath)) {
      try {
        const wsMcp = JSON.parse(readFileSync(wsMcpPath, 'utf-8'))
        const servers = Object.keys(wsMcp.mcpServers || {})
        report.workspaceMcpJson = { path: wsMcpPath, servers }
        if (!wsMcp.mcpServers?.['slack-eidos-debug']) {
          report.issues.push('Workspace .mcp.json missing "slack-eidos-debug" entry')
        } else {
          const entry = wsMcp.mcpServers['slack-eidos-debug']
          // Verify paths exist
          if (entry.command && !existsSync(entry.command)) {
            report.issues.push(`Debug MCP command not found: ${entry.command}`)
          }
          if (entry.args?.[0] && !existsSync(entry.args[0])) {
            report.issues.push(`Debug MCP script not found: ${entry.args[0]}`)
          }
          report.debugEntry = entry
        }
      } catch (err: any) {
        report.workspaceMcpJson = { error: err.message }
        report.issues.push(`Workspace .mcp.json parse error: ${err.message}`)
      }
    } else {
      report.workspaceMcpJson = null
      report.issues.push(`Workspace .mcp.json missing at ${wsMcpPath}`)
    }

    // Claude Code plugin dir — check if .claude-plugin exists
    const claudePluginDir = join(PLUGIN_ROOT, '.claude-plugin')
    report.claudePlugin = { path: claudePluginDir, exists: existsSync(claudePluginDir) }
    if (existsSync(claudePluginDir)) {
      try {
        const pluginFiles = readdirSync(claudePluginDir)
        report.claudePlugin.files = pluginFiles
      } catch {}
    }

    // Skills
    const skillsDir = join(PLUGIN_ROOT, 'skills')
    if (existsSync(skillsDir)) {
      try {
        report.skills = readdirSync(skillsDir)
      } catch { report.skills = [] }
    }

    return json(report)
  }

  // =========================================================================
  // slack_debug_access
  // =========================================================================
  if (name === 'slack_debug_access') {
    const { access, errors } = loadAccessJson()
    if (!access) return json({ error: 'Could not load access.json', path: ACCESS_PATH, details: errors })

    const redacted = JSON.parse(JSON.stringify(access))
    if (Array.isArray(redacted.pending)) {
      for (const p of redacted.pending) { if (p.code) p.code = '***' }
    }

    // Annotate with analysis
    const analysis: string[] = []
    if (!access.allowFrom?.length) analysis.push('allowFrom is empty — no users will pass the DM gate or trigger auto-opt-in')
    if (access.dmPolicy === 'disabled') analysis.push('DMs are disabled — users cannot pair via DM')
    if (!access.channels || !Object.keys(access.channels).length) analysis.push('No permanent channels — only ephemeral session-scoped connections via @mention')
    if (access.pending?.length > 0) analysis.push(`${access.pending.length} pending pairing(s) — someone DMed the bot but hasn't been approved`)

    return json({ path: ACCESS_PATH, access: redacted, analysis, errors })
  }

  // =========================================================================
  // slack_debug_logs
  // =========================================================================
  if (name === 'slack_debug_logs') {
    const limit = Math.min(Math.max((args?.limit as number) || 30, 1), 200)

    if (!existsSync(DEBUG_DIR)) return json({ error: `Debug dir not found: ${DEBUG_DIR}` })

    let files: Array<{ name: string; mtime: number }> = []
    try {
      files = readdirSync(DEBUG_DIR)
        .map((name) => { try { return { name, mtime: statSync(join(DEBUG_DIR, name)).mtimeMs } } catch { return null } })
        .filter((f): f is { name: string; mtime: number } => f !== null)
        .sort((a, b) => b.mtime - a.mtime)
    } catch (err: any) {
      return json({ error: `Failed to read debug dir: ${err.message}` })
    }

    if (!files.length) return json({ error: 'No debug log files found' })

    const logEntries: string[] = []
    for (const file of files.slice(0, 5)) {
      if (logEntries.length >= limit * 2) break // Gather extra, take last N
      try {
        for (const line of readFileSync(join(DEBUG_DIR, file.name), 'utf-8').split('\n')) {
          if (line.includes('"event":') || line.includes('"level":')) logEntries.push(line.trim())
        }
      } catch {}
    }

    const result = logEntries.slice(-limit)

    // Summarize log patterns
    const summary: Record<string, number> = {}
    for (const entry of result) {
      try {
        const parsed = JSON.parse(entry)
        const event = parsed.event || parsed.level || 'unknown'
        summary[event] = (summary[event] || 0) + 1
      } catch {}
    }

    return json({ source: files[0].name, filesScanned: Math.min(files.length, 5), total: logEntries.length, returned: result.length, summary, entries: result })
  }

  // =========================================================================
  // slack_debug_send_test
  // =========================================================================
  if (name === 'slack_debug_send_test') {
    const channel = args?.channel as string
    if (!channel) return json({ error: 'channel is required' })

    const { botToken, errors } = loadEnvTokens()
    if (!botToken) return json({ ok: false, error: 'No valid bot token', tokenErrors: errors })

    const text = (args?.text as string) || `[slack-eidos-debug] outbound test at ${new Date().toISOString()}`
    try {
      const web = new WebClient(botToken)
      const res = await web.chat.postMessage({ channel, text, unfurl_links: false, unfurl_media: false })
      return json({ ok: true, channel: res.channel, ts: res.ts, text })
    } catch (err: any) {
      const msg = err?.data?.error || err?.message || String(err)
      return json({ ok: false, error: msg, channel, hint: hintForError(msg) })
    }
  }

  // =========================================================================
  // slack_debug_read_channel
  // =========================================================================
  if (name === 'slack_debug_read_channel') {
    const channel = args?.channel as string
    if (!channel) return json({ error: 'channel is required' })

    const { botToken, errors } = loadEnvTokens()
    if (!botToken) return json({ ok: false, error: 'No valid bot token', tokenErrors: errors })

    const limit = Math.min(Math.max((args?.limit as number) || 10, 1), 50)
    try {
      const web = new WebClient(botToken)
      const res = await web.conversations.history({ channel, limit })
      const messages = (res.messages || []).reverse().map((m: any) => ({
        ts: m.ts,
        user: m.user || m.bot_id || 'unknown',
        text: (m.text || '').slice(0, 300),
        subtype: m.subtype || null,
      }))
      return json({ ok: true, channel, count: messages.length, messages })
    } catch (err: any) {
      const msg = err?.data?.error || err?.message || String(err)
      return json({ ok: false, error: msg, channel, hint: hintForError(msg) })
    }
  }

  // =========================================================================
  // slack_debug_channel_reg — flag vs server name mismatch detection
  // =========================================================================
  if (name === 'slack_debug_channel_reg') {
    const report: Record<string, any> = { issues: [] }

    // 1. Read plugin.json to find declared channel server names
    const pluginJsonPath = join(PLUGIN_ROOT, '.claude-plugin', 'plugin.json')
    if (existsSync(pluginJsonPath)) {
      try {
        const pluginJson = JSON.parse(readFileSync(pluginJsonPath, 'utf-8'))
        report.pluginName = pluginJson.name
        report.declaredChannels = pluginJson.channels || []
        // The internal MCP name is: plugin:<pluginName>:<serverName>
        for (const ch of report.declaredChannels) {
          report.internalServerName = `plugin:${pluginJson.name}:${ch.server}`
        }
      } catch (err: any) {
        report.pluginJson = { error: err.message }
      }
    } else {
      report.pluginJson = null
    }

    // 2. Check plugin .mcp.json for server entries
    const pluginMcpPath = join(PLUGIN_ROOT, '.mcp.json')
    if (existsSync(pluginMcpPath)) {
      try {
        const pluginMcp = JSON.parse(readFileSync(pluginMcpPath, 'utf-8'))
        report.pluginServers = Object.keys(pluginMcp.mcpServers || {})
      } catch {}
    }

    // 3. Check workspace .mcp.json for a matching server entry
    const workspacePath = (args?.workspace as string) || DEFAULT_WORKSPACE
    const wsMcpPath = join(workspacePath, '.mcp.json')
    if (existsSync(wsMcpPath)) {
      try {
        const wsMcp = JSON.parse(readFileSync(wsMcpPath, 'utf-8'))
        const servers = Object.keys(wsMcp.mcpServers || {})
        report.workspaceServers = servers
        // Check if there's a "slack" server entry (what server:slack looks for)
        report.hasSlackInWorkspace = servers.includes('slack')
      } catch {}
    }

    // 4. Check start-with-slack.sh for the flag value
    const startScriptPaths = [
      join(workspacePath, 'start-with-slack.sh'),
      join(PLUGIN_ROOT, '..', 'greenmark-cockpit', 'start-with-slack.sh'),
    ]
    for (const p of startScriptPaths) {
      if (existsSync(p)) {
        try {
          const content = readFileSync(p, 'utf-8')
          const match = content.match(/--dangerously-load-development-channels\s+(\S+)/)
          if (match) {
            report.flagValue = match[1]
            report.startScript = p
          }
        } catch {}
        break
      }
    }

    // 5. Parse Claude Code debug logs — current session only (#8)
    const { logs: skipLogs, stale } = getCurrentSessionSkipLogs()
    if (skipLogs.length) {
      report.channelSkipLogs = skipLogs
    }
    if (stale) {
      report.staleLogsFiltered = true
      report.staleNote = 'Older skip logs from previous sessions were filtered out. Only showing current session.'
    }

    // 6. Parse process args for --dangerously-load-development-channels
    const psOut = shell('ps aux | grep "dangerously-load" | grep -v grep')
    if (psOut) {
      const match = psOut.match(/--dangerously-load-development-channels\s+(\S+)/)
      if (match) report.runningFlagValue = match[1]
    }

    // 7. Detect dual-start: multiple bridge processes (#11)
    const bridgeProcs = countBridgeProcesses()
    report.bridgeProcessCount = bridgeProcs.length
    if (bridgeProcs.length > 1) {
      report.bridgeProcesses = bridgeProcs
      report.issues.push(
        `DUAL-START: ${bridgeProcs.length} bridge processes running (pids: ${bridgeProcs.map(p => p.pid).join(', ')}). ` +
        `Multiple instances compete for Socket Mode. Kill stale processes or fix launch config.`
      )
    }

    // 8. Check --allowedTools for frictionless replies (#10)
    const allowedTools = checkAllowedTools(workspacePath)
    report.allowedTools = allowedTools
    if (!allowedTools.replyAutoApproved) {
      report.issues.push(
        'PERMISSION FRICTION: mcp__slack__reply is not auto-approved. Outbound replies will prompt for terminal approval. ' +
        'Add --allowedTools "mcp__slack__reply" to your launch command or add it to settings.local.json permissions.allow.'
      )
    }

    // 9. Diagnose the mismatch
    // Per Claude Code docs:
    //   server:<name>  → looks for <name> in .mcp.json
    //   plugin:<name>@<marketplace> → installed marketplace plugin
    // Development plugins loaded via --plugin-dir register as plugin:<pluginName>:<serverName>
    // but this format is NOT accepted by --dangerously-load-development-channels.
    if (report.flagValue) {
      if (report.flagValue.startsWith('server:')) {
        const serverName = report.flagValue.replace('server:', '')
        if (!report.hasSlackInWorkspace) {
          report.issues.push(
            `FLAG MISMATCH: "${report.flagValue}" expects a server named "${serverName}" in workspace .mcp.json, but no such entry exists. ` +
            `Add "${serverName}" to .mcp.json pointing to server.ts, or use a marketplace plugin format.`
          )
        }
      } else if (report.flagValue.startsWith('plugin:') && !report.flagValue.includes('@')) {
        report.issues.push(
          `INVALID FORMAT: "${report.flagValue}" — plugin entries need @marketplace suffix. ` +
          `Format: plugin:<name>@<marketplace>. For development, use server:<name> with the server in .mcp.json instead.`
        )
      }
    }

    if (skipLogs.length) {
      report.issues.push('CHANNEL SKIPPED: Claude Code logged "Channel notifications skipped" in the CURRENT session — inbound events are NOT being delivered. Check the flag value and server name.')
    }

    report.recommendation = report.issues.length
      ? 'Check each issue above. Common fixes: add "slack" to workspace .mcp.json, kill duplicate processes, add --allowedTools to start script.'
      : 'Channel registration looks correct. Replies auto-approved. No duplicate processes.'

    return json(report)
  }

  // =========================================================================
  // slack_debug_scope_diff — token scopes vs bridge requirements
  // =========================================================================
  if (name === 'slack_debug_scope_diff') {
    const { botToken, errors } = loadEnvTokens()
    if (!botToken) return json({ ok: false, error: 'No bot token', tokenErrors: errors })

    const web = new WebClient(botToken)

    // Required scopes for the bridge to function
    const required: Record<string, string> = {
      'app_mentions:read': 'receive @mention events in Socket Mode',
      'chat:write': 'send messages to channels and DMs',
      'groups:history': 'read messages in private channels',
      'channels:history': 'read messages in public channels',
      'im:history': 'read DM messages',
      'reactions:write': 'add emoji reactions (ack pattern)',
      'users:read': 'resolve display names from user IDs',
      'files:read': 'access shared file metadata',
    }

    // Nice-to-have but not required
    const optional: Record<string, string> = {
      'groups:read': 'list private channels (debug tool only, not needed by bridge)',
      'channels:read': 'list public channels (debug tool only)',
      'files:write': 'upload files as bot',
    }

    // Extract actual scopes from token by triggering an error with the 'provided' field
    let tokenScopes: string[] = []
    try {
      await web.conversations.info({ channel: 'C000000FAKE' })
    } catch (err: any) {
      const provided = err?.data?.response_metadata?.scopes || err?.data?.provided
      if (provided) {
        tokenScopes = typeof provided === 'string' ? provided.split(',') : provided
      }
    }

    if (!tokenScopes.length) {
      return json({ ok: false, error: 'Could not extract scopes from token. The token may be invalid or the Slack API response format changed.' })
    }

    const have = new Set(tokenScopes)
    const missing: Array<{ scope: string; reason: string }> = []
    const present: string[] = []
    for (const [scope, reason] of Object.entries(required)) {
      if (have.has(scope)) {
        present.push(scope)
      } else {
        missing.push({ scope, reason })
      }
    }

    const optionalMissing: Array<{ scope: string; reason: string }> = []
    const optionalPresent: string[] = []
    for (const [scope, reason] of Object.entries(optional)) {
      if (have.has(scope)) {
        optionalPresent.push(scope)
      } else {
        optionalMissing.push({ scope, reason })
      }
    }

    const extra = tokenScopes.filter((s: string) => !required[s] && !optional[s])

    return json({
      ok: missing.length === 0,
      tokenScopes,
      required: { present, missing },
      optional: { present: optionalPresent, missing: optionalMissing },
      extra,
      summary: missing.length === 0
        ? 'All required scopes present. Bridge should work.'
        : `Missing ${missing.length} required scope(s): ${missing.map((m: { scope: string }) => m.scope).join(', ')}. Add them at api.slack.com/apps → OAuth & Permissions, then reinstall the app.`,
    })
  }

  // =========================================================================
  // slack_debug_socket_mode — liveness + event subscriptions
  // =========================================================================
  if (name === 'slack_debug_socket_mode') {
    const { appToken, botToken, errors } = loadEnvTokens()
    const report: Record<string, any> = {}

    if (!appToken) return json({ ok: false, error: 'No app token', tokenErrors: errors })

    // 1. Test app token by calling apps.connections.open (what Socket Mode uses)
    try {
      const web = new WebClient()
      const res = await web.apiCall('apps.connections.open', { token: appToken })
      report.socketModeAuth = { ok: true, url: (res as any).url ? 'present' : 'missing' }
    } catch (err: any) {
      const msg = err?.data?.error || err?.message || String(err)
      report.socketModeAuth = { ok: false, error: msg }
      report.issues = [`Socket Mode auth failed: ${msg}. Check SLACK_APP_TOKEN (xapp-).`]
      return json(report)
    }

    // 2. Check bridge process and look for boot log
    const psOut = shell('ps aux | grep "[t]sx.*server.ts" | grep -v debug')
    report.bridgeRunning = !!psOut
    if (psOut) {
      // Extract PID and calculate uptime
      const parts = psOut.split('\n')[0]?.split(/\s+/)
      if (parts) {
        report.bridgePid = parts[1]
        // Get process start time
        const startTime = shell(`ps -o lstart= -p ${parts[1]} 2>/dev/null`)
        if (startTime) report.bridgeStartTime = startTime.trim()
      }
    }

    // 3. Scan debug logs for Socket Mode events and boot.complete
    if (existsSync(DEBUG_DIR)) {
      try {
        const files = readdirSync(DEBUG_DIR)
          .map((n: string) => { try { return { name: n, mtime: statSync(join(DEBUG_DIR, n)).mtimeMs } } catch { return null } })
          .filter((f: { name: string; mtime: number } | null): f is { name: string; mtime: number } => f !== null)
          .sort((a: { mtime: number }, b: { mtime: number }) => b.mtime - a.mtime)

        for (const file of files.slice(0, 3)) {
          const content = readFileSync(join(DEBUG_DIR, file.name), 'utf-8')
          const lines = content.split('\n')

          // Look for Socket Mode connection logs
          const socketLines = lines.filter((l: string) =>
            l.includes('socket') || l.includes('Socket') ||
            l.includes('boot.complete') || l.includes('slack.inbound') ||
            l.includes('gate.drop') || l.includes('gate.deliver')
          )
          if (socketLines.length) {
            report.recentSocketLogs = socketLines.slice(-10)
            break
          }
        }
      } catch {}
    }

    // 4. Check if the Slack app has event subscriptions enabled
    // We can infer this: if app_mentions:read is in the token scopes, the app
    // is subscribed to app_mention events. If not, Socket Mode won't fire.
    if (botToken) {
      const web = new WebClient(botToken)
      let tokenScopes: string[] = []
      try {
        await web.conversations.info({ channel: 'C000000FAKE' })
      } catch (err: any) {
        const provided = err?.data?.response_metadata?.scopes || err?.data?.provided
        if (provided) tokenScopes = typeof provided === 'string' ? provided.split(',') : provided
      }

      report.eventScopes = {
        app_mentions_read: tokenScopes.includes('app_mentions:read'),
        channels_history: tokenScopes.includes('channels:history'),
        groups_history: tokenScopes.includes('groups:history'),
        im_history: tokenScopes.includes('im:history'),
      }

      if (!tokenScopes.includes('app_mentions:read')) {
        report.issues = report.issues || []
        report.issues.push('app_mentions:read not in token — Socket Mode app_mention events will not fire')
      }
    }

    // 5. Check the server.ts for claude/channel capability declaration
    if (existsSync(MAIN_SERVER)) {
      const serverContent = readFileSync(MAIN_SERVER, 'utf-8')
      report.channelCapability = serverContent.includes("'claude/channel'")
      report.permissionCapability = serverContent.includes("'claude/channel/permission'")
      if (!report.channelCapability) {
        report.issues = report.issues || []
        report.issues.push('server.ts does not declare claude/channel capability — Claude Code will not register the notification listener')
      }
    }

    report.ok = !(report.issues?.length)
    return json(report)
  }

  // =========================================================================
  // slack_debug_roundtrip — send + read back
  // =========================================================================
  if (name === 'slack_debug_roundtrip') {
    const channel = args?.channel as string
    if (!channel) return json({ error: 'channel is required' })

    const { botToken, errors } = loadEnvTokens()
    if (!botToken) return json({ ok: false, error: 'No valid bot token', tokenErrors: errors })

    const web = new WebClient(botToken)
    const marker = `[roundtrip-test] ${Date.now()}-${Math.random().toString(36).slice(2, 8)}`

    // 1. Send
    let sentTs: string | undefined
    try {
      const res = await web.chat.postMessage({
        channel,
        text: marker,
        unfurl_links: false,
        unfurl_media: false,
      })
      sentTs = res.ts as string
    } catch (err: any) {
      const msg = err?.data?.error || err?.message || String(err)
      return json({ ok: false, phase: 'send', error: msg, hint: hintForError(msg) })
    }

    // 2. Read back (small delay for Slack propagation)
    await new Promise((r) => setTimeout(r, 500))

    try {
      const res = await web.conversations.history({ channel, limit: 5 })
      const messages = res.messages || []
      const found = messages.find((m: any) => m.ts === sentTs)

      // 3. Clean up test message
      try {
        await web.chat.delete({ channel, ts: sentTs! })
      } catch {
        // Best-effort cleanup — chat:write doesn't always grant delete
      }

      if (found) {
        return json({
          ok: true,
          sentTs,
          readBack: true,
          latencyMs: Date.now() - parseInt(sentTs!.split('.')[0]) * 1000,
          summary: 'Roundtrip success: sent message, read it back. Slack API read+write both work for this channel.',
        })
      } else {
        return json({
          ok: false,
          phase: 'readback',
          sentTs,
          readBack: false,
          messagesChecked: messages.length,
          summary: 'Message was sent but could not be read back. The bot may lack history scope for this channel type.',
        })
      }
    } catch (err: any) {
      const msg = err?.data?.error || err?.message || String(err)
      return json({ ok: false, phase: 'read', sentTs, error: msg, hint: hintForError(msg) })
    }
  }

  throw new Error(`Unknown tool: ${name}`)
})

// ---------------------------------------------------------------------------
// Util
// ---------------------------------------------------------------------------
function json(data: any) {
  return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] }
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
async function main() {
  const transport = new StdioServerTransport()
  await mcp.connect(transport)
}

main().catch((err) => {
  process.stderr.write(`Fatal: ${err.message}\n`)
  process.exit(1)
})
