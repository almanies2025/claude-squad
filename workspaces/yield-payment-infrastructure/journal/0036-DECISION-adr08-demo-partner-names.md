---
type: DECISION
date: 2026-05-01
author: agent
session_id: current
project: yield-payment-infrastructure
topic: ADR-08: Demo partners renamed to remove false partnership implication
phase: implement
tags: [adr-08, demo-data, partner-names, sprint-1, false-partnership]
---

## Decision

Seeded demo partner names changed from real-sounding institutions (Celtic Bank, BlueRidge Credit Union, Coastal Community Bank) to clearly fictional names (Demo Partner A, Demo Partner B, Demo Partner C).

## Why

Celtic Bank, BlueRidge Credit Union, and Coastal Community Bank are plausible fictional archetypes used for demo purposes. However, real bank names in a dashboard imply active partnerships that do not exist. If shown to real prospects, this creates false confidence in FloatYield's existing bank relationships.

The original names were chosen to make the demo look realistic. The cost was misrepresentation risk. The fix is to make the demo look clearly fictional.

## Implementation

**Database seed** (`backend/app/main.py:init_db`):
```python
'Demo Partner A' (was: Celtic Bank)
'Demo Partner B' (was: BlueRidge Credit Union)
'Demo Partner C' (was: Coastal Community Bank)
```

**Note added**: `DEMO ONLY, not live partners`

**UI** (`apps/web/app/page.tsx`):
- Demo disclosure banner at top of dashboard: "DEMO MODE — All data is synthetic. No live bank accounts or yield data are connected."

## Consequences

- Internal demos look slightly less polished (obviously fictional names)
- False partnership implication removed
- Safe to show to external prospects without legal risk

## For Discussion

- Should we use more descriptive fictional names (e.g., "Regional Bank Alpha", "Credit Union Beta") for slightly more realistic demos while remaining clearly non-real?
