# EU Regulatory Framework for Yield-Bearing Payment Infrastructure

**Project:** FloatYield — B2B platform for interest-bearing payment accounts
**Region:** European Union
**Date:** April 2026
**Regulation:** MiCA, PSD2, EMD2, and national banking supervisory frameworks
**Status:** Requirements Analysis — Research Phase

---

## Executive Summary

FloatYield's EU strategy requires navigating three overlapping regulatory regimes: MiCA (crypto-assets), PSD2/EMD2 (payment services and e-money), and national banking supervisory frameworks. The core finding is that **yield-bearing payment accounts in the EU are legally viable but require either an e-money institution (EMI) license or a partnership with an existing EMI**. The €350K minimum capital requirement and 6-18 month licensing timeline make the direct licensing path expensive but viable for a B2B infrastructure company targeting bank/fintech clients. The estimated total cost is €500K-2M and 12-24 months to first client activation, compared to the US path (state-by-state, $50K-500K per state, 12-36 months).

---

## 1. MiCA Overview

### What Is MiCA?

The **Markets in Crypto-Assets Regulation (MiCA)** is EU Regulation 2023/1114, establishing a unified regulatory framework for crypto-assets across all 27 EU member states. It is the cornerstone of the EU's digital finance strategy.

### Timeline

| Milestone                                      | Date              |
| ---------------------------------------------- | ----------------- |
| MiCA enters into force                         | June 29, 2023     |
| Title I (General provisions) applicable        | June 30, 2023     |
| Title II (Asset-referenced tokens) applicable  | June 30, 2024     |
| Title III (Electronic money tokens) applicable | June 30, 2024     |
| Stablecoin provisions fully applicable         | December 30, 2024 |

As of the current date (April 2026), MiCA is fully in effect for all stablecoin issuance and crypto-asset services.

### What MiCA Regulates

MiCA creates three categories of regulated crypto-assets:

1. **Asset-Referenced Tokens (ARTs)** — tokens referencing multiple assets (currency baskets, commodities, crypto assets)
2. **Electronic Money Tokens (EMTs)** — tokens purporting to maintain a stable value by reference to one official currency
3. **Utility Tokens** — tokens providing access to a service or function

MiCA also regulates **Crypto-Asset Service Providers (CASPs)** — entities providing crypto custody, exchange, trading, portfolio management, or advisory services.

### Relevance to FloatYield

FloatYield's platform involves tokenized deposits or stablecoins used as the underlying yield-bearing instrument. If the yield-bearing instrument is denominated in EUR and maintains a 1:1 peg to the EUR, it falls under **EMT** classification under MiCA Title III. If FloatYield issues its own stablecoin, it must comply with MiCA's EMT requirements. If it uses an existing EUR stablecoin (e.g., from a partner bank), the partner must hold the relevant license.

---

## 2. Electronic Money Tokens (EMT) Under MiCA

### Classification Criteria

A crypto-asset is an EMT under MiCA Article 3(1)(6) if it:

1. Purports to maintain a stable value by reference to the value of one official currency (EUR or another EU member state currency)
2. Is not an asset-referenced token
3. Is not a utility token

In practice, any EUR-pegged stablecoin issued as electronic money is an EMT. Examples include EUR-pegged stablecoins from e-money institutions or credit institutions.

### License Required to Issue an EMT

Under MiCA Article 59, only the following entities may issue EMTs in the EU:

1. **Credit institutions** (banks with full banking licenses)
2. **Electronic money institutions (EMIs)** licensed under EMD2
3. **Central banks** and other public authorities

**FloatYield cannot issue EMTs directly** unless it obtains an EMI license or banking authorization. The practical path is:

- **Option A:** Partner with an existing EMI or credit institution that issues the underlying e-money/stablecoin
- **Option B:** Obtain an EMI license directly (significant capital and compliance investment)

### Reserve Requirements for EMTs

