# US Regulatory Framework: Yield-Bearing Payment Infrastructure

**Date:** April 30, 2026
**Analysis Type:** Regulatory Pathway Analysis
**Complexity Score:** Complex (22/30)

---

## Executive Summary

FloatYield's regulatory pathway hinges on a single strategic choice: pursue state-by-state money transmitter licensing (cost: $500K-$2M+, timeline: 18-36 months) or partner with a Sponsor Bank (cost: $50K-$200K/year, timeline: 3-6 months). For a B2B platform targeting banks and fintechs, the **Sponsor Bank model is the only viable near-term path**. The critical legal distinction is whether FloatYield's yield-bearing accounts constitute "deposits" (requiring bank charter) or "payment instruments" (requiring money transmitter licenses). Under the Sponsor Bank model, the bank holds the deposits and extends FDIC pass-through insurance, while FloatYield operates as the technology/ service provider under a written agreement.

**Complexity Score:** Complex (22/30) — Governance 6, Legal 9, Strategic 7
**Recommendation:** Partner with a Sponsor Bank. Do not pursue direct licensing unless you have $5M+ and 24 months to burn.

---

## 1. Money Transmitter License (MTL)

### 1.1 Which States Require MTL

A money transmitter license is required when a company transmits money or holds funds on behalf of others. Most states define this broadly. States requiring MTL include:

**Full MTL States (40+ states):**

- California, Texas, Florida, New York, Illinois, Pennsylvania, Ohio, Georgia, North Carolina, Michigan, New Jersey, Virginia, Washington, Arizona, Massachusetts, Tennessee, Indiana, Missouri, Wisconsin, Minnesota, Colorado, Alabama, South Carolina, Louisiana, Kentucky, Oregon, Oklahoma, Connecticut, Utah, Iowa, Nevada, Arkansas, Mississippi, Kansas, New Mexico, Nebraska, West Virginia, Idaho, Hawaii, Maine, New Hampshire, Rhode Island, Vermont, Montana, Wyoming, Alaska, South Dakota, North Dakota

**Exempt or Limited License States:**

- **New York:** Requires BitLicense for crypto; Article 13-B for money transmission. Application cost: $50K-$100K (application fee + bond). Timeline: 12-18 months minimum.
- **Washington, D.C.:** Requires money transmitter license through DC Department of Insurance, Securities and Banking. Similar to NY in complexity.
- **Montana, Wyoming:** Very limited licensing, low costs.
- **South Dakota:** Favorable regulatory environment, no state income tax, dedicated fintech sandbox.

**No State-Level MTL ( federally regulated):**

- **Puerto Rico, US Virgin Islands:** Separate territory regulations.

### 1.2 Application Requirements

Typical MTL application requires:

- Detailed business plan
- Financial statements ($100K-$1M minimum net worth depending on state)
- Background checks for all principals (fingerprints, FBI check)
- Anti-money laundering (AML) program (Bank Secrecy Act compliance)
- Consumer complaint procedures
- Surety bond or letter of credit ($25K-$1M depending on state)

### 1.3 Costs and Timelines

| State        | Application Fee        | Timeline     | Notes                                      |
| ------------ | ---------------------- | ------------ | ------------------------------------------ |
| New York     | $50K-$100K (inc. bond) | 12-18 months | Most rigorous; known for 18+ month reviews |
| California   | $10K-$25K + annual     | 6-12 months  | More predictable than NY                   |
| Texas        | $5K-$10K + annual      | 3-6 months   | MTL via TX Department of Banking           |
| Florida      | $2K-$5K + annual       | 3-6 months   | DFKI (Division of Financial Institutions)  |
| Illinois     | $5K-$10K + annual      | 4-8 months   | IDFPR (Dept. of Financial & Prof. Reg.)    |
| South Dakota | $1K-$3K + annual       | 2-4 months   | Most favorable; fintech sandbox available  |

**Total Cost Estimate (all 50 states):** $500K-$2M+ (application fees, legal counsel, compliance infrastructure, annual renewals)

**Timeline for full US coverage:** 18-36 months minimum.

---

## 2. Sponsor Bank Model

### 2.1 Legal Framework

The Sponsor Bank model allows a fintech (FloatYield) to offer payment/yield accounts by partnering with an FDIC-insured bank. The bank:

1. Holds deposits on its balance sheet
2. Extends FDIC insurance to end users (pass-through)
3. Provides the "bank" legal identity for Reg E, CFPB oversight
4. Maintains the charter and regulatory relationships

FloatYield operates as a:

- **Technology provider** (under a Technology Service Agreement / TSA)
- **Program manager** (under a Program Manager Agreement)
- **Service provider** to the bank

### 2.2 Key Regulatory Requirements

