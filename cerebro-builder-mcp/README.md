# cerebro-builder

The mayor. Holds the mission, knows the topology, delegates to child MCPs.

## Why

`cerebro-github` handles PR ceremony. `railguey` handles deploys. `wrike` handles stakeholders. But nobody held the *mission* — the thing that ties all the children together. Session 22 proved this: 8 hours of infrastructure work while the Sage pipeline (what Michael pays for) sat untouched. The agent was productive but not aligned.

cerebro-builder is the orchestrator that checks every piece of work against the mission before it starts, and orchestrates the full change lifecycle across children.

## Children

| MCP | Domain | What it does |
|-----|--------|-------------|
| `cerebro-github` | GitHub | PR ceremony: issues, PRs, CI, merge, bulk ops |
| `railguey` | Railway | Deploy status, logs, redeploy, variables |
| `cerebro-vault` | Supabase | Secrets management |
| `wrike` | Stakeholders | Executive visibility for Michael and Alex |
| `rhea` | Reasoning | Adversarial challenges at decision points |

## Tools

| Tool | What it does |
|------|-------------|
| `check_mission` | Is this task advancing the current milestone? Flags drift, requires Rhea for infrastructure work. |
| `get_mission` | Full mission status: milestones, progress, guardrails, drift warning. |
| `get_lifecycle` | The 12-step change lifecycle and which child handles each step. |
| `ship_to_staging` | Merge PR → wait for deploy → verify via railguey. |
| `ship_to_production` | Requires Rhea decision. Orchestrates develop→main promotion. |

## The Mission

> Get real Sage financial data onto the Cerebro dashboard so Michael and Alex can see their business on Monday morning.

**North star:** Alex's Greenmark_Metrics spreadsheet — populated with real numbers, not mocks.

## Install

```bash
pip install -e .
claude mcp add --scope user cerebro-builder -- cerebro-builder serve
```
