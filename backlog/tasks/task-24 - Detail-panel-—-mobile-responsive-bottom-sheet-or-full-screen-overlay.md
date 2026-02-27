---
id: TASK-24
title: Detail panel — mobile responsive (bottom sheet or full-screen overlay)
status: To Do
assignee: []
created_date: '2026-02-27 00:28'
labels:
  - cerebro
  - layout
  - mobile
milestone: Cerebro — UX Polish
dependencies: []
references:
  - cerebro/components/detail-panel.tsx
  - cerebro/app/dashboard/layout.tsx
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The layout-level detail panel currently compresses main content on all screen sizes. On mobile (< lg breakpoint), it should switch to either:

1. **Bottom sheet** — slides up from bottom, half-screen, swipeable
2. **Full-screen overlay** — takes over the viewport with a back button

Currently the panel is 380px wide which doesn't work on mobile viewports. Need responsive behavior that detects breakpoint and renders appropriately.

Consider: shadcn Drawer component (Vaul-based) for mobile, keep the current push layout for desktop.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Detail panel renders as push sidebar on desktop (lg+)
- [ ] #2 Detail panel renders as bottom sheet or overlay on mobile (<lg)
- [ ] #3 Smooth transitions on both modes
- [ ] #4 Close/dismiss works on both modes
- [ ] #5 No content clipping on small screens
<!-- AC:END -->
