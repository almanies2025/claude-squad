---
type: GAP
date: 2026-04-30
created_at: 2026-04-30T00:00:00Z
author: agent
session_id: deep-analysis-session
session_turn: 2
project: mbridge-redteam
topic: Simulation uses entirely fictional data — no path to real mBridge transaction data
phase: redteam
tags: [data-gap, mbridge, settlement-data, simulation, product-viability]
---

## Gap

The FX Settlement Lock simulation uses entirely fictional Nostro balances (CBUAE: CNY 1000.0, PBOC: AED 1000.0) and fictional FX rates (CNY:AED 2:1, THB:AED 37:1). There is no identified source for real mBridge settlement data, and no pathway to obtaining it.

**Why this is critical**:

1. **A product without real data is a research toy**: Central bank treasury directors and correspondent bank analysts will immediately recognize the fictional data and dismiss the product.

2. **No empirical validation possible**: The simulation's settlement path predictions cannot be validated against actual mBridge behavior without real transaction data. The product cannot demonstrate accuracy.

3. **Calibration impossible**: Real Nostro management involves billions in daily flows with complex replenishment cycles. The 1000-unit fictional balances are not just wrong — they are orders of magnitude off from real correspondent banking volumes.

4. **No data partnership identified**: The product brief does not identify any mBridge participant willing to share transaction data. Without a data partnership, the product cannot move beyond a simulation.

**What the product actually has**: A rules engine that models settlement constraints. This is architecturally sound but empirically empty without data.

## For Discussion

- Is there any publicly available mBridge transaction data? BIS publishes aggregate statistics, but transaction-level data is not public. What is the realistic path to obtaining it?
- If real data is unavailable, should the product pivot to a consulting/research positioning rather than a commercial analytics product?
- Could the simulation be calibrated against BIS aggregate statistics as a minimum viable validation? What would that prove or disprove?
- Is it ethical to sell a product that uses fictional data as if it represents real settlement behavior?
