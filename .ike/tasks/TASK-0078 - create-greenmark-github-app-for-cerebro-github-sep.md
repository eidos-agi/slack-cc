---
id: TASK-0078
title: Create Greenmark GitHub App for cerebro-github — separate rate limit bucket
status: To Do
created: '2026-04-23'
priority: high
tags:
  - cerebro-github
  - rate-limits
  - infrastructure
acceptance-criteria:
  - GitHub App created and installed on greenmark-waste-solutions org
  - cerebro-github uses app installation tokens for all API calls
  - GraphQL rate limit bucket is separate from Daniel's personal PAT
  - rate_status shows app installation limits, not user limits
---
GraphQL rate limit (5000/hr) is shared across ALL tools using dshanklin-bv PAT — every Claude session, every MCP, every gh CLI call. We've been repeatedly exhausted (682→0 in under 5 minutes this session, 4th time hitting 0 in 2 days).

Solution: Create a GitHub App for the Greenmark org. cerebro-github authenticates as the app installation instead of Daniel's PAT.

Benefits:
- Separate 5,000-12,500/hr bucket (scales with org size)
- No cross-session starvation
- Installation tokens are scoped to the org's repos (least privilege)
- ETags for conditional requests (304 doesn't count against limit)

Implementation:
1. Create GitHub App in greenmark-waste-solutions org
2. Grant repo, issues, PRs, checks, actions permissions
3. Generate private key, store in cerebro-vault or Railway env
4. Update cerebro-github MCP to authenticate as app installation
5. Keep PAT as fallback for user-scoped operations (if any)
