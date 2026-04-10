"""
SDAIA AI Project Proposal Evaluator
FastAPI Backend — Full Evaluation Engine
"""

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="SDAIA AI Proposal Evaluator", version="1.0.0")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ─────────────────────────────────────────────
# UTF-8 ENCODING FIX — ensure all JSON responses include charset=utf-8
# ─────────────────────────────────────────────
class UTF8JSONResponse(JSONResponse):
    charset = "utf-8"

    def __init__(self, content=None, **kwargs):
        kwargs.setdefault("media_type", "application/json; charset=utf-8")
        super().__init__(content, **kwargs)

    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

# Override FastAPI's default response class to use UTF-8 JSON
app.router.default_response_class = UTF8JSONResponse

# ─────────────────────────────────────────────
# DATA STORE (in-memory for prototype)
# ─────────────────────────────────────────────
proposals_db: dict = {}

def seed_demo_data():
    """Seed 14 demo proposals for the dashboard demo."""
    import random
    demo_proposals = [
        {"ministry": "Ministry of Health", "project_name": "AI-Powered Chronic Disease Management Platform", "nsaid_pillar": "health", "budget": 35000000, "timeline_months": 18, "beneficiaries": 5200000, "ai_expertise": True, "personal_data": True, "biometric": True, "predictive_ai": True, "transparency": True, "bias": True, "cross_ministry": True, "outcome": "vision_2030_priority"},
        {"ministry": "Ministry of Health", "project_name": "National Telemedicine Network Expansion", "nsaid_pillar": "health", "budget": 18000000, "timeline_months": 12, "beneficiaries": 3100000, "ai_expertise": True, "personal_data": True, "biometric": False, "predictive_ai": False, "transparency": True, "bias": False, "cross_ministry": False, "outcome": "single_entity"},
        {"ministry": "Saudi Data & AI Authority", "project_name": "National Government Data Exchange (NGDE)", "nsaid_pillar": "governance", "budget": 80000000, "timeline_months": 24, "beneficiaries": 30000000, "ai_expertise": True, "personal_data": False, "biometric": False, "predictive_ai": False, "transparency": True, "bias": False, "cross_ministry": True, "outcome": "vision_2030_priority"},
        {"ministry": "Ministry of Interior", "project_name": "Predictive Security & Threat Detection System", "nsaid_pillar": "security", "budget": 120000000, "timeline_months": 30, "beneficiaries": 25000000, "ai_expertise": True, "personal_data": True, "biometric": True, "predictive_ai": True, "transparency": False, "bias": True, "cross_ministry": True, "outcome": "national_impact"},
        {"ministry": "Ministry of Economy & Planning", "project_name": "AI-Driven Economic Diversification Monitor", "nsaid_pillar": "economy", "budget": 22000000, "timeline_months": 15, "beneficiaries": 5000000, "ai_expertise": True, "personal_data": False, "biometric": False, "predictive_ai": True, "transparency": True, "bias": False, "cross_ministry": True, "outcome": "vision_2030_priority"},
        {"ministry": "Saudi Arabian Oil Company (Aramco)", "project_name": "AI-Enhanced Oil Field Predictive Maintenance", "nsaid_pillar": "economy", "budget": 95000000, "timeline_months": 20, "beneficiaries": 75000, "ai_expertise": True, "personal_data": False, "biometric": False, "predictive_ai": True, "transparency": True, "bias": False, "cross_ministry": False, "outcome": "economic_growth"},
        {"ministry": "Capital Market Authority", "project_name": "AI-Powered Market Surveillance & Fraud Detection", "nsaid_pillar": "economy", "budget": 45000000, "timeline_months": 16, "beneficiaries": 1200000, "ai_expertise": True, "personal_data": True, "biometric": False, "predictive_ai": True, "transparency": True, "bias": True, "cross_ministry": False, "outcome": "regulatory_compliance"},
        {"ministry": "Ministry of Education", "project_name": "National AI Tutoring System — Vision 2030 Aligned", "nsaid_pillar": "society", "budget": 60000000, "timeline_months": 14, "beneficiaries": 10000000, "ai_expertise": True, "personal_data": True, "biometric": False, "predictive_ai": True, "transparency": True, "bias": True, "cross_ministry": True, "outcome": "vision_2030_priority"},
        {"ministry": "Ministry of Housing", "project_name": "Smart City Infrastructure AI Planning Tool", "nsaid_pillar": "society", "budget": 28000000, "timeline_months": 18, "beneficiaries": 7000000, "ai_expertise": True, "personal_data": False, "biometric": False, "predictive_ai": True, "transparency": True, "bias": True, "cross_ministry": True, "outcome": "vision_2030_priority"},
        {"ministry": "Ministry of Energy", "project_name": "Renewable Energy Grid Optimization AI", "nsaid_pillar": "economy", "budget": 38000000, "timeline_months": 22, "beneficiaries": 3500000, "ai_expertise": True, "personal_data": False, "biometric": False, "predictive_ai": True, "transparency": True, "bias": False, "cross_ministry": True, "outcome": "sustainability"},
        {"ministry": "Ministry of Communications", "project_name": "National Fiber Network AI Optimization", "nsaid_pillar": "governance", "budget": 15000000, "timeline_months": 10, "beneficiaries": 28000000, "ai_expertise": True, "personal_data": False, "biometric": False, "predictive_ai": False, "transparency": True, "bias": False, "cross_ministry": True, "outcome": "single_entity"},
        {"ministry": "Saudi Customs Authority", "project_name": "AI Cargo Inspection & Trade Facilitation", "nsaid_pillar": "security", "budget": 42000000, "timeline_months": 14, "beneficiaries": 450000, "ai_expertise": True, "personal_data": False, "biometric": True, "predictive_ai": True, "transparency": True, "bias": False, "cross_ministry": True, "outcome": "national_security"},
        {"ministry": "Ministry of Hajj & Umrah", "project_name": "Smart Pilgrimage Crowd Management AI", "nsaid_pillar": "society", "budget": 72000000, "timeline_months": 12, "beneficiaries": 3000000, "ai_expertise": True, "personal_data": True, "biometric": True, "predictive_ai": True, "transparency": True, "bias": True, "cross_ministry": True, "outcome": "vision_2030_priority"},
        {"ministry": "National Center for AI", "project_name": "Generative AI Sandbox for Government Innovation", "nsaid_pillar": "governance", "budget": 55000000, "timeline_months": 12, "beneficiaries": 500000, "ai_expertise": True, "personal_data": False, "biometric": False, "predictive_ai": True, "transparency": True, "bias": True, "cross_ministry": True, "outcome": "innovation_leader"},
    ]
    for p in demo_proposals:
        proposal = ProposalSubmission(
            ministry=p["ministry"],
            project_name=p["project_name"],
            project_type="government_ai",
            description=p["project_name"],
            nsaid_pillar=p["nsaid_pillar"],
            budget=p["budget"],
            timeline_months=p["timeline_months"],
            data_types=["government_ops"],
            target_beneficiaries=p["beneficiaries"],
            has_ai_expertise=p["ai_expertise"],
            uses_personal_data=p["personal_data"],
            uses_biometric=p["biometric"],
            uses_predictive_ai=p["predictive_ai"],
            has_transparency_plan=p["transparency"],
            has_bias_mitigation=p["bias"],
            cross_ministry=p["cross_ministry"],
            expected_outcome=p["outcome"],
            contact_name="Demo User",
            contact_email="demo@sdaia.gov.sa",
        )
        result = evaluate_proposal(proposal)
        proposals_db[result.proposal_id] = {
            "proposal": proposal.model_dump(),
            "result": result.model_dump(),
            "submitted_at": result.submitted_at,
        }

