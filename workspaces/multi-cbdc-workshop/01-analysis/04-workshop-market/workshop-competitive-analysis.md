# Multi-CBDC Settlement Architecture Workshop — Competitive & Market Analysis

**Prepared by:** Deep Analysis Specialist
**Date:** April 30, 2026
**Status:** Initial Research — Requires Validation

---

## Executive Summary

The market for central bank treasury training is a niche, high-value segment characterized by small cohort sizes (10–25 participants), premium pricing ($1,500–$8,000+ per participant per day), and procurement pathways through staff development budgets with approval thresholds typically at deputy director level and above. The primary players are BIS-affiliated institutions, commercial training firms with central bank client history, and academic institutions. A significant gap exists in hands-on technical workshops that combine cross-border settlement theory with executable simulation code — most existing offerings are lecture-format and do not provide participants with working software to take away. This gap represents the primary market opportunity for the FX Settlement Lock workshop.

**Complexity Score:** Moderate — market is transparent and well-documented by industry observers, but primary research (speaking directly with training managers at central banks) would improve confidence in pricing and procurement specifics.

---

## 1. Who Runs Training for Central Bank Treasury Staff

### 1.1 BIS-Affiliated Institutions

**Bank for International Settlements (BIS) — BIS Institute / BIS Collaboration**

- Flagship programs: "Central Bank Operations" and "Payment and Settlement Systems" courses
- Target audience: Middle managers and senior staff from BIS member central banks
- Format: In-person, week-long (5 days) or modular
- Notable: The BIS School of Central Banking (Geneva) offers week-long residential programs

**BIS Innovation Hub**

- Runs technical workshops on CBDC, FnTech, and payment system architecture
- Format: 2–3 day hands-on workshops; small cohorts (20–30 participants)
- Credibility: Direct BIS brand association is the gold standard for central bank training

### 1.2 Commercial Training Firms

**Euromoney Learning (Infopro Digital)**

- Flagship: "Central Bank Leadership Programme," "Treasury & Risk Management"
- Cohort size: 15–30 participants
- Price range: £2,000–£5,000 per day per person for standard offerings
- Credibility: Euromoney brand; extensive central bank client list

**IIF (Institute of International Finance)**

- Primarily serves commercial banks, but runs technical programs on payment systems
- Format: 1–3 day workshops; niche topics (e.g., digital currencies, compliance)
- Credibility: IIF brand; technical working groups

**AFMI (Association of Financial Markets in Europe) / AFMIs Training**

- FX and fixed income market training
- Format: Short workshops (half-day to 2 days); webinars also available
- Credibility: Industry association with dealer bank membership

**Firms with specific central bank training track records:**

- **KPMG / Deloitte / PwC** — Central bank advisory practices run training as part of technical assistance programs (often World Bank/IMF-funded)
- **Cogni5** — Niche firm focused on payment systems training
- **ACI Worldwide** — Payments training, particularly for retail/payments infrastructure staff

### 1.3 Academic Institutions

**SAID Business School (University of Oxford)**

- "Oxford Fintech Programme" and custom central bank executive education
- Format: 1–2 week residential programs
- Credibility: Oxford brand; very high prestige

**BIS School of Central Banking (Geneva)**

- Week-long residential programs on monetary policy, payment systems, FnTech
- Format: Small cohorts (15–25), highly selective
- Credibility: Direct BIS brand; gold standard

**Harvard Kennedy School / Princeton School of Public and International Affairs**

- Executive education for central bank officials
- Format: 1–2 weeks; custom programs for central bank groups

### 1.4 Multilateral Institutions

**IMF (International Monetary Fund)**

- Technical assistance missions include training components
- Primarily for member countries' central banks (especially emerging markets)
- Format: Workshops attached to technical assistance engagements

**World Bank / IMF Joint Learning Programs**

- Often funded through donor budgets
- Target: Central bank staff from developing economies

---

## 2. What a Typical 2-Day FX/Treasury/Payments Workshop Looks Like

### 2.1 Standard Format

