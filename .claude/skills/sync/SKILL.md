---
description: "Sync claude-squad .claude artifacts with upstream kailash-coc-claude-py template"
enabled: true
---

Sync pulls changes from `../../loom/kailash-coc-claude-py/` into claude-squad's `.claude/` directory.

Upstream: `https://github.com/terrene-foundation/kailash-coc-claude-py`

## Usage

`/sync` — run the sync workflow

## Sync Protocol

1. Pull latest from upstream into `../../loom/kailash-coc-claude-py/`
2. Diff against current `.claude/` state
3. Present changes for review before applying
4. After merge, run `/codify` to validate artifact quality

## Report

```
Sync is active.
Template: kailash-coc-claude-py
Upstream: https://github.com/terrene-foundation/kailash-coc-claude-py
Policy: review changes before applying; codify validation after merge
```
