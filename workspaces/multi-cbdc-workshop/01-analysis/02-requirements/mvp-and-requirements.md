# FX Settlement Lock — MVP and Requirements Breakdown

**Project:** mBridge FX Settlement Lock Simulation
**Phase:** 02 — Requirements
**Author:** requirements-analyst
**Date:** 2026-04-30

---

## 1. MVP Definition

The Minimum Viable Product is a **standalone Python package** that reproduces the simulation from `fx_settlement_lock.py` in a production-grade, auditable form, plus a web-based visualization for non-technical stakeholders.

### MVP Feature List

| ID     | Feature                    | Description                                                                                                | Buyer Priority     |
| ------ | -------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------ |
| MVP-01 | Settlement engine core     | The `SettlementEngine` class that models parties, currencies, Nostro accounts, and atomic settlement logic | P0 — Core          |
| MVP-02 | Scenario runner            | Load and execute settlement scenarios from YAML/JSON configuration files                                   | P0 — Core          |
| MVP-03 | Pairwise settlement matrix | Generate the NxN settlement success matrix for all party-currency pairs                                    | P0 — Core          |
| MVP-04 | Settlement lock detection  | Identify which leg blocks atomic settlement and explain why                                                | P0 — Core          |
| MVP-05 | CLI interface              | `fx-settlement-lock run scenario.yaml` — analyst-facing command                                            | P0 — Core          |
| MVP-06 | Web visualization          | Browser-based interactive view of settlement paths and the pairwise matrix                                 | P1 — Stakeholder   |
| MVP-07 | Pre-built scenario library | JSON/YAML files for scenarios A-F in the current simulation                                                | P1 — Validation    |
| MVP-08 | Documentation              | Sphinx docs with API reference, scenario format spec, and architecture overview                            | P1 — Institutional |

### MVP Non-Goals (Out of Scope for V1)

- Multi-currency FX rate handling (numeraire problem)
- Privacy-preserving settlement (the Oxford/SMU trilemma)
- Integration with real mBridge systems
- SaaS hosting or cloud deployment
- Mobile or offline-native interfaces
- Automated report generation

---

## 2. Full Roadmap

### Phase 2: Extended Settlement Modeling

| ID   | Feature                        | Description                                                                                                                       |
| ---- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| R-01 | Multi-hop pathfinding          | Given a settlement goal, automatically find the optimal settlement path (including bridging via HKMA-style dual-issuance parties) |
| R-02 | FX rate numeraire support      | Accept FX rate input and attempt value-equivalent settlement verification across currency pairs                                   |
| R-03 | Settlement failure probability | Model probabilistic settlement failure given Nostro account liquidity constraints                                                 |
| R-04 | Scenario comparison tool       | Diff the results of two scenarios side-by-side                                                                                    |
| R-05 | Batch scenario runner          | Run hundreds of scenarios from a directory and aggregate results                                                                  |

### Phase 3: Institutional Features

| ID   | Feature                          | Description                                                           |
| ---- | -------------------------------- | --------------------------------------------------------------------- |
| R-06 | REST API                         | Expose settlement engine via API for internal bank system integration |
| R-07 | Authentication and rate limiting | OAuth2 + API key auth, per-tenant rate limits                         |
| R-08 | Scenario sharing                 | Allow institutions to share scenario definitions (encrypted at rest)  |
| R-09 | Report generation                | PDF/HTML reports for internal stakeholder presentation                |
| R-10 | Air-gapped deployment package    | Docker image + helm chart for on-premises deployment                  |

### Phase 4: Research Extensions

| ID   | Feature                         | Description                                                                        |
| ---- | ------------------------------- | ---------------------------------------------------------------------------------- |
| R-11 | Plugin architecture             | Allow researchers to add custom party types, currency models, and settlement rules |
| R-12 | CoTi extension                  | Model contingent settlement (CoTi) as an alternative to atomic settlement          |
| R-13 | Privacy-preserving settlement   | Simulate the Oxford/SMU threshold encryption approach to settlement privacy        |
| R-14 | Network topology analysis       | Visualize the settlement network as a graph, highlighting bridge nodes             |
| R-15 | Time-zone aware Nostro modeling | Model Nostro account funding delays across time zones                              |

---

## 3. Key Architectural Decisions

### ADR-01: Settlement Engine as a Pure Function

**Status:** Proposed

