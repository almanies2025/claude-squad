# FloatYield — Course Deliverables Plan

## Context

FloatYield is a B2B yield-bearing payment infrastructure platform. The course requires: written report + pitch deck + working demo. All prior analysis is complete. Implementation is the remaining work.

## Deliverables

1. **yield_engine.py** — Python stdlib yield calculation engine
2. **yield_cli.py** — Interactive CLI interface
3. **pitch_deck.html** — Standalone HTML slide deck
4. **FloatYield_Report.md** — Comprehensive written report
5. **README.md** — Project packaging + how to run
6. **demo_test_run.txt** — Verified test output

## Order

1. yield_engine.py (foundation — all other components depend on it)
2. yield_cli.py (depends on engine)
3. Integration test (verifies 1+2)
4. pitch_deck.html (independent)
5. FloatYield_Report.md (independent, uses analysis files)
6. README.md + packaging (depends on all above)

## Constraints

- Python stdlib only — no PyPI dependencies
- pitch_deck.html: inline CSS, no external resources, single file
- yield_cli.py: pure stdlib, argparse-based
