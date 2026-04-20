---
id: "GUARD-004"
type: "guardrail"
title: "GR-PROD-001 \u2014 No ad-hoc scripts against production databases or APIs"
status: "active"
date: "2026-04-20"
---

All data loading, schema changes, and extraction MUST go through the production system (data-daemon for extraction, cerebro-migrations for DDL, npm run migrate for applying). Never run ad-hoc Python scripts, raw psql, or one-off loaders against Supabase.

If the production system is broken, fix it. Don't work around it.

Origin: Session 34 — loaded 28K records via ad-hoc script because data-daemon deploy was broken. Data had no provenance, no job tracking, no retry capability. Daniel: "WHY THE HELL WOULD I WANT YOU TO ADHOC FIX THIS"