Under MiCA Article 55 and the accompanying regulatory technical standards (RTS), EMT issuers must maintain:

| Requirement          | Specification                                                         |
| -------------------- | --------------------------------------------------------------------- |
| **Reserve assets**   | At least 30% in demand deposits with credit institutions              |
| **Investment grade** | Reserve assets must be of high credit quality                         |
| **Custody**          | Reserve assets must be held by a regulated credit institution or CASP |
| **Segregation**      | Reserve assets must be segregated from the issuer's own assets        |
| **Disclosures**      | White paper required, quarterly reserve reports                       |

Additionally, under **EMD2 (Electronic Money Directive 2)**, e-money institutions must:

- Hold 100% of e-money funds in secure, low-risk assets
- Not lend out e-money funds
- Provide for redemption at par value on demand

### EMT Redemption Rights

MiCA Article 57 guarantees EMT holders the right to redeem at par value. EMT issuers must:

- Redeem at par value in fiat currency upon request
- Complete redemptions within 5 business days
- Not charge excessive fees for redemption

---

## 3. Asset-Referenced Tokens (ART) vs. EMT

### Classification Decision Tree

```
Is the token's value referenced to ONE official currency?
├── YES → EMT (Electronic Money Token)
└── NO
    ├── Referenced to MULTIPLE currencies/commodities/assets?
    │   └── YES → ART (Asset-Referenced Token)
    └── Primarily used for utility/access to service?
        └── YES → Utility Token
```

### Key Differences: ART vs. EMT

| Aspect                          | EMT                         | ART                                                   |
| ------------------------------- | --------------------------- | ----------------------------------------------------- |
| **Peg**                         | Single fiat currency        | Multiple assets (currencies, commodities, crypto)     |
| **Reserve requirement**         | MiCA + EMD2 (100% backing)  | MiCA + EBA guidelines (detailed reserve rules)        |
| **Stablecoin designation**      | "Stablecoin" colloquially   | "Stablecoin" colloquially                             |
| **Supervisory authority**       | National central bank + NCA | European Banking Authority (EBA) for significant ARTs |
| **White paper**                 | Required                    | Required + EBA approval for significant ARTs          |
| **Interest/yield restrictions** | EMD2 restrictions apply     | No specific EMD2 restrictions                         |

### Relevance to FloatYield

FloatYield's yield-bearing accounts, if denominated in EUR, would be EMTs. If FloatYield designed a multi-currency or commodity-backed instrument, it would be an ART — with significantly more regulatory burden (EBA oversight, reserve composition requirements, and enhanced disclosure).

**Recommendation:** FloatYield should remain in the EMT classification by using EUR-denominated instruments only.

---

## 4. Yield on Payment Accounts Under EU Law

### The Core Question

Can an EU payment institution or e-money institution legally pay interest (yield) on a payment account holding user funds?

### PSD2 Framework

**PSD2 (Payment Services Directive 2)** — Directive 2015/2366/EU — governs payment services across the EU. Key provisions:

- **Article 3** — PSD2 applies to payment institutions, not credit institutions
- **Article 18** — Payment institutions may hold funds for payment execution
- **Article 19** — Payment institutions must segregate customer funds from own funds

**PSD2 does NOT prohibit paying interest on payment accounts.** However:

1. Payment institutions under PSD2 are **not permitted to lend out customer funds** (no credit intermediation)
2. Paying interest on large balances could be interpreted as engaging in banking activity (requiring a full banking license)
3. The interest paid must come from the institution's own capital, not from investment of customer funds

### EMD2 Framework

**EMD2 (Electronic Money Directive 2)** — Directive 2011/61/EU as amended — governs e-money institutions. Key provisions:

- **Article 6** — E-money institutions may pay interest on e-money
- **Interest restrictions** — EMD2 allows interest payments but EU member states may impose restrictions
- **Redemption at par** — E-money must be redeemable at par value at any time