# seed_demo_data() called after evaluate_proposal is defined — see bottom

# ─────────────────────────────────────────────
# NSDAI STRATEGIC PILLARS & CRITERIA WEIGHTS
# ─────────────────────────────────────────────
NSDAI_PILLARS = {
    "health": {
        "label": "Healthcare & Life Sciences",
        "icon": "🏥",
        "nsdai_targets": ["Life expectancy 74→80", "Chronic disease management", "Telemedicine scale"],
        "weight": 0.22,
    },
    "governance": {
        "label": "Government & Public Services",
        "icon": "🏛️",
        "nsdai_targets": ["Cross-ministry data sharing", "Citizen service digitization", "AI governance frameworks"],
        "weight": 0.25,
    },
    "economy": {
        "label": "Economy & Digital Transformation",
        "icon": "💰",
        "nsdai_targets": ["GDP diversification", "AI industry growth", "Startup ecosystem"],
        "weight": 0.28,
    },
    "security": {
        "label": "National Security & Defense",
        "icon": "🛡️",
        "nsdai_targets": ["Threat detection", "Border AI", "Cyber defense"],
        "weight": 0.15,
    },
    "society": {
        "label": "Society & Quality of Life",
        "icon": "🌍",
        "nsdai_targets": ["Education access", "Cultural AI", "Smart city integration"],
        "weight": 0.10,
    },
}

