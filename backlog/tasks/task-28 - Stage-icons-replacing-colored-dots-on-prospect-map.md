---
id: TASK-28
title: Stage icons replacing colored dots on prospect map
status: Done
assignee: []
created_date: '2026-02-27 00:28'
labels:
  - cerebro
  - prospect-map
  - ux
milestone: Cerebro — Prospect Map
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replaced colored dot indicators with lucide icons for each opportunity stage. Icons: CalendarCheck (Appt Scheduled), UserCheck (Qualified), Send (Proposal Sent), Scale (Negotiation), CircleCheckBig (Closed Won), CircleX (Closed Lost), Building2 (Customer). Applied to legend, company cards, and detail panel.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added STAGE_ICONS map and StageIcon component to map/page.tsx. Each stage has a distinct lucide icon colored by STAGE_COLORS. Legend, company cards, and detail panel all use icons instead of colored dots.
<!-- SECTION:FINAL_SUMMARY:END -->
