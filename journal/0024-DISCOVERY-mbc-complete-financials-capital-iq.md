---
type: DISCOVERY
date: 2026-04-24
created_at: 2026-04-24T00:00:00Z
author: co-authored
session_id: b00eb2df-676d-464d-a10e-68794f3e0b5d
session_turn: unknown
project: mbc-valuation
topic: MBC Group complete financials from Capital IQ Excel + DCF model built
phase: analyze
tags: [dcf, wacc, fcf, comparable-multiples, mbc-group, capital-iq]
---

# DISCOVERY: MBC Group complete financials sourced from Capital IQ; full DCF model built

**Date**: 2026-04-24

## Context

The user is an MBA student learning company valuation. They have access to Capital IQ and a local Excel file (`MBC Group SASE 4072 Financials.xls`) containing standardized Capital IQ data. The annual report PDF had multi-column formatting that defeated text extraction for primary financial statements. The Excel file solved this completely.

## Finding: Capital IQ Excel has complete structured financials

The file at `C:\Users\User\Desktop\المستندات\applied finance\MBC Group SASE 4072 Financials.xls` contains 14 sheets:

| Sheet             | Contents                                                                      |
| ----------------- | ----------------------------------------------------------------------------- |
| Income Statement  | FY2020–FY2025 annual, standardized                                            |
| Balance Sheet     | FY2020–FY2025 annual                                                          |
| Cash Flow         | Full indirect method cash flow                                                |
| Key Stats         | Revenue, EBITDA, EBIT, Net Income, EPS + consensus forecasts FY2026E, FY2027E |
| Multiples         | Quarterly TEV/EBITDA, TEV/Revenue, P/E (LTM and NTM)                          |
| Ratios            | ROE, ROA, margins, turnover, liquidity, leverage                              |
| Capital Structure | Debt schedule, equity issuance                                                |
| Segments          | Segment revenue and results                                                   |

**Critical data points extracted:**

- **Revenue FY2020–2025**: 2,318 → 2,845 → 3,489 → 2,559 (restated) → 4,185 → 5,379 SAR M
- **EBITDA FY2025**: SAR 266.7M (5.0% margin) — first full year of positive EBITDA
- **CapEx FY2025**: SAR 221.4M (4.1% of revenue)
- **D&A FY2025**: SAR 123.1M (2.3% of revenue)
- **Total assets FY2025**: SAR 8,535.5M | Total liabilities: SAR 3,915.3M
- **Cash: SAR 1,316.7M | Debt: SAR 121.2M (net cash ~SAR 1.2B)**
- **TEV: SAR 7,683.4M | Market cap: SAR 8,844.5M**
- **Capital IQ consensus FY2026E**: Revenue 5,515.8M (+2.3%), EBITDA 692.8M (12.6% margin)
- **Capital IQ consensus FY2027E**: Revenue 6,087.6M (+10.4%), EBITDA 934.0M (15.3% margin)

## Finding: FCF was negative in FY2025 despite positive EBITDA

Operating cash flow: SAR 175.3M (positive)
CapEx: SAR 221.4M
Levered FCF: SAR −180.7M

Root cause: Large working capital swings — AR increased SAR 550M and inventory decreased SAR 917M (content production cycle). The company also had one-time items. Underlying operations generated cash, but working capital consumed it.

**For DCF purposes**: FCF should be normalized by averaging multiple years or adjusting for working capital. Pure EBITDA-to-FCFF conversion is misleading for this company.

## Finding: No reliable beta — WACC is the model's biggest weakness

4072.SR has only ~2 years of public trading history. Yahoo Finance shows no beta. Capital IQ has no disclosed beta. This makes WACC estimation essentially subjective.

**Three scenarios used**:

- Bear: WACC = 12%
- Base: WACC = 10% (1.0x beta, EM ERP 5.5%, risk-free 4.75%)
- Bull: WACC = 8%

## DCF Model Results

Built 5-year DCF (FY2026–FY2030) with:

- Revenue from Capital IQ consensus for FY2026–2027, then fading to Saudi nominal GDP growth by FY2030
- EBITDA margin expanding from 5.0% (FY2025) to 18.0% (FY2030) — consistent with streaming scale economics
- Terminal value via Gordon Growth model

**Valuation outputs:**

| Scenario | WACC    | Terminal g | Implied Share Price |
| -------- | ------- | ---------- | ------------------- |
| Bear     | 12%     | 4.5%       | SAR 37.7            |
| **Base** | **10%** | **4.5%**   | **SAR 48.8**        |
| Bull     | 8%      | 4.5%       | SAR 112.4           |

**Current market price: SAR 26.26** → base case implies 85.8% upside.

## Key Tension Discovered

The market prices MBC at ~11x NTM EBITDA (from Capital IQ multiples: 11.21x on FY2026E EBITDA of 692.8). Our DCF base case implies an EV/EBITDA of ~26x on FY2026E — 2.3x what the market currently assigns.

This means the market either:

1. Doesn't believe the EBITDA margin expansion story (12.6% → 15.3% in one year seems aggressive)
2. Is pricing this as a growth stock but the multiple compression is already happening
3. Is ignoring FY2026E estimates as too optimistic

## Implications for Learning

1. **Data sourcing hierarchy**: Excel/structured data > PDF text extraction; Capital IQ is the gold standard for this work
2. **FCF ≠ EBITDA**: Companies in growth phase can have negative FCF despite positive EBITDA — normalization matters
3. **WACC is not academic when beta is unavailable**: The sensitivity table is the real output, not a point estimate
4. **DCF is a story**: The numbers require a narrative about streaming margins, Vision 2030, and pan-Arab market growth

## For Discussion

1. The market assigns ~11x NTM EBITDA while our DCF implies 26x on FY2026E. If you were the analyst, which assumptions would you defend — revenue growth, margin expansion, or WACC — to justify the gap?

2. MBC's FY2025 negative FCF (SAR −180.7M) was driven by a SAR 550M increase in accounts receivable. Is this a sign of aggressive revenue recognition, a timing issue from rapid growth, or a structural problem with collection? How should it affect our FCF normalization?

3. The company has net cash of ~SAR 1.2B. In a liquidation scenario (bear case), does net cash meaningfully support the equity value, or is the balance sheet mostly non-deployment-ready content/PP&E?