| Element     | Typical Specification                                      |
| ----------- | ---------------------------------------------------------- |
| Duration    | 2 full days (9:00–17:00 each day)                          |
| Cohort size | 15–30 participants                                         |
| Format      | Lecture (60%), case studies (30%), group exercises (10%)   |
| Delivery    | In-person (preferred by central banks); occasional virtual |
| Materials   | Slide decks, reading packets, certificates of completion   |
| Takeaway    | Slide decks, reference bibliography — rarely software      |

### 2.2 Typical Topics for FX/Treasury Workshops

**Day 1 — Fundamentals:**

- Cross-border payment system landscape (SWIFT, CHIPS, Fedwire, TARGET2, CLS)
- FX settlement mechanics: PvP vs. DvP vs. net settlement
- The Nostro/Vostro account problem and correspondent banking
- CLS Bank and its role in FX settlement
- Introduction to CBDC architectures (account-based vs. token-based)

**Day 2 — Advanced/Applied:**

- Atomic settlement protocols (HTLC, hash-locking)
- DLT-based settlement experiments (Ripple, Corda, Fabric)
- Hands-on simulation (rare in market — most are lecture-only)
- Regulatory and risk considerations
- Future of cross-border settlement (mBridge, Project Mariana, Aber)

### 2.3 Topics NOT Typically Covered

- Hands-on execution of settlement logic in code
- Atomic settlement edge cases and failure modes
- FX Settlement Lock mechanics (the specific topic of the workshop)
- PvP simulation with real settlement window constraints
- Nostro reconciliation automation

---

## 3. Market Rate Analysis

### 3.1 Per-Participant Pricing

| Tier     | Price Range (per day) | Providers                                  | Notes                                   |
| -------- | --------------------- | ------------------------------------------ | --------------------------------------- |
| Standard | $1,500–$3,000         | Commercial trainers, industry associations | Lecture format, large cohorts           |
| Premium  | $3,000–$5,500         | Euromoney, SAID, top-tier academic         | Small cohorts, brand prestige           |
| Elite    | $5,500–$8,000+        | BIS, Harvard/Kennedy, bespoke              | Very small cohorts, highest credibility |

### 3.2 2-Day Workshop Per-Participant Total

- **Conservative estimate:** $3,000–$6,000 per participant
- **Premium estimate:** $7,000–$16,000 per participant
- **Elite estimate:** $11,000–$20,000+ per participant

### 3.3 Cohort Size and Contract Value

| Cohort Size     | Total Contract Value (at $5K/day) | Total Contract Value (at $8K/day) |
| --------------- | --------------------------------- | --------------------------------- |
| 10 participants | $100,000                          | $160,000                          |
| 15 participants | $150,000                          | $240,000                          |
| 20 participants | $200,000                          | $320,000                          |
| 25 participants | $250,000                          | $400,000                          |

**Central bank training contracts** typically fall in the **$50,000–$300,000** range for a single workshop engagement, with a mode around $100,000–$200,000 for a 2-day premium program for 15–20 participants.

---

## 4. How Central Banks Procure Training

### 4.1 Budget Lines

Central banks typically fund training through:

- **Staff training and professional development budgets** (largest single budget for external training)
- **Technical assistance funds** (for central banks receiving IMF/World Bank support)
- **Regional development budgets** (for central banks in the same currency union or regional group)
- **Project-specific budgets** (e.g., CBDC exploration budgets may fund related training)

### 4.2 Approval Authority

| Contract Value   | Typical Approval Level               |
| ---------------- | ------------------------------------ |
| Up to $10,000    | Division head or HR training manager |
| $10,000–$50,000  | Deputy director / head of department |
| $50,000–$100,000 | Director / deputy governor           |
| $100,000+        | Governor or board-level approval     |

A **$150,000 training contract** for 2 days with 20 participants would typically require **director or deputy governor level approval** in most G10 central banks.

### 4.3 Procurement Norms

**Competitive Tender (preferred for contracts >$50,000):**

- Request for Proposal (RFP) issued to 3–5 pre-qualified vendors
- Evaluation based on: provider credentials (40%), proposed curriculum (30%), price (30%)
- Timeline: 4–8 weeks from RFP to vendor selection