**12 CFR Part 30 (OCC) / 12 CFR Part 225 (Federal Reserve):**

- Bank cannot contract away fiduciary duty
- Bank must exercise "adequate supervision" (heightened expectation for fintech programs)
- Bank's board must approve the program and conduct ongoing oversight

**FDIC Guidance (FIL-29-2020, updated 2023):**

- Bank must conduct due diligence on FloatYield's:
  - AML/BSA compliance program
  - Consumer complaint management
  - Financial condition and viability
  - Ability to comply with consumer protection laws
- Bank must maintain direct contact with customers or ensure FloatYield does so on bank's behalf
- Bank must conduct periodic reviews (at least annually)

**CFPB / Reg E:**

- The bank is responsible for Reg E error resolution and consumer protections
- FloatYield's contract must specify who handles customer complaints
- Bank must have access to books and records

### 2.3 Contract Structure

A typical Sponsor Bank agreement includes:

**1. Program Manager Agreement (PMA) / Bank Partner Agreement:**

- Roles and responsibilities matrix
- Revenue sharing (bank takes 10-30 bps of net interest margin typically)
- Compliance obligations split
- Data rights and ownership
- Termination provisions (30-90 days typical)
- Liability for regulatory violations (typically joint and several)

**2. Technology Service Agreement (TSA):**

- FloatYield provides the tech stack (mobile app, yield calculation, account management)
- Bank licenses its systems integration (core banking connection, FedNow/RTP rails)
- Service level agreements (SLA) with penalties
- IP ownership: FloatYield owns its technology; bank owns customer relationship data

**3. Deposit Agreement (between bank and end customer):**

- Bank is the named issuer
- FDIC disclosures required
- Yield rate disclosure requirements
- Terms and conditions

**4. Addenda:**

- AML/BSA procedures
- Complaint escalation procedures
- Business continuity requirements
- Subcontracting limitations

### 2.4 Known Sponsor Bank Partners

| Fintech        | Sponsor Bank(s)                                             | Structure                         |
| -------------- | ----------------------------------------------------------- | --------------------------------- |
| Greenlight     | Coastal Community Bank (Member FDIC)                        | Consumer-focused debit/yield      |
| Column         | Column Bank, N.A. (FDIC)                                    | Column itself is a bank + fintech |
| Unit           | Pathward (formerly Signature), Celtic Bank, Blue Ridge Bank | BaaS platform                     |
| Treasury Prime | Celtic Bank, Lineage Bank                                   | Bank-as-a-Service                 |
| Stripe         | Goldman Sachs, JPMorgan                                     | Large-scale payment processing    |

---

## 3. FDIC Insurance

### 3.1 Pass-Through Insurance Mechanics

FDIC insurance passes through from the bank to the depositor when:

1. The deposit is held by the bank (not FloatYield)
2. The customer is identified as the beneficial owner
3. The deposit is in an account that evidences the customer's ownership

**Maximum coverage:** $250,000 per depositor, per insured bank, per account ownership category.

### 3.2 Common Structure

```
Customer funds → Bank (deposit on bank's balance sheet) → Bank invests in US Treasuries (reserve assets)
                   ↑
              FDIC insured up to $250K

FloatYield's role: Technology, yield calculation, distribution, reporting
Bank's role: Deposit holder, FDIC conduit, regulatory compliance
```

### 3.3 What Triggers FDIC Loss

- Bank failure (rare but possible)
- Fraud or misrepresentation in the deposit relationship
- Failure to properly title accounts (pass-through fails)

### 3.4 What FDIC Does NOT Cover

- FloatYield's technology failure
- Yield calculation errors
- Fraud by FloatYield employees
- Losses from Treasury reserve investments (market risk)
- Any entity other than the named bank

---

## 4. CFPB and Reg D

### 4.1 Reg D (Reserve Requirements)

**Historical context:** Reg D limited savings account withdrawals to 6 per month (3 by check, 3 by ACH). This was eliminated effective April 24, 2020, by the Fed (Regulation II amendment).

**Current Reg D status:** No restrictions on withdrawal frequency from savings accounts. Banks may choose to impose their own limits but are not required to.

### 4.2 Interest on Transaction Accounts

**12 CFR Part 204 (Reg D) — Payable on Demand:**

- Historically prohibited banks from paying interest on "demand deposits" (checking accounts used for transactions)
- This is why "interest-bearing checking" products historically required workarounds

**Current law:** Banks CAN pay interest on checking/transaction accounts. Reg D's prohibition was removed in 2010 (Dodd-Frank Section 627). The 6-withdrawal limit was removed in 2020.

**Yield products caveat:** A "yield" on a checking account is legally the same as interest. Banks are permitted to offer this.

