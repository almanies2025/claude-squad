# Most Novel Commercial Path: FX Settlement Lock Simulation

**Date:** April 30, 2026
**Author:** Deep-analyst
**Phase:** 01 — Strategic Path Identification

---

## 1. Who Else Is in This Space

| Category | Players | Gap |
|---|---|---|
| **Terminal vendors** | Bloomberg, Refinitiv | No mBridge-specific modules; cover legacy FX only |
| **BIS/Academic** | BIS Innovation Hub, Oxford, SMU | Publish qualitative findings; no commercial tools |
| **Treasury tech vendors** | Finastra, FIS, Temenos | No CBDC settlement analytics built in |
| **CBDC infrastructure** | R3 (Corda), Hyperledger | Build the ledger, not analysis tools for it |
| **Consulting firms** | Accenture, Deloitte, PwC | CBDC advisory without standardized assessment tools |

**The critical finding:** The market has a complete gap at the intersection of CBDC settlement analysis AND commercial distribution. Every category above either doesn't cover CBDC settlement mechanics (terminal vendors), or covers it qualitatively without commercial tooling (BIS/academic), or builds infrastructure without analytics (CBDC platforms).

---

## 2. The Ignored Buyer: Commercial Bank Treasury Technology Vendors

Every prior path assumed central banks as the buyer. The ignored buyer is **not a central bank at all** — it is the vendor who sells treasury management systems to commercial banks globally.

**Who this is:**
- **Finastra** — Core banking and treasury; serves 9,000+ financial institutions
- **FIS** — Treasury management systems; serves major global banks
- **Temenos** — Treasury and payments; serves 300+ banks globally

**Why they are the buyer, not the end bank:**
- They have existing procurement relationships with commercial bank treasuries
- They have engineering teams that can integrate a module
- They have sales cycles measured in months, not years
- They sell functionality, not "software licenses" — avoids central bank procurement category problems
- They bundle the cost into an existing contract — no new budget line needed

**What they pay:** $50K–$200K per year for a module license, embedded in their TMS product. This is a rounding error in their annual revenue.

---

## 3. The "Unknown Unknown": Settlement Topology Is a Network Design Problem

The FX Settlement Lock simulation reveals something nobody else has articulated commercially:

**The settlement lock problem is not a currency problem — it is a network topology problem.**

The simulation shows that whether atomic settlement succeeds depends entirely on:
1. Which parties have pre-funded Nostro accounts in which currencies (the network edges)
2. Whether there exists a path through dual-issuance or pre-funding that satisfies all legs simultaneously

This is a **graph connectivity problem in a weighted network**. The insight that changes the framing:

> "Which corridors CANNOT settle atomically, and what pre-funding investment would unblock them?"

This is fundamentally different from what BIS papers discuss (which focus on the neutral numeraire token as the solution). The simulation answers: "given the current topology, here is exactly where the deadlock occurs and why."

This is a capital allocation question, not just an architecture question.

---

## 4. The Unknown Unknown Applied: Nostro Pre-Funding as Investment Decision

Nobody else frames Nostro pre-funding as an **investment decision that can be modeled**.

Commercial bank treasury departments worldwide manage Nostro accounts costing 3-5% annually in opportunity cost. The simulation can tell a treasury director:

- "Your THB-AED corridor deadlocks today. A $50M CNY pre-fund at CBUAE would unblock 80% of your cross-corridor volume."
- "Here is the exact ROI on pre-funding one additional currency pair versus using legacy correspondent banking."

This is **capital efficiency analysis**, not just settlement mechanics. Banks already buy tools that optimize capital efficiency. This is the commercial hook.

---

## 5. The Viable Novel Path

### Target: Treasury Technology Vendors (Finastra, FIS, Temenos)

**The product:** An embedded CBDC settlement feasibility module — a Python library + API — that their TMS products call to evaluate whether proposed cross-border payment corridors can settle atomically on CBDC networks.

**What they get:**
- A differentiated CBDC analytics feature in their TMS product
- No engineering investment — just a module license with documented API
- Sales talking points: "Tell your treasury clients which corridors will work on mBridge before they commit"

**What they pay:** $75K–$150K annual license. Wrapped into existing support contracts. No new procurement.

**What the commercial bank treasury gets:**
- Settlement feasibility analysis embedded in their existing treasury workstation
- No new system, no new vendor relationship, no new budget line
- Pays for itself if it prevents one failed settlement or identifies one capital efficiency improvement

**Why nobody else is doing this:**
- Terminal vendors (Bloomberg/Refinitiv) don't build embedded modules for TMS vendors — they compete directly
- BIS/academic produces research, not productized SDKs
- Consulting firms sell engagements, not embeddable libraries
- Treasury tech vendors have no CBDC settlement expertise and no incentive to build it themselves

---

## 6. Why This Path Survives the Three Fatal Flaws

| Fatal Flaw | Why This Path Survives |
|---|---|
| **No data access** | The module evaluates prospective corridors — no transaction data required, only network topology (who issues what, who has pre-funded what). This is publicly knowable from BIS publications. |
| **Buyer incentive mismatch** | The buyer (TMS vendor) is not disadvantaged by CNY dominance. They sell to ALL banks regardless of which corridors work. The beneficiary is the end treasury, who wants the analysis. |
| **No procurement path** | TMS vendors procure modules constantly. This is a standard software license, not a multi-year central bank procurement cycle. |

---

## 7. The "Nobody Else Is Doing This" Test

Name one commercial entity selling an embeddable CBDC settlement feasibility SDK to treasury technology vendors.

Answer: **None.** The closest is:
- Bloomberg running internal CBDC research (not a product)
- Consulting firms doing one-off engagements (not a repeatable product)
- Academic papers (not commercial)

The gap is genuine. The distribution channel (TMS vendors) is real and has existing commercial relationships with every commercial bank treasury that matters.

---

## 8. Critical Assumption and Risk

**The critical assumption:** Treasury technology vendors see CBDC features as a competitive differentiator in the next 2-3 years, and will pay to add these features rather than build them.

**The critical risk:** TMS vendors move slowly (12-18 month engineering roadmaps). The CBDC settlement module must be ready to embed before the TMS vendor's next major release planning cycle.

**Mitigation:** Pursue a pilot with one TMS vendor's innovation team first — Finastra has an active fintech partnership program. Get one named reference before going to others.

---

## Summary: One Sentence

**License the FX Settlement Lock simulation as an embeddable CBDC settlement feasibility SDK to treasury technology vendors (Finastra, FIS, Temenos), who bundle it into their treasury management systems and sell it to commercial bank treasuries globally — bypassing central bank procurement entirely by selling to the TMS vendor, not the end bank.**
