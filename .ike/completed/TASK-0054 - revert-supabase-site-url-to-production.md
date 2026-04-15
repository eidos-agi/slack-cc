---
id: TASK-0054
title: REVERT SUPABASE SITE URL TO PRODUCTION
status: Done
created: '2026-04-14'
priority: high
tags:
  - oauth
  - supabase
  - revert-required
  - production-safety
acceptance-criteria:
  - Supabase Site URL is back to https://cerebro.greenmark.jettaintelligence.com
  - Preview Authorization URL in Supabase dashboard shows the production URL again
  - cockpit-status no longer shows this task as open
updated: '2026-04-14'
---
Supabase OAuth Server Site URL was temporarily changed to https://staging-cerebro-greenmark.jettaintelligence.com to test the /oauth/consent page end-to-end via claude.ai.

Must be reverted to https://cerebro.greenmark.jettaintelligence.com after testing is complete. If left pointed at staging, any production user attempting an OAuth flow will get redirected to staging's consent page, which is confusing (not data-losing, but wrong UX).

Supabase dashboard path: Authentication → OAuth Server → Site URL field.

**Completion notes:** Not needed — we merged develop → main (PR #56) instead of changing Supabase Site URL, because the Site URL was grayed out in the OAuth Server panel (only editable via URL Configuration, which affects all Auth-related redirects). Production got the /oauth/consent page deployed from the PR. Site URL was never changed, so nothing to revert.
