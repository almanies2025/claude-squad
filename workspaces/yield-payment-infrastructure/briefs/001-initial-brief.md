# Yield-Bearing Payment Infrastructure — Product Brief

## Product Name

**FloatYield Infrastructure** (working title)

## Product Type

B2B payments infrastructure platform — white-label yield-distribution engine for banks and fintechs

## Core Capability

API platform that enables banks and fintechs to offer interest-bearing payment accounts by passing through Treasury reserve yield to their customers. The platform handles reserve management, yield calculation, distribution accounting, and regulatory reporting.

## The Problem It Solves

Currently:

- Commercial banks pay ~0% interest on checking/transaction balances
- Stablecoin issuers (USDC, Tether) earn ~4.5% on Treasury reserves
- Customers receive 0% on payment balances
- The seigniorage spread is captured entirely by the issuer

With FloatYield:

- Bank/fintech integrates via API
- Customer balances earn ~3-4% yield
- Platform manages reserve assets and yield distribution
- Bank/fintech earns the spread between reserve yield (4.5%) and customer yield (3-4%)
- FloatYield earns a platform fee per account per month

## Business Model

| Party                | Earns                                  |
| -------------------- | -------------------------------------- |
| End customer         | 3-4% on transaction balances           |
| Bank/Fintech partner | 0.5-1% spread                          |
| FloatYield platform  | 0.1-0.3% platform fee on managed float |

## Target Buyers (Course Assignment Framing)

Primary: Commercial banks and neobanks (US, EU)
Secondary: Payment processors (Stripe, Adyen) who want to offer yield on balances
Tertiary: Fintech infrastructure companies (Airwallex, Wise, Nium)

## Regulatory Framework

**United States:**

- State-by-state money transmitter licensing OR
- Sponsor Bank model: partner with federally chartered bank (Silvergate, Cross River, etc.)
- FDIC insurance considerations for sponsored accounts
- CFPB and state banking regulators

**European Union:**

- MiCA (Markets in Crypto-Assets Regulation) — unified EU framework
- EBA guidelines on electronic money
- PSD2 payment institution license

**Key regulatory distinction:**

- Payment account (paying interest): generally permissible
- Deposits (taking custody of funds): requires bank charter
- The Sponsor Bank model is the most viable path — the bank holds the charter, FloatYield operates as the technology/ops layer

## Course Assignment Deliverables (Market-Ready Standard)

1. Product brief and concept document
2. Regulatory analysis (US + EU, with geographic recommendation)
3. Market analysis (TAM, SAM, SOM)
4. Go-to-market strategy
5. Financial model (unit economics, pricing)
6. Competitive landscape
7. Risk register
8. Product walkthrough / user flow

## Key Assumptions

- Treasury yield assumed at 4.5% (current market rate)
- Customer yield at 3.5%; partner spread at 0.5-1%
- Target: 100,000 accounts in year 3
- Sponsor Bank partnership secured in Year 1

## Status

Concept stage — full COC analysis to be completed.