**The Germany-specific situation:** BaFin (German Federal Financial Supervisory Authority) has taken the position that paying interest on e-money balances is permissible but must be structured carefully. German e-money institutions (such as those operating card programs) routinely pay yield/incentive payments to customers.

### Yield Structure for FloatYield

The most legally sound structure for FloatYield to pay yield:

1. **Partner bank/EMI holds the underlying e-money** — the bank/EMI is the e-money issuer and holds 100% reserves
2. **FloatYield operates as a program manager or agent** — FloatYield provides the technology and B2B platform, not the e-money itself
3. **Yield is paid by the partner bank/EMI** — from the bank's own capital or from yield generated on 100% reserves (invested in low-risk government bonds, etc.)
4. **FloatYield takes a platform fee or spread** — B2B revenue model, not interest spread from customer funds

This structure avoids FloatYield requiring its own e-money institution license while still enabling yield-bearing accounts for bank/fintech clients.

---

## 5. E-Money Institution License: The EU Equivalent of US Money Transmitter

### Definition

An **Electronic Money Institution (EMI)** is a licensed entity authorized under EMD2 to issue electronic money. It is the EU regulatory equivalent of:

| US                                         | EU                                                                      |
| ------------------------------------------ | ----------------------------------------------------------------------- |
| Money Transmitter License (state-by-state) | Electronic Money Institution License (national, passportable across EU) |
| FinCEN MSB registration                    | National competent authority (NCA) registration                         |
| Variable capital requirements by state     | €350K minimum for e-money issuance                                      |
| State-by-state licensing timeline          | Single national license via EU passporting                              |

### Capital Requirements

| Requirement                 | Specification                                                                |
| --------------------------- | ---------------------------------------------------------------------------- |
| **Minimum initial capital** | €350,000 (for e-money issuance)                                              |
| **Own funds**               | Must always be >= €350K or average outstanding e-money (whichever is higher) |
| **Calculation basis**       | Average e-money in circulation over preceding 6 months                       |
| **Investment restrictions** | Own funds must be in low-risk, liquid assets                                 |

### Application Requirements

To obtain an EMI license from a national competent authority (e.g., BaFin in Germany, FCA in the UK pre-Brexit, AMGK in Greece):

1. **Business plan** — Detailed description of e-money issuance and payment services
2. **Risk assessment** — Comprehensive IT, operational, and compliance risk framework
3. **Governance structure** — Fit and proper directors, robust governance
4. **Initial capital** — €350K in own funds, deposited before application
5. **Safeguarding plan** — How customer funds will be segregated and protected
6. **Anti-money laundering (AML) policies** — AML/CFT procedures per EU regulations
7. **IT and security framework** — Systems for e-money issuance, redemption, and transaction monitoring
8. **Outsourcing arrangements** — If using third-party processors

### Timeline

| Phase                       | Duration         |
| --------------------------- | ---------------- |
| Pre-application preparation | 3-6 months       |
| NCA review and questions    | 6-12 months      |
| License grant               | 1-2 months       |
| **Total**                   | **12-24 months** |

### EU Passporting

A key advantage of the EMI license over US state-by-state licensing: once an EMI license is granted by one EU member state (e.g., Germany), it can be **passported** to all other 26 EU member states through a notification process. This means a single EMI license covers the entire EU market.

---

## 6. Actual Licensing Pathway for FloatYield in the EU

### Option A: Direct EMI License (Full Licensing)

**Appropriate if:** FloatYield intends to issue its own e-money and operate independently across the EU.

**Steps:**

