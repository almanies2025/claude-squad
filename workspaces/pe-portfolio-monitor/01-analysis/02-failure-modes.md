# Failure Modes — PE Portfolio Monitoring

Three reasons this product fails in market despite being well-built.

---

## Failure Mode 1: The Portco-CFO Veto Scales Worse Than Expected

**The mechanism**: The PE firm signs the contract. The operating partner is thrilled. Then the team has to convince 10–20 portco CFOs — who do not work for the PE firm and have their own incentives — to grant ERP access. Each takes 2–8 weeks. IT reviews. Legal reviews of data-use agreements. Fear of surveillance. By month 4, 6 of 15 portcos are connected; the firm loses patience; the renewal is at risk.

**Why it's likely**: This is the failure mode iLEVEL spent 15 years fighting with template-based requests. The reason incumbents use templates is that direct ERP access is politically harder than it looks from the PE firm's side.

**Leading indicators**:

- Pilot portco onboarding takes >6 weeks per portco
- Renewal conversations focus on "we're not getting full coverage"
- Churn reason: "we couldn't get enough portcos connected to justify the cost"

**Mitigation**:

- A portco-facing value proposition (benchmarks, peer cash-flow data, free tools) that makes portco CFOs _want_ to connect
- Pre-negotiated portco data-use agreement from day one
- "We'll get your portcos onboarded in 45 days or your money back" guarantee
- CSV-drop fallback per portco that maintains "coverage" even when API access is denied

---

## Failure Mode 2: Incumbents Ship "Good-Enough AI Monitoring" and the Wedge Closes

**The mechanism**: Allvue, iLEVEL, and 73 Strings each ship ML-powered anomaly detection in 2026–2027. They don't have live ERP pulls, but they have the install base, fund-accounting integration, and LP-reporting incumbency. A mid-market PE firm thinks: "Our Allvue handles fund accounting and now does AI anomaly detection — do we really need a second tool?" The technical inferiority of incumbents' engines is not visible enough to overcome institutional incumbency.

**Why it's likely**: AI features are the current roadmap focus of every vendor in this space. The gap the proposed product has is finite — 12–18 months — and closes whether or not incumbents execute well. Even a 60%-as-good feature from Allvue prevents displacement.

**Leading indicators**:

- Incumbent product launches mentioning "AI-powered portfolio monitoring"
- Lost deals where buyer cites "we already have Allvue/iLEVEL for this"
- Declining win rates when CFO is in the room (vs. OP alone)

**Mitigation**:

- Ship the ERP-pulled anomaly detection **fast** — 6 months is the window, not 12
- Publish quality difference publicly with case studies, not just demo wins
- Build integrations _with_ fund accounting incumbents (push data to Allvue) rather than competing head-on for that workflow
- Lock design partners into 3-year contracts with expansion commits

---

## Failure Mode 3: The Market Is Smaller Than Modeled

**The mechanism**: The mid-market PE ICP ($500M–$5B AUM, 10–20 portcos) contains fewer serviceable firms than pitch decks assume. Of the ~500–700 firms in that band in the US, probably 30–40% have already bought iLEVEL/Allvue/Dynamo; another 20–30% are "we'll always use Excel" firms; another 10–20% are too early in fund lifecycle to buy tooling. The actual addressable pool of "will consider a new tool in the next 24 months" is ~150–250 firms. At 10% win rate and $85K ACV, that is $1.3M–$2.1M of reachable ARR in a year of outbound — not the $5M–$10M the business plan likely assumes.

**Why it's likely**: Narrow-vertical B2B SaaS with a 500-firm TAM is the classic "great product, small market" trap. PE is concentrated, trust-gated, and slow-moving. Category expansion (VC, family offices, independent sponsors) sounds easy but each segment has different workflows and different buyer personas.

**Leading indicators**:

- Pipeline quality deteriorates after the first 30 warm-intro customers
- CAC creeps from $50K to $100K+ as reach goes beyond the warm network
- New-logo growth slowing while expansion revenue dominates

**Mitigation**:

- Pre-validate TAM with a data-driven ICP count (PitchBook + LinkedIn) before scaling hiring
- Plan a credible adjacent-segment expansion path with honest assumptions about buyer differences
- Build product extensibility for international mid-market PE (UK, Nordics, Benelux — same workflow, different ERPs)
- Aim for 125%+ NRR to make a smaller TAM still work — requires portfolio-expansion pricing and multi-fund deployment

---

## Composite Failure Likelihood

| Failure Mode                   | Likelihood (24-month horizon) | Severity                                |
| ------------------------------ | ----------------------------- | --------------------------------------- |
| Portco-CFO onboarding friction | 50–65%                        | High (renewal risk, margin compression) |
| Incumbent AI catch-up          | 40–55%                        | High (wedge erosion)                    |
| TAM smaller than modeled       | 40–50%                        | Medium (slower growth, not death)       |

These failure modes correlate — a firm that sees slow onboarding AND hears about Allvue AI AND is in a crowded ICP is a near-certain loss.

## Three Questions That Must Have Non-Wavy Answers

1. **Onboarding**: "How do we get a portco connected in under 3 weeks, and what is our guarantee?"
2. **Wedge**: "Why is our anomaly engine 5x better than what Allvue ships in 12 months, and how do we prove that in 30 minutes?"
3. **Market**: "Who are the 500 specific firms in our ICP, and do we have warm-intro paths into at least 100 of them?"

If any of the three has a hand-wavy answer, the product is at material risk of well-built failure.
