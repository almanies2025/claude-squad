# FX Settlement Lock — Product Viability Analysis

**Project:** mBridge FX Settlement Lock Simulation
**Phase:** 01 — Research
**Author:** requirements-analyst
**Date:** 2026-04-30

---

## Executive Summary

The FX Settlement Lock simulation proves a structurally grounded insight: e-CNY dominates mBridge settlement volume not merely due to policy preference, but because CNY's dual-issuance architecture (PBOC + HKMA) creates the only zero-pre-fund bridge path in the 4-party network. This is a genuine architectural finding with implications for central bank treasury operations, correspondent banking, and BIS wholesale CBDC design.

The product viability question is whether this simulation — and the analytical capability it represents — can become something that central banks, BIS, correspondent banks, and researchers will pay for or adopt.

**Viability verdict:** The technical insight is novel and valuable. The market is narrow but real. The path to monetization is consulting-driven initially, with a possible SaaS or open-source play for the tooling layer. The key risk is that the only natural buyers (central banks, BIS) are slow, political procurement environments.

---

## 1. Buyer Profiles

### 1.1 Central Bank Treasury Technologist

**Who they are:** Staff in a central bank's treasury or payments department who manage Nostro accounts, FX settlement operations, and cross-border payment infrastructure. They are the technical counterpart to the policy staff who approve mBridge participation.

**What they actually need:**

- Quantify pre-funding costs: If their bank joins mBridge, how much Nostro capital must they pre-fund in foreign currencies? The simulation calculates this given a settlement scenario.
- Stress-test settlement paths: Before committing to mBridge, they want to know which currency pairs can settle atomically and which will deadlock.
- Scenario modeling: "What if BOT joins mBridge?" or "What if CBUAE opens a THB Nostro?" The technologist needs a tool to run these what-ifs rapidly.
- Internal buy-in: They need a quantitative argument to present to senior management explaining why atomic settlement has structural constraints, not just political ones.

**What they will pay:** Treasury operations budgets, not IT budgets. These are cost-center decisions. A tool that reduces pre-funding capital requirements or prevents settlement failures has quantifiable ROI.

**Estimated willingness to pay:** High (six figures) if the tool demonstrably reduces capital requirements or operational risk. However, procurement cycles are 12-24 months for central banks.

### 1.2 Correspondent Bank FX Desk

**Who they are:** The FX sales and trading desks at banks that serve as correspondent banks for cross-border CBDC settlement. They intermediate between central banks that lack direct Nostro relationships.

**What they actually need:**

- Revenue model clarity: Correspondent banks earn fees on Nostro accounts. If atomic settlement eliminates the need for pre-funded Nostros, their fee income is at risk.
- Risk assessment: If their bank provides Nostro services for CBDC settlement, what is the settlement failure rate? The simulation could model failure modes.
- Product development: Some correspondent banks are exploring "settlement-as-a-service" offerings. They need tools to design these products.

**What they will pay:** These are profit-center decisions. A tool that helps design new revenue-generating settlement products has clearer ROI. However, correspondent banks are secondary buyers — the primary decision is at the central bank level.

**Estimated willingness to pay:** Medium. They benefit indirectly and have faster procurement cycles (3-6 months for internal tooling).

### 1.3 BIS / Market Transaction Architect

**Who they are:** Technical staff at the Bank for International Settlements, or equivalent institutions (IMF, World Bank, OTC derivatives clearing houses), who design multi-currency settlement infrastructure for wholesale CBDC platforms.

**What they actually need:**

- Architecture validation: Before proposing a neutral numeraire token (Project Agora/Mandola), they need to validate whether the settlement lock problem is real and quantified.
- Design feedback: If the insight that CNY dominates due to dual-issuance is correct, what are the design implications for a neutral settlement token?
- Publication: BIS publishes technical papers. A quantified, validated settlement analysis with a simulation is publication-quality material.

**What they will pay:** BIS has research budgets and accepts consulting contracts. However, BIS is also a potential collaborator, not just a customer — they may want to open-source the tool rather than buy it.

**Estimated willingness to pay:** Zero for ownership, but high for collaboration. BIS will want the tool to be openly available for the broader central bank community.

### 1.4 Academic Researcher

**Who they are:** Academic economists and computer scientists studying CBDC design, cross-border settlement architecture, and monetary policy implications. This includes Oxford, SMU, HKUST, and BIS-affiliated academic networks.

**What they actually need:**

