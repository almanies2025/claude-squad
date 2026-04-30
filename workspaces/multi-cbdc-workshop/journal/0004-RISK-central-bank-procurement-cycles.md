---
type: RISK
date: 2026-04-30
created_at: 2026-04-30T00:00:00Z
author: agent
session_id: deep-analysis-session
session_turn: 4
project: mbridge-redteam
topic: Central bank procurement cycles are 2-5 years — startup economics make this unviable
phase: redteam
tags:
  [
    procurement-risk,
    central-banks,
    startup-economics,
    commercial-model,
    fatal-flaw,
  ]
---

## Risk

Central bank procurement cycles are 2-5 years for technology products, requiring security certifications (Common Criteria, FIPS 140-2), source code escrow, open-source license review, domestic preference compliance, and often competitive tender. A startup building this product will run out of capital long before the first central bank sale closes.

**Why this is particularly acute for this product**:

1. **Target buyers are all public sector**: PBOC, HKMA, CBUAE, BOT, BIS — none are private-sector companies with agile procurement. Every sale requires public tender or direct negotiation with government technology procurement offices.

2. **Security certification is non-negotiable**: Central banks will not deploy a settlement analytics tool without Common Criteria certification (ISO/IEC 15408) or equivalent. Achieving this certification for a new product takes 12-18 months and costs $500K-2M.

3. **No fast path exists**: Even "partnership with a large SI" (Infosys, TCS, Accenture) requires the SI to win a competitive tender, adding 2-3 years and 3-5x markup.

4. **The 95%+ volume figure compounds the problem**: If the actual addressable market is small (5% non-CNY settlements), the total revenue potential from the entire global mBridge ecosystem is insufficient to justify the procurement investment from any SI.

**Why this is a fatal flaw for a startup**: A startup burning $200K/month needs to reach revenue in 18-24 months to survive. A 2-5 year procurement cycle kills the company before the first check clears.

## For Discussion

- Is there a pathway to selling to a central bank's innovation unit (not procurement) as an initial engagement? What are the limits of that pathway?
- Could the product be repositioned for non-central-bank buyers (e.g., commercial banks, fintechs) who have faster procurement cycles?
- If the commercial model is consulting/research rather than software license, does that bypass procurement requirements?
- What would the revenue model need to look like to sustain a 3-year procurement cycle? (e.g., pre-sales, grants, BIS partnership)
