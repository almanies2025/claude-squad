# RISK-002: Clearing-Hub Framing Is Politically Sensitive for HKMA

## Risk Record

| Field        | Value                      |
| ------------ | -------------------------- |
| **ID**       | RISK-002                   |
| **Type**     | RISK                       |
| **Severity** | HIGH                       |
| **Date**     | 2026-04-30                 |
| **Source**   | bis-engagement-red-team.md |

## Finding

The corrected CNY-dominance mechanism (HKMA as offshore CNY clearing hub via PBOC RTGS) makes HKMA LESS likely to engage as a co-sponsor. The correction improved technical accuracy but damaged the sponsorship pitch. The clearing-hub framing reveals a structural dependency that HKMA may not want to publicize.

### Why the Correction Made Things Worse

**Original framing (dual-issuance, since corrected):**

- Positioned HKMA as a peer monetary authority with its own CNY liability
- HKMA appeared to be a policy authority making a sovereign decision
- Politically clean: HKMA choosing to support CNY internationalization

**Corrected framing (HKMA as clearing hub):**

- Reveals HKMA processes CNY on behalf of PBOC
- Implicitly acknowledges PBOC RTGS control over Hong Kong's CNY infrastructure
- Positions HKMA as a service provider, not a policy authority
- Creates public record that PBOC controls Hong Kong's CNY clearing infrastructure
- Invites scrutiny: is HKMA a monetary authority or a processing conduit?

### The Geopolitical Dimension

In the current environment (US-China tensions, de-dollarization debates, scrutiny of Hong Kong's financial autonomy), HKMA co-sponsoring a workshop on "CNY dominance enabled by Hong Kong's clearing hub" creates optics HKMA leadership may actively avoid:

- Associates HKMA with a specific monetary narrative (CNY dominance)
- Creates a public record of the PBOC-HKMA structural relationship
- Risks drawing PBOC attention to a workshop that frames CNY as dominant
- Potentially invites questions about Hong Kong's monetary policy independence

### Quantitative Assessment of HKMA Response Likelihood

| Response             | Likelihood | Notes                                                    |
| -------------------- | ---------- | -------------------------------------------------------- |
| No response          | 40%        | Most likely; silence avoids political cost               |
| Polite decline       | 30%        | "Bandwidth constraints" — coded no                       |
| Subordinate referral | 20%        | Cannot approve; buys time but no decision                |
| Genuine interest     | 10%        | Requires specific internal mandate for FinTech promotion |

## Mitigation

1. **Do not ask HKMA to co-sponsor.** Approach HKMA as technical advisor or observer only.
2. **Do not lead with CNY-dominance framing in the HKMA outreach.** Lead with "multi-CBDC interoperability" — the CNY-dominance thesis can be workshop content, not sponsorship rationale.
3. **Get signal from BIS before approaching HKMA.** If BIS is not receptive, HKMA engagement is moot.
4. **Pre-qualify MAS as parallel track, not fallback.** MAS has FinTech credibility without the political sensitivity.

## Cross-References

- `04-validate/bis-engagement-red-team.md` — Full BIS engagement red team
- `0007-risk-cny-dominance-mechanism.md` — Prior CNY dominance mechanism correction