- Reproducibility: The ability to reproduce the settlement analysis and extend it with new parties, currencies, or scenarios.
- Publication-ready visualizations: Charts and tables showing settlement paths, failure modes, and network topology.
- Pedagogy: A teaching tool for central bank workshops on CBDC mechanics.
- Extendability: The ability to add parties, modify pre-funding assumptions, and explore novel settlement architectures.

**What they will pay:** Academic budgets are limited. The tool needs to be free or very low-cost for academic use. The value is adoption and citation, not revenue.

**Estimated willingness to pay:** Near zero. But academic adoption builds legitimacy and provides citations that help sell to institutional buyers.

---

## 2. Product Format Options

### 2.1 Interactive Web Simulation

**Description:** A browser-based visualization where users can select parties, currencies, and settlement scenarios, and see the settlement path animate. Includes the pairwise settlement matrix, settlement lock detection, and a "what-if" scenario builder.

**Pros:**

- Immediate value without installation
- Visual output is compelling for stakeholder presentations
- Easy to share with non-technical stakeholders
- Can embed in BIS/central bank intranets

**Cons:**

- Requires ongoing hosting and maintenance
- Security review required for central bank environments (many are air-gapped)
- Limited programmatic extension

**Best for:** Central bank treasury technologists and BIS researchers who need to present findings to non-technical stakeholders.

**Estimated build:** 2-3 months for MVP.

### 2.2 API for Programmatic Access

**Description:** A REST/GraphQL API that exposes the settlement engine. Banks and research institutions integrate it into their internal systems for scenario analysis, automated testing, and data pipelines.

**Pros:**

- Maximum flexibility for institutional buyers
- Supports internal toolchains and automation
- Can be consumed by the web UI
- Enables a SaaS licensing model

**Cons:**

- Requires API documentation, authentication, rate limiting
- Institutional buyers require SOC2/ISO27001 compliance
- Higher support burden

**Best for:** Correspondent banks with internal FX systems, and BIS research teams running automated scenario sweeps.

**Estimated build:** 3-4 months for MVP including auth and docs.

### 2.3 Consulting Deliverable / Research Report

**Description:** A polished PDF/HTML report with the simulation results, settlement path diagrams, and narrative analysis. Delivered as part of a consulting engagement or as a standalone product.

**Pros:**

- Fastest time-to-revenue (write the report, sell it)
- No ongoing maintenance burden
- Natural fit for consulting engagements
- Publication-ready for academic venues

**Cons:**

- One-time revenue, not recurring
- No tool for the buyer to run new scenarios -容易被复制分发

**Best for:** Initial revenue and market validation. Establishes thought leadership before the tool is built.

**Estimated build:** 2-4 weeks.

### 2.4 Academic Paper Supplement

**Description:** An open-source tool (Python + Jupyter notebooks) released alongside an academic paper. Researchers can reproduce the findings, extend the model, and build on it.

**Pros:**

- Establishes academic credibility and citations
- Community contributions extend the tool for free
- Aligns with open-science norms in central banking
- No maintenance cost if properly community-managed

**Cons:**

- Zero direct revenue
- Academic publication cycle is 1-2 years
- Tool quality must be high for academic standards

**Best for:** Academic researchers and BIS-affiliated scholars. Also the right move if the goal is adoption over monetization.

**Estimated build:** 1-2 months for polished notebooks + paper submission.

### 2.5 CLI Tool for Analysts

**Description:** A command-line tool (`fx-settlement-lock`) that analysts install locally. Accepts scenario definitions in JSON/YAML and outputs settlement results in text, JSON, or graph format.

**Pros:**

- Zero deployment complexity
- Easy to integrate into existing analyst workflows
- Scriptable for batch scenario analysis
- No hosting costs

**Cons:**

- Limited appeal to non-technical stakeholders
- Hard to sell as a "product" to central bank management
- No visual output without separate tooling

**Best for:** Correspondent bank FX analysts and academic researchers who prefer command-line workflows.

**Estimated build:** 1-2 months for polished CLI.

---

## 3. Monetization Models

### 3.1 Open-Source + Paid Support (Red Hat Model)

**Model:** Core simulation is open-source (Apache 2.0). Paid support contracts for institutional buyers who need SLA, customization, and dedicated support.

**Revenue potential:** $50K-$200K per annual support contract. Target 5-10 institutional buyers = $250K-$2M annually.

**Viability:** This model works if the open-source tool gains traction in the academic and research community, establishing legitimacy. Institutional buyers (central banks) then pay for support rather than build internally.