**Context:** The settlement engine must be auditable by institutional buyers (central banks require the ability to inspect and validate the logic). It also needs to be fast enough for batch scenario analysis.

**Decision:** The core `SettleAtomically(legs)` function is a pure function with no side effects. Party and Nostro state are managed in a separate `SettlementContext` object that is created fresh for each scenario run.

**Consequences:**

- **Positive:** The engine is fully deterministic and auditable. Scenarios can be serialized to JSON and replayed exactly. Testing is trivial.
- **Positive:** Parallel execution of scenarios is trivial (no shared state).
- **Negative:** Users accustomed to in-place state mutation must adapt.

**Alternatives considered:**

- _In-place mutation_ — rejected because it makes scenario replay non-deterministic and auditing harder.
- _Database-backed state_ — rejected because it introduces infrastructure dependencies unsuitable for air-gapped deployment.

---

### ADR-02: Scenario Definition Format — YAML + JSON Schema

**Status:** Proposed

**Context:** Institutional buyers need to define their own scenarios (e.g., "what if CBUAE opens a THB Nostro?"). These scenarios must be shareable, versionable, and validatable.

**Decision:** Scenarios are defined in YAML with a JSON Schema that describes the full schema. The schema is published alongside the tool so users can validate scenarios in their own CI pipelines.

**Consequences:**

- **Positive:** Human-readable, easy to hand-edit.
- **Positive:** Schema validation catches errors before simulation runs.
- **Negative:** YAML is not ideal for complex nested structures (but JSON Schema handles validation, not ergonomics).

**Alternatives considered:**

- _Pure JSON_ — rejected as less human-readable for the primary use case (treasury technologists writing what-if scenarios).
- _Domain-specific language (DSL)_ — rejected because it adds a custom parsing layer that auditing teams don't want to trust.
- _Python API only_ — rejected because non-programmer treasury staff need a configuration-file interface.

---

### ADR-03: Deployment Model — Client-Side Python Package (Not Server)

**Status:** Proposed

**Context:** Central bank data cannot leave the institution's premises. Correspondent banks have strict data residency requirements. BIS cannot host a tool that processes member bank data.

**Decision:** The primary product is a Python package distributed via PyPI and GitHub. Deployment is `pip install fx-settlement-lock`. For the web visualization, a static HTML/JS bundle is served from the user's own infrastructure (or runs locally).

**Consequences:**

- **Positive:** No data ever leaves the institution. Full auditability of the execution environment.
- **Positive:** No SaaS infrastructure costs. No vendor lock-in for buyers.
- **Negative:** Support is harder (different environments). Upgrades require coordinated rollouts.
- **Negative:** SaaS recurring revenue is not available for the central bank segment.

**Alternatives considered:**

- _SaaS with data residency addendum_ — rejected because central banks often cannot accept third-party data processing agreements.
- _Hosted trial instance_ — viable for correspondent banks; worth adding in Phase 3.

---

### ADR-04: Visualization — Standalone HTML Over Framework

**Status:** Proposed

**Context:** The web visualization must work on air-gapped central bank intranets without access to CDN-hosted libraries. It also must not require a build step.

**Decision:** The visualization is a single self-contained HTML file with inline CSS and JavaScript. It uses vanilla JS with no framework dependencies. It loads scenario data from a local JSON file.

**Consequences:**

- **Positive:** Zero deployment complexity. Open the HTML file and it works.
- **Positive:** No CDN dependency. Works on air-gapped networks.
- **Positive:** Auditability: a technically proficient reader can read the JS and understand exactly what it does.
- **Negative:** Less interactive than a React/Vue app. Animations are limited.
- **Negative:** No real-time collaboration features (out of scope anyway).

**Alternatives considered:**

- _React SPA deployed to S3_ — rejected due to CDN and build-step requirements.
- _Jupyter notebook with ipywidgets_ — good for researchers but not for non-technical stakeholders.

---

### ADR-05: API Layer — Optional, Opt-In

**Status:** Proposed

**Context:** An API layer enables correspondent banks to integrate the settlement engine into internal systems. But building a full API with auth, rate limiting, and versioning adds significant complexity and support burden.

**Decision:** The API is **not** in MVP. It is a Phase 3 feature. The CLI and YAML scenario files are the primary interface for MVP. If a correspondent bank has an internal need, they can build a thin wrapper around the Python package.

**Consequences:**

