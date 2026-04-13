# tools/ — Cockpit Automation

> **[← Back to Cockpit README](../README.md)** — project status, decisions index, reference docs

Scripts that enforce engineering standards across all Greenmark repos. Run from the cockpit root.

## Release Practices (Tier System)

Every repo is classified into one of three tiers. The tier determines what release practices get applied. See [ADR-2026-02](../decisions/ADR-2026-02.md) for the full decision record.

| Tier | What gets installed | Repos |
|------|-------------------|-------|
| **T1 Production** | CI, guard-main, PR template, CODEOWNERS, dependabot (human review), branch protection, pre-push hook | cerebro, cerebro-migrations, data-daemon |
| **T2 Supporting** | CI, guard-main, PR template, dependabot (auto-merge patches), pre-push hook | cerebro-qa, cerebro-warp-speed, cerebro-warp-speed-excel, cerebro-ai-services, cerebro-bot-farm |
| **T3 Reference** | Pre-push hook only | infra, greenmark-cockpit, cerebro-mcp, cerebro-vault, cerebro-excel |

### Common operations

```bash
# Audit all 13 repos — see what's compliant and what's drifted
./tools/ensure-release.sh

# Fix all drift in one shot
./tools/ensure-release.sh --apply

# Bootstrap a single repo (auto-detects tier from tier-map.sh)
./tools/bootstrap-repo.sh /path/to/repo

# Override tier for a repo not yet in the map
./tools/bootstrap-repo.sh /path/to/repo --tier 2

# Add a new repo: edit tier-map.sh, then run ensure-release.sh --apply
```

## Tool Index

| Script | What it does | When to run |
|--------|-------------|-------------|
| **tier-map.sh** | Shared tier classification. Sourced by bootstrap-repo.sh and ensure-release.sh. | Edit when adding/reclassifying repos |
| **bootstrap-repo.sh** | Applies tier-appropriate artifacts to a single repo. Idempotent. | When a new repo is created or a repo changes tier |
| **ensure-release.sh** | Audits all repos against tier-map.sh. Reports drift. `--apply` fixes gaps. | Periodically, or after adding repos |
| **ensure-flow.sh** | Audits the feature-develop-main branch flow and pre-push hooks. | Subsumed by ensure-release.sh for hooks; still useful for develop-branch staleness checks |
| **setup-ci.sh** | **Legacy.** Original CI installer. Superseded by bootstrap-repo.sh for tier-aware setup. Kept for its `--deploy` smoke-test option which bootstrap-repo.sh doesn't handle. | Only for adding deploy smoke tests (`--deploy URL`) |
| **gh-guard.sh** | Shell wrapper for `gh`. Blocks `gh pr merge --delete-branch` on long-lived branches. | Install once: `ln -sf $(pwd)/tools/gh-guard.sh ~/.local/bin/gh` |
| **hooks/pre-bash-branch-guard.sh** | Claude Code PreToolUse hook. Blocks `gh pr merge --delete-branch` on long-lived branches. | Wired in `~/.claude/settings.json` — already active |
| **hooks/pre-pr-issue-guard.sh** | Claude Code PreToolUse hook. Blocks `gh pr create` without `Closes #N` in the body. | Wired in `~/.claude/settings.json` — already active |
| **open-prs.sh** | Lists all open PRs across the org. `--checks` includes CI status. | Anytime: `./tools/open-prs.sh --checks` |
| **../cerebro-github/** | MCP server: 14 tools encoding engineering ceremony. Issue→PR→CI→merge, bulk ops, Rhea gates, incident ledger. | `claude mcp add --scope user cerebro-github -- cerebro-github serve` |
| **intel.sh** | Cross-repo intelligence sweep at session start. Writes intel.json. | Called by `/takeoff` |
| **debrief.sh** | Session delta computation at session end. Writes debrief.json. | Called by `/land` |
| **hygiene.sh** | Cleanup rules for common repo cruft. Dry run by default. | `./tools/hygiene.sh --apply` when needed |

## How the tools relate

```
tier-map.sh (single source of truth)
    ├── bootstrap-repo.sh (applies artifacts to one repo)
    └── ensure-release.sh (audits all repos, calls bootstrap-repo.sh --apply)

ensure-flow.sh (branch flow + staleness — overlaps with tier system for hooks)

gh-guard.sh ←→ hooks/pre-bash-branch-guard.sh (same protection, different layers)
    Local shell        Claude tool calls

hooks/pre-pr-issue-guard.sh (blocks PRs without Closes #N)
    Enforces: issue → sub-issue → PR → CI check → merge → auto-close
```

## Enforcement Hooks (Claude Code)

Two hooks in `~/.claude/settings.json` fire on every Bash tool call. They can't be bypassed by the AI — they're enforced by the harness.

| Hook | What it blocks | Why |
|------|---------------|-----|
| **pre-bash-branch-guard.sh** | `gh pr merge --delete-branch` when HEAD is main/master/develop | Prevents deleting long-lived branches (the cerebro develop deletion incident) |
| **pre-pr-issue-guard.sh** | `gh pr create` without `Closes #N` in the body | Forces every PR to link to an issue so the GitHub Project board tracks progress |

Both exit code 2 (block with message) when triggered. The AI sees the error and must adjust — create the issue first, or drop the `--delete-branch` flag.

**Escape hatch (branch guard only):** Prefix with `GH_SKIP_BRANCH_GUARD=1` if intentionally decommissioning a branch.

## PR Workflow (Enforced)

The issue guard makes this mandatory, not optional:

1. **Create an issue** describing the work
2. **Link it as a sub-issue** of the relevant milestone (if applicable)
3. **Add it to the GitHub Project** ([Cerebro Engineering](https://github.com/orgs/greenmark-waste-solutions/projects/1))
4. **Create the PR** with `Closes #N` in the body ← hook enforces this step
5. **Check CI** after creation ← memory enforces this step
6. **Merge** → issue auto-closes, project board updates, milestone progress fills

## Adding a new repo

1. Add it to `tier-map.sh` with the appropriate tier
2. Run `./tools/ensure-release.sh --apply`
3. Commit the generated `.github/` files in the new repo
4. If T1 and it deploys somewhere, write a deploy workflow by hand (deploy patterns are repo-specific)

## Tracking work

All engineering work is tracked in the [Cerebro Engineering](https://github.com/orgs/greenmark-waste-solutions/projects/1) GitHub Project. Wrike stays executive-level for Michael and Alex.

- **Milestones** are parent issues (M-01 through M-07 for Sage)
- **Tasks** are sub-issues linked to milestones — progress bars fill as they close
- **PRs** link to issues via `Closes #N` — shows in "Linked pull requests" column
- **Roadmap view** shows the Gantt (Start Date / Target Date fields)
- Quick audit: `./tools/open-prs.sh --checks`
