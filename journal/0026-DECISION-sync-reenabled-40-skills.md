---
type: DECISION
date: 2026-04-30
author: claude
project: claude-squad
topic: Sync re-enabled, 40 skills synced from upstream
---

## Decision

Re-enabled `/sync` command and expanded skill set from 13 → 40 skills.

## What Changed

- **Sync re-enabled**: `sync/SKILL.md` updated with `enabled: true`, new sync protocol (pull → diff → review → apply → codify)
- **Upstream cloned**: `kailash-coc-claude-py` cloned to `/mnt/c/Users/User/Documents/GitHub/loom/kailash-coc-claude-py/` (was missing)
- **New rule**: `upstream-issue-hygiene.md` — GitHub issue filing hygiene (3 MUSTs: human gate, redaction, minimal-repro)
- **27 new skills** synced from upstream
- **15 new commands** synced from upstream

## 40 Skills Now Present

Phase workflow (9): analyze, cc-audit, checkpoint, codify, implement, journal, learn, redteam, todos, wrapup, ws, start, sync, project, spec-compliance, test-skip-discipline

CO/Framework (4): co-reference, 28-coc-reference, 30-claude-code-patterns, 29-pact

Visual/UX (4): 23-uiux-design-principles, 11-frontend-integration, 21-enterprise-ai-ux, 22-conversation-ux

Reasoning/Utility (9): 06-cheatsheets, 09-workflow-patterns, 12-testing-strategies, 16-validation-patterns, 17-gold-standards, 18-security-patterns, 24-value-audit, 25-ai-interaction-patterns, 31-error-troubleshooting

Enterprise/Architecture (5): 04-kaizen, 08-nodes-reference, 13-architecture-decisions, 14-code-templates, 15-enterprise-infrastructure, 20-interactive-widgets, 26-eatp-reference

## Pre-existing Issue Noted (not from this session)

`scripts/hooks/lib/version-utils.js:44` — `execSync` with string interpolation. Should be `execFileSync` with array args. Fix in future session.

## Why

User requested sync re-enabled. Upstream template was missing from expected path — cloned it first. Then selectively synced broadly-useful skills to reach 40 total.

## Outstanding

- Pre-existing `execSync` security issue in version-utils.js (not from this session)
- `project` skill is essentially empty (stub)
- Many synced skills are Kailash SDK-specific — won't fire unless invoked
