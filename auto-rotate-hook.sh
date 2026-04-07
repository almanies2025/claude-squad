#!/usr/bin/env bash
# Auto-rotation hook — DISABLED.
# Auto-rotation caused random account switching when triggered on stale
# rate_limits data. Users now manually swap with `! csq swap N` when they
# hit a rate limit. The user is in control; csq does not silently change
# accounts behind their back.
exit 0
