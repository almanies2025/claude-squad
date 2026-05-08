---
description: "Sync claude-squad .claude artifacts with upstream kailash-coc-claude-py template"
enabled: true
---

**Sync is disabled.** claude-squad has forked from the upstream USE template (2026-05-XX).
Local divergence includes: Kailash-specific artifact pruning, csq-scope rules adaptation,
and Foundation-naming rewrites. Running sync would overwrite these deliberate changes.

Upstream: `https://github.com/terrene-foundation/kailash-coc-claude-py`
Loom: `../../loom/kailash-coc-claude-py/`

## If Sync Is Needed

If upstream changes must be pulled in future:

1. Re-enable: set `enabled: true` in this file
2. Fetch latest: `git fetch origin` in `../../loom/kailash-coc-claude-py/`
3. Diff: compare upstream changes against local `.claude/` state
4. Selective merge: cherry-pick only relevant upstream changes (csq-relevant rules/agents only)
5. Validate: run `/codify` to validate artifact quality
6. Re-disable: set `enabled: false` after sync

## Report

```
Sync is disabled (forked from upstream).
Template: kailash-coc-claude-py
Upstream: https://github.com/terrene-foundation/kailash-coc-claude-py
Policy: fork — sync would overwrite local divergence; re-enable manually if needed
```
