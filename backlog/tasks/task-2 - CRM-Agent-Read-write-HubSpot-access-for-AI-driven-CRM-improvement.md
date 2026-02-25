---
id: TASK-2
title: 'CRM Agent: Read-write HubSpot access for AI-driven CRM improvement'
status: To Do
assignee:
  - Daniel
created_date: '2026-02-25 07:49'
labels:
  - hubspot
  - ai-agent
  - future
  - crm-automation
dependencies:
  - TASK-1
references:
  - notes/2026-02-24_teams_michael_daniel.md
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Future project: Give a Claude agent expanded read-write access to HubSpot CRM to improve data quality, organization, and automation. Michael expressed interest in "Claude helping make the CRM more efficient" and "automation" (Teams chat, Feb 24).

This is deliberately sequenced AFTER the read-only data extraction work (TASK-1 tree) is proven safe. The approach:

1. First prove read-only PAK works safely (current TASK-1 work)
2. Then design a separate read-write Private App or PAK with appropriate scopes
3. Build an agent that can clean up contacts, normalize company data, suggest deal stage transitions, automate follow-ups, etc.
4. Human-in-the-loop approval for any destructive or bulk changes

This aligns with HubSpot's new MCP remote server (beta) which Daniel noticed on login — potential native integration path for Claude.

Key guardrails:
- Separate credential from read-only extraction key
- Audit log of all write operations
- Approval workflow for bulk changes
- Rollback capability for any modifications
- Never modify deals/pipeline without human approval
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Read-write Private App or PAK created with scoped write permissions
- [ ] #2 Agent can read, normalize, and suggest CRM data improvements
- [ ] #3 Human-in-the-loop approval for all write operations
- [ ] #4 Audit log captures every modification with before/after state
- [ ] #5 Rollback mechanism tested for bulk operations
- [ ] #6 Michael approves the agent's access scope before go-live
<!-- AC:END -->