EVALUATION_CRITERIA = {
    "strategic_alignment": {
        "label": "NSDAI Strategic Alignment",
        "description": "How well does this project align with Vision 2030 & NSDAI pillars?",
        "weight": 0.25,
        "max_score": 100,
    },
    "technical_feasibility": {
        "label": "Technical Feasibility",
        "description": "Is the technology mature, tested, and implementable within timeline?",
        "weight": 0.20,
        "max_score": 100,
    },
    "ethical_risk": {
        "label": "Ethical & Bias Risk",
        "description": "Does the project have adequate safeguards against AI bias, privacy violations, and discrimination?",
        "weight": 0.15,
        "max_score": 100,
        "invert_risk": True,  # higher risk = lower score
    },
    "data_readiness": {
        "label": "Data Governance Readiness",
        "description": "Is the required data available, clean, governed by PDPL, and shareable?",
        "weight": 0.15,
        "max_score": 100,
    },
    "resource_adequacy": {
        "label": "Budget & Resource Adequacy",
        "description": "Is the proposed budget realistic for the scope and timeline?",
        "weight": 0.10,
        "max_score": 100,
    },
    "impact_outcome": {
        "label": "Expected Impact & Scalability",
        "description": "Will this create measurable positive outcomes and scale across government?",
        "weight": 0.15,
        "max_score": 100,
    },
}

ETHICAL_RISK_FACTORS = {
    "facial_recognition": {"label": "Facial Recognition / Biometric", "risk": "HIGH", "weight": 0.20},
    "personal_data_processing": {"label": "Personal Data Processing", "risk": "HIGH", "weight": 0.18},
    "decision_automation": {"label": "Automated Decision-Making", "risk": "HIGH", "weight": 0.17},
    "predictive_scoring": {"label": "Predictive Scoring of Citizens", "risk": "MEDIUM", "weight": 0.12},
    "public_surveillance": {"label": "Public Surveillance", "risk": "HIGH", "weight": 0.15},
    "health_diagnostic": {"label": "Health / Medical Diagnosis", "risk": "MEDIUM", "weight": 0.10},
    "financial_decision": {"label": "Financial Decision-Making", "risk": "MEDIUM", "weight": 0.08},
}


# ─────────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────────
class ProposalSubmission(BaseModel):
    ministry: str
    project_name: str
    project_type: str
    description: str
    nsaid_pillar: Literal["health", "governance", "economy", "security", "society"]
    budget: float = Field(gt=0)
    timeline_months: int = Field(gt=0, le=60)
    data_types: list[str]
    target_beneficiaries: int
    has_ai_expertise: bool
    uses_personal_data: bool
    uses_biometric: bool
    uses_predictive_ai: bool
    has_transparency_plan: bool
    has_bias_mitigation: bool
    cross_ministry: bool
    expected_outcome: str
    contact_name: str
    contact_email: str


class EvaluationResult(BaseModel):
    proposal_id: str
    overall_score: float
    recommendation: str
    tier: str
    evaluation_details: dict
    ethical_risk_profile: dict
    nsaid_alignment: dict
    strengths: list[str]
    gaps: list[str]
    recommendations: list[str]
    submitted_at: str