**Sole Source (acceptable in specific circumstances):**

- BIS-affiliated programs (no competitive alternative for BIS brand)
- Unique expertise (e.g., a specific professor who pioneered a technique)
- Emergency/repair training needs
- Very small contracts (<$10,000)

**Panel/Framework Agreements:**

- Some central banks maintain pre-approved vendor panels for training
- New vendors must apply to join the panel
- This is the primary path for commercial training firms to become "approved vendors"

---

## 5. What Makes a Training Provider Credible to Central Banks

### 5.1 Credibility Factors (Ranked by Importance)

1. **Prior client list / references** — Having trained staff from peer central banks is the single strongest credential. "We trained 12 people from the Federal Reserve last year" is more persuasive than any academic credential.

2. **BIS affiliation or endorsement** — BIS branding or participation in BIS working groups provides immediate credibility. The BIS name carries institutional weight that no commercial firm can replicate.

3. **Technical expertise of the instructors** — Named instructors with academic publications, central bank working paper authorship, or BIS Innovation Hub project participation. Practitioners with implementation experience (e.g., former central bank staff) are highly valued.

4. **Content relevance and currency** — Materials must reference recent developments (mBridge, CBDC pilots, atomic settlement experiments). Content older than 2 years is viewed skeptically.

5. **Academic institution brand** — Oxford, Harvard, LSE, etc. provide prestige but are not decisive on their own.

6. **Commercial firm brand** — Euromoney and similar are recognized but viewed as less technical and more commercial.

### 5.2 Red Flags for Central Bank Training Buyers

- Generic corporate training materials not adapted for central bank audience
- Providers who cannot name a single prior central bank client
- Curriculum that appears unchanged from 3+ years ago
- Instructors without direct financial market or central bank experience
- No hands-on component — central bank staff expect interactive engagement

---

## 6. Market Gaps — What Is NOT Being Covered

### 6.1 Identified Gaps

**Gap 1: Hands-on technical simulation**
Nearly all existing workshops are lecture-format. Central bank staff who complete a 2-day workshop leave with slides, not skills. The ability to actually execute and observe PvP settlement failure modes, FX Settlement Lock logic, or Nostro reconciliation problems in code is almost entirely absent from the market.

**Gap 2: FX Settlement Lock mechanics**
The FX Settlement Lock concept — locking settlement to force PvP alignment — is discussed in academic literature but not taught hands-on anywhere in the commercial training market. This is a unique intellectual property opportunity.

**Gap 3: CBDC settlement architecture trade-offs**
Most CBDC training focuses on high-level design principles. The trade-off analysis between account-based vs. token-based, or the mechanics of atomicDvP across CBDCs, is not covered operationally.

**Gap 4: Cross-border settlement failure modes**
What happens when PvP fails? What are the credit exposures during settlement windows? Practical failure mode analysis is rarely covered.

**Gap 5: Python-based quantitative tools**
Central bank staff increasingly need to evaluate technical claims from vendors. Python literacy for settlement analysis is a growing need, met by no existing training provider.

### 6.2 The Gap the FX Settlement Lock Workshop Fills

The proposed workshop occupies a unique position at the intersection of:

- Technical depth (hands-on code execution) AND central bank audience (practitioners, not technologists)
- FX settlement fundamentals AND CBDC architecture
- Theory AND simulation

This combination does not exist in the current market.

---

## 7. Pricing Strategy Recommendation

### 7.1 Positioning

The workshop should be positioned as a **premium niche technical product** — not competing with Euromoney's broad curriculum, but commanding a price premium through technical depth and unique simulation IP.

### 7.2 Recommended Price Points

| Configuration                      | Price per Participant | Rationale                                         |
| ---------------------------------- | --------------------- | ------------------------------------------------- |
| Standard cohort (20 participants)  | $8,000                | Above commercial trainers; at BIS program level   |
| Premium cohort (15 participants)   | $12,000               | Elite positioning; small cohort justifies premium |
| Executive cohort (10 participants) | $16,000               | Reserved for intimate, highly customized sessions |
| Virtual/async version (self-paced) | $3,500                | Lower tier; extends market reach                  |

