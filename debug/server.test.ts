#!/usr/bin/env tsx
/**
 * slack-eidos-debug — diagnostic server tests
 *
 * Tests the pure helper functions used by debug tools:
 * - Current-session skip log filtering (#8)
 * - Dual-start process detection (#11)
 * - --allowedTools / settings.local.json permission check (#10)
 */
import { test, describe, beforeEach, afterEach } from 'node:test'
import assert from 'node:assert/strict'
import { mkdirSync, writeFileSync, readFileSync, rmSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

// ---------------------------------------------------------------------------
// Test state
// ---------------------------------------------------------------------------
const TEST_DIR = join(tmpdir(), `cc-slack-debug-test-${process.pid}`)

function setup() {
  rmSync(TEST_DIR, { recursive: true, force: true })
  mkdirSync(TEST_DIR, { recursive: true, mode: 0o700 })
}

// ---------------------------------------------------------------------------
// Re-implement pure helper functions from debug/server.ts for testing
// ---------------------------------------------------------------------------

/**
 * Parse skip logs filtered to current session (#8).
 * bootTimeMs: when the bridge process started (epoch ms)
 * logContent: raw debug log file content
 */
function filterSkipLogs(logContent: string, bootTimeMs: number | null): { logs: string[]; stale: boolean } {
  const allSkipLogs = logContent.split('\n').filter((l) => l.includes('Channel notifications skipped'))

  if (!bootTimeMs || !allSkipLogs.length) return { logs: allSkipLogs.slice(0, 5), stale: false }

  const currentLogs = allSkipLogs.filter((line) => {
    const tsMatch = line.match(/^(\d{4}-\d{2}-\d{2}T[\d:.]+Z)/)
    if (!tsMatch) return true
    const logTime = new Date(tsMatch[1]).getTime()
    return logTime >= bootTimeMs - 5000
  })

  return { logs: currentLogs.slice(0, 5), stale: currentLogs.length < allSkipLogs.length }
}

/**
 * Parse process list output to detect multiple bridge instances (#11).
 */
function parseBridgeProcesses(psOutput: string): Array<{ pid: string; user: string; cpu: string; mem: string; command: string }> {
  if (!psOutput.trim()) return []
  return psOutput.split('\n').filter(Boolean).map((line) => {
    const parts = line.split(/\s+/)
    return { user: parts[0], pid: parts[1], cpu: parts[2], mem: parts[3], command: parts.slice(10).join(' ') }
  })
}

/**
 * Check settings.local.json for auto-approved slack tools (#10).
 */
function checkSettingsAllowList(settingsPath: string): { found: boolean; tools: string[]; replyAutoApproved: boolean } {
  if (!existsSync(settingsPath)) return { found: false, tools: [], replyAutoApproved: false }
  try {
    const settings = JSON.parse(readFileSync(settingsPath, 'utf-8'))
    const allow = settings?.permissions?.allow
    if (!Array.isArray(allow)) return { found: false, tools: [], replyAutoApproved: false }
    const slackTools = allow.filter((t: string) => t.startsWith('mcp__slack__'))
    return {
      found: slackTools.length > 0,
      tools: slackTools,
      replyAutoApproved: slackTools.includes('mcp__slack__reply'),
    }
  } catch {
    return { found: false, tools: [], replyAutoApproved: false }
  }
}

/**
 * Parse --allowedTools from a process command line (#10).
 */
function parseAllowedToolsFromArgs(psLine: string): string[] {
  const match = psLine.match(/--allowedTools\s+"?([^"]+)"?/)
  if (!match) return []
  return match[1].split(',').map((t: string) => t.trim())
}

// ===========================================================================
// Tests
// ===========================================================================

describe('Skip log filtering (#8)', () => {
  test('returns all logs when no boot time available', () => {
    const logContent = [
      '2026-04-22T00:08:12.863Z [DEBUG] MCP server "plugin:slack-channel:slack": Channel notifications skipped: not in list',
      '2026-04-22T00:08:12.864Z [DEBUG] MCP server "ide": Channel notifications skipped: no capability',
    ].join('\n')

    const result = filterSkipLogs(logContent, null)
    assert.equal(result.logs.length, 2)
    assert.equal(result.stale, false)
  })

  test('filters out logs from before boot time', () => {
    const oldTime = '2026-04-21T12:00:00.000Z' // old session
    const newTime = '2026-04-22T00:08:12.863Z' // current session
    const bootTime = new Date('2026-04-22T00:08:00.000Z').getTime()

    const logContent = [
      `${oldTime} [DEBUG] MCP server "old": Channel notifications skipped: stale`,
      `${newTime} [DEBUG] MCP server "new": Channel notifications skipped: current`,
    ].join('\n')

    const result = filterSkipLogs(logContent, bootTime)
    assert.equal(result.logs.length, 1)
    assert.ok(result.logs[0].includes('"new"'))
    assert.equal(result.stale, true)
  })

  test('includes all logs when all are after boot time', () => {
    const bootTime = new Date('2026-04-22T00:00:00.000Z').getTime()
    const logContent = [
      '2026-04-22T00:08:12.863Z [DEBUG] Channel notifications skipped: a',
      '2026-04-22T00:08:12.864Z [DEBUG] Channel notifications skipped: b',
    ].join('\n')

    const result = filterSkipLogs(logContent, bootTime)
    assert.equal(result.logs.length, 2)
    assert.equal(result.stale, false)
  })

  test('returns empty when no skip logs present', () => {
    const result = filterSkipLogs('some other log line\nanother line', Date.now())
    assert.equal(result.logs.length, 0)
    assert.equal(result.stale, false)
  })

  test('caps at 5 logs', () => {
    const bootTime = new Date('2026-04-22T00:00:00.000Z').getTime()
    const lines = Array.from({ length: 10 }, (_, i) =>
      `2026-04-22T00:08:12.${String(i).padStart(3, '0')}Z [DEBUG] Channel notifications skipped: server ${i}`
    ).join('\n')

    const result = filterSkipLogs(lines, bootTime)
    assert.equal(result.logs.length, 5)
  })

  test('5-second grace window catches boot-race logs', () => {
    // Log is 3 seconds before boot — should be included (within 5s grace)
    const bootTime = new Date('2026-04-22T00:08:15.000Z').getTime()
    const logContent = '2026-04-22T00:08:12.000Z [DEBUG] Channel notifications skipped: boot race'

    const result = filterSkipLogs(logContent, bootTime)
    assert.equal(result.logs.length, 1)
    assert.equal(result.stale, false)
  })
})