# ─────────────────────────────────────────────
# EVALUATION ENGINE
# ─────────────────────────────────────────────
def evaluate_proposal(p: ProposalSubmission) -> EvaluationResult:
    proposal_id = f"SDAIA-{uuid.uuid4().hex[:8].upper()}"
    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── 1. Strategic Alignment Score ──────────────
    pillar = NSDAI_PILLARS[p.nsaid_pillar]
    alignment_keywords = {
        "health": ["health", "medical", "hospital", "patient", "diagnostic", "clinical", "telemedicine", "chronic", "life expectancy"],
        "governance": ["government", "citizen", "service", " ministry", "public", "administrative", "permits", "documentation"],
        "economy": ["economy", "business", "investment", "startup", "industry", "trade", "finance", "revenue", "GDP"],
        "security": ["security", "threat", "border", "defense", "cyber", "surveillance", "emergency", "crime"],
        "society": ["education", "social", "community", "culture", "smart city", "environment", "transport", "quality of life"],
    }
    keywords = alignment_keywords[p.nsaid_pillar]
    desc_lower = p.description.lower()
    keyword_matches = sum(1 for kw in keywords if kw in desc_lower)
    strategic_score = min(100, 40 + keyword_matches * 12)
    if p.cross_ministry:
        strategic_score = min(100, strategic_score + 10)

    # ── 2. Technical Feasibility ───────────────────
    feasibility_score = 60
    if p.has_ai_expertise:
        feasibility_score += 20
    if p.timeline_months <= 12:
        feasibility_score += 10
    elif p.timeline_months > 24:
        feasibility_score -= 15
    if p.uses_personal_data and not p.has_transparency_plan:
        feasibility_score -= 10
    if p.uses_biometric:
        feasibility_score -= 8
    feasibility_score = max(5, min(100, feasibility_score))

    # ── 3. Ethical Risk Score ──────────────────────
    risk_factors_identified = []
    risk_score = 100
    if p.uses_biometric:
        risk_score -= 30
        risk_factors_identified.append("Biometric data processing — HIGH RISK")
    if p.uses_predictive_ai:
        risk_score -= 20
        risk_factors_identified.append("Predictive AI — MEDIUM-HIGH RISK")
    if p.uses_personal_data:
        risk_score -= 15
        risk_factors_identified.append("Personal data processing — requires PDPL compliance")
    if p.has_bias_mitigation:
        risk_score += 12
    else:
        risk_factors_identified.append("No bias mitigation plan specified")
    if p.has_transparency_plan:
        risk_score += 8
    if p.nsaid_pillar == "security":
        risk_score -= 10
        risk_factors_identified.append("Defense/security application — elevated scrutiny required")
    risk_score = max(5, min(100, risk_score))
    ethical_risk_inverted = risk_score  # high risk score = low risk

    # ── 4. Data Governance Readiness ──────────────
    data_score = 55
    data_types_count = len(p.data_types)
    if data_types_count >= 3:
        data_score += 15
    elif data_types_count == 1:
        data_score -= 10
    if not p.uses_personal_data:
        data_score += 15
    if p.has_transparency_plan:
        data_score += 10
    if p.cross_ministry:
        data_score -= 12  # cross-ministry data sharing is harder
    data_score = max(5, min(100, data_score))

    # ── 5. Resource Adequacy ───────────────────────
    resource_score = 65
    if p.budget >= 5_000_000:
        resource_score += 10
    if p.budget >= 20_000_000:
        resource_score += 8
    if p.timeline_months <= 6 and p.budget < 500_000:
        resource_score -= 20
    if p.has_ai_expertise:
        resource_score += 8
    # Ministry funding signals
    ministry_size_factor = {
        "Ministry of Health": 15, "Ministry of Interior": 15, "Ministry of Commerce": 10,
        "Saudi Authority for Data and AI": 12, "Ministry of Education": 10,
        "General Entertainment Authority": 5, "Saudi Aramco": 18,
    }
    resource_score = min(100, resource_score + ministry_size_factor.get(p.ministry, 5))
    resource_score = max(5, min(100, resource_score))

    # ── 6. Impact & Scalability ────────────────────
    impact_score = 50
    if p.target_beneficiaries > 1_000_000:
        impact_score += 25
    elif p.target_beneficiaries > 100_000:
        impact_score += 15
    elif p.target_beneficiaries > 10_000:
        impact_score += 8
    if p.cross_ministry:
        impact_score += 12
    if p.expected_outcome in ["national_scale", "vision_2030_priority"]:
        impact_score += 15
    elif p.expected_outcome == "regional":
        impact_score += 8
    impact_score = max(5, min(100, impact_score))

    # ── WEIGHTED OVERALL SCORE ─────────────────────
    overall = (
        strategic_score * EVALUATION_CRITERIA["strategic_alignment"]["weight"] +
        feasibility_score * EVALUATION_CRITERIA["technical_feasibility"]["weight"] +
        ethical_risk_inverted * EVALUATION_CRITERIA["ethical_risk"]["weight"] +
        data_score * EVALUATION_CRITERIA["data_readiness"]["weight"] +
        resource_score * EVALUATION_CRITERIA["resource_adequacy"]["weight"] +
        impact_score * EVALUATION_CRITERIA["impact_outcome"]["weight"]
    )
    overall = round(overall, 1)

    # ── TIER ASSIGNMENT ────────────────────────────
    if overall >= 80:
        tier = "🏆 Tier 1 — Strategic National Priority"
        recommendation = "APPROVE — Fast-track for NSDAI funding consideration. Strong alignment with Vision 2030."
    elif overall >= 68:
        tier = "✅ Tier 2 — Approved with Conditions"
        recommendation = "APPROVE WITH CONDITIONS — Requires PDPL compliance verification and bias audit before deployment."
    elif overall >= 52:
        tier = "⚠️ Tier 3 — Needs Revision"
        recommendation = "REVISE AND RESUBMIT — Address scoring gaps. Consider cross-ministry partnership to improve scale."
    else:
        tier = "❌ Tier 4 — Not Recommended"
        recommendation = "NOT RECOMMENDED — Significant misalignment with NSDAI or unmitigated ethical risks. Reconsider approach."

    # ── STRENGTHS & GAPS ───────────────────────────
    strengths = []
    gaps = []
    recs = []

    if strategic_score >= 75:
        strengths.append(f"Strong NSDAI alignment ({strategic_score}/100) — matches {pillar['label']} pillar")
    elif strategic_score < 60:
        gaps.append(f"Weak NSDAI alignment ({strategic_score}/100) — reframe project around Vision 2030 goals")

    if feasibility_score >= 75:
        strengths.append(f"Technically sound ({feasibility_score}/100) — realistic timeline and expertise available")
    elif feasibility_score < 55:
        gaps.append(f"Feasibility concerns ({feasibility_score}/100) — review timeline, budget, or expertise gaps")

    if risk_score >= 75:
        strengths.append(f"Low ethical risk profile ({risk_score}/100) — strong safeguards in place")
    elif risk_score < 55:
        gaps.append(f"HIGH ETHICAL RISK ({100-risk_score}/100) — must implement bias mitigation & transparency plan before proceeding")

    if data_score >= 70:
        strengths.append(f"Data governance adequate ({data_score}/100)")
    else:
        gaps.append(f"Data governance gap ({data_score}/100) — ensure PDPL compliance and cross-ministry data agreements")

    if impact_score >= 70:
        strengths.append(f"High-impact project ({impact_score}/100) — {p.target_beneficiaries:,} beneficiaries targeted")
    elif p.target_beneficiaries < 10_000:
        gaps.append(f"Limited scalability — only {p.target_beneficiaries:,} beneficiaries. Consider national scope.")

    if p.cross_ministry:
        strengths.append("Cross-ministry collaboration enhances strategic value")

    if p.has_ai_expertise:
        strengths.append("AI expertise confirmed — reduces implementation risk")
    else:
        recs.append("Hire or partner with AI-experienced team before deployment")

    if not p.has_bias_mitigation:
        recs.append("Develop and submit an AI bias mitigation & explainability plan")
    if not p.has_transparency_plan:
        recs.append("Create public-facing AI transparency documentation for citizens")
    if p.uses_biometric:
        recs.append("Subject to SDAIA's Biometric AI Ethics Guidelines — submit for review")
    if p.uses_predictive_ai:
        recs.append("Predictive AI requires human-in-the-loop safeguards and appeal mechanism")

    # ── BUILD RESULT ────────────────────────────────
    result = EvaluationResult(
        proposal_id=proposal_id,
        overall_score=overall,
        recommendation=recommendation,
        tier=tier,
        evaluation_details={
            "strategic_alignment": round(strategic_score, 1),
            "technical_feasibility": round(feasibility_score, 1),
            "ethical_risk": round(100 - risk_score, 1),  # report as RISK level
            "data_readiness": round(data_score, 1),
            "resource_adequacy": round(resource_score, 1),
            "impact_outcome": round(impact_score, 1),
        },
        ethical_risk_profile={
            "overall_risk_score": round(100 - risk_score, 1),
            "risk_rating": "LOW" if risk_score >= 75 else ("MEDIUM" if risk_score >= 55 else "HIGH"),
            "factors_identified": risk_factors_identified,
        },
        nsaid_alignment={
            "primary_pillar": p.nsaid_pillar,
            "pillar_label": pillar["label"],
            "pillar_icon": pillar["icon"],
            "nsdai_targets": pillar["nsdai_targets"],
            "alignment_score": round(strategic_score, 1),
        },
        strengths=strengths,
        gaps=gaps,
        recommendations=recs,
        submitted_at=submitted_at,
    )
    return result


