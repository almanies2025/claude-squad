---
type: GAP
date: 2026-04-20
created_at: 2026-04-20T00:00:00Z
author: agent
session_id: redteam-round-1
session_turn: 1
project: pe-portfolio-monitor
topic: kpi_engine.py orphaned — compute_period_metrics never called
phase: redteam
tags: [dead-code, architecture, kpi-engine]
---

## Summary

`app/domain/kpi_engine.py` contained a `compute_period_metrics()` function (81-316 lines) that was **never called from any route or data ingestion path**. The actual KPI computation lived in `csv_processor._upsert_metrics()` which duplicated the logic.

## Root Cause

The kpi_engine module was built as a standalone computation engine but the CSV processor was implemented separately and reimplemented the same KPI formulas inline.

## Fix Applied

Deleted `app/domain/kpi_engine.py` entirely. All KPI computation now lives in `csv_processor._upsert_metrics()` which is the actual ingestion path.

## For Discussion

1. If kpi_engine was meant to be the canonical computation layer called from multiple places (CSV, QB connector, manual recalculation), should it be restored as a shared module that csv_processor calls? Or is inline computation acceptable for v1?
2. The KPI_SOURCE_ACCOUNTS mapping in kpi_engine is more complete than what csv_processor uses — should the csv_processor be refactored to call a unified compute function rather than inline formulas?
