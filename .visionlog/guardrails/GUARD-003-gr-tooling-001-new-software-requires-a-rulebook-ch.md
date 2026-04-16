---
id: "GUARD-003"
type: "guardrail"
title: "GR-TOOLING-001 \u2014 New software requires a rulebook check, and paid software defaults to no"
status: "active"
date: "2026-04-16"
---

# GR-TOOLING-001 — Software adoption requires rulebook consultation

**Scripture. Not a preference. A rule for this engagement.**

## Rule

Before installing, adopting, or proposing **any** new third-party software — library, SaaS, GitHub App, CLI, Cloudflare add-on, Railway add-on, browser extension, Supabase extension, vendor integration — an agent (human or AI) must:

1. **State the problem in one sentence.** What breaks today without this software?
2. **Name the existing alternative.** What's already installed / already paid for that would cover 80% of the need?
3. **Declare the cost.** Monetary ($/month now or eventually), operational (another service to run), cognitive (another thing future-Daniel has to reason about), identity (another credential to rotate).
4. **Frame the ROI in AI-leverage terms.** Not "this is production-grade" — "this collapses X hours of recurring work to Y minutes."
5. **If any monetary cost exists, even $0-now-paid-later**: expect default rejection and require explicit Daniel approval before install.

**"Free tier" does not exempt.** Sentry free, PostHog free, Axiom free, R2 free, GitHub Actions minutes — all create accounts, credentials, expectations, and usually grow into spend. Count them.

## Scope

Applies to every Greenmark repo, every Daniel-led engagement artifact, every session. No agent installs software into a Greenmark workflow without this check.

Does **not** apply to:
- Transient sandbox installs that don't persist (e.g., `pip install pre-commit` to run a single pre-commit hook in CI)
- Existing Greenmark infrastructure already in use (Cloudflare Workers, Railway, Supabase, Browserbase — already approved)
- Claude Code / Claude API itself (the engagement's foundation)

## Why

The Greenmark stakeholders at the far end of the chain — Michael, Alex, Robert — do not yet internalize that **AI creates leverage proportional to tooling spend**. Asking them to approve "$10/month for Sentry" or "$25/month for Axiom" will return a reflexive "no" because the mental model is "software cost = liability." Without the framing "AI agent operating against this tool collapses weeks of human effort into hours," the spend looks like waste.

Meanwhile, AI agents (including me) pattern-match reflexively to "production-grade systems have X" from training data — Litestream, Sentry, cross-cloud DR, monitoring dashboards, feature flag services. Every one of those would have been rejected by Daniel during session 29–30. Pattern-matching without consulting this rulebook wastes real hours and creates drift from stakeholder trust.

This rule exists to catch that drift at the earliest point: before the tool is installed, not after.

## Red flags that trigger this rule

Any of these phrases in an AI proposal should trigger immediate consultation:
- "Production-grade systems have this"
- "Industry best practice is to add…"
- "While we're at it, let's also add…"
- "The complete version of this would include…"
- "Free tier should be enough for now"
- "We can always add it back later" (this one — if we can always add it back later, default to NOT having it today)

## How to apply

**When proposing software:**
1. Open a proposal with: "I want to add X. Here's the problem it solves." (one sentence)
2. List the existing alternative and say why it's insufficient.
3. Name the cost: $/mo, account, credential, operational, cognitive.
4. Frame ROI in AI-leverage hours saved, not features gained.
5. Wait for explicit Daniel approval before install, unless the software is already on the approved list.

**When catching yourself about to install something:**
1. Stop.
2. Ask: did I consult this rule?
3. If no: apply steps 1–4 above before proceeding.

**Approved software list (maintained in `policies/software-approved.md`):**
- Cloudflare Workers (runtime)
- Railway (runtime)
- Supabase (data + auth)
- Browserbase (browser automation)
- GitHub (source + Actions)
- Claude API / Claude Code (AI runtime)
- Probot/Settings (governance-as-code reconciler, per ADR-2026-03)
- pre-commit, pytest, oxlint, wrangler, railway CLI, litestream CLI, gh CLI (dev tooling)

Anything not on this list needs a rulebook pass.

## Examples of decisions this rule would have changed

- **Session 29**: I proposed Litestream + Cloudflare R2 for telemetry DR. Cost: new vendor, new credentials, new operational surface. Would have been caught — no "real problem it solves today" for internal observability at ~1k events/day.
- **Session 29**: I suggested Sentry for error tracking "because production systems have errors." Would have been caught — pattern-matching, not stakeholder need.
- **Session 30 (governance)**: I referenced Grafana Cloud, Honeycomb, Datadog, Axiom, PostHog, Langfuse as alternatives. Would have been immediately deprioritized in favor of "build it on Supabase."

## Related

- ADR-2026-03 (governance as code) — canonical structure for what we DO install
- `feedback_simple_thing.md` in user memory — the complement: "for internal observability, choose the simple thing"
- `feedback_ai_velocity.md` — the tension: AI speed doesn't equal AI scope. This rule enforces the boundary.
- `policies/software-approved.md` — maintained list of green-lit software (to be created as companion)

## Consequences if violated

- Wasted credentials / half-configured services that leak cost
- Stakeholder trust erosion when software bills show up they didn't approve
- Dependency sprawl that future-Daniel has to untangle
- Pattern drift: every skipped consultation makes the next one easier to skip

## Enforcement

Primarily honor-based within sessions. Secondarily: any proposal that names software should be caught by Daniel or a reviewing agent and redirected here. Long-term: a pre-commit / CI check that scans proposals and new `package.json` / `pyproject.toml` / `requirements.txt` entries for unapproved packages and blocks the commit — but that's a future hardening, not a today requirement.

