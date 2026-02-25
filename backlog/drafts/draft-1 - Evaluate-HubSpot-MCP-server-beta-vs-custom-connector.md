---
id: DRAFT-1
title: Evaluate HubSpot MCP server beta vs custom connector
status: Draft
assignee:
  - Daniel
created_date: '2026-02-24 21:35'
updated_date: '2026-02-24 21:39'
labels:
  - hubspot
  - data-integration
  - architecture
dependencies:
  - TASK-1.2
parent_task_id: TASK-1
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
HubSpot has a remote MCP server in beta: "Bring HubSpot context to the tools you already use. Build secure, custom integrations powered by your HubSpot data." This could potentially shortcut a lot of the data-daemon HubSpot connector work. Evaluate: (1) What does the MCP server provide? (2) Can it replace or supplement our custom API connector? (3) What are the limitations? (4) Is it production-ready enough for Cerebro? Document the decision with pros/cons for both approaches.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 MCP server beta capabilities documented
- [ ] #2 Comparison: MCP server vs custom API connector (coverage, reliability, maintenance)
- [ ] #3 Decision recorded in decisions/ with reasoning
- [ ] #4 If MCP server viable, prototype integration tested
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: Daniel says skip MCP server beta for now. Focus on CLI usage with Claude Code skills to drive the HubSpot CLI directly. MCP evaluation deferred — revisit later if CLI approach hits limits.
<!-- SECTION:NOTES:END -->
