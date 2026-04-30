# FX Settlement Lock — Product Brief

## Product Name

**FX Settlement Lock Analyzer** (working title)

## Product Type

Multi-CBDC atomic settlement analysis tool / decision-support system for central bank and correspondent bank treasury operators.

## Core Capability

Simulates and visualizes multi-currency atomic settlement paths in mBridge-style multi-party networks. Identifies which currency pairs can settle atomically vs. which dead-lock due to missing Nostro pre-funding relationships. Proves why CNY dominates mBridge volume structurally.

## Current State

Single Python simulation file (`fx_settlement_lock.py`) demonstrating 6 scenarios across a 4-party mBridge network (PBOC · HKMA · CBUAE · BOT). Well-structured, executable, with clear thesis documentation.

## Source Material

- `fx_settlement_lock.py` — 485-line simulation
- Commit: `d5d0709 feat(mbridge): FX Settlement Lock simulation`
- Key insight: CNY dual-issuance (PBOC + HKMA) creates zero-pre-fund bridge path; every other currency pair requires absent correspondent pre-funding

## Product Thesis

The simulation proves a structural (not policy-driven) CNY dominance in cross-border multi-currency settlement. This is valuable because:

1. Central banks running mBridge pilots need to understand settlement path constraints
2. Correspondent banks need to know which currency corridors are viable vs. deadlocked
3. BIS/MTAs need evidence for why a neutral numeraire token is architecturally necessary

## Target Buyers

1. **Central bank treasury desks** (PBOC, HKMA, CBUAE, BOT) — understand their own settlement constraints
2. **Correspondent banks** operating in RMB-internationalized corridors
3. **BIS / Market Transaction Architects** building next-gen settlement infrastructure
4. **Academic researchers** studying CBDC interoperability and settlement finality

## Known Unknowns

- Is there a market beyond simulation? What does "product" actually mean here?
- Who pays? Central banks don't buy software the way startups do
- Is the output a web app? An API? A consulting deliverable? A research paper tool?
- What's the monetization model?
- Is there IP (mBridge is a BIS project)?

## Blocking Questions

1. What is the actual product format — simulation tool, API, consulting deliverable, or something else?
2. Who is the actual buyer — central bank technologist, correspondent bank treasury, BIS working group?
3. What problem does it solve for the buyer — internal analysis, external advocacy, protocol design?
4. Is there existing competition — Capital Markets , Chord, SETNA, or just in-house tools?
5. What's the commercial model — open-source, SaaS, consulting, research partnership?