**Challenges:** Central banks often cannot pay vendors due to procurement restrictions. Requires a pre-existing relationship or framework agreement.

### 3.2 SaaS Subscription

**Model:** Hosted API + web UI with per-seat or per-query pricing. Academic accounts free; institutional accounts paid.

**Revenue potential:** $10K-$50K/year per institutional seat. Target 20-50 seats = $200K-$2.5M annually.

**Viability:** Works for correspondent banks and commercial institutions. Central banks are often prohibited from storing data on third-party servers, which limits the SaaS model for that segment.

**Challenges:** Data residency requirements for central bank data are strict. Many central banks require air-gapped or on-premises deployment.

### 3.3 Government / Research Grant

**Model:** Fund the development through a grant from a research institution (BIS, IMF, World Bank, or national research council).

**Revenue potential:** $100K-$500K per grant. Typically one-time, renewable for follow-on projects.

**Viability:** BIS Innovation Hub and IMF TechLab fund CBDC infrastructure research. A well-validated simulation with academic publication backing is a strong grant candidate.

**Challenges:** Grant timelines are slow (6-18 months from application to funding). Requires academic collaborators for most grant mechanisms.

### 3.4 Consulting Hours

**Model:** Sell engagements where the simulation is used to analyze a specific central bank's settlement architecture. Engagement includes a custom report + tool access.

**Revenue potential:** $10K-$50K per engagement. Limited by consultant availability (not scalable).

**Viability:** Fastest path to revenue if the founders have existing central bank relationships. Natural bridge between research and commercial adoption.

**Challenges:** Not scalable beyond individual relationships. Not a product company.

### 3.5 The "Too Niche" Problem

**Model:** No monetization — treat this as an open-source research contribution.

**Viability:** Realistic assessment. The total addressable market is 20-50 institutions globally. The procurement cycle is 12-24 months. The tool requires constant updating as mBridge evolves. Without a well-connected champion inside a central bank or BIS, this may not be commercially viable.

**This is the default outcome if no strong institutional relationship exists.** The simulation is valuable academically, but commercial translation requires relationships that do not exist yet.

---

## 4. Unique Selling Point Validation

### Is the CNY Dual-Issuance Insight Novel?

**Claim:** "CNY dominates mBridge volume because PBOC and HKMA both issue CNY, creating a zero-pre-fund bridge path that no other currency pair can replicate."

**Prior art check:**

| Source                                   | Claims                                                                           | Overlap                                                                                                       |
| ---------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| BIS Project Agora papers (2025)          | Proposes neutral settlement token to resolve multi-currency settlement locks     | Agrees problem exists; does not quantify CNY's structural advantage                                           |
| Oxford/SMU mBridge trilemma paper (2023) | mBridge faces a trilemma between atomicity, privacy, and a trusted intermediary  | Agrees atomic settlement is problematic; does not identify CNY dual-issuance as the specific structural cause |
| PBOC mBridge technical reports           | Describes RTGS integration and CNY settlement mechanics                          | Does not frame CNY dual-issuance as a settlement architecture advantage                                       |
| Commercial bank FX research              | Notes CNY's growing mBridge share; attributes to policy and internationalization | Does not identify the architectural mechanism                                                                 |

**Assessment:** The specific framing — that CNY dual-issuance creates a structurally unique zero-pre-fund bridge path — does not appear in published literature. The simulation quantifies something that is qualitatively understood but not mathematically demonstrated.

**Novelty:** MODERATELY NOVEL. The insight is directionally obvious to settlement engineers (dual-issuance eliminates correspondent risk for that currency), but the specific topological analysis and the pairwise settlement matrix are new contributions.

### Is It Useful?

**Usefulness to central bank treasury:** High. If a central bank is deciding whether to join mBridge, understanding which currency pairs can settle atomically is directly relevant to capital and operational planning.

**Usefulness to BIS:** High. Project Agora needs to understand exactly why current multi-currency settlement fails before proposing solutions.

**Usefulness to academic researchers:** High. This is a publishable finding that advances the field.

**Usefulness to correspondent banks:** Medium. They benefit indirectly but are not the primary decision-makers about mBridge participation.

---

## 5. What "Market-Ready" Means in This Domain

### The Central Bank Procurement Reality

Central banks are not typical technology buyers. Key characteristics:

1. **Air-gapped environments:** Many central bank systems are not connected to the public internet. A SaaS product is not viable for the core product. On-premises or air-gapped deployment is required.

2. **Long procurement cycles:** 12-24 months from initial contact to contract signature is normal. Frame agreements with approved vendors can shorten this.

