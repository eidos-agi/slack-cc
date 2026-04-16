# Approved software — Greenmark engagement

**Source of truth for what agents can install/use without consultation.**

Governed by [GR-TOOLING-001](../.visionlog/guardrails/GUARD-003*.md). Anything
NOT on this list requires a rulebook pass before install.

## How this list changes

- **Add**: by explicit Daniel approval, captured as a line here with date + one-sentence justification.
- **Remove**: by explicit Daniel approval if the software proves harmful or redundant. Removing implies sunsetting any repo that depends on it.
- **Never** add by "seemed fine, everyone uses it." That's exactly what this list is preventing.

## Infrastructure (runtimes, hosts, data platforms)

| Software | Use | Cost posture |
|---|---|---|
| **Cloudflare Workers** | Edge runtime for MCP servers (cerebro-mcp, remote-mcp-server-authless) | Greenmark-billed, existing |
| **Cloudflare R2** | NOT adopted. Evaluated session 30, explicitly rejected — see `feedback_simple_thing.md` | — |
| **Railway** | Container runtime for cerebro, data-daemon, cerebro-telemetry, cerebro-ai-services, cerebro-bot-farm, cerebro-qa, cerebro-warp-speed, portal | Greenmark-billed, existing |
| **Supabase** | Postgres + auth + OAuth Server + JWKS for the whole ecosystem | Greenmark-billed, existing |
| **Browserbase** | Cloud browser sessions for `ab -p browserbase` and CI self-tests | Daniel-personal key, shared with Greenmark |
| **GitHub** | Source hosting, Actions CI, Issues, Projects | Free tier + $4/user/month on the org |
| **Claude API / Claude Code** | The engagement's AI runtime. Not optional. | Daniel's Anthropic account |

## Development tooling (CLIs, local dev)

| Software | Use |
|---|---|
| `gh` CLI | GitHub scripting from hooks, CI, and agent sessions |
| `wrangler` | Cloudflare Workers deploy + secret management |
| `railway` CLI | Railway deploy + log tailing (used indirectly via railguey MCP) |
| `pre-commit` | Python pre-commit hook runner (data-daemon uses this) |
| `pytest`, `oxlint`, `tsc`, `eslint`, `ruff` | Standard language-native test + lint runners |
| `litestream` CLI | **Reserved** — not wired into any service today (removed from cerebro-telemetry); kept available for any repo that actually needs SQLite DR |
| `agent-browser` (ab) | Per-repo browser automation via Browserbase, in `greenmark-cockpit/tools/agent-browser/` |

## GitHub Apps

| App | Use | Status |
|---|---|---|
| Probot/Settings | Reconciles `.github/settings.yml` to actual repo state per ADR-2026-03 | **Not installed yet** — pending Daniel's dashboard install on the org |
| Dependabot | Auto-PR for dependency updates (T1/T2 tier contract) | Installed, per-repo config in settings.yml |

## MCP servers (used inside this engagement)

| Server | Provider | Purpose |
|---|---|---|
| cerebro-builder | Daniel (in `cerebro-builder-mcp/`) | Session orchestration, topology, mission |
| cerebro-github | Daniel (in `cerebro-github/`) | GitHub ceremony (create_work, merge_pr, etc.) |
| cerebro-verifier | Daniel | Parity checks + ground truth |
| cerebro-vault | Daniel | Secrets management |
| cerebro-mcp (Worker) | Daniel | Live Cerebro data to claude.ai |
| railguey | Daniel (`eidos-agi/railguey`) | Railway automation |
| visionlog | Daniel | Vision, goals, guardrails, SOPs |
| ike.md | Daniel | Tasks, milestones, execution |
| research.md | Daniel | Decisions with evidence |
| rhea | Daniel | 3-model Socratic debate |
| agent-browser MCP | upstream | Browser automation |
| browsermcp | upstream | NOT used — per cockpit CLAUDE.md, `ab` is mandatory, this is deferred-only |
| context7 | upstream | Fresh library docs |
| github | upstream | GitHub API wrapper |
| ide | upstream | IDE integration |
| wrike | upstream | Wrike integration |
| Gmail / Google Calendar / Fireflies / Linear / Notion / Vercel | upstream | Per-integration auth surfaces |

All of the above are already authenticated and approved for this engagement.

## Paid SaaS considered and rejected (or deferred)

| Software | Decision | Reason |
|---|---|---|
| **Sentry** | Deferred | Free tier exists, but errors are logged to Cloudflare Workers Logs + cerebro-telemetry; Sentry adds another dashboard for no current unlocked value |
| **Datadog / New Relic / Dynatrace** | Rejected | Comically over-priced for a solo-dev engagement |
| **Honeycomb** | Deferred | Useful for high-cardinality tracing if we ever need it, but telemetry is in SQLite today and that works |
| **Axiom** | Deferred | Similar — our Supabase-backed telemetry is sufficient |
| **Grafana Cloud** | Deferred | Free tier is fine, but "yet another UI" cost is real for solo dev |
| **PostHog** | Deferred | Product analytics angle is appealing; not the current need |
| **Langfuse / Helicone / Braintrust** | Deferred | LLM observability is useful but premature — we don't have an LLM product surface needing eval at scale |
| **Litestream + R2** | Rejected (session 30) | Internal observability DR not worth the vendor surface. Documented in cerebro-telemetry README. |

## When this list is wrong

If you're an agent and need software that's not on this list:

1. Don't install it. Stop.
2. Propose it per GR-TOOLING-001.
3. If Daniel approves: add it here in the same commit that ships the install.
4. If Daniel rejects: record the rejection in the "rejected" table above with the reason, so future agents don't re-propose.

If you think this list is missing something that's already installed:

1. Find the receipts — where was it approved originally?
2. Add it here with a date and reference to the approval conversation.
3. If no approval exists: flag it to Daniel. Might be drift we should retroactively approve or remove.
