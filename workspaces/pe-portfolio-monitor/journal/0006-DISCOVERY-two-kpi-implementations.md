---
type: DISCOVERY
date: 2026-04-20
created_at: 2026-04-20T00:00:00Z
author: agent
session_id: redteam-round-1
session_turn: 2
project: pe-portfolio-monitor
topic: Two KPI implementations existed — csv_processor and kpi_engine had different formulas
phase: redteam
tags: [kpi-engine, csv-processor, formula-divergence]
---

## Summary

Two separate KPI computation implementations existed in the codebase:

1. `csv_processor._upsert_metrics()` — inline formulas, used by the CSV ingestion path
2. `kpi_engine.compute_period_metrics()` — separate module, never called

The `csv_processor` computes 14 KPIs (revenue_net, gross_profit, gross_margin_pct, ebitda, ebitda_margin_pct, cogs_total, opex_total, dso, dio, dpo, working_capital, cash_balance, net_debt, operating_cash_flow). The `kpi_engine` listed 18 KPIs in KPI_SOURCE_ACCOUNTS but only computed the same core set — the extra 4 (YoY%, MoM%, ARR, NRR) were never implemented anywhere.

## Key Finding: EBITDA D&A Add-Back

The original `kpi_engine` formula was: `ebitda = gross_profit - opex_total` — **missing the D&A add-back**. This was caught during unit testing and fixed. The csv_processor already had the correct formula: D&A is included as a component that gets added back to compute true EBITDA.

## Action Taken

- Deleted orphaned kpi_engine.py
- Fixed EBITDA formula in csv_processor's \_upsert_metrics to include D&A (depreciation + amortization + da_other)
- Unit tests verify: gross_profit=40, opex=20, D&A=7 → EBITDA=27

## For Discussion

1. Should kpi_engine be restored as the authoritative computation module with the csv_processor calling into it, so there's one canonical formula per KPI?
2. The 4 missing KPIs (YoY%, MoM%, ARR, NRR, logo churn%, FTE) require period-over-period data — should they be added to csv_processor's \_upsert_metrics or implemented as a separate post-processing step?
