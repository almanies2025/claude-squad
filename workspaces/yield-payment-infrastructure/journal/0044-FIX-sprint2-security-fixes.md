---
type: FIX
date: 2026-05-03
created_at: 2026-05-03T00:00:00Z
author: co-authored
session_id: current
session_turn: 3
project: yield-payment-infrastructure
topic: Sprint 2 redteam — 3 security fixes applied
phase: redteam
tags: [sprint2, security, fix, redteam]
---

## Sprint 2 Redteam — Security Fixes

### What Triggered This Round

Ran `/redteam` to validate Sprint 2 implementation after building the ETL simulator and real yield history.

### Fixes Applied

**H-1: CSV error log info disclosure** (`load_yield_events.py:139`)

- Was: `print(f"[WARN] Line {lineno}: skipped — {e} ({raw})", file=sys.stderr)`
- Now: `print(f"[WARN] Line {lineno}: skipped — {e} (missing or invalid field)", file=sys.stderr)`
- Risk: If sponsor bank CSV contained fields beyond the 6 expected (e.g., SSN, account numbers), those would appear in logs

**H-2: validate_db.py --output path traversal** (new finding)

- Added path containment check against `scripts/` directory
- Blocked with exit(1) if path escapes allowed directory
- Verified: `python validate_db.py --output /etc/test.json` → blocked with error

**M-1: ETL get_db() missing check_same_thread=False** (new finding)

- Both `load_yield_events.py` and `run_t1_batch.py` now use `check_same_thread=False`
- Consistent with `main.py`'s `get_db()` implementation
- Prevents `sqlite3.ProgrammingError` if scripts are ever used in threaded context

### Verified Clean

- SQL injection: all queries use `?` parameterized placeholders ✅
- ETL race condition: `INSERT OR IGNORE` + `UNIQUE INDEX` prevents double-insert ✅
- Path traversal: CSV source path containment check still in place ✅
- Input validation: `field_validator` on `ForecastParams` still present ✅
- No hardcoded secrets in any modified files ✅

### Spec Coverage: 100%

All 5 Sprint 2 features verified as implemented and wired to real data.

## For Discussion

1. The directional accuracy of ~45–54% across all models is essentially coin-flip. Is this the expected floor given the 1:1 signal-to-noise ratio in yield data — or should a model that beats random on direction be rewarded even if MAE is higher?
2. M-4 (CORS localhost:3000 only) remains unfixed. For a course project demo this is correct. What's the threshold at which this becomes a real concern — when partners start making browser-based API calls from their own domains?
