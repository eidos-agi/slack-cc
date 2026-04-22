# MCP Trim Plan — Reduce 65K → ~40K Tool Context

## Tier 1: Remove (broken or redundant)

| MCP | Tools | Tokens | Action | CLI alternative |
|-----|-------|--------|--------|-----------------|
| `director-daemon` | ? | ~1K | **Delete** — Mac path, doesn't exist in container | N/A (not used) |
| `keeper` | ? | ~1K | **Delete** — Mac path, doesn't exist in container | N/A (not used) |
| `pal` | ? | ~1K | **Delete** — Mac path, doesn't exist in container | N/A (not used) |
| `github` (raw) | 38 | ~11K | **Delete** — cerebro-github wraps this with ceremony | `gh` CLI already available via Bash |

**Savings: ~14K tokens**

## Tier 2: Trim (too many tools loaded)

| MCP | Total tools | Used tools | Unused | Tokens | Action |
|-----|-------------|------------|--------|--------|--------|
| `wrike` | 51 | ~5 | ~46 | ~9K | **Filter to 5 tools** or convert unused to CLI wrapper |
| `railguey` | 42 | ~10 | ~32 | ~9K | **Filter to 15 tools** — keep deploy/service/account/doctor/variables |

**Potential savings: ~10K tokens** (if MCP tool filtering is supported)

### Wrike — keep only:
- `pm_add_comment` — comment on existing tasks
- `pm_list_tasks` — see what's there
- `pm_get_task` — read a task
- `pm_status` — dashboard
- `pm_search` — find tasks

### Railguey — keep only:
- `railguey_deploy`, `railguey_redeploy`, `railguey_rollback`
- `railguey_service_info`, `railguey_services`
- `railguey_account_default`, `railguey_accounts`
- `railguey_variable_set`, `railguey_variables`
- `railguey_logs`, `railguey_deployment_logs`, `railguey_http_logs`
- `railguey_doctor`, `railguey_doctor_project_level`, `railguey_doctor_service_level`
- `railguey_status`

### CLI conversion option:
For tools removed from MCP, wrap as Bash commands:
```bash
# Instead of mcp__wrike__create_task (forbidden anyway):
rtk wrike create-task "title"  # blocked by hook

# Instead of mcp__railguey__volume_create (rare):
railguey volume create --name X --size 1Gi  # CLI exists
```

Railguey already HAS a CLI — the MCP just wraps it. Many tools could be CLI-only without loss.

## Tier 3: Move to per-project config

| MCP | Currently | Should be |
|-----|-----------|-----------|
| `vercel` | global | cerebro project only |
| `rhea-diagrams` | global | remove (localhost, rarely up) |
| `browsermcp` | global | cockpit project only |
| `ask-ai-web` | global | remove or cockpit only |
| `cerebro-mcp` | global | cerebro project only |

**Savings: ~5K tokens** when not in the relevant project

## Implementation

### Phase 1: Delete broken MCPs (5 min, zero risk)
Remove `director-daemon`, `keeper`, `pal` from `.mcp.json`. They fail silently anyway.

### Phase 2: Remove raw `github` MCP (5 min, low risk)
Remove `github` from `.mcp.json`. Verify `cerebro-github` still works (it uses its own auth). The `gh` CLI remains available via Bash.

### Phase 3: Investigate tool filtering
Check if MCP protocol supports `toolFilter` or similar. If yes, filter wrike and railguey to essential tools only. If not, file feature requests on both MCPs.

### Phase 4: Per-project configs
Move vercel, rhea-diagrams, browsermcp, ask-ai-web to project-level `.mcp.json` files in the repos that need them.

## Expected Result

| Stage | Tools | Tokens |
|-------|-------|--------|
| Current | ~250+ | ~65K |
| After Phase 1-2 | ~210 | ~51K |
| After Phase 3 | ~180 | ~42K |
| After Phase 4 | ~160 | ~38K |

**42% reduction in tool context.** Not a budget doubler, but meaningfully more room for conversation before compression kicks in.
