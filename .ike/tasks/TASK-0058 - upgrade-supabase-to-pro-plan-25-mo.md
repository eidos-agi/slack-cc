---
id: TASK-0058
title: Upgrade Supabase to Pro plan ($25/mo)
status: To Do
created: '2026-04-18'
priority: high
tags:
  - supabase
  - infrastructure
definition-of-done:
  - Supabase plan upgraded to Pro in dashboard
  - Confirm 8GB disk available
  - REFRESH MATERIALIZED VIEW CONCURRENTLY sage_silver.gl_entries succeeds (proves disk
  headroom)
---
Free tier is 500MB. With 1.38M GL entries in sage_bronze plus silver materialized views, we're at the limit. Adding Navusoft + Fleetio data will double the load. Pro plan gives 8GB — enough headroom for the next 6+ months of vendor integrations. $25/mo. Daniel does this in the Supabase dashboard (Billing → Upgrade).