1. Choose home member state (Germany recommended — BaFin is experienced, English-speaking, and Germany is Europe's largest fintech market)
2. Capital injection: €350K minimum into EU-incorporated entity
3. Prepare full EMI license application (business plan, risk framework, governance, AML policies, IT systems)
4. Submit to BaFin (or chosen NCA)
5. Respond to NCA questions (typically 2-4 rounds of questions over 6-12 months)
6. Receive EMI license
7. Passport to other EU member states as needed via freedom of services notification

**Costs:**

- Legal/advisory for application: €150K-400K
- Capital lockup: €350K minimum
- Compliance infrastructure: €100K-300K
- Ongoing compliance: €100K-200K annually
- **Total estimated: €600K-1.2M + 12-24 months**

### Option B: Partnership with Existing EMI (Recommended for MVP)

**Appropriate if:** FloatYield wants to reach market quickly with B2B bank/fintech clients before investing in own license.

**Structure:**

- Partner with an existing German or EU e-money institution
- FloatYield acts as the **program manager** or **white-label technology provider**
- Partner EMI holds the e-money license and issues e-money
- FloatYield provides the B2B platform, yield management, and banking/fintech integration
- Revenue: Platform fees, technology licensing, or revenue share with partner EMI

**Benefits:**

- Time to market: 3-6 months (vs. 12-24 months)
- Capital required: €50K-100K (vs. €600K-1.2M)
- Lower regulatory risk (partner handles compliance and licensing)

**Examples of EU EMI partners:**

- **Solaris SE** (Berlin) — Banking and e-money platform for fintechs
- **P probiotic** (various) — E-money institution for card programs
- **Penta** (Germany) — Business banking API
- **Holvi** (Finland, now part of Nasdaq) — Business banking for SMEs

### Option C: Payment Institution Registration

**Appropriate if:** FloatYield's yield accounts do NOT constitute e-money (e.g., the yield is a rebate or service credit rather than interest on a deposit).

PSD2-based payment institutions:

- Can hold customer funds for payment execution
- Cannot issue e-money
- Cannot lend out customer funds
- Cannot pay interest on customer balances without additional analysis

This path is **not recommended** for FloatYield's core product because the yield mechanism (interest on deposits) is characteristic of e-money or banking activity.

### Option D: Full Banking License

**Appropriate if:** FloatYield's long-term strategy includes deposit-taking and lending.

Full banking license requirements:

- Minimum capital: €5M (initial), with ongoing requirements
- Application timeline: 18-36 months
- Cost: €1M-5M
  -Supervisory burden: Significant

This is NOT recommended for the MVP phase. Mondi (German neobank) and N26 both hold full German banking licenses, but they are consumer-facing retail banks with significant capital.

---

## 7. Case Studies: EU Fintechs and Their Licensing Structures

### N26 (Germany)

- **License:** Full German banking license (Kreditinstitut), granted by BaFin
- **Founded:** 2013
- **Product:** Consumer mobile bank with payment accounts, no interest on deposits (as of 2024)
- **EMI vs. Bank:** Full banking license, not EMI
- **Relevance to FloatYield:** N26's banking license is overkill for FloatYield's B2B model; however, it demonstrates that German licensing from BaFin is possible for foreign-founded companies.

### Mondi (Germany, part of Lunar Group)

- **License:** Full German banking license
- **Product:** Consumer and business accounts, cross-border payments
- **Relevance to FloatYield:** Like N26, Mondi pursued full banking status for consumer trust and product expansion. For B2B infrastructure, a full banking license is not necessary.

### Revolut (UK/EU)

- **EU License:** E-money institution license (issued by Lithuania — which passporting makes valid across EU)
- **Structure:** EU customers are serviced by Revolut's EU entity (Revolut Ltd was UK, now under Revolut Payments UAB in Lithuania)
- **Product:** Multi-currency accounts, card payments, some interest/yield products in select markets
- **Relevance to FloatYield:** Revolut demonstrates that an e-money institution license (not full banking license) can support a broad range of payment products across the EU.

### Solaris SE (Germany)

- **License:** Full banking license (Kreditinstitut) + e-money institution
- **Product:** Banking-as-a-Service (BaaS) platform — provides banking infrastructure to fintechs
- **Relevance to FloatYield:** Solaris is a potential **partner** for FloatYield's B2B platform. Solaris provides the underlying e-money/banking license; FloatYield provides the yield management and B2B interface.

### Penta (Germany)

- **License:** E-money institution (previously payment institution)
- **Product:** Business banking API for SME finance tools
- **Relevance to FloatYield:** Penta demonstrates the EMI path for B2B-focused fintechs in Germany.

---

## 8. Comparison: EU vs. US Regulatory Path

### At a Glance

| Aspect                        | EU Path                                      | US Path                                                |
| ----------------------------- | -------------------------------------------- | ------------------------------------------------------ |
| **Primary regulation**        | MiCA + EMD2 + PSD2                           | State money transmitter licenses + FinCEN              |
| **Single license covers**     | All 27 EU member states                      | Single state only                                      |
| **Minimum capital**           | €350K (EMI)                                  | $50K-$500K per state (varies)                          |
| **Timeline to first client**  | 3-6 months (partner) / 12-24 months (direct) | 3-12 months per state                                  |
| **Total cost to market**      | €100K-1.2M (depending on path)               | $150K-2M (50 states)                                   |
| **Passporting/ reciprocity**  | EU passporting across all member states      | No interstate reciprocity                              |
| **Federal overlay**           | None (EU-level regulation)                   | FinCEN + federal banking regulators                    |
| **Stablecoin classification** | EMT under MiCA                               | State-by-state; federal stablecoin legislation pending |

### EU Advantages for FloatYield

1. **Single license, entire EU market** — Unlike US state-by-state licensing, one EMI license is valid across all 27 EU member states
2. **Clearer regulatory framework** — MiCA is comprehensive and specifically addresses stablecoins; US has no federal stablecoin framework
3. **Passporting** — After obtaining an EMI license in Germany, FloatYield can operate in France, Italy, Spain, etc. without additional licensing
4. **Regulatory clarity on yield** — EMD2 explicitly permits e-money institutions to pay interest (with restrictions), whereas US regulations on yield-bearing accounts are fragmented

### EU Challenges for FloatYield

1. **Capital requirements** — €350K minimum is higher than many US state requirements
2. **Timeline** — 12-24 months for direct licensing vs. 3-6 months for US state applications (though US requires 50 states for full coverage)
3. **Local presence** — Most NCAs prefer/require an EU-established entity with local governance
4. **Yield restrictions** — EMD2 interest payment restrictions require careful structuring

---

## 9. Risk Assessment

### High Probability, High Impact

1. **Partner EMI dependency** — If FloatYield relies on a partner EMI and that partner loses its license or changes terms, FloatYield's entire EU operation is disrupted.
   - **Mitigation:** Dual-source partner strategy; maintain relationships with at least two EU EMIs.
   - **Prevention:** Contractual protections; SLA-backed agreements; regular partner audits.

2. **EMT classification challenge** — If FloatYield's yield product is reclassified as an ART (due to multi-currency exposure or complex reserve structure), it faces significantly higher regulatory burden.
   - **Mitigation:** Keep all products EUR-denominated and single-currency.
   - **Prevention:** Pre-clearance discussion with BaFin before launching new products.

3. **PSD2/EMD2 yield restrictions** — If regulators determine FloatYield's yield product constitutes prohibited interest under EMD2 in a specific member state, the product is unusable there.
   - **Mitigation:** Jurisdiction-specific legal opinions; product modifications for restrictive markets.
   - **Prevention:** Engagement with national competent authorities in target markets.

### Medium Risk (Monitor)

4. **MiCA regulatory evolution** — The EBA is still issuing technical standards and guidance on EMT reserve requirements and investor protections. Changes could affect FloatYield's product structure.
   - **Mitigation:** Active monitoring of EBA publications; regulatory counsel on retainer.
   - **Prevention:** Modular product architecture that can adapt to new reserve requirements.

5. **AML/KYC compliance burden** — EMD2 and PSD2 impose AML/KYC obligations on e-money issuance and payment services. Inconsistent KYC across EU member states could create compliance gaps.
   - **Mitigation:** Single KYC standard across all markets (highest standard applies); EU-wide AML framework (AMLD6).
   - **Prevention:** Automated KYC verification; regular compliance audits.

### Low Risk (Accept)

6. **Documentation drift** — Regulatory requirements may change between document publication and implementation.
   - **Mitigation:** Quarterly review of regulatory landscape.
   - **Prevention:** Close engagement with regulatory counsel.

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Months 1-6)

