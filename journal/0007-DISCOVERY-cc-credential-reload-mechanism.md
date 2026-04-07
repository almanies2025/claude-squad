---
type: DISCOVERY
date: 2026-04-07
created_at: 2026-04-07T16:30:00+08:00
author: co-authored
session_id: 56e0a0d5-bb6f-4bbe-a71a-dc06dac9f951
session_turn: 35
project: claude-squad
topic: Live credential rotation works without restarting Claude Code
phase: implement
tags: [oauth, credentials, rotation, cross-process]
---

## Discovery

When `.credentials.json` is updated by an external process, the running Claude Code instance picks up the new credentials on its next interaction. No restart needed.

We discovered this empirically: prior assumption was that credential rotation required CC restart. Live test disproved that — wrote new credentials to `.credentials.json` from outside the process, then submitted a message in CC, and the request used the new token.

## Implication for csq

`swap_to()` already writes `.credentials.json` and the per-config-dir keychain entry. The mtime change is automatic. **No restart is needed.** The "restart CC to activate" warning that lived in `swap_to()` was based on a wrong assumption that pre-dated empirical verification. Removed in commit ceb3a5d.

Verified live: user ran `! csq swap 7` inside a CC session running on account 2; statusline updated to 7 immediately (because we now also write `.current-account` directly), and the next API call used account 7's credentials.

## For Discussion

1. What was the original failure that prompted this multi-process credential coordination feature in Claude Code? Was it a multi-terminal user case like ours, or something else (e.g., browser-based OAuth completing in a different process)?
2. If we had tried rotating credentials before this feature existed, the swap_to() warning would have been correct. How would we know when an external dependency's behavior changes silently? The defensive assumption was right at one point and wrong now — what's the equivalent of a regression test for upstream behavior?
3. The user pushed back on the "restart required" warning by trying it and seeing it just worked. This empirical-first approach caught the wrong assumption faster than any reasoning could have. How do we build that habit into earlier phases of work?
