# SDAIA AI Project Proposal Evaluator

## What It Is

A working internal tool for SDAIA that evaluates AI project proposals from Saudi government ministries against NSDAI strategic criteria. Ministries submit proposals → the engine scores them across 6 dimensions → SDAIA staff see instant recommendations.

## To Run

```bash
cd sdaia-evaluator
pip install -r requirements.txt
python main.py
```

Then open **http://localhost:8000** in your browser.

## What It Does

**Submit View** — Ministries fill out a 5-section form:
1. Project identity (name, ministry, type, NSDAI pillar, description)
2. Resources (budget, timeline, beneficiaries, data types)
3. AI characteristics (expertise, biometric, predictive AI, cross-ministry)
4. Governance safeguards (transparency plan, bias mitigation)
5. Contact info

**Evaluation Engine** scores each proposal on:
- NSDAI Strategic Alignment (25%) — keyword matching against Vision 2030 pillars
- Technical Feasibility (20%) — budget, timeline, AI expertise
- Ethical & Bias Risk (15%) — biometric, personal data, predictive AI flags
- Data Governance Readiness (15%) — data types, PDPL compliance signals
- Budget & Resource Adequacy (10%) — realistic funding for scope
- Impact & Scalability (15%) — beneficiary count, national scope

**Result View** — Radar chart, score breakdown, ethical risk profile, NSDAI alignment card, gaps, strengths, and recommended actions.

**Dashboard** — SDAIA staff see all submitted proposals with scores and tier badges.

## Tier System

| Score | Tier | Decision |
|-------|------|----------|
| 80+ | 🏆 Tier 1 | APPROVE — Fast-track NSDAI funding |
| 68-79 | ✅ Tier 2 | APPROVE WITH CONDITIONS |
| 52-67 | ⚠️ Tier 3 | REVISE AND RESUBMIT |
| <52 | ❌ Tier 4 | NOT RECOMMENDED |

## The Argument

> SDAIA's biggest blind spot globally: no unified view of all government AI projects. This evaluator gives SDAIA the infrastructure to receive, score, and track every AI proposal coming in — and gives the president a dashboard showing exactly where Saudi Arabia's AI portfolio stands against Vision 2030 targets.
