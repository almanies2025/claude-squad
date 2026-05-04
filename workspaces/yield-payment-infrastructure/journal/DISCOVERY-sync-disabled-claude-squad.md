---
name: DISCOVERY sync disabled for claude-squad
description: /sync is a deliberate no-op in claude-squad because it was forked and pruned from kailash-coc-claude-py template
type: DISCOVERY
date: 2026-05-04
created_at: 2026-05-04T13:00:00Z
author: agent
session_id: current
session_turn: 1
project: claude-squad
topic: sync command disabled in claude-squad fork
phase: analyze
tags: [claude-squad, sync, fork, kailash]
---

## Finding: `/sync` Is a No-Op in claude-squad

claude-squad was originally scaffolded from the `kailash-coc-claude-py` USE template on 2026-04-08 (version 1.4.0), then **heavily pruned** for its scope as a Python/bash OAuth rotation tool. The `kailash-coc-claude-py` template has continued to evolve with Kailash SDK-specific content that is completely irrelevant to csq.

### Why Sync Is Disabled

The `VERSION` file at `.claude/VERSION` documents the fork rationale:
- 31 Kailash SDK skills removed (01-core-sdk through 31-error-troubleshooting)
- 6 framework agents removed (dataflow, nexus, kaizen, mcp, infrastructure, pact specialists)
- 5 frontend agents removed (ai-ux, flutter, frontend-developer, react, uiux designers)
- 7 SDK commands removed (ai, api, db, sdk, design, deploy, release)
- All adapted to Python/bash OAuth rotation scope

Running sync would reintroduce all that Kailash-specific bloat.

### How to Pull Specific Artifacts

If a specific generic artifact is needed from upstream:
1. Copy manually from `../../loom/kailash-coc-claude-py/` (or `../../kailash-coc-claude-py/`)
2. Adapt to csq's context
3. Commit

### Cross-References

- `.claude/VERSION` — full fork changelog
- `.claude/commands/sync.md` — the no-op command file with full rationale
