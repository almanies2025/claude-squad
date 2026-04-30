# GAP-001: No Resolution Mechanism for Tolerance Breach

## Metadata

| Field      | Value                   |
| ---------- | ----------------------- |
| Gap ID     | GAP-001                 |
| Severity   | High                    |
| Category   | Governance / Contract   |
| Discovered | 2026-04-30              |
| Source     | Unit Economics Red Team |

## Finding

The reconciliation architecture relies on a "tolerance threshold agreed in contract" as the resolution mechanism. No such mechanism is defined. The contract draft does not specify:

- Who absorbs variance within tolerance
- What triggers renegotiation when tolerance is breached
- Exit terms if resolution fails
- Dispute resolution (commercial negotiation vs. litigation)

## Impact

- Tolerance breach defaults to commercial negotiation under duress
- FloatYield has structural disadvantage (bank relationship is more important to FloatYield than to the bank)
- Simultaneous breaches across multiple banks create systemic risk
- Legal costs of contested disputes not modeled in unit economics

## Root Cause (5-Why)

1. **Why**: Tolerance breach has no defined resolution path
2. **Why**: Contract draft focuses on getting product working, not liability allocation
3. **Why**: MVP scope excluded legal/commercial framework for stress scenarios
4. **Why**: Urgency of product-market fit overshadowed legal infrastructure
5. **Why**: No red team review of contract architecture before implementation

## Required Action

Add explicit contract language covering:

1. Variance absorption: specify whether FloatYield, bank, or shared absorbs within tolerance
2. Renegotiation triggers: define breach threshold (e.g., 3 consecutive days outside tolerance)
3. Exit provisions: what happens if renegotiation fails — buyout, transition assistance, data return
4. Dispute resolution: commercial arbitration vs. litigation

## Status

**OPEN** — Required before any sponsor bank agreement is signed