# ─────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    return open("static/index.html").read()


@app.post("/api/submit", response_model=EvaluationResult)
async def submit_proposal(
    ministry: str = Form(...),
    project_name: str = Form(...),
    project_type: str = Form("government_ai"),
    description: str = Form(""),
    nsaid_pillar: str = Form(...),
    budget: float = Form(...),
    timeline_months: int = Form(...),
    data_types: str = Form("government_ops"),
    target_beneficiaries: int = Form(0),
    has_ai_expertise: str = Form("false"),
    uses_personal_data: str = Form("false"),
    uses_biometric: str = Form("false"),
    uses_predictive_ai: str = Form("false"),
    has_transparency_plan: str = Form("false"),
    has_bias_mitigation: str = Form("false"),
    cross_ministry: str = Form("false"),
    expected_outcome: str = Form("single_entity"),
    contact_name: str = Form(""),
    contact_email: str = Form(""),
):
    def b(val: str) -> bool:
        return val.lower() in ("true", "1", "yes") if val else False

    proposal = ProposalSubmission(
        ministry=ministry,
        project_name=project_name,
        project_type=project_type,
        description=description or project_name,
        nsaid_pillar=nsaid_pillar,
        budget=budget,
        timeline_months=timeline_months,
        data_types=[d.strip() for d in data_types.split(",") if d.strip()] or ["government_ops"],
        target_beneficiaries=target_beneficiaries,
        has_ai_expertise=b(has_ai_expertise),
        uses_personal_data=b(uses_personal_data),
        uses_biometric=b(uses_biometric),
        uses_predictive_ai=b(uses_predictive_ai),
        has_transparency_plan=b(has_transparency_plan),
        has_bias_mitigation=b(has_bias_mitigation),
        cross_ministry=b(cross_ministry),
        expected_outcome=expected_outcome,
        contact_name=contact_name,
        contact_email=contact_email,
    )

    result = evaluate_proposal(proposal)
    proposals_db[result.proposal_id] = {
        "proposal": proposal.model_dump(),
        "result": result.model_dump(),
        "submitted_at": result.submitted_at,
    }
    return result