**Objective:** Establish EU market access via partner EMI

- Identify and contract with 2 EU e-money institution partners (target: German EMI + secondary EU EMI)
- Establish EU-incorporated entity (GmbH in Germany or equivalent)
- Legal opinion on PSD2/EMD2 yield compliance for each target market
- Technology integration with partner EMI APIs
- AML/KYC framework implementation
- **Cost:** €100K-200K
- **Owner:** Legal/Compliance + Engineering

### Phase 2: MVP Launch (Months 7-12)

**Objective:** Activate first B2B bank/fintech clients in Germany and 2-3 additional EU markets

- Pilot program with 2-3 bank/fintech clients
- Yield product live in Germany (initial market)
- Regulatory monitoring for MiCA compliance
- Passport notifications to 2-3 additional EU member states
- **Cost:** €50K-100K
- **Owner:** Business Development + Engineering

### Phase 3: Scale (Months 13-24)

**Objective:** Full EU coverage via passporting; evaluate own EMI license

- Passport to all 27 EU member states
- Assess whether own EMI license is warranted based on client volume
- If yes: Begin direct EMI license application to BaFin
- Build dedicated EU compliance team
- **Cost:** €100K-200K annually (compliance + regulatory)
- **Owner:** Compliance + Operations

---

## 11. Conclusion