**Fintech workaround:** Many fintech "checking" products are technically savings accounts or money market deposit accounts to avoid demand deposit regulations, or they partner with banks that have appropriate charter authority.

### 4.3 CFPB Oversight

CFPB has supervisory authority over:

- Banks > $10B assets (direct supervision)
- Nonbanks offering consumer financial products (authority granted by Dodd-Frank)
- Service providers to banks (examination authority)

FloatYield as a B2B platform serving banks may escape direct CFPB supervision if it does not hold itself out to consumers directly. However, the Sponsor Bank will be supervised and may push compliance obligations down.

---

## 5. e-Money vs. Deposit Distinction

### 5.1 Legal Classification

**Deposit (Bank Deposit):**

- Accepted by a bank
- Evidences a debtor-creditor relationship (bank owes depositor money)
- Subject to FDIC insurance when held at FDIC member bank
- Subject to bank regulatory framework (OCC, Fed, FDIC supervision)
- "Deposit" is defined under 12 USC 1813(l)

**Payment Instrument / e-Money:**

- Stored value card, digital wallet balance, prepaid access
- Issued by a non-bank (requires MTL in most states)
- Represents an obligation of the issuer, not a bank deposit
- NOT FDIC insured (unless deposited into a bank account)
- Subject to state money transmitter laws

### 5.2 The Critical Distinction for FloatYield

If FloatYield holds customer funds itself (even temporarily), those funds are likely "payment instruments" requiring MTL.

If the Sponsor Bank holds funds, they are "deposits" and FDIC insured.

**The Hybrid Problem:**

- If FloatYield calculates yield and distributes it, but funds sit at Sponsor Bank: FloatYield is a service provider (good)
- If FloatYield sweeps funds into a Treasury-only reserve that FloatYield controls: FloatYield is holding funds (bad — requires MTL)
- If FloatYield offers "savings" accounts: typically a deposit product

### 5.3 Why This Matters

| Scenario                                                  | Legal Classification      | License Required    |
| --------------------------------------------------------- | ------------------------- | ------------------- |
| Funds at Sponsor Bank, FloatYield is tech provider        | Deposit (bank product)    | None for FloatYield |
| Funds at FloatYield (even "in trust")                     | Payment instrument        | MTL in all states   |
| FloatYield issues its own "account number" linked to bank | Likely payment instrument | MTL                 |
| FloatYield acts as agent of bank                          | Deposit (bank product)    | None                |

---

## 6. Actual Licensing Pathway for FloatYield

### 6.1 Decision Tree

```
Is FloatYield holding customer funds directly?
    YES → MTL required in all 50 states (or find a bank custodian)
    NO → Is FloatYield partnering with a Sponsor Bank?
        YES → No MTL required for FloatYield. Bank holds deposits.
        NO → Must obtain bank charter or MTL.
```

### 6.2 Recommended Path: Sponsor Bank Model

**Phase 1: Bank Partnership (Months 1-6)**

1. Identify 2-3 potential Sponsor Banks (Community banks, Regional banks seeking fintech revenue)
2. Negotiate Program Manager Agreement
3. Bank conducts due diligence on FloatYield (AML, compliance, financials)
4. Bank files required notices with regulators (OCC/Fed if applicable)
5. Launch with single bank partner in 1-2 states initially

**Estimated cost:** $50K-$200K/year (revenue share + compliance support)
**Timeline:** 3-6 months

**Key Sponsor Banks for Fintech Programs:**

- Pathward (formerly Signature Bank) — established BaaS
- Celtic Bank — fintech-friendly
- Blue Ridge Bank — fintech partnerships
- Coastal Community Bank — Greenlight's partner
- Column Bank — built for fintechs

### 6.3 Alternative Path: State MTL (If No Bank Partner)

**If FloatYield cannot find a Sponsor Bank:**

- Apply for MTL in South Dakota first (fastest, cheapest)
- Then apply in: California, Texas, Florida, Illinois, New York
- Full 50-state coverage: 18-36 months, $500K-$2M+

**This path is not recommended for initial launch.**

### 6.4 Additional Licenses/Registrations

**FinCEN (Federal):**

- Money Services Business (MSB) registration with FinCEN (mandatory for MTL holders)
- AML/BSA compliance program required

**State-Level:**

- MTL in states where FloatYield has customers above de minimis thresholds
- Most states have $1K-$5K transaction de minimis before MTL required

**SEC (if applicable):**

- If yield is paid from investment returns and not bank interest: potential securities implications
- Treasury reserve management likely not a security (Treasuries are commodities)

**CFTC (unlikely):**

- Only if engaging in derivatives or futures

---

## 7. Case Studies

### 7.1 Greenlight

**Structure:** Greenlight is a fintech offering debit cards with parental controls and yield. Partner: Coastal Community Bank (Member FDIC).

