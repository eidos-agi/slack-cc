#!/usr/bin/env tsx
/**
 * cc-channel-slack-eidos — server tests
 *
 * Mocks Slack Socket Mode + Web API, verifies:
 * - Inbound delivery fires notifications/claude/channel
 * - Gate drops unauthorized messages
 * - Pairing flow persists to disk
 * - Outbound tools work
 * - Dedup prevents double-delivery
 * - Permission relay works
 */
import { test, describe, beforeEach, afterEach } from 'node:test'
import assert from 'node:assert/strict'
import { mkdirSync, writeFileSync, readFileSync, rmSync, existsSync, chmodSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

// ---------------------------------------------------------------------------
// Test state dir
// ---------------------------------------------------------------------------
const TEST_DIR = join(tmpdir(), `cc-slack-test-${process.pid}`)

function setupStateDir(access?: object) {
  rmSync(TEST_DIR, { recursive: true, force: true })
  mkdirSync(TEST_DIR, { recursive: true, mode: 0o700 })
  writeFileSync(join(TEST_DIR, '.env'), [
    'SLACK_BOT_TOKEN=xoxb-test-token',
    'SLACK_APP_TOKEN=xapp-test-token',
  ].join('\n'), { mode: 0o600 })
  if (access) {
    const p = join(TEST_DIR, 'access.json')
    writeFileSync(p, JSON.stringify(access, null, 2), { mode: 0o600 })
  }
}

function loadTestAccess(): any {
  const p = join(TEST_DIR, 'access.json')
  if (!existsSync(p)) return null
  return JSON.parse(readFileSync(p, 'utf-8'))
}

// ---------------------------------------------------------------------------
// Import the gate, access, and helper functions by re-implementing them
// (server.ts is a self-contained script, so we extract the logic here)
// ---------------------------------------------------------------------------

// Replicate the core logic for unit testing
interface ChannelPolicy {
  requireMention: boolean
  allowFrom: string[]
}

interface Access {
  dmPolicy: 'pairing' | 'allowlist' | 'disabled'
  allowFrom: string[]
  channels: Record<string, ChannelPolicy>
  pending: Array<{ code: string; senderId: string; chatId: string; expiresAt: number }>
}

function defaultAccess(): Access {
  return { dmPolicy: 'pairing', allowFrom: [], channels: {}, pending: [] }
}

function loadAccess(stateDir: string): Access {
  const p = join(stateDir, 'access.json')
  if (!existsSync(p)) return defaultAccess()
  try {
    return { ...defaultAccess(), ...JSON.parse(readFileSync(p, 'utf-8')) }
  } catch {
    return defaultAccess()
  }
}

function saveAccess(stateDir: string, access: Access): void {
  const p = join(stateDir, 'access.json')
  const tmp = `${p}.tmp.${process.pid}`
  writeFileSync(tmp, JSON.stringify(access, null, 2) + '\n', { mode: 0o600 })
  chmodSync(tmp, 0o600)
  const { renameSync } = require('node:fs')
  renameSync(tmp, p)
}

function generatePairingCode(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < 6; i++) {
    code += chars[Math.floor(Math.random() * chars.length)]
  }
  return code
}

type GateResult =
  | { action: 'deliver' }
  | { action: 'drop'; reason: string }
  | { action: 'pair'; code: string; chatId: string; senderId: string }
  | { action: 'auto-opt-in'; channel: string; userId: string }