- **Positive:** MVP is smaller and ships faster.
- **Positive:** No API versioning, auth, or infrastructure burden in MVP.
- **Negative:** Correspondent banks with internal integration needs must wait for Phase 3.

**Alternatives considered:**

- _API in MVP_ — rejected because the auth/infrastructure overhead would delay MVP by 2 months.

---

## 4. Functional Requirements Matrix

| Req ID | Requirement                                              | Input                                                       | Output                                          | Business Logic                                                           | Edge Cases                                        | SDK Mapping                      |
| ------ | -------------------------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------- | -------------------------------- |
| F-01   | Model a party with currency issuance and Nostro accounts | Party definition (name, issued currencies, Nostro balances) | `Party` object                                  | Validate that Nostro balances are non-negative                           | Duplicate currency issuance                       | `Party` dataclass                |
| F-02   | Execute atomic settlement across multiple legs           | List of `Leg` objects                                       | `SettlementAttempt` with success/failure state  | Both debtor must `can_send` and creditor must `can_receive` for all legs | Settlement lock on any leg                        | `settle_atomically()` function   |
| F-03   | Report which leg blocked settlement                      | `SettlementAttempt`                                         | Blocked leg identifier and reason string        | Identify first leg where conditions fail                                 | Multiple simultaneous failures (report first)     | `SettlementAttempt.blocked_leg`  |
| F-04   | Generate pairwise settlement matrix                      | Network of parties and their capabilities                   | NxN matrix of settlement success/failure        | For each party-currency pair, evaluate `can_send`                        | Missing Nostro accounts for non-issued currencies | `print_pair_matrix()` equivalent |
| F-05   | Load scenario from YAML                                  | YAML file path                                              | Parsed scenario with party definitions and legs | JSON Schema validation of scenario structure                             | Invalid schema, missing required fields           | `ScenarioLoader` class           |
| F-06   | CLI run scenario                                         | Scenario YAML path                                          | Console output of settlement results            | Execute F-02, format results for terminal                                | File not found, schema validation errors          | `fx-settlement-lock run` CLI     |

---

## 5. Non-Functional Requirements

### Performance

- Single scenario execution: <100ms
- 100-scenario batch: <5 seconds
- Pairwise matrix (10 parties, 5 currencies): <500ms
- Memory footprint: <50MB for any scenario

### Security

- No network calls during simulation execution (air-gap compatible)
- No secrets in scenario files (no credentials, tokens, or keys)
- Settlement results contain no PII (party names are institutional identifiers, not personal data)
- Scenario files are validated against schema before execution (blocks code injection)

### Scalability

- Support up to 50 parties and 20 currencies in a single scenario
- Network topology with up to 200 settlement paths evaluated

### Auditability

- Every scenario execution is deterministic given the same input
- Scenario files can be committed to git and reviewed in diff
- Settlement results are serializable to JSON for audit logging

### Compatibility

- Python 3.10+ (no `match` statement for compatibility with 3.10)
- No C extensions (pure Python for auditability)
- Works on Linux, macOS, Windows (pure Python + stdlib)

---

## 6. Implementation Dependencies

### Must Have (MVP)

- Python 3.10+ standard library only
- PyYAML (for scenario file parsing)
- jsonschema (for scenario validation)
- click (for CLI framework)
- No external runtime dependencies beyond stdlib + PyYAML + jsonschema + click

### Should Have (MVP polish)

- rich (for terminal output formatting)
- sphinx (for documentation)

### Phase 2+

- NetworkX (for pathfinding in multi-hop scenarios)
- matplotlib / plotly (for settlement path visualization)
- fastapi + uvicorn (for optional REST API)

---

## 7. Success Criteria

### MVP Success

- [ ] All 6 scenarios from the original simulation produce identical results
- [ ] CLI runs a scenario from YAML in under 100ms
- [ ] Web visualization renders the pairwise matrix correctly
- [ ] Scenario schema validation catches malformed input with a clear error
- [ ] Documentation includes API reference and scenario format specification
- [ ] Tool runs fully air-gapped (no network required for execution)

### Full Product Success

- [ ] At least 2 central bank treasury teams have used the tool for internal analysis
- [ ] BIS or equivalent institution has cited the tool in a publication
- [ ] Academic paper using the tool has been submitted to a peer-reviewed venue
- [ ] Support contract signed with at least 1 institutional buyer
