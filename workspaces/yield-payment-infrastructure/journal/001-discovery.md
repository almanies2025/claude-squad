# DISCOVERY: Reconciliation Liability Scales with Float, Not Accounts

## Finding

The reconciliation fee misalignment is worse than initially stated. The day-count mismatch creates a liability of ~$900K/year per $1B book, which is:

- NOT proportional to accounts (customer count)
- IS proportional to deposits (float)

At Year 3 ($1.5B ADB), the liability is $1.35M/year. With the proposed 50 bps fee, revenue is $7.5M/year, yielding 5.6× coverage. This is healthy, but only if the fee model change is executed before hitting Year 3 scale.

**Critical timing**: The sponsor bank renegotiation pressure will peak at Year 2–3, exactly when the new fee model needs to be in production.

## Implication

The fee model transition must happen no later than Year 2 to avoid a scenario where:

1. Old fee model generates $2–3M revenue
2. Liability is already $900K–$1.8M
3. Bank sees FloatYield margins and triggers renegotiation
4. FloatYield has no leverage because switching cost is too high

**Fix**: Lock in the 50 bps ADB pricing with current sponsor bank if possible, or accelerate CUSO migration.

## Status

Open