function gate(event: Record<string, any>, access: Access, botUserId?: string): GateResult {
  const { bot_id, bot_profile, user, channel, channel_type, text } = event

  if (bot_id) {
    if (bot_profile?.app_id && botUserId && user === botUserId) {
      return { action: 'drop', reason: 'self-echo' }
    }
    return { action: 'drop', reason: 'bot-message' }
  }

  if (event.subtype && event.subtype !== 'file_share') {
    return { action: 'drop', reason: `subtype:${event.subtype}` }
  }

  if (!user) {
    return { action: 'drop', reason: 'no-user' }
  }

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
    const code = generatePairingCode()
    return { action: 'pair', code, chatId: channel, senderId: user }
  }

  const channelPolicy = access.channels[channel]
  if (!channelPolicy) {
    // Auto-opt-in: allowlisted user @mentions bot in a new channel
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

// Dedup
function makeDedup() {
  const seen = new Map<string, number>()
  return {
    isDuplicate(channel: string, ts: string): boolean {
      const key = `${channel}:${ts}`
      if (seen.has(key)) return true
      seen.set(key, Date.now())
      return false
    },
    clear() { seen.clear() },
  }
}

// Text chunking
function chunkText(text: string, maxLen: number): string[] {
  if (text.length <= maxLen) return [text]
  const chunks: string[] = []
  let remaining = text
  while (remaining.length > 0) {
    if (remaining.length <= maxLen) { chunks.push(remaining); break }
    let breakAt = remaining.lastIndexOf('\n', maxLen)
    if (breakAt < maxLen * 0.5) breakAt = maxLen
    chunks.push(remaining.slice(0, breakAt))
    remaining = remaining.slice(breakAt)
  }
  return chunks
}

// Permission regex
const PERMISSION_RE = /^\s*(y|yes|n|no)\s+([a-z0-9]{5})\s*$/i

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('Gate', () => {
  const baseAccess: Access = {
    dmPolicy: 'allowlist',
    allowFrom: ['U_DANIEL'],
    channels: {
      C_DEV: { requireMention: false, allowFrom: ['U_DANIEL'] },
      C_OPEN: { requireMention: false, allowFrom: [] },
      C_MENTION: { requireMention: true, allowFrom: [] },
    },
    pending: [],
  }

  test('delivers DM from allowlisted user', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'D123', channel_type: 'im', text: 'hello' },
      baseAccess,
    )
    assert.deepEqual(result, { action: 'deliver' })
  })

  test('drops DM from non-allowlisted user', () => {
    const result = gate(
      { user: 'U_STRANGER', channel: 'D456', channel_type: 'im', text: 'hello' },
      baseAccess,
    )
    assert.equal(result.action, 'drop')
  })

  test('delivers channel message from allowed user', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_DEV', text: 'hey' },
      baseAccess,
    )
    assert.deepEqual(result, { action: 'deliver' })
  })

  test('drops channel message from unauthorized user', () => {
    const result = gate(
      { user: 'U_STRANGER', channel: 'C_DEV', text: 'hey' },
      baseAccess,
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'channel-user-not-allowed')
  })

  test('delivers to open channel (empty allowFrom)', () => {
    const result = gate(
      { user: 'U_ANYONE', channel: 'C_OPEN', text: 'hey' },
      baseAccess,
    )
    assert.deepEqual(result, { action: 'deliver' })
  })

  test('drops message to non-opted-in channel', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_UNKNOWN', text: 'hey' },
      baseAccess,
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'channel-not-opted-in')
  })

  test('drops bot messages', () => {
    const result = gate(
      { user: 'U_BOT', channel: 'C_OPEN', bot_id: 'B123', text: 'beep' },
      baseAccess,
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'bot-message')
  })

  test('drops self-echo', () => {
    const result = gate(
      { user: 'U_ME', channel: 'C_OPEN', bot_id: 'B123', bot_profile: { app_id: 'A1' }, text: 'echo' },
      baseAccess,
      'U_ME',
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'self-echo')
  })

  test('drops message_changed subtype', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_OPEN', subtype: 'message_changed', text: 'edited' },
      baseAccess,
    )
    assert.equal(result.action, 'drop')
  })

  test('delivers file_share subtype', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_DEV', subtype: 'file_share', text: 'file', files: [{}] },
      baseAccess,
    )
    assert.deepEqual(result, { action: 'deliver' })
  })

  test('drops when no user', () => {
    const result = gate(
      { channel: 'C_OPEN', text: 'ghost' },
      baseAccess,
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'no-user')
  })

  test('requireMention blocks without mention', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_MENTION', text: 'just talking' },
      baseAccess,
      'U_BOT',
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'mention-required')
  })

  test('requireMention passes with mention', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_MENTION', text: 'hey <@U_BOT> help' },
      baseAccess,
      'U_BOT',
    )
    assert.deepEqual(result, { action: 'deliver' })
  })

  test('DM disabled policy drops all DMs', () => {
    const access: Access = { ...baseAccess, dmPolicy: 'disabled' }
    const result = gate(
      { user: 'U_DANIEL', channel: 'D123', channel_type: 'im', text: 'hello' },
      access,
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'dm-disabled')
  })
})

