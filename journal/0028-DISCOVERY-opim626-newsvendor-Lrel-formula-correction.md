---
name: OPIM626 Newsvendor Formula Correction
description: Root cause identified — student used φ(z) instead of L_rel = φ(z)/z − (1−Φ(z)); corrected Q1 and Q2 profit figures
type: discovery
---

## OPIM626 Newsvendor Formula Error — Root Cause

**Context**: Student's solution `OPIM626_SOLUTION.docx` (at `C:\Users\User\Desktop\Supply\`) had wrong profit figures across Q1 and Q2. This session wrote `OPIM626_SOLUTION_CORRECTED.docx`.

### Root Error

Student used **φ(z) (normal PDF value)** as the newsvendor loss function instead of the **standard per-unit loss function**:

```
L_rel = φ(z)/z − (1−Φ(z))   [standard per-unit newsvendor loss]
E[underage in units] = σ × L_rel
E[overage in units]  = (Q−μ) + σ × L_rel
```

**Validated against**:

- Columbia lecture notes (lect_07.pdf): `L(z) = φ(z) − z·Φ(−z)` (equivalent form)
- UTDallas newsvendor slides (omnewsvendor.pdf): Excel formula `NORM.S.DIST(z,0,1,0) − z*(1-NORM.DIST(z,0,1,1))`
- Reference Excel `Newsvendor_SweaterParadise.xlsx`: Lost Sales = σ × [φ(z)−z(1−Φ(z))] = 4.968 ✓ at z=1.15, σ=80

### All Corrected Values

|                      | Student's (wrong)         | Corrected        |
| -------------------- | ------------------------- | ---------------- |
| Q1a L_rel            | 0.3188 (φ)                | **0.2243**       |
| Q1a Geoff profit     | $6,409.40                 | **$6,404.00**    |
| Q1a Lands End profit | $8,390.60                 | **$15,987.03**   |
| Q1b L_rel            | 0.3989 (φ)                | **2.1895**       |
| Q1b Geoff profit     | $7,141.05                 | **$7,135.00**    |
| Q1b Lands End profit | $15,159.26                | **$15,153.10**   |
| Q1d Geoff (e×E[D])   | 5×280=$1,400              | **5×272=$6,316** |
| Q1d Lands End profit | $17,437.61                | **$16,084.00**   |
| **Q2a L_rel**        | **22.66 (unknown table)** | **0.0240**       |
| Q2a profit/color     | $40,782.20                | **$22,886.40**   |
| Q2a total profit     | $81,564.40                | **$45,772.80**   |
| Q2b profit           | $58,302.90                | **$52,880.10**   |
| Δ (postponement)     | −$23,261.50 ❌            | **+$7,107.30** ✓ |

**Q3 unchanged** — was already correct.

### Files

- Corrected: `C:\Users\User\Desktop\Supply\OPIM626_SOLUTION_CORRECTED.docx`
- Source: `C:\Users\User\Desktop\EF\OPIM626_3_2026_distributed.pdf` (assignment)
- Reference: `C:\Users\User\Desktop\EF\Newsvendor_SweaterParadise.xlsx`