3. **No "software license" line item:** Central banks budget for services, not software. They buy consulting engagements, not SaaS subscriptions. The vendor structure matters.

4. **Validation requirements:** Before procurement, central banks require validation by a trusted third party (typically BIS or another central bank). Independent validation is not optional.

5. **Open-source preference:** Many central banks prefer open-source tools that they can inspect, modify, and run without vendor dependency. This complicates monetization.

### What a "Product" Actually Looks Like

Given the above constraints, a "market-ready" product for central banks is:

1. **An open-source Python package** that runs on-premises and can be audited by the buyer's technical staff.
2. **A validation report** from BIS or an academic institution confirming the correctness of the simulation.
3. **A consulting engagement** for customization and integration support.
4. **Jupyter notebooks** for exploration and stakeholder presentations.

The commercial layer (support contracts, SaaS) is secondary and must be optional. The product must be usable without ongoing vendor dependency.

---

## 6. Real Buyer Alternatives

### What Organizations Use Today Instead of This Tool

| Buyer                      | Current Alternative                                               | Gap This Tool Fills                                                          |
| -------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Central bank treasury      | Internal spreadsheet models; ad-hoc simulation in Python or Excel | Quantified settlement path analysis with atomicity constraints               |
| Correspondent bank FX desk | Commercial FX settlement systems (Bloomberg, Refinitiv)           | Specific multi-currency atomic settlement modeling these systems don't cover |
| BIS / Market architect     | In-house research prototypes; academic collaborations             | Validated, published simulation with reproducible results                    |
| Academic researcher        | Custom Python scripts; published paper reproduction               | Ready-made, extensible settlement engine with documentation                  |

### Competitive Landscape

**Direct competitors:** None identified. There is no publicly available tool that specifically models multi-currency atomic settlement constraints for mBridge-style configurations.

**Adjacent tools:**

- **BIS Project Agora simulation** (internal, not publicly available)
- **Commercial CBDC platforms** (Ripple, Corda, Hyperledger Fabric based) — these are infrastructure, not analytical tools
- **Acadia Labs mBridge dashboard** — tracks transaction volumes, not settlement mechanics
- **Bloomberg FX trading tools** — cover spot/forward FX, not atomic multi-currency settlement

**Assessment:** The competitive landscape is thin. This is both an opportunity and a warning — either the market doesn't exist, or no one has successfully served it yet.

---

## 7. Strategic Recommendations

### Short-Term (0-6 months): Consulting + Academic Publication

1. **Publish an academic paper** with the simulation and findings. Target venues: BIS Working Papers, Journal of Financial Market Infrastructure, or Oxford CBDC Workshop proceedings.
2. **Release open-source tool** (Python + Jupyter) alongside paper. Maximize academic citations.
3. **Pursue one consulting engagement** with a correspondent bank or willing central bank to validate the tool in a real context.

**Rationale:** Academic publication establishes novelty. Open-source release builds adoption. Consulting validates the commercial path.

### Medium-Term (6-18 months): BIS Engagement + Tool Polish

1. **Engage BIS Innovation Hub** to present findings. If BIS endorses the tool, institutional adoption follows.
2. **Polish the web simulation** for non-technical stakeholders. Central bank managers need visuals, not code.
3. **Build the API layer** for correspondent banks with internal integration needs.

### Long-Term (18-36 months): Support Contracts + Ecosystem

1. **Offer support contracts** to the 5-10 institutions that adopt the tool.
2. **Build a community** of central bank treasury technologists exchanging scenario definitions.
3. **Evolve toward a SaaS product** if data residency restrictions ease (unlikely for central banks).

### Most Likely Outcome

The most likely outcome is **open-source research contribution with limited commercial translation**. The tool will be used by 3-5 academic research groups and 1-2 central bank treasury teams, but will not generate significant commercial revenue. The founders will need to either (a) accept this as a thought leadership asset for consulting, or (b) find an institutional champion who can drive procurement.

The CNY dual-issuance insight is genuine and publishable. The path to commercial product requires institutional relationships that don't exist yet.

---

## Appendix: Key Research Questions for Market Validation

1. Has any central bank published analysis of CNY dual-issuance settlement advantages?
2. What is the current mBridge transaction volume breakdown by currency (to validate the "CNY dominates" claim empirically)?
3. Which central banks have expressed interest in Project Agora-style neutral settlement tokens?
4. What is the current status of BIS Project Mandola's technical specification?
