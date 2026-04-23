# ADR-001 — Anomaly Detection: Rule-Based vs. ML-Based for v1

**Status**: Accepted
**Date**: 2026-04-20
**Phase**: analyze

---

## Context

The product's core value is surfacing anomalies in portfolio company KPIs before the quarterly board pack. We must choose the v1 implementation approach: rule-based thresholds or ML-based detection.

**Constraints that shape the decision:**

1. **Data volume is tiny.** 13–36 months of monthly KPI data = 13–36 observations per metric per company. Nowhere near the volume needed for stable unsupervised ML.
2. **Heterogeneity across companies.** 15 portcos in different industries. A model trained on one portco is useless on another. Cross-portco pooling requires similarity assumptions that don't hold.
3. **Explainability is mandatory.** A PE partner receiving an alert needs a one-sentence reason. "Isolation forest score 0.87" is not acceptable. Partners will not act on scores they can't justify to their investment committee.
4. **False positive cost is high.** A false "EBITDA down 40%" alert that escalates to a GP and turns out to be a mapping bug is a trust-ending event. Partners unsubscribe after ~3 bad alerts.
5. **Zero-data onboarding requirement.** A buyer onboards a new portco Tuesday; they expect working alerts Wednesday. ML requiring 12 months of historical data fails this.
6. **Buyer-side skepticism.** PE partners evaluate quantitative tools skeptically. "Rules you set during onboarding" is a crisp, defensible answer.

---

## Decision

**v1 uses rule-based anomaly detection exclusively. ML-based detection is deferred to v2, where it augments (does not replace) rule-based detection.**

**v1 rule types (5):**

1. **Absolute threshold** — "Gross margin below 25% for any month"
2. **Relative threshold** — "EBITDA falls >15% vs trailing 3-month average"
3. **Directional sustained** — "DSO rises for 3 consecutive months"
4. **Ratio breach** — "Working capital / revenue > 1.5x historical median"
5. **Plan variance** — "Actual revenue < 90% of plan" (requires plan upload)

Thresholds seeded at onboarding from a per-industry default library, reviewed by the PE firm ops lead, and tuned via false-positive feedback loop.

---

## Consequences

**Positive:**

- Works on day one for a newly onboarded company with no historical data
- Every alert is explainable in one sentence; partners can justify action to investment committee
- Deterministic — same input produces same alert; easy to test and audit
- No MLOps infrastructure required in v1
- Buyer-evaluable — a PE firm can look at the rule list and say "yes, those are the things I want to know about"
- False-positive control directly in the customer's hands

**Negative:**

- Cannot catch subtle multivariate anomalies where gross margin, DSO, and headcount drift within individual thresholds but their _joint pattern_ is unusual
- Threshold tuning requires human effort per company in the first 30–60 days
- Doesn't improve automatically as data accumulates

---

## Alternatives Rejected

### Alternative 1 — ML-Based Detection Primary (Isolation Forest + Changepoint Detection)

13–36 monthly observations per metric per company is catastrophically insufficient for stable isolation forest models. Unstable models produce oscillating alert rates — the worst possible failure mode for buyer trust. No explainability path acceptable to a PE investment committee. Zero-data onboarding fallback reinvents the rule-based system with extra infrastructure.

**Rejected for v1.** Revisit when 18+ months of production data across 20+ portcos exists.

### Alternative 2 — Hybrid (Rules Primary, ML Advisory Flag)

Rules fire alerts as in the decision above. ML runs in parallel and adds an "unusual pattern" advisory label to the dashboard (not a push alert). Advisory labels that the partner doesn't trust will be ignored, making the investment unjustified. Still requires ML infrastructure in v1.

**Rejected for v1.** An advisory label is a feature looking for a user.

### Alternative 3 — Statistical Control Charts (CUSUM, EWMA)

Control charts assume roughly stationary distributions with known variance. KPIs during growth or through seasonality violate this. Calibrating control limits requires ~20+ in-control observations — back to the data volume problem. Harder to explain than "margin below 25%."

**Rejected for v1.** Worth revisiting in v2 for specific metrics (DSO, DIO) where the stationarity assumption is more defensible.

---

## Implementation Plan for v1 (Rule-Based)

| Phase                         | Work                                                                                  | Effort      |
| ----------------------------- | ------------------------------------------------------------------------------------- | ----------- |
| 1 — Rule engine               | `AlertRule` + `Alert` entities; 5 rule types; default library per industry            | 1 session   |
| 2 — Explainability + feedback | One-sentence explanation templates; false-positive status + note field; ops dashboard | 0.5 session |
| 3 — Deduplication + lifecycle | Open-alert tracking; suppression; auto-resolution after 2 clean periods               | 0.5 session |
| 4 — Onboarding flow           | Threshold-tuning wizard for new portco; 30-day review checkpoint                      | 0.5 session |

---

## Success Criteria

- [ ] False-positive rate <10% per company after 60 days of tuning
- [ ] Every alert has a one-sentence explanation automatically generated
- [ ] A newly onboarded company gets working alerts within 24 hours with no historical data
- [ ] Zero customer escalations of "why did this alert fire, what does it mean?"
- [ ] Time from metric arrival to delivered alert: <30 minutes p95

---

## Revisit Trigger

Revisit when all three hold simultaneously:

1. 18+ months of production metric history
2. 20+ portfolio companies across 3+ PE firms live
3. At least 10 customer-validated "missed signal" cases where rule-based demonstrably failed to catch something subtle but real

At that point we have the data volume, customer trust, and labelled signal set to justify ML investment.
