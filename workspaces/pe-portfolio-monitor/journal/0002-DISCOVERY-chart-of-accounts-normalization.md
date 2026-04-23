---
type: DISCOVERY
date: 2026-04-20
created_at: 2026-04-20T00:00:00Z
author: agent
session_id: pe-portfolio-monitor
session_turn: 1
project: pe-portfolio-monitor
topic: Chart-of-accounts normalization is ~40-50% of engineering cost and the true product moat
phase: analyze
tags: [data-model, erp, normalization, moat, engineering]
---

# Chart-of-Accounts Normalization Is the Real Product

The ERP API integrations (QuickBooks, NetSuite, Sage Intacct) are a solved engineering problem. Rutter and Codat have already built the connectors. The **true technical difficulty** — and the true moat — is normalizing heterogeneous charts of accounts across 15 portfolio companies into a single canonical KPI schema.

Every portco's chart of accounts is different:

- Company A's `40000 Product Revenue` = Company B's `4100 Subscription Income` + `4050 Usage Revenue` = Company C's `Total Sales` from a CSV
- "EBITDA" means different things to different PE firms depending on which addbacks they include
- Companies re-charter their accounts; July 2025 COA is different from January 2026

This is ~40–50% of the product's actual engineering cost. It is also where incumbents (iLEVEL, Allvue) have not solved the problem — they still use request-based data collection precisely because automated normalization is hard.

## The Two-Layer Solution

The data model uses a strict two-layer approach:

1. **Raw layer**: ERP data preserved exactly as received, never modified
2. **Canonical layer**: everything consumer-facing reads from here

The bridge is a declarative `AccountMapping` config with effective dates — human-assisted at first onboarding, then automated. Changes to COA only require updating the mapping config, not the downstream code.

## Why This Is the Moat

Once a PE firm has 15 portcos mapped and validated over 6 months, switching to a competitor requires re-mapping every account at every company. The mapping config IS the accumulated institutional knowledge. Switching cost is high not because of lock-in mechanics but because the work cannot be easily replicated.

## For Discussion

1. The mapping config is human-assisted at first onboarding — this creates an onboarding bottleneck. Is the right model to hire PE-industry-experienced "onboarding specialists" (ex-controller types who can read a NetSuite COA and map it in hours), or to build a UI where the portco CFO does their own mapping under guided templates? The former is faster but doesn't scale; the latter scales but adds friction.

2. If the account mapping is the moat, what prevents a large PE firm from building their own mapping layer in Power BI and using Rutter for ERP connectivity? The answer should drive pricing and feature decisions.

3. "Confidence" on each metric (high/medium/low based on mapping quality) is an honest signal to PE partners. But a partner who sees `medium` confidence on EBITDA may trust the number less — potentially defeating the product's purpose. How should confidence be presented to avoid creating doubt rather than transparency?
