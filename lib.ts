/**
 * slack-cc — shared pure logic
 *
 * Extracted so server.ts and tests import the same code.
 * No side effects, no Slack SDK imports, no MCP imports.
 */
import { chmodSync, existsSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export interface ChannelPolicy {
  requireMention: boolean
  allowFrom: string[]
}

export interface Access {
  dmPolicy: 'pairing' | 'allowlist' | 'disabled'
  allowFrom: string[]
  channels: Record<string, ChannelPolicy>
  pending: Array<{
    code: string
    senderId: string
    chatId: string
    expiresAt: number
  }>
}

export type GateResult =
  | { action: 'deliver' }
  | { action: 'drop'; reason: string }
  | { action: 'pair'; code: string; chatId: string; senderId: string }
  | { action: 'auto-opt-in'; channel: string; userId: string }

// ---------------------------------------------------------------------------
// Access control
// ---------------------------------------------------------------------------
export function defaultAccess(): Access {
  return {
    dmPolicy: 'pairing',
    allowFrom: [],
    channels: {},
    pending: [],
  }
}

export function loadAccess(stateDir: string): Access {
  const p = join(stateDir, 'access.json')
  if (!existsSync(p)) return defaultAccess()
  try {
    return { ...defaultAccess(), ...JSON.parse(readFileSync(p, 'utf-8')) }
  } catch {
    return defaultAccess()
  }
}

export function saveAccess(stateDir: string, access: Access): void {
  const p = join(stateDir, 'access.json')
  const tmp = `${p}.tmp.${process.pid}`
  writeFileSync(tmp, JSON.stringify(access, null, 2) + '\n', { mode: 0o600 })
  chmodSync(tmp, 0o600)
  renameSync(tmp, p)
}

// ---------------------------------------------------------------------------
// Gate — decide whether an inbound Slack event should reach Claude
// ---------------------------------------------------------------------------
export interface GateContext {
  access: Access
  botUserId?: string
  sessionChannels?: Map<string, ChannelPolicy>
}

export function gate(event: Record<string, any>, ctx: GateContext): GateResult {
  const { bot_id, bot_profile, user, channel, channel_type, text } = event
  const { access, botUserId, sessionChannels } = ctx

  // Block 1: Bot messages (always drop self-echoes)
  if (bot_id) {
    if (bot_profile?.app_id && botUserId && user === botUserId) {
      return { action: 'drop', reason: 'self-echo' }
    }
    return { action: 'drop', reason: 'bot-message' }
  }

  // Block 2: Non-message subtypes (edits, deletes, etc.)
  if (event.subtype && event.subtype !== 'file_share') {
    return { action: 'drop', reason: `subtype:${event.subtype}` }
  }

  // Block 3: No user
  if (!user) {
    return { action: 'drop', reason: 'no-user' }
  }

  // Block 4: DMs
  if (channel_type === 'im') {
    if (access.dmPolicy === 'disabled') {
      return { action: 'drop', reason: 'dm-disabled' }
    }
    if (access.allowFrom.includes(user)) {
      return { action: 'deliver' }
    }
    if (access.dmPolicy === 'allowlist') {
      return { action: 'drop', reason: 'dm-not-allowlisted' }
    }
    // Pairing mode
    const code = generatePairingCode()
    return { action: 'pair', code, chatId: channel, senderId: user }
  }

  // Block 5: Channels — check permanent AND session-scoped opt-ins
  const channelPolicy = access.channels[channel] || sessionChannels?.get(channel)
  if (!channelPolicy) {
    if (access.allowFrom.includes(user) && botUserId && text?.includes(`<@${botUserId}>`)) {
      return { action: 'auto-opt-in', channel, userId: user }
    }
    return { action: 'drop', reason: 'channel-not-opted-in' }
  }
  if (channelPolicy.allowFrom.length > 0 && !channelPolicy.allowFrom.includes(user)) {
    return { action: 'drop', reason: 'channel-user-not-allowed' }
  }
  if (channelPolicy.requireMention && botUserId && !text?.includes(`<@${botUserId}>`)) {
    return { action: 'drop', reason: 'mention-required' }
  }

  return { action: 'deliver' }
}

// ---------------------------------------------------------------------------
// Pairing code generation
// ---------------------------------------------------------------------------
const PAIRING_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789' // No 0/O/1/I

export function generatePairingCode(): string {
  let code = ''
  for (let i = 0; i < 6; i++) {
    code += PAIRING_CHARS[Math.floor(Math.random() * PAIRING_CHARS.length)]
  }
  return code
}

// ---------------------------------------------------------------------------
// Text chunking
// ---------------------------------------------------------------------------
export function chunkText(text: string, maxLen: number): string[] {
  if (text.length <= maxLen) return [text]
  const chunks: string[] = []
  let remaining = text
  while (remaining.length > 0) {
    if (remaining.length <= maxLen) {
      chunks.push(remaining)
      break
    }
    let breakAt = remaining.lastIndexOf('\n', maxLen)
    if (breakAt < maxLen * 0.5) breakAt = maxLen
    chunks.push(remaining.slice(0, breakAt))
    remaining = remaining.slice(breakAt)
  }
  return chunks
}

// ---------------------------------------------------------------------------
// Display name sanitization
// ---------------------------------------------------------------------------
export function sanitizeDisplayName(name: string): string {
  return name
    .replace(/[\x00-\x1f\x7f]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 64)
}

// ---------------------------------------------------------------------------
// Permission reply regex
// ---------------------------------------------------------------------------
export const PERMISSION_RE = /^\s*(y|yes|n|no)\s+([a-z0-9]{5})\s*$/i

// ---------------------------------------------------------------------------
// Dedup
// ---------------------------------------------------------------------------
export function makeDedup(ttlMs = 60_000) {
  const seen = new Map<string, number>()
  return {
    isDuplicate(channel: string, ts: string): boolean {
      const key = `${channel}:${ts}`
      const now = Date.now()
      if (seen.has(key)) return true
      seen.set(key, now)
      if (seen.size % 100 === 0) {
        for (const [k, v] of seen) {
          if (now - v > ttlMs) seen.delete(k)
        }
      }
      return false
    },
    clear() { seen.clear() },
    get size() { return seen.size },
  }
}

// ---------------------------------------------------------------------------
// .env parsing
// ---------------------------------------------------------------------------
export function loadEnv(stateDir: string): { botToken: string; appToken: string } {
  const envPath = join(stateDir, '.env')
  if (!existsSync(envPath)) {
    throw new Error(`No .env found at ${envPath}. Run /slack-cc:configure first.`)
  }
  const lines = readFileSync(envPath, 'utf-8').split('\n')
  const env: Record<string, string> = {}
  for (const line of lines) {
    const match = line.match(/^(\w+)=(.+)$/)
    if (match) env[match[1]] = match[2].trim()
  }
  const botToken = env.SLACK_BOT_TOKEN
  const appToken = env.SLACK_APP_TOKEN
  if (!botToken?.startsWith('xoxb-')) throw new Error('Missing or invalid SLACK_BOT_TOKEN')
  if (!appToken?.startsWith('xapp-')) throw new Error('Missing or invalid SLACK_APP_TOKEN')
  return { botToken, appToken }
}
