# ERP Integration Complexity — PE Portfolio Monitoring

## Mid-Market PE-Backed Portco ERP Distribution

> **[VERIFY 2026]**: These are directional estimates. Verify against Software Advice, G2 market share reports, or a sample of actual portco data before finalizing roadmap.

| ERP / Accounting               | Est. Share of Mid-Market PE Portcos | v1 Priority             |
| ------------------------------ | ----------------------------------- | ----------------------- |
| **NetSuite** (Oracle)          | 30–40%                              | Must-have               |
| **QuickBooks Online** (Intuit) | 20–30%                              | Must-have               |
| **Sage Intacct**               | 10–15%                              | Must-have               |
| **Microsoft Dynamics 365 BC**  | 8–12%                               | Nice-to-have v1         |
| **SAP Business One**           | 3–6%                                | Out of v1; CSV fallback |
| **Xero**                       | 2–5%                                | Nice-to-have v1         |
| **Other / bespoke / vertical** | 5–10%                               | CSV upload fallback     |

## Technical Integration Paths

### Direct API Integration

| ERP                   | Auth                    | Protocol                        | Build Effort | Notes                             |
| --------------------- | ----------------------- | ------------------------------- | ------------ | --------------------------------- |
| **QuickBooks Online** | OAuth 2                 | REST                            | 3–5 weeks    | Well-documented; rate limits real |
| **NetSuite**          | TBA / OAuth 2           | SuiteTalk REST + SuiteAnalytics | 6–10 weeks   | Most complex; most valuable       |
| **Sage Intacct**      | Session-based + API key | XML Gateway                     | 4–6 weeks    | Older but stable                  |
| **Dynamics 365 BC**   | OAuth 2                 | OData REST                      | 4–6 weeks    | Modern; growing share             |
| **Xero**              | OAuth 2                 | REST                            | 2–4 weeks    | Cleanest API                      |

### Middleware / Unified API Providers

- **Rutter** — unified accounting API (QBO, Xero, NetSuite, Sage, Dynamics); saves 6–9 months build time but costs 5–15% GM per customer at scale
- **Codat** — similar, more mature, deeper bank/commerce coverage
- **Merge.dev** — broad unified API with accounting; common for early-stage plays

**Trade-off:** Middleware cuts build time but adds dependency risk and ongoing cost. Reasonable v1 strategy; plan in-house migration for top-3 ERPs once unit economics demand it.

### CSV/XLSX Upload Fallback

Always required. Every unsupported ERP or non-integrated subsidiary uses this. SFTP dropbox + standardized template + parser. Covers the tail 10–15% of portcos.

## The Chart-of-Accounts Problem

This is the real integration difficulty, not the API.

Every portco's chart of accounts is different. "Revenue" might be one line at QB-PortcoA and twelve lines at NetSuite-PortcoB. Normalizing requires:

1. A canonical KPI taxonomy
2. A portco-specific mapping layer (human-assisted for first onboarding per portco)
3. Ongoing maintenance — COA changes at portcos trigger remapping

**This is ~40–50% of the product's actual engineering cost** and is where differentiation happens — and where implementation timelines die.

## Integration Risk Register

| Risk                                  | Likelihood                   | Impact | Mitigation                                                    |
| ------------------------------------- | ---------------------------- | ------ | ------------------------------------------------------------- |
| Portco IT refuses API access          | Medium                       | High   | Read-only creds; SOC 2 collateral; CFO onboarding playbook    |
| NetSuite token revocation at portco   | High (1/yr across portfolio) | Medium | Auto-reauth flow; portco-CFO ping workflow                    |
| Middleware (Rutter/Codat) outage      | Medium                       | High   | Circuit breaker; cache last-good; in-house fallback for top-3 |
| COA drift (portco re-charts accounts) | Very High                    | High   | Versioned mapping configs with effective dates                |
| QBO Desktop portcos                   | Medium                       | Medium | Skip or use specialist; be honest with buyers                 |
| API rate limits at large portcos      | Medium                       | Medium | Incremental sync + batching                                   |

## v1 ERP Priority Decision

**Must-have for v1 (covers ~60–70% of portcos):**

1. QuickBooks Online
2. NetSuite
3. Sage Intacct
4. CSV/XLSX upload (universal fallback)

**Nice-to-have v1 (pushes to ~80%):** 5. Dynamics 365 Business Central 6. Xero

**Out of v1:**

- QuickBooks Desktop (technical nightmare; use middleware or skip)
- SAP Business One (complex, niche; CSV fallback)
- On-prem legacy systems
