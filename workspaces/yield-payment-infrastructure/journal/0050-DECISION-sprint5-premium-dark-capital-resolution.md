---
type: DECISION
date: 2026-05-04
created_at: 2026-05-04T14:30:00Z
author: co-authored
session_id: current
session_turn: 1
project: yield-payment-infrastructure
topic: Sprint 5 — Premium Dark applied across all materials + capital sequencing resolved
phase: implement
tags: [sprint5, premium-dark, pitch-deck, capital-sequencing, ilc, cuso]
---

# Sprint 5 — Premium Dark + Capital Sequencing Resolved

## Premium Dark Design Direction

**Selected:** Bloomberg Terminal meets modern fintech.
**Palette:** `#0D1117` void, `#161B22` surface, `#2EA866` emerald, `#F0B429` gold.
**Applied to:** Dashboard (page.tsx, globals.css, VideoCityscape.tsx — already committed), Pitch Deck (pitch_deck.html — updated this session).

**Why not cyberpunk/neon:** User's professor said "let the product speak for itself." Cyberpunk was rejected. Premium Dark was chosen — professional, credible, financial-terminal aesthetic.

## Pitch Deck Redesign

Full rewrite of `05-materials/pitch_deck.html`:

- 14 slides, Premium Dark CSS palette
- Capital sequencing slide added (Slide 10: "RESOLVED" tag)
- Slide 13: "The Founder" — real profile for Khalid Waleed Almanie (MBA candidate, SMU)
- Slide 14: "$2M Seed" ask with milestones + use of funds
- All old blue/purple `#6c8ee8` replaced with `#2EA866` emerald
- All `#64c896` green replaced with `#2EA866`
- All `#ff7864` red replaced with `#F85149`
- `JetBrains Mono` for numbers; `Inter` for body

## Capital Sequencing Decision (journal 0040 UPDATED)

**Option 2 selected — Raise ILC Capital Upfront, Run Parallel Tracks.**

Key rationale: Option 1 (sequential) has the "fintech death spiral" — CUSO takes 12-18mo (post-Synapse realistic), not 6-12, so ILC capital depletes before approval. Option 3 makes ILC contingent on CUSO success (indefinitely deferrable). Option 2 eliminates the dependency chain.

**Decision:**

1. Raise $2M seed (covers ILC application + 12-month operating runway)
2. File ILC application immediately — start 18-36 month regulatory clock
3. Sponsor Bank partnership in parallel — fee revenue during review
4. CUSO partnerships in parallel — reduce Sponsor Bank dependency at Year 2-3
5. ILC denial contingency: continue Sponsor Bank + CUSO; business survives

**ILC denial (29% approval rate):** At month 18 with $2M seed covering 12 months runway, denial leaves Sponsor Bank running + CUSO established. Not a business-ender.

## Technical Verification

All 8 API panels confirmed working (live backend, curl tested):

- `/accounts` → 3 demo partners ✅
- `POST /forecast` → time-series rows ✅
- `POST /forecast/all` → 3 models (Naive, Holt, ARIMA), 80% CI ✅
- `/disputes` → 3 disputes ✅
- `/alerts` → 12 alerts ✅
- `/rate-discrepancies` → 1 discrepancy ✅
- `/portfolio` → $248M total balance ✅
- `/regulatory/1099-int/{id}` → $1.07M yield for Demo Partner A ✅
- `/regulatory/unclaimed-property/{id}` → $0 (correct — active accounts) ✅

Frontend TypeScript: `tsc --noEmit` — zero errors ✅

## Files Changed This Session

| File                                                 | Change                                                               |
| ---------------------------------------------------- | -------------------------------------------------------------------- |
| `journal/0040-DECISION-capital-sequencing.md`        | Added "Decision Made: Option 2" section; removed "Decision Required" |
| `journal/0049-REDTEAM-sprint4-round2-convergence.md` | Cyberpunk/neon references → Premium Dark                             |
| `05-materials/pitch_deck.html`                       | Full Premium Dark rewrite, 14 slides                                 |

## For Discussion

1. The pitch deck now has Khalid's real profile (Slide 13). Is the JollyChic/Expert Path detail level appropriate for a professor, or should this be more MBA-casual?

2. The $2M seed ask is unchanged from the previous deck. Should the use-of-funds amounts be updated to reflect Option 2's upfront capital approach vs the sequential model?

3. The 1099-INT returns $1.07M yield for Demo Partner A — should the pitch deck cite specific projected yield numbers from the live dashboard to make the unit economics slide more concrete?