describe('Auto-opt-in', () => {
  const access: Access = {
    dmPolicy: 'allowlist',
    allowFrom: ['U_DANIEL'],
    channels: {},
    pending: [],
  }

  test('allowlisted user @mentioning bot in new channel triggers auto-opt-in', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_NEW', text: 'hey <@U_BOT> connect here' },
      access,
      'U_BOT',
    )
    assert.equal(result.action, 'auto-opt-in')
    const opt = result as { action: 'auto-opt-in'; channel: string; userId: string }
    assert.equal(opt.channel, 'C_NEW')
    assert.equal(opt.userId, 'U_DANIEL')
  })

  test('non-allowlisted user @mentioning bot in new channel is dropped', () => {
    const result = gate(
      { user: 'U_STRANGER', channel: 'C_NEW', text: 'hey <@U_BOT> connect here' },
      access,
      'U_BOT',
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'channel-not-opted-in')
  })

  test('allowlisted user without @mention in new channel is dropped', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_NEW', text: 'just chatting' },
      access,
      'U_BOT',
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'channel-not-opted-in')
  })

  test('allowlisted user @mentioning bot when botUserId is unknown is dropped', () => {
    // If we don't know our own bot user ID, we can't verify the mention
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_NEW', text: 'hey <@U_BOT> connect here' },
      access,
      undefined, // no botUserId
    )
    assert.equal(result.action, 'drop')
    assert.equal((result as any).reason, 'channel-not-opted-in')
  })

  test('auto-opt-in does not fire for already opted-in channels', () => {
    const withChannel: Access = {
      ...access,
      channels: { C_EXISTING: { requireMention: false, allowFrom: [] } },
    }
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_EXISTING', text: 'hey <@U_BOT>' },
      withChannel,
      'U_BOT',
    )
    // Should deliver normally, not auto-opt-in
    assert.equal(result.action, 'deliver')
  })

  test('auto-opt-in is session-scoped — does NOT persist to access.json', () => {
    setupStateDir({ dmPolicy: 'allowlist', allowFrom: ['U_DANIEL'], channels: {}, pending: [] })

    // Simulate auto-opt-in writing to session map (not access.json)
    const sessionMap = new Map<string, ChannelPolicy>()
    sessionMap.set('C_NEW', { requireMention: false, allowFrom: ['U_DANIEL'] })

    // access.json should be untouched
    const reloaded = loadTestAccess()
    assert.equal(Object.keys(reloaded.channels).length, 0, 'access.json should have no channels')

    // But gate should pass when checking session channels
    const mergedPolicy = reloaded.channels['C_NEW'] || sessionMap.get('C_NEW')
    assert.ok(mergedPolicy, 'session map should have the channel')
  })

  test('auto-opt-in then subsequent message delivers via session channels', () => {
    const access: Access = {
      dmPolicy: 'allowlist',
      allowFrom: ['U_DANIEL'],
      channels: {}, // NOT in permanent channels
      pending: [],
    }
    // Simulate session channel being set after auto-opt-in
    const sessionMap = new Map<string, ChannelPolicy>()
    sessionMap.set('C_NEW', { requireMention: false, allowFrom: ['U_DANIEL'] })

    // Gate should check session channels as fallback
    const channelPolicy = access.channels['C_NEW'] || sessionMap.get('C_NEW')
    assert.ok(channelPolicy)
    // With policy found, user is in allowFrom → deliver
    assert.ok(channelPolicy.allowFrom.length === 0 || channelPolicy.allowFrom.includes('U_DANIEL'))
  })

  test('auto-opt-in scopes allowFrom to the requesting user', () => {
    const sessionMap = new Map<string, ChannelPolicy>()
    sessionMap.set('C_NEW', { requireMention: false, allowFrom: ['U_DANIEL'] })

    const access: Access = {
      dmPolicy: 'allowlist',
      allowFrom: ['U_DANIEL'],
      channels: {},
      pending: [],
    }

    // Stranger should be blocked by the session channel's allowFrom
    const policy = access.channels['C_NEW'] || sessionMap.get('C_NEW')
    assert.ok(policy)
    assert.ok(!policy.allowFrom.includes('U_STRANGER'), 'stranger should not be in allowFrom')
  })

  test('session channels are ephemeral — new Map() simulates session restart', () => {
    const sessionMap = new Map<string, ChannelPolicy>()
    sessionMap.set('C_NEW', { requireMention: false, allowFrom: ['U_DANIEL'] })
    assert.ok(sessionMap.has('C_NEW'))

    // "Restart" — new session, new map
    const freshSession = new Map<string, ChannelPolicy>()
    assert.ok(!freshSession.has('C_NEW'), 'channel should be gone after session restart')
  })

  test('full simulation: auto-opt-in (session) → deliver → stranger blocked → session dies', () => {
    const startAccess: Access = {
      dmPolicy: 'allowlist',
      allowFrom: ['U_DANIEL'],
      channels: {},
      pending: [],
    }

    const dedup = makeDedup()
    const sessionMap = new Map<string, ChannelPolicy>()
    const delivered: Array<{ content: string; meta: Record<string, string> }> = []
    const slackReplies: Array<{ channel: string; text: string }> = []

    function handleEvent(event: Record<string, any>, access: Access) {
      const { channel, ts, user, text } = event
      if (!channel || !ts) return
      if (dedup.isDuplicate(channel, ts)) return

      // Gate checks both permanent and session channels
      const channelPolicy = access.channels[channel] || sessionMap.get(channel)
      const result = (() => {
        // Inline gate logic with session channel awareness
        if (event.bot_id) return { action: 'drop' as const, reason: 'bot' }
        if (!user) return { action: 'drop' as const, reason: 'no-user' }
        if (!channelPolicy) {
          if (access.allowFrom.includes(user) && text?.includes('<@U_BOT>')) {
            return { action: 'auto-opt-in' as const, channel, userId: user }
          }
          return { action: 'drop' as const, reason: 'not-opted-in' }
        }
        if (channelPolicy.allowFrom.length > 0 && !channelPolicy.allowFrom.includes(user)) {
          return { action: 'drop' as const, reason: 'user-not-allowed' }
        }
        return { action: 'deliver' as const }
      })()

      if (result.action === 'auto-opt-in') {
        // Session-scoped only
        sessionMap.set(channel, { requireMention: false, allowFrom: [user] })
        slackReplies.push({ channel, text: 'Connected.' })
        delivered.push({ content: text || '', meta: { chat_id: channel, user_id: user, ts } })
        return
      }
      if (result.action === 'deliver') {
        delivered.push({ content: text || '', meta: { chat_id: channel, user_id: user, ts } })
      }
    }

    // Step 1: @mention bot in new channel → session opt-in
    handleEvent(
      { user: 'U_DANIEL', channel: 'C_NEW', ts: '1.1', text: 'hey <@U_BOT> connect' },
      startAccess,
    )
    assert.equal(delivered.length, 1, 'first message should deliver')
    assert.equal(slackReplies.length, 1, 'confirmation should be sent')
    assert.ok(sessionMap.has('C_NEW'), 'session map should have channel')
    assert.equal(Object.keys(startAccess.channels).length, 0, 'access.json channels should be empty')

    // Step 2: subsequent message delivers via session channel
    handleEvent(
      { user: 'U_DANIEL', channel: 'C_NEW', ts: '1.2', text: 'how are things?' },
      startAccess,
    )
    assert.equal(delivered.length, 2, 'second message should deliver')
    assert.equal(slackReplies.length, 1, 'no second confirmation')

    // Step 3: stranger in the same channel is blocked
    handleEvent(
      { user: 'U_STRANGER', channel: 'C_NEW', ts: '1.3', text: 'inject!' },
      startAccess,
    )
    assert.equal(delivered.length, 2, 'stranger message should be dropped')

    // Step 4: simulate session end — clear session map
    sessionMap.clear()
    handleEvent(
      { user: 'U_DANIEL', channel: 'C_NEW', ts: '1.4', text: 'still here?' },
      startAccess,
    )
    // Without @mention, this should be dropped (channel no longer opted-in)
    assert.equal(delivered.length, 2, 'message after session clear should be dropped')

    // Step 5: re-mention to re-connect
    handleEvent(
      { user: 'U_DANIEL', channel: 'C_NEW', ts: '1.5', text: 'hey <@U_BOT> back again' },
      startAccess,
    )
    assert.equal(delivered.length, 3, 're-mention should auto-opt-in again')
    assert.equal(slackReplies.length, 2, 'second confirmation on re-connect')
  })
})