# Seed demo data after app is fully set up
seed_demo_data()


@app.get("/api/proposals")
async def list_proposals():
    return [
        {
            "proposal_id": pid,
            "project_name": data["proposal"]["project_name"],
            "ministry": data["proposal"]["ministry"],
            "overall_score": data["result"]["overall_score"],
            "tier": data["result"]["tier"],
            "submitted_at": data["submitted_at"],
        }
        for pid, data in proposals_db.items()
    ]


@app.get("/api/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    if proposal_id not in proposals_db:
        raise HTTPException(404, "Proposal not found")
    return proposals_db[proposal_id]


# ─────────────────────────────────────────────
# DASHBOARD ENDPOINTS
# ─────────────────────────────────────────────
@app.get("/api/dashboard")
async def get_dashboard():
    """Aggregated portfolio stats across all proposals."""
    if not proposals_db:
        return {
            "total_proposals": 0, "avg_score": 0.0,
            "tier_breakdown": {"tier1": 0, "tier2": 0, "tier3": 0, "tier4": 0},
            "pillar_coverage": {p: {"count": 0, "avg_score": 0.0} for p in ["health","governance","economy","security","society"]},
            "ministry_summary": [], "monthly_submissions": [],
            "gap_pillars": ["health","governance","economy","security","society"],
            "high_risk_count": 0, "pdpl_flags": 0,
        }

    all_results = [d["result"] for d in proposals_db.values()]
    total = len(all_results)
    avg_score = round(sum(r["overall_score"] for r in all_results) / total, 1)

    # Tier breakdown
    tier_counts = {"tier1": 0, "tier2": 0, "tier3": 0, "tier4": 0}
    for r in all_results:
        s = r["overall_score"]
        if s >= 80: tier_counts["tier1"] += 1
        elif s >= 68: tier_counts["tier2"] += 1
        elif s >= 52: tier_counts["tier3"] += 1
        else: tier_counts["tier4"] += 1

    # Pillar coverage
    pillars = ["health", "governance", "economy", "security", "society"]
    pillar_data = {p: {"scores": [], "count": 0} for p in pillars}
    for d in proposals_db.values():
        p = d["proposal"]["nsaid_pillar"]
        if p in pillar_data:
            pillar_data[p]["scores"].append(d["result"]["overall_score"])
            pillar_data[p]["count"] += 1

    pillar_coverage = {}
    for p in pillars:
        scores = pillar_data[p]["scores"]
        pillar_coverage[p] = {
            "count": pillar_data[p]["count"],
            "avg_score": round(sum(scores)/len(scores), 1) if scores else 0.0,
        }

    # Gap pillars (< 3 proposals)
    gap_pillars = [p for p in pillars if pillar_data[p]["count"] < 3]

    # Ministry summary
    ministry_data = {}
    for d in proposals_db.values():
        m = d["proposal"]["ministry"]
        if m not in ministry_data:
            ministry_data[m] = {"scores": [], "budget": 0}
        ministry_data[m]["scores"].append(d["result"]["overall_score"])
        ministry_data[m]["budget"] += d["proposal"]["budget"]

    ministry_summary = [
        {
            "ministry": m,
            "count": len(v["scores"]),
            "avg_score": round(sum(v["scores"])/len(v["scores"]), 1),
            "total_budget": v["budget"],
        }
        for m, v in ministry_data.items()
    ]
    ministry_summary.sort(key=lambda x: x["count"], reverse=True)

    # Monthly submissions
    from collections import defaultdict
    monthly = defaultdict(int)
    for d in proposals_db.values():
        month = d["submitted_at"][:7]  # YYYY-MM
        monthly[month] += 1
    monthly_submissions = [{"month": m, "count": c} for m, c in sorted(monthly.items())]

    # High risk & PDPL flags
    high_risk_count = sum(1 for r in all_results if r["evaluation_details"]["ethical_risk"] > 50)
    pdpl_flags = sum(1 for d in proposals_db.values() if d["proposal"]["uses_personal_data"])
    cross_ministry_count = sum(1 for d in proposals_db.values() if d["proposal"]["cross_ministry"])
    total_budget = sum(d["proposal"]["budget"] for d in proposals_db.values())

    # Recent proposals (last 10)
    recent_sorted = sorted(proposals_db.items(), key=lambda x: x[1]["submitted_at"], reverse=True)
    recent_proposals = [
        {
            "proposal_id": pid,
            "project_name": d["proposal"]["project_name"],
            "ministry": d["proposal"]["ministry"],
            "pillar": d["proposal"]["nsaid_pillar"],
            "overall_score": d["result"]["overall_score"],
            "tier": d["result"]["tier"],
        }
        for pid, d in recent_sorted[:10]
    ]

    return {
        "total_proposals": total,
        "avg_score": avg_score,
        "tier_breakdown": tier_counts,
        "pillar_coverage": pillar_coverage,
        "ministry_summary": ministry_summary,
        "monthly_submissions": monthly_submissions,
        "gap_pillars": gap_pillars,
        "high_risk_count": high_risk_count,
        "pdpl_flags": pdpl_flags,
        "cross_ministry_count": cross_ministry_count,
        "total_budget": total_budget,
        "recent_proposals": recent_proposals,
    }


@app.get("/api/dashboard/recent")
async def get_dashboard_recent():
    """Last 10 proposals for the dashboard."""
    sorted_proposals = sorted(
        proposals_db.items(),
        key=lambda x: x[1]["submitted_at"],
        reverse=True,
    )
    return [
        {
            "proposal_id": pid,
            "project_name": d["proposal"]["project_name"],
            "ministry": d["proposal"]["ministry"],
            "pillar": d["proposal"]["nsaid_pillar"],
            "overall_score": d["result"]["overall_score"],
            "tier": d["result"]["tier"],
            "submitted_at": d["submitted_at"],
        }
        for pid, d in sorted_proposals[:10]
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
