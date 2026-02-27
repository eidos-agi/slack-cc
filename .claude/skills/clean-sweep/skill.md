# /clean-sweep — Workspace Clean Sweep

## When to Use
When the workspace is behind — uncommitted work scattered across repos, unpushed changes, stale state. The trigger is urgency: everything gets checked in, pushed, built, and tested. No questions asked.

## What It Does
Discovers every Greenmark repo, commits all dirty work, pushes everything, runs builds and tests where applicable, and produces a single status report. Fully autonomous — infer everything, ask nothing.

## Execution Steps

### Stage 1 — Discovery (parallel)

Scan for all git repos in the workspace:

```bash
# For each directory in ~/repos-greenmark-waste-solutions/*/
# Filter: only dirs containing .git
# For each repo, gather (parallel per repo):
#   git status --porcelain
#   git branch --show-current
#   git log origin/<branch>..HEAD --oneline  (unpushed commits)
```

Run all discovery commands in parallel — one Bash call per repo.

Categorize each repo into one of:
- **clean** — no dirty files, no unpushed commits
- **dirty** — uncommitted changes exist
- **unpushed** — committed but not pushed to remote
- **no-remote** — no remote configured (local only)

A repo can be both dirty AND unpushed.

### Stage 2 — Commit All Dirty Repos (sequential per repo)

For each dirty repo, in sequence:

1. **Stage files** — `git add` everything EXCEPT:
   - `.env*`
   - `credentials*`
   - `*.key`
   - `*.pem`
   - `node_modules/`
   - Use: `git add . && git reset HEAD -- '.env*' 'credentials*' '*.key' '*.pem' 'node_modules/'`
   - Verify with `git diff --cached --stat` that nothing sensitive was staged

2. **Infer commit message** from `git diff --cached --stat`:
   - Look at file paths and change counts
   - Generate a concise message: what changed and why (infer from filenames/paths)
   - Format: `clean-sweep: <summary of changes>`
   - Example: `clean-sweep: sync 28 backlog tasks, update meeting notes, add SEO plan`

3. **Commit** — standard `git commit`. Never use `--no-verify`. Never force.
   - If pre-commit hook fails: read the error, fix the issue, re-stage, commit again
   - If it fails twice: log the failure, skip this repo, continue sweep

4. **Track** — note the repo name, file count, and commit hash for the report

### Stage 3 — Push All Repos (parallel)

For every repo with unpushed commits (including newly committed ones):

```bash
git push
```

Run pushes in parallel — one Bash call per repo.

**If push is rejected (diverged):**
1. `git pull --rebase` — try to reconcile
2. `git push` — retry once
3. If merge conflict on rebase: `git rebase --abort`, flag the repo as CONFLICT, skip it

**If push fails (no remote, auth):** Flag it, skip it, continue.

### Stage 4 — Build & Test (parallel subagents)

For each repo, detect what's buildable by checking for files:

| File Present | Action |
|-------------|--------|
| `package.json` with `build` script | `npm run build` |
| `package.json` with `lint` script | `npm run lint` (after build) |
| `package.json` with `test` script | `npm run test` |
| `tests/` dir or `pytest.ini` or `pyproject.toml` with pytest | `python -m pytest tests/ -x -q` |
| None of the above | Docs/config repo — skip |

Launch **parallel subagents** (Task tool, subagent_type: `general-purpose`) — one per buildable repo. Each subagent:
1. `cd` into the repo
2. Run `npm install` if `node_modules/` is missing and `package.json` exists
3. Run the detected build/test commands
4. Return: repo name, exit codes, last 30 lines of output

### Stage 5 — Finalize Cockpit

Back in the cockpit repo (`greenmark-cockpit`):

1. Read `state.json`
2. Set `custom.last_clean_sweep` to current ISO timestamp
3. Write `state.json`
4. If cockpit has uncommitted changes (from state.json update or anything else):
   - `git add state.json`
   - `git commit -m "clean-sweep: update state.json with sweep timestamp"`
   - `git push`

### Stage 6 — Report

Output the final report in this exact format:

```
  ██████╗██╗     ███████╗ █████╗ ███╗   ██╗
 ██╔════╝██║     ██╔════╝██╔══██╗████╗  ██║
 ██║     ██║     █████╗  ███████║██╔██╗ ██║
 ██║     ██║     ██╔══╝  ██╔══██║██║╚██╗██║
 ╚██████╗███████╗███████╗██║  ██║██║ ╚████║
  ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝
 ███████╗██╗    ██╗███████╗███████╗██████╗
 ██╔════╝██║    ██║██╔════╝██╔════╝██╔══██╗
 ███████╗██║ █╗ ██║█████╗  █████╗  ██████╔╝
 ╚════██║██║███╗██║██╔══╝  ██╔══╝  ██╔═══╝
 ███████║╚███╔███╔╝███████╗███████╗██║
 ╚══════╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝

CLEAN SWEEP — Greenmark Workspace
Swept: N repos | Committed: N | Pushed: N | Built: N | Tested: N

REPO                          COMMIT    PUSH   BUILD   TEST
cerebro                       3 files   ✓      ✓       —
data-daemon                   —         ✓      —       82/82 ✓
greenmark-cockpit             28 files  ✓      —       —
infra                         —         ✓      —       —

WARNINGS: <any failed pushes, hook failures, skipped repos>
FAILURES: <any build/test failures with brief reason>

Workspace: CLEAN ✓
```

Column definitions:
- **COMMIT**: `N files` if committed this sweep, `—` if was already clean
- **PUSH**: `✓` if pushed, `—` if nothing to push, `✗ <reason>` if failed
- **BUILD**: `✓` if build passed, `—` if no build, `✗` if failed
- **TEST**: `N/N ✓` if tests passed, `—` if no tests, `✗ N failed` if failures

If everything is clean with no warnings or failures:
```
Workspace: CLEAN ✓
```

If there are issues:
```
Workspace: SWEPT (N warnings, N failures)
```

## Rules

- **Discover repos dynamically** — scan `~/repos-greenmark-waste-solutions/*/`, never hardcode repo names
- **Skip non-git dirs** — if no `.git`, it's not a repo
- **Never commit secrets** — exclude `.env*`, `credentials*`, `*.key`, `*.pem`, `node_modules/`
- **Never force push** — no `--force`, no `-f`
- **Never skip hooks** — no `--no-verify`
- **Diverged push** → `git pull --rebase`, retry once. Conflict → `git rebase --abort`, flag and skip
- **Build/test failures are warnings, not blockers** — report them but don't stop the sweep
- **No questions** — infer everything from git state, file names, and diff stats. Act autonomously.
- **Always update state.json** with `custom.last_clean_sweep` timestamp at the end
- **Parallel where possible** — discovery, pushes, and builds all run in parallel. Only commits are sequential (to avoid race conditions on shared state).
- **Commit message prefix** — all sweep commits use the prefix `clean-sweep: `