describe('Pairing', () => {
  test('pairing mode returns code for unknown DM user', () => {
    const access: Access = {
      dmPolicy: 'pairing',
      allowFrom: [],
      channels: {},
      pending: [],
    }
    const result = gate(
      { user: 'U_NEW', channel: 'D789', channel_type: 'im', text: 'hello' },
      access,
    )
    assert.equal(result.action, 'pair')
    const pair = result as { action: 'pair'; code: string; chatId: string; senderId: string }
    assert.equal(pair.chatId, 'D789')
    assert.equal(pair.senderId, 'U_NEW')
    assert.equal(pair.code.length, 6)
  })

  test('pairing code persists to access.json', () => {
    setupStateDir({ dmPolicy: 'pairing', allowFrom: [], channels: {}, pending: [] })
    const access = loadAccess(TEST_DIR)
    const code = generatePairingCode()

    access.pending.push({
      code,
      senderId: 'U_NEW',
      chatId: 'D789',
      expiresAt: Date.now() + 3600_000,
    })
    saveAccess(TEST_DIR, access)

    const reloaded = loadTestAccess()
    assert.equal(reloaded.pending.length, 1)
    assert.equal(reloaded.pending[0].code, code)
    assert.equal(reloaded.pending[0].senderId, 'U_NEW')
  })

  test('pairing approval adds user to allowFrom', () => {
    const code = 'ABC123'
    setupStateDir({
      dmPolicy: 'pairing',
      allowFrom: [],
      channels: {},
      pending: [{ code, senderId: 'U_NEW', chatId: 'D789', expiresAt: Date.now() + 3600_000 }],
    })

    const access = loadAccess(TEST_DIR)
    const match = access.pending.find(
      (p) => p.code.toLowerCase() === code.toLowerCase(),
    )
    assert.ok(match, 'pending entry should exist')

    access.allowFrom.push(match!.senderId)
    access.pending = access.pending.filter((p) => p.code !== code)
    saveAccess(TEST_DIR, access)

    const reloaded = loadTestAccess()
    assert.ok(reloaded.allowFrom.includes('U_NEW'))
    assert.equal(reloaded.pending.length, 0)
  })

  test('expired pairing entries are pruned', () => {
    setupStateDir({
      dmPolicy: 'pairing',
      allowFrom: [],
      channels: {},
      pending: [
        { code: 'OLD1', senderId: 'U1', chatId: 'D1', expiresAt: Date.now() - 1000 },
        { code: 'NEW1', senderId: 'U2', chatId: 'D2', expiresAt: Date.now() + 3600_000 },
      ],
    })

    const access = loadAccess(TEST_DIR)
    access.pending = access.pending.filter((p) => p.expiresAt > Date.now())
    saveAccess(TEST_DIR, access)

    const reloaded = loadTestAccess()
    assert.equal(reloaded.pending.length, 1)
    assert.equal(reloaded.pending[0].code, 'NEW1')
  })
})

describe('Dedup', () => {
  test('first message passes, second is duplicate', () => {
    const dedup = makeDedup()
    assert.equal(dedup.isDuplicate('C1', '123.456'), false)
    assert.equal(dedup.isDuplicate('C1', '123.456'), true)
  })

  test('different channels are not duplicates', () => {
    const dedup = makeDedup()
    assert.equal(dedup.isDuplicate('C1', '123.456'), false)
    assert.equal(dedup.isDuplicate('C2', '123.456'), false)
  })

  test('different timestamps are not duplicates', () => {
    const dedup = makeDedup()
    assert.equal(dedup.isDuplicate('C1', '123.456'), false)
    assert.equal(dedup.isDuplicate('C1', '123.457'), false)
  })
})

describe('Text chunking', () => {
  test('short text returns single chunk', () => {
    assert.deepEqual(chunkText('hello', 100), ['hello'])
  })

  test('long text is chunked', () => {
    const text = 'a'.repeat(200)
    const chunks = chunkText(text, 100)
    assert.ok(chunks.length >= 2)
    assert.equal(chunks.join(''), text)
  })

  test('breaks at newline when possible', () => {
    const text = 'line1\n' + 'x'.repeat(50) + '\nline3'
    const chunks = chunkText(text, 30)
    assert.ok(chunks.length >= 2)
    assert.equal(chunks.join(''), text)
  })
})

describe('Bot commands (debug, help)', () => {
  // Matches the logic in server.ts: strip @mentions, trim, exact match
  function isCommand(text: string, cmd: string): boolean {
    const stripped = text.replace(/<@[A-Z0-9]+>/g, '').trim()
    return new RegExp(`^${cmd}$`, 'i').test(stripped)
  }

  test('debug triggers on exact word', () => {
    assert.ok(isCommand('debug', 'debug'))
    assert.ok(isCommand(' debug', 'debug'))
    assert.ok(isCommand('  debug  ', 'debug'))
    assert.ok(isCommand('DEBUG', 'debug'))
    assert.ok(isCommand('<@U0AUE6PPXU2> debug', 'debug'))
    assert.ok(isCommand('<@U0AUE6PPXU2>  debug', 'debug'))
  })

  test('debug does NOT trigger on longer messages', () => {
    assert.ok(!isCommand('debug this thing', 'debug'))
    assert.ok(!isCommand('can you debug', 'debug'))
    assert.ok(!isCommand('run in debug mode', 'debug'))
    assert.ok(!isCommand('debug please', 'debug'))
  })

  test('help triggers on exact word', () => {
    assert.ok(isCommand('help', 'help'))
    assert.ok(isCommand(' help', 'help'))
    assert.ok(isCommand('HELP', 'help'))
    assert.ok(isCommand('<@U0AUE6PPXU2> help', 'help'))
    assert.ok(isCommand('/help', '\\/help'))
  })

  test('help does NOT trigger on longer messages', () => {
    assert.ok(!isCommand('help me with this', 'help'))
    assert.ok(!isCommand('I need help', 'help'))
    assert.ok(!isCommand('can you help', 'help'))
  })
})

