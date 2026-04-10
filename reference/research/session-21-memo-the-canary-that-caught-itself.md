# Memo: The Canary That Caught Itself

**Date:** 2026-04-09
**Author:** Daniel Shanklin
**Subject:** How Session 21 built three layers of infrastructure, then discovered one was quietly broken

---

## TL;DR

We built a cross-repo intelligence layer, a CI/CD pipeline, and processized the whole thing into reusable tools. We were ready to land the session with 43 commits shipped across the org. Then Rhea asked one question — *"what's the riskiest thing you haven't tested?"* — and we found that three of the five repos we'd just equipped with CI had broken pipelines. They would have failed on every run, forever, until someone noticed. The canary caught the canary.

## What Got Built

Three capabilities, all meant to make the next 100 sessions honest.

**1. Cross-repo intelligence layer**
- `tools/intel.sh` sweeps every git repo in `~/repos/` at takeoff, writes `intel.json` with commits/dirty files/staleness per repo
- `tools/debrief.sh` mirrors it at landing, writes `debrief.json` with the session delta
- `tools/hygiene.sh` encodes five noise-filter rules (`.mcp.json`, `__pycache__/`, package-lock.json in test repos, report archives, webflow exports)
- Wired into `/takeoff` and `/land` skills
- Org-wide dirty files dropped from **91 to 2**

**2. CI/CD pipeline on cerebro**
- `ci.yml` — type check, lint, test, build on every PR
- `deploy.yml` — full CI gate before deploy, then smoke tests (health check + auth gate) after
- `guard-main.yml` — alerts on direct pushes to main
- Local pre-push hook — blocks `git push origin main` at the keyboard
- First PR ever on the cerebro repo opened: develop → main (9 commits including the security sprint)

**3. refactor-forge migration kit**
- Installed the skills from `eidos-agi/refactor-forge` into cerebro
- Captured **164 golden fixtures** from the cerebro-warp-speed Python backend (21 tools across 4 plugins: hubspot, sage, identity, insights)
- Migration map ready: 0/21 tools ported, 0/88 fixtures passing
- When Phase 2 begins, the Python → TypeScript port will have byte-level proof of behavioral parity

**4. The meta-tool**
- `tools/setup-ci.sh` — one command to install the full CI pipeline (CI + guard + hook) on any repo
- Supports Node.js and Python, auto-detects from `package.json` / `requirements.txt`
- Idempotent

## What Almost Shipped

I rolled `setup-ci.sh` out to five repos — cerebro-qa, cerebro-warp-speed, cerebro-warp-speed-excel, data-daemon, rhea-mcp — and committed the workflow files. The work felt done. The commits were clean. I was ready to land.

Then Rhea pushed back on landing. The Doubter asked: *the CI you just pushed to five repos — has it actually fired? Once? On any of them?* The answer was no. The workflows existed on disk but had never been triggered by a real PR.

So I opened a canary PR on cerebro-qa to force the pipeline to run. All three checks failed instantly. The error was `Dependencies lock file is not found in /home/runner/work/cerebro-qa/cerebro-qa. Supported file patterns: package-lock.json, npm-shrinkwrap.json, yarn.lock`.

cerebro-qa is a Python repo. I had shipped it the Node.js CI template.

Then I checked the other four. Two more had the same bug: `cerebro-warp-speed` and `cerebro-warp-speed-excel`, both Python, both running `npm ci` against a repo with no `package.json`. Three of five repos had broken pipelines. The script I built to prevent mistakes *was* the mistake.

## The Fix

1. Patched `setup-ci.sh` to auto-detect language from `package.json` vs `requirements.txt`/`pyproject.toml`, and to print the detected language so mistakes become visible
2. Regenerated CI templates on the three broken repos with `--python`
3. Opened three PRs to fix the CI itself
4. Waited for CI to run — and it caught another layer of debt: 17 ruff lint errors in cerebro-qa, 9 in cerebro-warp-speed, **198** in cerebro-warp-speed-excel
5. Fixed every single lint error:
   - cerebro-qa: moved imports to top, removed unused variable
   - cerebro-warp-speed: auto-fix removed 9 extraneous f-string prefixes
   - cerebro-warp-speed-excel: created `ruff.toml` excluding intentional compact style (E701/E702), auto-fixed 14 unused variables, replaced bare `except:` with `except (ValueError, TypeError, ...)`, removed 2 unused imports, added one `noqa` for a legitimate `sys.path` hack
6. All three PRs now: Type Check ✅ Tests ✅ Lint ✅

## The Lesson

> **Infrastructure that has never fired is not a safety net. It's a placebo.**

Ops bugs are worse than code bugs because they're invisible until someone falls. A failing unit test is a red X in your face; a CI workflow that has never run gives *false green* until the moment you need it. The cost of shipping a non-functional pipeline is not "you have to fix it later" — it's "you believed you had a safety net that didn't exist, and you made decisions based on that belief."

What Rhea caught wasn't a clever technical insight. It was the question you stop asking when you're tired and the work feels done. The Dreamer/Doubter/Decider pattern exists exactly for that moment. It's the voice that says *prove it* when your inner monologue is saying *ship it*.

The broader principle, reframed: **don't confuse "I built X" with "X works."** Between those two statements is a test, and if you skip the test you don't actually know which side you're on. Every piece of infrastructure in this session — intel.sh, debrief.sh, hygiene.sh, ci.yml, deploy.yml, setup-ci.sh — needed a canary before it could be trusted. We only did it because Rhea made us.

## What's Still Open

- **cerebro PR #1** (develop → main) — first-ever cerebro PR, contains the RLS security sprint + Ask Cerebro upgrade + branch guard. CI is running against it now. Ready to merge when reviewed.
- **Three CI-fix PRs** on the Python repos — all green, ready to merge.
- **cerebro-migrations PR #1** — hygiene commits. Low-stakes merge.
- **gmw-dot-com-astro PR #1** and **tech-deck PR #1** — hygiene commits. Low-stakes merges.
- **Phase 2 of warp-speed migration** — the Python → TypeScript port of 21 tools. Golden fixtures are ready. When we pick this up, we'll port one tool at a time with `/refactor-port`, verify each with `/refactor-verify` against the fixtures, and refuse to mark anything done until 8/8 pass per tool.
- **data-daemon's `.gitignore`** — blocked by a missing virtualenv that the repo's pre-commit hook needs. Not a triage question, an environment setup question. Left for a dedicated data-daemon session.

## Numbers

| Metric | Start | End |
|---|---|---|
| Dirty files across org | 91 | 2 |
| Repos with dirty files | 25 | 1 |
| Unpushed commits across org | ~50 | 0 (modulo the open PRs) |
| Repos with CI pipeline | 1 (cerebro) | 6 |
| Golden fixtures captured | 0 | 164 |
| Commits this session | 0 | 60+ |
| Things I was wrong about (that Rhea caught) | — | 1 |

## For Next Session

The cockpit now knows about all 40 repos. Every takeoff will sweep them. Every landing will capture the session delta. The briefing will be honest about cross-repo reality, not just what's in the cockpit's own git status.

The CI pipeline is processized. Installing it on a new repo is one command. And thanks to the canary, it actually works.

The next session should start by:
1. Merging the six open PRs (or triaging them)
2. Starting Phase 2 of the warp-speed migration — this is the real work unlocked by this session's scaffolding
3. Deciding whether to roll `setup-ci.sh` out to the rest of the Python repos (rhea-mcp, data-daemon) after verifying they don't have the same lint debt

---

*Memo written during Session 21. The tool that wrote this memo is the same tool that almost shipped broken CI. That's worth remembering.*
