# cerebro-github

MCP server that encodes the Greenmark engineering ceremony. One tool call does the right thing — no hooks, no memory, no forgetting.

## Why

The ceremony exists because we kept getting it wrong:
- PRs without issues → project board has no linked PRs
- Issues not added to the project → invisible work
- CI not checked after PR → broken builds go unnoticed
- Wrong branch deleted → develop branch incident
- Credentials copy-pasted ad-hoc → drift between environments
- No adversarial check before production merges → risky deploys

Instead of remembering 12 steps, call one tool.

## Tools (14)

### Do — execute the ceremony

| Tool | What it does |
|------|-------------|
| `create_work` | Create issue → link as sub-issue → add to project → return issue number |
| `close_work` | Close an issue without a PR (won't-fix, resolved by conversation) → set project to Done |
| `open_pr` | Verify issue exists → create PR with `Closes #N` → add issue to project → check CI |
| `check_ci` | Check CI status on a PR — SKIPPED checks don't block merging |
| `merge_pr` | CI green → branch safety → **Rhea gate if T1→main** → squash merge |

### See — observe the state

| Tool | What it does |
|------|-------------|
| `dashboard` | All open PRs across org with CI status, one table |
| `bulk_merge` | Preview or merge all green PRs (**dry run by default**) |
| `health_check` | Conflicts, stale PRs, Railway deploy status for all T1 services |
| `changelog` | What shipped since date X — merged PRs + closed issues across org |
| `stale` | PRs >3 days, issues >7 days untouched |

### Know — understand and evolve the ceremony

| Tool | What it does |
|------|-------------|
| `onboard` | Full briefing: workflow, repos, tiers, infrastructure, incident ledger |
| `why` | Explain why a tool exists — the incident, the cost, the principle |
| `retro` | Review recent work, find ceremony gaps (PRs without issues, unfixed CI, etc.) |
| `learn` | Record a new incident → persists to ledger.json → future sessions inherit it |

## Rhea Token Gates

T1 repos merging to main (production) require adversarial reasoning before execution. The gate is structural — the MCP errors without a valid token.

**Two-call handshake:**
```
Agent: merge_pr("cerebro", 42)
MCP:   → returns {gate: "rhea_review_required", gate_token, challenge_prompt}

Agent: mcp__rhea__rhea_challenge(proposal=challenge_prompt)
Rhea:  → Dreamer/Doubter/Decider debate → returns decision

Agent: merge_pr("cerebro", 42, gate_token="gate-...", rhea_decision="Accept...")
MCP:   → validates token (hash + expiry) → validates decision → executes merge
```

Gates fire on: T1→main merges, milestone closure, credential provisioning.
Gates do NOT fire on: T2/T3 repos, develop-target merges, read-only operations.

## Infrastructure Model

The MCP knows the full system topology (`topology.py`):

- **Environments:** develop (staging) + production, each with Railway tokens, Supabase projects, service domains
- **Services:** cerebro, data-daemon, cerebro-qa, etc. — mapped to Railway services with per-env domains
- **Vendor credentials:** which env vars each vendor needs, whether they differ by environment
- **Deploy order:** cerebro-migrations → cerebro → data-daemon → cerebro-qa → ...

## Incident Ledger

Every ceremony rule traces to a real incident. The ledger persists to `ledger.json` and is returned by `onboard()`. When something goes wrong, call `learn()` to add to the ledger — future sessions inherit it automatically.

## Config

- `config.py` → tier map, project IDs, status field IDs, protected branches
- `topology.py` → environments, services, credentials, deploy order
- `gate.py` → token creation/validation, context snapshots
- `ledger.json` → persistent incident history

## Install

```bash
pip install -e .
claude mcp add --scope user cerebro-github -- cerebro-github serve
```