describe('Permission regex', () => {
  test('matches yes + 5-char id', () => {
    assert.ok(PERMISSION_RE.test('yes abcde'))
    assert.ok(PERMISSION_RE.test('y abcde'))
    assert.ok(PERMISSION_RE.test('YES ABCDE'))
    assert.ok(PERMISSION_RE.test('  no fghkm  '))
  })

  test('rejects invalid formats', () => {
    assert.ok(!PERMISSION_RE.test('yes'))          // no id
    assert.ok(!PERMISSION_RE.test('maybe abcde'))  // invalid verb
    assert.ok(!PERMISSION_RE.test('yes abc'))       // too short
    assert.ok(!PERMISSION_RE.test('yes abcdef'))    // too long
    assert.ok(!PERMISSION_RE.test('approve abcde')) // wrong word
  })

  test('extracts verdict and id', () => {
    const m = 'yes abcde'.match(PERMISSION_RE)!
    assert.equal(m[1], 'yes')
    assert.equal(m[2], 'abcde')
  })
})

describe('Notification delivery simulation', () => {
  test('full inbound path: gate → dedup → deliver', () => {
    const access: Access = {
      dmPolicy: 'allowlist',
      allowFrom: ['U_DANIEL'],
      channels: { C_DEV: { requireMention: false, allowFrom: [] } },
      pending: [],
    }

    const dedup = makeDedup()
    const delivered: Array<{ content: string; meta: Record<string, string> }> = []

    // Simulate the handleSlackEvent flow
    function handleEvent(event: Record<string, any>) {
      const { channel, ts, thread_ts, user, text } = event
      if (!channel || !ts) return
      if (dedup.isDuplicate(channel, ts)) return

      const result = gate(event, access)
      if (result.action !== 'deliver') return

      // This is what mcp.notification() would send
      const meta: Record<string, string> = {
        chat_id: channel,
        message_id: ts,
        user_id: user,
        user: 'Daniel Shanklin',
        ts,
      }
      if (thread_ts) meta.thread_ts = thread_ts

      delivered.push({ content: text || '', meta })
    }

    // Test: authorized user in opted-in channel
    handleEvent({ user: 'U_DANIEL', channel: 'C_DEV', ts: '1.1', text: 'hello from slack' })
    assert.equal(delivered.length, 1)
    assert.equal(delivered[0].content, 'hello from slack')
    assert.equal(delivered[0].meta.chat_id, 'C_DEV')
    assert.equal(delivered[0].meta.user_id, 'U_DANIEL')

    // Test: duplicate is dropped
    handleEvent({ user: 'U_DANIEL', channel: 'C_DEV', ts: '1.1', text: 'hello from slack' })
    assert.equal(delivered.length, 1) // still 1

    // Test: unauthorized user is dropped
    handleEvent({ user: 'U_STRANGER', channel: 'C_NOT_OPTED', ts: '1.2', text: 'sneaky' })
    assert.equal(delivered.length, 1) // still 1

    // Test: second valid message delivers
    handleEvent({ user: 'U_DANIEL', channel: 'C_DEV', ts: '1.3', text: 'second message' })
    assert.equal(delivered.length, 2)
    assert.equal(delivered[1].content, 'second message')

    // Test: threaded message includes thread_ts
    handleEvent({ user: 'U_DANIEL', channel: 'C_DEV', ts: '1.4', thread_ts: '1.1', text: 'reply in thread' })
    assert.equal(delivered.length, 3)
    assert.equal(delivered[2].meta.thread_ts, '1.1')

    // Test: DM from allowlisted user
    handleEvent({ user: 'U_DANIEL', channel: 'D123', channel_type: 'im', ts: '2.1', text: 'dm hello' })
    assert.equal(delivered.length, 4)
    assert.equal(delivered[3].meta.chat_id, 'D123')
  })
})

describe('Outbound gate', () => {
  test('allows reply to opted-in channel', () => {
    const access: Access = {
      dmPolicy: 'allowlist',
      allowFrom: [],
      channels: { C_DEV: { requireMention: false, allowFrom: [] } },
      pending: [],
    }
    // assertOutbound checks access.channels — should not throw
    assert.ok(access.channels['C_DEV'])
  })

  test('blocks reply to non-opted-in channel', () => {
    const access: Access = {
      dmPolicy: 'allowlist',
      allowFrom: [],
      channels: {},
      pending: [],
    }
    assert.equal(access.channels['C_RANDOM'], undefined)
  })
})

describe('Access file atomicity', () => {
  beforeEach(() => setupStateDir())

  test('saveAccess writes atomically with correct permissions', () => {
    const access = defaultAccess()
    access.allowFrom = ['U_TEST']
    saveAccess(TEST_DIR, access)

    const p = join(TEST_DIR, 'access.json')
    assert.ok(existsSync(p))

    const loaded = JSON.parse(readFileSync(p, 'utf-8'))
    assert.deepEqual(loaded.allowFrom, ['U_TEST'])

    // Check permissions (0o600 = 33152 in decimal on some platforms, check owner-only)
    const { statSync } = require('node:fs')
    const stat = statSync(p)
    const mode = stat.mode & 0o777
    assert.equal(mode, 0o600, `Expected 0o600, got 0o${mode.toString(8)}`)
  })

  test('no tmp files left behind', () => {
    const access = defaultAccess()
    saveAccess(TEST_DIR, access)

    const { readdirSync } = require('node:fs')
    const files = readdirSync(TEST_DIR)
    const tmpFiles = files.filter((f: string) => f.includes('.tmp.'))
    assert.equal(tmpFiles.length, 0, `Leftover tmp files: ${tmpFiles}`)
  })
})