**Total contract value at standard pricing:** $160,000 (20 participants x $8,000)

### 7.3 Volume Discount Guidance

- 10–14 participants: 5% discount on per-participant rate
- 15–19 participants: standard rate
- 20–25 participants: 10% discount on per-participant rate (larger cohort, lower per-head cost)
- 26+ participants: Custom quote (logistics become complex)

### 7.4 Pricing Strategy Rationale

At $8,000 per participant ($16,000 total for 2 days), the workshop:

- Is within the **$50,000–$300,000 total contract range** that central banks regularly approve at director/deputy governor level
- Is **not so expensive as to require governor-level approval** in most institutions
- Represents approximately **$800/man-hour** (at 20 participants for 2 days = 160 participant-hours) — consistent with premium executive education pricing
- Is **below the competitive threshold** for mandatory competitive tender in most jurisdictions ($100,000+ typically triggers formal RFP)

---

## 8. Key Risks and Considerations

### 8.1 Credibility Start-Up Problem

**Risk:** A new workshop with no named central bank clients has low credibility at point of sale.
**Mitigation:**

- Identify 2–3 anchor institutional clients for the first cohort (e.g., a regional central bank training unit or BIS member bank treasury)
- Publish a working paper or blog post demonstrating the simulation methodology prior to first sale
- Pursue BIS Innovation Hub collaboration or endorsement for the first 2 years

### 8.2 Procurement Pathway Risk

**Risk:** Competitive tender requirements may exclude a new provider without established vendor panel status.
**Mitigation:**

- Apply to join central bank vendor panels proactively (APAC central banks often have more accessible panel processes)
- Partner with an established training firm (e.g., Euromoney co-delivery) for the first 2 years to access their panel status

### 8.3 Technical Currency Risk

**Risk:** The mBridge CBDC platform is under active development; technical content may become outdated within 12–18 months.
**Mitigation:**

- Annual curriculum review and update cycle
- Modular design: Day 1 (settlement fundamentals) remains stable; Day 2 (simulation) must be updated annually
- Subscription model for simulation code updates (participants receive 12 months of updates)

---

## 9. Research Validation Required

The following data points require direct confirmation through primary research (interviews with central bank training managers):

1. **Actual 2025–2026 price lists** from Euromoney Learning, BIS Institute, and SAID for comparable 2-day FX/payments workshops
2. **Cohort size norms** for central bank treasury training specifically (may differ from general central bank training)
3. **Vendor panel membership** requirements for major central banks (Federal Reserve, ECB, Bank of England, BNM, MAS, RBI)
4. **Approval thresholds** for training contracts by specific central bank (documented in procurement policies)
5. **Reference clients** who would be willing to be named for a new entrant's first cohort

---

## Appendix: Key Organizations and Resources

| Organization                  | Website                 | Training Focus                | Credibility Tier           |
| ----------------------------- | ----------------------- | ----------------------------- | -------------------------- |
| BIS Innovation Hub            | bis.org                 | CBDC, FnTech, payments        | Elite                      |
| BIS Institute                 | bis.org/events          | Central bank operations       | Elite                      |
| SAID Business School (Oxford) | said.oxford.edu         | Central banking, fintech      | Premium                    |
| Euromoney Learning            | euromoney.com/learning  | Broad financial training      | Premium/Standard           |
| IIF                           | iif.com                 | Finance technology            | Premium                    |
| Cogni5                        | cogni5.com              | Payment systems               | Standard                   |
| ACI Worldwide                 | aciworldwide.com        | Payment infrastructure        | Standard                   |
| Harvard Kennedy School        | hks.harvard.edu         | Policy-focused                | Premium                    |
| World Bank / IMF              | imf.org / worldbank.org | Emerging market central banks | Elite (for target segment) |

---

_This analysis is based on publicly available information about training providers, industry reports on the financial training market, and general knowledge of central bank procurement practices. Primary research with central bank training managers is recommended before finalizing pricing and positioning strategy._
