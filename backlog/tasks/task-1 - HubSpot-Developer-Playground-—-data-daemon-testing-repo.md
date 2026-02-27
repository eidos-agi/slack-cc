---
id: TASK-1
title: HubSpot Developer Playground — data-daemon-testing repo
status: Done
assignee:
  - Daniel
created_date: '2026-02-24 21:35'
updated_date: '2026-02-26 08:43'
labels:
  - hubspot
  - data-integration
  - infrastructure
dependencies: []
references:
  - notes/2026-02-24_153037_0049.md
  - notes/2026-02-24_152936_1271.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Set up a new `data-daemon-testing` repo under greenmark-waste-solutions as a playground for testing real HubSpot data. Daniel has logged into HubSpot Developer Portal (account: Greenmark Waste Solutions, ID 244562652) and confirmed access. The goal is to install the HubSpot CLI, authenticate against the Greenmark account, explore what real data is available, and determine the best integration path for data-daemon (custom API connector vs HubSpot's MCP server beta).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 data-daemon-testing repo exists in greenmark-waste-solutions GitHub org
- [x] #2 HubSpot CLI installed and authenticated against Greenmark account
- [x] #3 Can query real HubSpot data (contacts, deals, companies) via CLI
- [ ] #4 Decision documented: custom API connector vs HubSpot MCP server for data-daemon integration
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24 22:40: Exploration phase complete. 7 of 18 subtasks done. Key outcome: REST API patterns for all CRM extraction proven. Remaining work: expand PAK scopes (1.12), seed test data (1.13/1.14), custom properties (1.15), write commands (1.16), connector design (1.17). Private App evaluation (1.7) deferred until after scope expansion.

2026-02-25: Updated status to In Progress. AC #1-3 met (repo exists, CLI authed, can query CRM via REST API). AC #4 partially met — MCP server deferred, REST API confirmed as integration path. 8 of 17 subtasks done. Next priorities: expand test PAK scopes (1.12), then seed data (1.13/1.14), then connector design (1.17).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
HubSpot Developer Playground phase complete. Sandbox fully explored: 36 scopes mapped, REST API wrapper (hs-api.sh) built with 9 commands, data patterns proven. Daniel now has admin access to production HubSpot (granted by Michael, Feb 25). Moving to production security review + connector build.
<!-- SECTION:FINAL_SUMMARY:END -->