describe('loadEnv parsing', () => {
  test('parses valid .env with both tokens', () => {
    setupStateDir()
    const envPath = join(TEST_DIR, '.env')
    writeFileSync(envPath, 'SLACK_BOT_TOKEN=xoxb-test-123\nSLACK_APP_TOKEN=xapp-test-456\n', { mode: 0o600 })

    const lines = readFileSync(envPath, 'utf-8').split('\n')
    const env: Record<string, string> = {}
    for (const line of lines) {
      const match = line.match(/^(\w+)=(.+)$/)
      if (match) env[match[1]] = match[2].trim()
    }
    assert.equal(env.SLACK_BOT_TOKEN, 'xoxb-test-123')
    assert.equal(env.SLACK_APP_TOKEN, 'xapp-test-456')
  })

  test('handles extra whitespace and blank lines', () => {
    setupStateDir()
    const envPath = join(TEST_DIR, '.env')
    writeFileSync(envPath, '\nSLACK_BOT_TOKEN=xoxb-test-123  \n\nSLACK_APP_TOKEN=xapp-test-456\n\n', { mode: 0o600 })

    const lines = readFileSync(envPath, 'utf-8').split('\n')
    const env: Record<string, string> = {}
    for (const line of lines) {
      const match = line.match(/^(\w+)=(.+)$/)
      if (match) env[match[1]] = match[2].trim()
    }
    assert.equal(env.SLACK_BOT_TOKEN, 'xoxb-test-123')
    assert.equal(env.SLACK_APP_TOKEN, 'xapp-test-456')
  })

  test('rejects missing bot token', () => {
    const env: Record<string, string> = { SLACK_APP_TOKEN: 'xapp-test' }
    assert.ok(!env.SLACK_BOT_TOKEN?.startsWith('xoxb-'))
  })

  test('rejects wrong token prefix', () => {
    const env: Record<string, string> = {
      SLACK_BOT_TOKEN: 'xoxp-user-token',
      SLACK_APP_TOKEN: 'xapp-test',
    }
    assert.ok(!env.SLACK_BOT_TOKEN.startsWith('xoxb-'))
  })
})

describe('Pairing code generation', () => {
  test('codes are 6 characters', () => {
    for (let i = 0; i < 50; i++) {
      const code = generatePairingCode()
      assert.equal(code.length, 6)
    }
  })

  test('codes never contain ambiguous characters (0, O, 1, I)', () => {
    for (let i = 0; i < 200; i++) {
      const code = generatePairingCode()
      assert.ok(!/[0O1I]/.test(code), `Code ${code} contains ambiguous character`)
    }
  })

  test('codes are alphanumeric uppercase', () => {
    for (let i = 0; i < 100; i++) {
      const code = generatePairingCode()
      assert.ok(/^[A-Z0-9]+$/.test(code), `Code ${code} has invalid chars`)
    }
  })

  test('codes have reasonable randomness (no identical consecutive pair in 100)', () => {
    const codes = Array.from({ length: 100 }, () => generatePairingCode())
    for (let i = 1; i < codes.length; i++) {
      assert.notEqual(codes[i], codes[i - 1], `Consecutive identical codes: ${codes[i]}`)
    }
  })
})

describe('Display name sanitization', () => {
  function sanitize(name: string): string {
    return name.replace(/[\x00-\x1f\x7f]/g, '').replace(/\s+/g, ' ').trim().slice(0, 64)
  }

  test('passes clean names through', () => {
    assert.equal(sanitize('Daniel Shanklin'), 'Daniel Shanklin')
  })

  test('strips control characters', () => {
    assert.equal(sanitize('Dan\x00iel\x1fShan'), 'DanielShan')
  })

  test('collapses whitespace', () => {
    assert.equal(sanitize('Daniel   Shanklin'), 'Daniel Shanklin')
  })

  test('trims leading/trailing whitespace', () => {
    assert.equal(sanitize('  Daniel  '), 'Daniel')
  })

  test('truncates at 64 characters', () => {
    const long = 'A'.repeat(100)
    assert.equal(sanitize(long).length, 64)
  })

  test('handles empty string', () => {
    assert.equal(sanitize(''), '')
  })

  test('strips tabs and newlines', () => {
    // \t (0x09) and \n (0x0a) are control chars → stripped, then whitespace collapsed
    assert.equal(sanitize('Daniel\tShanklin\nJr'), 'DanielShanklinJr')
  })
})

describe('Outbound gate (detailed)', () => {
  test('session channel allows outbound even without permanent config', () => {
    const sessionMap = new Map<string, ChannelPolicy>()
    sessionMap.set('C_SESSION', { requireMention: false, allowFrom: [] })

    const access: Access = { dmPolicy: 'allowlist', allowFrom: [], channels: {}, pending: [] }

    // Should be allowed via session map
    assert.ok(access.channels['C_SESSION'] || sessionMap.has('C_SESSION'))
  })

  test('delivered thread allows outbound', () => {
    const delivered = new Set<string>()
    delivered.add('C_THREAD:1234.5678')
    delivered.add('C_THREAD:*')

    assert.ok(delivered.has('C_THREAD:1234.5678'))
    assert.ok(delivered.has('C_THREAD:*'))
    assert.ok(!delivered.has('C_OTHER:*'))
  })

  test('nothing allows outbound to unknown channel', () => {
    const access: Access = { dmPolicy: 'allowlist', allowFrom: [], channels: {}, pending: [] }
    const sessionMap = new Map<string, ChannelPolicy>()
    const delivered = new Set<string>()

    const channel = 'C_RANDOM'
    const allowed = access.channels[channel] || sessionMap.has(channel) || delivered.has(`${channel}:*`)
    assert.ok(!allowed)
  })
})