describe('Bridge process detection (#11)', () => {
  test('returns empty array for no output', () => {
    assert.deepEqual(parseBridgeProcesses(''), [])
    assert.deepEqual(parseBridgeProcesses('  '), [])
  })

  test('parses single process', () => {
    const ps = 'dev      51094  0.0  0.7 782372 59376 pts/0    Sl+  19:18   0:00 node /path/to/tsx /path/to/server.ts'
    const result = parseBridgeProcesses(ps)
    assert.equal(result.length, 1)
    assert.equal(result[0].pid, '51094')
    assert.equal(result[0].user, 'dev')
  })

  test('detects dual-start with multiple processes', () => {
    const ps = [
      'dev      51094  0.0  0.7 782372 59376 pts/0    Sl+  19:18   0:00 node /path/to/tsx /path/to/server.ts',
      'dev      52000  0.1  0.8 782372 59376 pts/0    Sl+  19:20   0:00 node /path/to/tsx /path/to/server.ts',
    ].join('\n')
    const result = parseBridgeProcesses(ps)
    assert.equal(result.length, 2)
    assert.equal(result[0].pid, '51094')
    assert.equal(result[1].pid, '52000')
  })

  test('skips blank lines in ps output', () => {
    const ps = 'dev      51094  0.0  0.7 782372 59376 pts/0    Sl+  19:18   0:00 node tsx server.ts\n\n'
    const result = parseBridgeProcesses(ps)
    assert.equal(result.length, 1)
  })
})

describe('Settings allow list check (#10)', () => {
  beforeEach(() => setup())

  test('reports not found for missing file', () => {
    const result = checkSettingsAllowList(join(TEST_DIR, 'nonexistent.json'))
    assert.equal(result.found, false)
    assert.equal(result.replyAutoApproved, false)
  })

  test('detects mcp__slack__reply in allow list', () => {
    const settings = {
      permissions: {
        allow: [
          'mcp__slack__reply',
          'mcp__slack__react',
          'Bash(git status:*)',
        ],
      },
    }
    const path = join(TEST_DIR, 'settings.local.json')
    writeFileSync(path, JSON.stringify(settings))

    const result = checkSettingsAllowList(path)
    assert.equal(result.found, true)
    assert.equal(result.replyAutoApproved, true)
    assert.deepEqual(result.tools, ['mcp__slack__reply', 'mcp__slack__react'])
  })

  test('reports not auto-approved when reply is missing', () => {
    const settings = {
      permissions: {
        allow: ['mcp__slack__react', 'mcp__slack__fetch_messages'],
      },
    }
    const path = join(TEST_DIR, 'settings.local.json')
    writeFileSync(path, JSON.stringify(settings))

    const result = checkSettingsAllowList(path)
    assert.equal(result.found, true)
    assert.equal(result.replyAutoApproved, false)
  })

  test('handles empty allow list', () => {
    const settings = { permissions: { allow: [] } }
    const path = join(TEST_DIR, 'settings.local.json')
    writeFileSync(path, JSON.stringify(settings))

    const result = checkSettingsAllowList(path)
    assert.equal(result.found, false)
    assert.equal(result.replyAutoApproved, false)
  })

  test('handles corrupt JSON gracefully', () => {
    const path = join(TEST_DIR, 'settings.local.json')
    writeFileSync(path, '{bad json')

    const result = checkSettingsAllowList(path)
    assert.equal(result.found, false)
    assert.equal(result.replyAutoApproved, false)
  })

  test('handles missing permissions key', () => {
    const path = join(TEST_DIR, 'settings.local.json')
    writeFileSync(path, JSON.stringify({ hooks: {} }))

    const result = checkSettingsAllowList(path)
    assert.equal(result.found, false)
  })
})

describe('--allowedTools CLI flag parsing (#10)', () => {
  test('parses comma-separated tools', () => {
    const line = 'claude --allowedTools "mcp__slack__reply,mcp__slack__react" --debug'
    const result = parseAllowedToolsFromArgs(line)
    assert.deepEqual(result, ['mcp__slack__reply', 'mcp__slack__react'])
  })

  test('returns empty for no flag', () => {
    const line = 'claude --debug --resume'
    assert.deepEqual(parseAllowedToolsFromArgs(line), [])
  })

  test('handles single tool', () => {
    const line = 'claude --allowedTools "mcp__slack__reply"'
    assert.deepEqual(parseAllowedToolsFromArgs(line), ['mcp__slack__reply'])
  })

  test('handles unquoted value', () => {
    const line = 'claude --allowedTools mcp__slack__reply --debug'
    const result = parseAllowedToolsFromArgs(line)
    assert.ok(result.length > 0)
    assert.ok(result[0].startsWith('mcp__slack__reply'))
  })
})

// Cleanup
afterEach(() => {
  rmSync(TEST_DIR, { recursive: true, force: true })
})