FloatYield's EU path is structurally clearer than the US path but requires front-loaded capital investment and regulatory patience. The recommended approach is:

1. **Short term (0-12 months):** Partner with an existing EU EMI (e.g., Solaris SE or similar) to reach market in 3-6 months at a cost of €100K-200K. This avoids the 12-24 month licensing timeline and €600K-1.2M direct licensing cost.

2. **Medium term (12-36 months):** Evaluate whether own EMI license is warranted. If FloatYield's B2B client base grows to 20+ bank/fintech partners across the EU, the own-license path becomes cost-effective due to passporting.

3. **Key regulatory distinction from US:** The EU's EMT framework under MiCA provides a clear, single-regulatory-home for EUR stablecoins, and the EMD2 explicitly permits yield payments on e-money — a more structured path than US state-by-state yield restrictions.

**Bottom line:** EU path is cheaper than US path for full-market coverage (one license vs. 50 states), clearer on stablecoin classification (MiCA vs. fragmented state laws), and faster to full EU coverage once licensed. The cost of the direct EMI path (€600K-1.2M, 12-24 months) is comparable to US multi-state licensing ($500K-2M, 18-36 months) but covers the entire EU market rather than one state at a time.

---

## Appendix: Key Regulatory References

| Regulation             | Description                             | Link          |
| ---------------------- | --------------------------------------- | ------------- |
| MiCA (EU) 2023/1114    | Markets in Crypto-Assets Regulation     | EUR-Lex       |
| EMD2 (EU) 2011/61/EU   | Electronic Money Directive 2            | EUR-Lex       |
| PSD2 (EU) 2015/2366    | Payment Services Directive 2            | EUR-Lex       |
| BaFin EMI Licensing    | German EMI application requirements     | bafin.de      |
| EBA Guidelines on EMTs | European Banking Authority EMT guidance | eba.europa.eu |

---

_Document prepared by: Requirements Analysis Specialist_
_Workspace: yield-payment-infrastructure_
_Phase: 01-analysis/regulatory_