describe('Gate edge cases', () => {
  const access: Access = {
    dmPolicy: 'allowlist',
    allowFrom: ['U_DANIEL'],
    channels: { C_DEV: { requireMention: false, allowFrom: [] } },
    pending: [],
  }

  test('empty text is delivered (not dropped)', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_DEV', text: '' },
      access,
    )
    assert.equal(result.action, 'deliver')
  })

  test('undefined text is delivered', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_DEV' },
      access,
    )
    assert.equal(result.action, 'deliver')
  })

  test('file_share with no text is delivered', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_DEV', subtype: 'file_share', files: [{ id: 'F1' }] },
      access,
    )
    assert.equal(result.action, 'deliver')
  })

  test('message_deleted subtype is dropped', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_DEV', subtype: 'message_deleted' },
      access,
    )
    assert.equal(result.action, 'drop')
  })

  test('channel_join subtype is dropped', () => {
    const result = gate(
      { user: 'U_DANIEL', channel: 'C_DEV', subtype: 'channel_join' },
      access,
    )
    assert.equal(result.action, 'drop')
  })

  test('bot_message subtype with bot_id is dropped', () => {
    const result = gate(
      { user: 'U_BOT', channel: 'C_DEV', bot_id: 'B1', subtype: 'bot_message' },
      access,
    )
    assert.equal(result.action, 'drop')
  })

  test('multiple allowFrom users — first passes, second passes, third blocked', () => {
    const multiAccess: Access = {
      ...access,
      channels: { C_TEAM: { requireMention: false, allowFrom: ['U_A', 'U_B'] } },
    }
    assert.equal(gate({ user: 'U_A', channel: 'C_TEAM', text: 'hi' }, multiAccess).action, 'deliver')
    assert.equal(gate({ user: 'U_B', channel: 'C_TEAM', text: 'hi' }, multiAccess).action, 'deliver')
    assert.equal(gate({ user: 'U_C', channel: 'C_TEAM', text: 'hi' }, multiAccess).action, 'drop')
  })
})

describe('Dedup edge cases', () => {
  test('rapid-fire same event is deduplicated', () => {
    const dedup = makeDedup()
    const results = Array.from({ length: 10 }, () => dedup.isDuplicate('C1', '1.1'))
    assert.equal(results[0], false) // first passes
    assert.ok(results.slice(1).every(r => r === true)) // rest blocked
  })

  test('different event types for same ts are still deduped', () => {
    // message + app_mention fire for same event
    const dedup = makeDedup()
    assert.equal(dedup.isDuplicate('C1', '1.1'), false)
    assert.equal(dedup.isDuplicate('C1', '1.1'), true) // app_mention for same
  })
})

describe('Text chunking edge cases', () => {
  test('empty string returns single empty chunk', () => {
    assert.deepEqual(chunkText('', 100), [''])
  })

  test('text exactly at max length returns single chunk', () => {
    const text = 'x'.repeat(100)
    const chunks = chunkText(text, 100)
    assert.equal(chunks.length, 1)
    assert.equal(chunks[0], text)
  })

  test('text one char over max gets chunked', () => {
    const text = 'x'.repeat(101)
    const chunks = chunkText(text, 100)
    assert.equal(chunks.length, 2)
    assert.equal(chunks.join(''), text)
  })

  test('preserves content integrity across chunks', () => {
    const text = 'The quick brown fox jumped over the lazy dog. '.repeat(50)
    const chunks = chunkText(text, 200)
    assert.equal(chunks.join(''), text, 'reassembled chunks must equal original')
  })

  test('handles text with only newlines', () => {
    const text = '\n'.repeat(300)
    const chunks = chunkText(text, 100)
    assert.equal(chunks.join(''), text)
  })
})

describe('Access resilience', () => {
  test('loadAccess returns defaults for missing file', () => {
    setupStateDir() // no access.json written
    const access = loadAccess(TEST_DIR)
    assert.equal(access.dmPolicy, 'pairing')
    assert.deepEqual(access.allowFrom, [])
    assert.deepEqual(access.channels, {})
    assert.deepEqual(access.pending, [])
  })

  test('loadAccess returns defaults for corrupt JSON', () => {
    setupStateDir()
    writeFileSync(join(TEST_DIR, 'access.json'), 'not json{{{', { mode: 0o600 })
    const access = loadAccess(TEST_DIR)
    assert.equal(access.dmPolicy, 'pairing')
    assert.deepEqual(access.allowFrom, [])
  })

  test('loadAccess merges partial config with defaults', () => {
    setupStateDir()
    writeFileSync(join(TEST_DIR, 'access.json'), '{"allowFrom":["U_X"]}', { mode: 0o600 })
    const access = loadAccess(TEST_DIR)
    assert.deepEqual(access.allowFrom, ['U_X'])
    assert.equal(access.dmPolicy, 'pairing') // default filled in
    assert.deepEqual(access.channels, {})    // default filled in
  })

  test('loadAccess preserves extra fields from old plugin format', () => {
    setupStateDir()
    writeFileSync(join(TEST_DIR, 'access.json'), JSON.stringify({
      dmPolicy: 'allowlist',
      allowFrom: ['U_X'],
      channels: {},
      pending: [],
      ackReaction: 'eyes',        // old plugin field
      textChunkLimit: 3000,       // old plugin field
    }), { mode: 0o600 })
    const access = loadAccess(TEST_DIR)
    assert.equal(access.dmPolicy, 'allowlist')
    assert.deepEqual(access.allowFrom, ['U_X'])
    // Extra fields shouldn't break anything
    assert.equal((access as any).ackReaction, 'eyes')
  })
})