**Regulatory approach:**

- Coastal Community Bank holds deposits, extends FDIC insurance
- Greenlight operates as program manager / technology provider
- Greenlight does NOT hold customer funds
- Greenlight does NOT have MTL (bank handles Reg E compliance)

**Yield mechanism:** Greenlight pays yield from interchange fees + cash back rewards, not from Treasury investments on customer balances. This avoids investment advisor / securities complications.

**Key lesson:** Greenlight's yield is subsidized (not market-driven). This may not scale for FloatYield's B2B model.

### 7.2 Column

**Structure:** Column Bank, N.A. — Column built its OWN bank charter specifically to serve fintechs. This is the "neo-bank for fintechs" model.

**Regulatory approach:**

- Column obtained a national bank charter (OCC)
- Column is the bank AND the fintech infrastructure
- Column provides FDIC insurance, Reg E compliance, bank services to other fintechs

**Key lesson:** This is the nuclear option — $10M+ in regulatory capital required, 18+ months to charter, significant ongoing regulatory burden. Only viable if FloatYield's long-term strategy is to become a bank.

### 7.3 Treasury Prime

**Structure:** Treasury Prime was a BaaS provider connecting fintechs to bank sponsors (Celtic Bank, Lineage Bank).

**Regulatory approach:**

- Treasury Prime was the "program manager" between fintechs and banks
- They collapsed in 2023 due to regulatory pressure (FDIC and state regulators cracked down on "rent-a-charter" arrangements)

**Key lesson:** The regulatory environment for BaaS tightened significantly after 2022. Sponsor banks now face more scrutiny. FloatYield needs a genuine bank partner, not a BaaS intermediary.

### 7.4 Unit

**Structure:** Unit is a BaaS platform that partners with multiple banks (Pathward, Celtic, Blue Ridge) to offer FDIC-insured accounts.

**Regulatory approach:**

- Unit handles the fintech side compliance and tech
- Bank partners handle deposit insurance, Reg E, bank regulatory compliance
- Unit does NOT hold MTL in most states (bank holds the deposits)

**Key lesson:** Multi-bank partnerships provide resilience. If one bank partner exits, Unit can migrate programs to another bank.

---

## Risk Register

| Risk                                        | Likelihood | Impact   | Mitigation                                                                           |
| ------------------------------------------- | ---------- | -------- | ------------------------------------------------------------------------------------ |
| Sponsor Bank terminates partnership         | Medium     | Critical | Maintain 2+ bank partners; have migration plan                                       |
| Regulatory crackdown on BaaS                | High       | Major    | Ensure bank genuinely supervises FloatYield; avoid "rent-a-charter" characterization |
| MTL required if FloatYield ever holds funds | Low        | Major    | Architecture must ensure bank always holds deposits                                  |
| State MTL cost underestimated               | High       | Major    | Budget $500K+ for full coverage; start with SD + 5 key states                        |
| CFPB scrutiny on yield products             | Medium     | Moderate | Ensure yield rate disclosures are clear; avoid deceptive practices                   |
| Bank fails (FDIC event)                     | Low        | Major    | Funds above $250K uninsured; customer disclosure required                            |

---

## Cross-Reference Audit

- **Foundational documents checked:** None in this repo (greenfield project)
- **Consistency assessment:** N/A (new project)
- **Dependencies:** FloatYield must have written agreements with Sponsor Bank before any customer-facing launch
- **Related regulations:** Bank Secrecy Act / AML (31 USC 5318), Dodd-Frank (P.L. 111-203), Reg E (12 CFR Part 205), FDIC Act (12 USC 1811)

---

## Decision Points

1. **Bank partner selection:** Which community/regional bank will be the first Sponsor Bank? Consider: Pathward, Celtic Bank, Blue Ridge Bank.
2. **Revenue share structure:** What percentage of net interest margin does FloatYield retain vs. bank? Typical: 70-90% to FloatYield, 10-30% to bank.
3. **Geographic scope at launch:** Start in 1-2 states or go nationwide via bank charter? Start narrow; expand.
4. **Reserve asset strategy:** Who manages Treasury investments? Must be the Sponsor Bank, not FloatYield.
5. **Yield disclosure compliance:** CFPB scrutiny on "yield" vs "interest" marketing; ensure disclosures are clear.

---

## Conclusion

The **Sponsor Bank model is the only viable regulatory path** for FloatYield to launch within 6 months. State-by-state MTL licensing requires $500K-$2M+ and 18-36 months — unacceptable for a B2B platform seeking to establish market traction. FloatYield must architect its product so the Sponsor Bank holds deposits and manages reserve assets; FloatYield provides only technology, yield calculation, and service orchestration. Any deviation that results in FloatYield holding customer funds (even temporarily) triggers MTL requirements.
