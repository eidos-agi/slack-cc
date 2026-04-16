# ADR-2026-03 — Repo governance as code via `.github/settings.yml`

## Status
Accepted — 2026-04-16

## Context

Until now, tier assignment and branching policy for Greenmark repos
lived in three places:

1. `greenmark-cockpit/tools/tier-map.sh` — bash script listing repos
2. `greenmark-cockpit/CLAUDE.md` — prose narrative
3. `cerebro-builder-mcp/cerebro_builder/topology.py` — Python `SERVICES` dict

None of these were consulted at runtime by the actual hooks, skills, or
GitHub itself. The result: **contract vs enforcement drift**. Session 29
surfaced this — `greenmark-cockpit` had GitHub branch protection
requiring PRs despite `tier-map.sh` declaring it T3 = direct-to-main.
Muscle-memory imports from T1 repos into T3 repos produced rebase
tangles and cognitive overhead.

Daniel surveyed the ecosystem. **The community has converged on
`.github/settings.yml`** as the de-facto standard for declarative repo
configuration, reconciled by the Probot/Settings GitHub App
(https://github.com/apps/settings). IDEs validate the schema via
SchemaStore. ~100k+ repos use it.

Alternatives considered:
- **Invent `.greenmark/repo.yaml`** — rejected; reinvents a solved
  problem, violates "don't wrap upstream before diagnosing"
- **Safe-Settings** (GitHub Engineering's newer alternative) — deferred
  until org-wide policy needs appear; Probot/Settings is sufficient today
- **Terraform for GitHub** — rejected; overkill for 13-repo solo-dev
  engagement
- **Keep central tier-map.sh** — rejected; less discoverable, does not
  reconcile against GitHub reality

## Decision

Adopt `.github/settings.yml` (Probot/Settings format) as the single
source of truth for GitHub-native repo concerns:

- **Repo topics** — including `tier-t1` / `tier-t2` / `tier-t3` as
  queryable metadata, visible on every repo page
- **Branch protection** — declared per tier, reconciled by Probot on
  every push
- **Labels, description, homepage, merge modes** — declared once

Non-GitHub concerns (runtime deploy_tool, environments, cerebro-builder
topology, stakeholders) stay in their native homes:
- `railway.toml` / `wrangler.jsonc` → deploy tool + environments
- `CODEOWNERS` → stakeholders / required reviewers
- `cerebro-builder-mcp/cerebro_builder/topology.py` → service catalog
  (will eventually derive `tier` by reading GitHub topics via API,
  replacing the hardcoded field)

## Tier contract

| Tier | Meaning | Branch protection | Required reviews | Required checks |
|------|---------|-------------------|------------------|-----------------|
| **T1 Production** | Deploy risk: breaking affects users | PR required | 0 (solo dev); set to 1+ if team grows | Type Check, Lint, Unit Tests, Build |
| **T2 Supporting** | Has CI but lower blast radius | PR required | 0 | Lint, Tests |
| **T3 Reference** | Docs + tools, no runtime | None — direct-to-main OK | 0 | None |

The `guard-main.yml` workflow remains on T1/T2 repos as a *warning*
annotation for direct pushes — not a block, just visibility.

## Canary sequence (per rhea, session 29)

1. **greenmark-cockpit (T3)** — this PR. Fixes the live contradiction.
2. **cerebro (T1)** — next PR. Validates the T1 schema against a real
   production repo. Retires cerebro from `tier-map.sh`, CLAUDE.md's
   tier table row, and eventually from topology.py's hardcoded field.
3. Once canary passes: roll to remaining 11 repos in one sweep. No
   staged rollout (AI-velocity principle).

## Probot/Settings installation

The Probot/Settings GitHub App must be installed on the
`greenmark-waste-solutions` organization for `.github/settings.yml`
files to be reconciled. Without it, the files are inert but still
useful as documentation of intent.

Installation: https://github.com/apps/settings → Install → select
organization → "All repositories" or per-repo.

## Consequences

**Positive:**
- Single source of truth per repo, version-controlled, PR-reviewable
- Stakeholders browsing GitHub web UI see topics + settings.yml both
  immediately
- Reconciler is a maintained third-party app, not homegrown code
- Schema has IDE validation (SchemaStore) and a large reference corpus
- Survives any individual engineer — standard format, findable by
  anyone who has seen Probot/Settings before

**Negative:**
- Requires a GitHub App installation (one-time dashboard click)
- `tier-map.sh` and `topology.py` must retire their hardcoded tier
  data over the canary rollout — three places of truth becoming one
  requires three edits
- Probot/Settings can be slow (runs on push events); drift possible
  between pushes, but bounded by "minutes" not "days"

**Neutral:**
- `.github/settings.yml` is only consumed if Probot is installed. Until
  then, it's documentation. This is not a regression from today (today
  tier-map.sh is also inert).

## Retirement plan (per rhea "retirement mandatory on same commit")

Per canary:

| On commit adding `.github/settings.yml` to repo X | Same commit removes from |
|---------------------------------------------------|--------------------------|
| greenmark-cockpit                                 | N/A (this is the doc itself; tier-map.sh already marks greenmark-cockpit T3) |
| cerebro                                           | `tools/tier-map.sh` cerebro line; `CLAUDE.md` tier table cerebro row; `topology.py` cerebro hardcoded tier |
| …etc for each subsequent repo                     | Same three places per repo |

After all 13 repos have `.github/settings.yml`:
- `tools/tier-map.sh` becomes empty → delete
- `CLAUDE.md` tier table replaced with pointer to "see each repo's
  `.github/settings.yml`"
- `topology.py` Service class gets `tier` as a property that fetches
  the repo's GitHub topics (cached)

## References

- rhea session 29 ruling on per-repo YAML + canary + retirement-mandatory
- Probot/Settings: https://github.com/probot/settings
- Schema: https://www.schemastore.org/json/
- Session 30 planning discussion (this commit + follow-ups)