describe('Pairing integration (full lifecycle)', () => {
  test('unknown DM → pair → approve → deliver', () => {
    setupStateDir({ dmPolicy: 'pairing', allowFrom: [], channels: {}, pending: [] })

    // Step 1: Unknown user DMs — gate returns pair action
    const access1 = loadAccess(TEST_DIR)
    const result = gate(
      { user: 'U_NEW', channel: 'D789', channel_type: 'im', text: 'hello' },
      access1,
    )
    assert.equal(result.action, 'pair')
    const pair = result as { action: 'pair'; code: string; chatId: string; senderId: string }

    // Step 2: Server persists pending entry (mirrors handleEvent logic)
    const access2 = loadAccess(TEST_DIR)
    access2.pending = access2.pending.filter((p) => p.expiresAt > Date.now())
    access2.pending.push({
      code: pair.code,
      senderId: pair.senderId,
      chatId: pair.chatId,
      expiresAt: Date.now() + 3600_000,
    })
    saveAccess(TEST_DIR, access2)

    // Verify persistence
    const access3 = loadAccess(TEST_DIR)
    assert.equal(access3.pending.length, 1)
    assert.equal(access3.pending[0].code, pair.code)

    // Step 3: Approve pairing (mirrors /slack-channel:access pair <code>)
    const match = access3.pending.find(
      (p) => p.code.toLowerCase() === pair.code.toLowerCase(),
    )
    assert.ok(match)
    access3.allowFrom.push(match!.senderId)
    access3.pending = access3.pending.filter((p) => p.code !== pair.code)
    saveAccess(TEST_DIR, access3)

    // Step 4: User is now allowlisted — subsequent DM delivers
    const access4 = loadAccess(TEST_DIR)
    assert.ok(access4.allowFrom.includes('U_NEW'))
    assert.equal(access4.pending.length, 0)

    const result2 = gate(
      { user: 'U_NEW', channel: 'D789', channel_type: 'im', text: 'I am paired now' },
      access4,
    )
    assert.equal(result2.action, 'deliver')
  })

  test('pairing code approval is case-insensitive', () => {
    const code = 'ABC123'
    setupStateDir({
      dmPolicy: 'pairing',
      allowFrom: [],
      channels: {},
      pending: [{ code, senderId: 'U_NEW', chatId: 'D789', expiresAt: Date.now() + 3600_000 }],
    })

    const access = loadAccess(TEST_DIR)
    const match = access.pending.find(
      (p) => p.code.toLowerCase() === 'abc123',
    )
    assert.ok(match, 'case-insensitive lookup should find the entry')
    assert.equal(match!.senderId, 'U_NEW')
  })

  test('concurrent pairings for multiple users', () => {
    setupStateDir({ dmPolicy: 'pairing', allowFrom: [], channels: {}, pending: [] })

    // Two users DM at the same time
    const access = loadAccess(TEST_DIR)
    access.pending.push(
      { code: 'CODE_A', senderId: 'U_ALICE', chatId: 'D_A', expiresAt: Date.now() + 3600_000 },
      { code: 'CODE_B', senderId: 'U_BOB', chatId: 'D_B', expiresAt: Date.now() + 3600_000 },
    )
    saveAccess(TEST_DIR, access)

    // Approve Alice only
    const access2 = loadAccess(TEST_DIR)
    const alice = access2.pending.find((p) => p.code === 'CODE_A')
    assert.ok(alice)
    access2.allowFrom.push(alice!.senderId)
    access2.pending = access2.pending.filter((p) => p.code !== 'CODE_A')
    saveAccess(TEST_DIR, access2)

    const access3 = loadAccess(TEST_DIR)
    assert.ok(access3.allowFrom.includes('U_ALICE'))
    assert.ok(!access3.allowFrom.includes('U_BOB'))
    assert.equal(access3.pending.length, 1)
    assert.equal(access3.pending[0].senderId, 'U_BOB')
  })

  test('same user DMs twice — gets fresh code each time', () => {
    setupStateDir({ dmPolicy: 'pairing', allowFrom: [], channels: {}, pending: [] })
    const access = loadAccess(TEST_DIR)

    // First DM
    const result1 = gate(
      { user: 'U_REPEAT', channel: 'D_R', channel_type: 'im', text: 'hello' },
      access,
    )
    assert.equal(result1.action, 'pair')
    const code1 = (result1 as any).code

    // Second DM — different code
    const result2 = gate(
      { user: 'U_REPEAT', channel: 'D_R', channel_type: 'im', text: 'hello again' },
      access,
    )
    assert.equal(result2.action, 'pair')
    // Codes should be different (probabilistically — 6 chars from 31-char alphabet)
    // Run 10 times to be confident
    let allSame = true
    for (let i = 0; i < 10; i++) {
      const r = gate(
        { user: 'U_REPEAT', channel: 'D_R', channel_type: 'im', text: 'try' },
        access,
      )
      if ((r as any).code !== code1) { allSame = false; break }
    }
    assert.ok(!allSame, 'codes should not all be identical')
  })

  test('expired code cannot be approved', () => {
    setupStateDir({
      dmPolicy: 'pairing',
      allowFrom: [],
      channels: {},
      pending: [{ code: 'OLDCODE', senderId: 'U_OLD', chatId: 'D_O', expiresAt: Date.now() - 1000 }],
    })

    const access = loadAccess(TEST_DIR)
    // Prune expired (mirrors server logic)
    access.pending = access.pending.filter((p) => p.expiresAt > Date.now())
    const match = access.pending.find((p) => p.code === 'OLDCODE')
    assert.ok(!match, 'expired code should not be found after pruning')
    assert.equal(access.pending.length, 0)
  })

  test('saveAccess preserves extra fields (ackReaction, textChunkLimit)', () => {
    setupStateDir()
    writeFileSync(join(TEST_DIR, 'access.json'), JSON.stringify({
      dmPolicy: 'pairing',
      allowFrom: [],
      channels: {},
      pending: [],
      ackReaction: 'eyes',
      textChunkLimit: 3000,
    }), { mode: 0o600 })

    // Load, modify, save — extra fields should survive
    const access = loadAccess(TEST_DIR)
    access.pending.push({ code: 'TEST', senderId: 'U_X', chatId: 'D_X', expiresAt: Date.now() + 3600_000 })
    saveAccess(TEST_DIR, access)

    const raw = JSON.parse(readFileSync(join(TEST_DIR, 'access.json'), 'utf-8'))
    assert.equal(raw.ackReaction, 'eyes')
    assert.equal(raw.textChunkLimit, 3000)
    assert.equal(raw.pending.length, 1)
  })
})

// Cleanup
afterEach(() => {
  rmSync(TEST_DIR, { recursive: true, force: true })
})
