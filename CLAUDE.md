# Claude Squad — Account Rotation & Session Management

Python tooling for Claude Code multi-account rotation, quota monitoring, and session management.

## Absolute Directives

### 1. .env Is the Single Source of Truth

All API keys and model names MUST come from `.env`. Never hardcode credentials. See `rules/env-models.md`.

### 2. Implement, Don't Document

When you discover a missing feature — implement it. Do not note it as a gap. See `rules/no-stubs.md`.

### 3. Zero Tolerance

Pre-existing failures MUST be fixed, not reported. Stubs are BLOCKED. See `rules/zero-tolerance.md`.

## Project Structure

```
rotation-engine.py       — Core engine: quota tracking, OAuth token refresh, in-place swap_to(), auto-rotate
statusline-quota.sh      — Statusline hook: feeds quota to engine, shows account + %; primary auto-rotate trigger
csq                      — CLI: login/run/status/suggest/swap/cleanup; `! csq swap N` for in-CC rate-limit recovery
auto-rotate-hook.sh      — UserPromptSubmit hook: backup auto-rotate trigger (requires CLAUDE_CONFIG_DIR)
install.sh               — One-time installer
```

In-place rotation works because Claude Code picks up updates to `.credentials.json`
on its next interaction. `swap_to()` updates the file and Claude
Code picks up the new token — no restart needed. Verified empirically with
live swap tests.

## Workspace Commands

| Command      | Phase | Purpose                                            |
| ------------ | ----- | -------------------------------------------------- |
| `/analyze`   | 01    | Load analysis phase for current workspace          |
| `/todos`     | 02    | Load todos phase; stops for human approval         |
| `/implement` | 03    | Load implementation phase; repeat until todos done |
| `/redteam`   | 04    | Load validation phase; red team testing            |
| `/codify`    | 05    | Load codification phase; create agents & skills    |
| `/ws`        | --    | Read-only workspace status dashboard               |
| `/wrapup`    | --    | Write session notes before ending                  |

## Rules

All COC rules apply. Key rules for this project:

| Concern               | Rule File                 |
| --------------------- | ------------------------- |
| No stubs/placeholders | `rules/no-stubs.md`       |
| Security (secrets)    | `rules/security.md`       |
| Git workflow          | `rules/git.md`            |
| Zero tolerance        | `rules/zero-tolerance.md` |
| Testing               | `rules/testing.md`        |
