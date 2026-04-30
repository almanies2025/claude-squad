# RISK-001: Reconciliation Divergence Creates Material Liability

## Metadata

| Field      | Value                   |
| ---------- | ----------------------- |
| Risk ID    | RISK-001                |
| Severity   | Critical                |
| Category   | Yield Reconciliation    |
| Discovered | 2026-04-30              |
| Source     | Unit Economics Red Team |

## Finding

Annual reconciliation divergence on $1B deposit book = ~$900K/year (0.09% of notional), not 1–3bp daily. The daily figure compounds to ~$1.8–2.7M over 90 days.

The day-count convention mismatch (FloatYield: 365/actual vs. Treasuries: actual/actual) creates **systematic, non-random divergence** that cannot be resolved by tolerance thresholds — only deferred.

## Impact

- Liability scales with deposit book size, not account count
- At $1B book, 90-day cumulative = $1.8–2.7M unresolved discrepancy
- Simultaneous impact across all banks in falling rate environment
- Legal and relationship cost of contested disputes not modeled

## Root Cause (5-Why)

1. **Why**: Reconciliation discrepancy exceeds revenue
2. **Why**: Fee model (per-account) does not scale with deposit liability
3. **Why**: Liability is structural (day-count convention) not random
4. **Why**: Contractual tolerance threshold defers, not resolves, the liability
5. **Why**: Business model misalignment — revenue per account, liability per dollar deposited

## Mitigation

1. Restructure fee to basis-points on deposits managed (aligns revenue with liability)
2. Pre-fund reconciliation reserve from platform fees
3. Add explicit contract language on absorption terms and renegotiation triggers

## Status

**OPEN** — Requires business model restructuring before proceeding
