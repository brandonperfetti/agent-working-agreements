# Claude Code

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first.**
This appendix adds only what is specific to this client; it never overrides Parts A–B, and a rule
here that contradicts one there is the rule that is wrong. **Name this file when you acknowledge
your reading** — "read the agreements and `clients/claude-code.md`" — so a skipped read is visible.

**Default mode: autonomous.** The capability guard (B0) still decides; this is where it starts.

---

Native shell on Brandon's machine (or a cloud checkout): `rm`, worktrees, `git branch -d`, and hook
execution all work [measured 2026-09-10]; none of the Cowork hazards (`cowork.md`) apply. **Still
check at pickup:** item 2 (run the gate once — the local shell's locale/env differs from the CI
runner; the project docs name the exports), item 4 (branch protection — query it, it has been
absent), item 5 (MPD §0). Whether the repo carries any hooks at all is a repo fact, not a Claude
Code fact.

- Lane isolation: `git worktree add ../<repo>-<lane> -b <initiative>/wave-<n>-<lane>` from the wave
  branch (flat form — git refuses a ref that is a path prefix of another, so `wave-<n>/<lane>`
  cannot coexist with `wave-<n>` [measured 2026-09-11]); remove the worktree after merge. The
  `EnterWorktree` tool, where present, does the same.
- **Agent-tool dispatches in one message run concurrently — ≥ 3 measured** (2026-09-10; the ceiling
  is unmeasured). Lanes share `.git/hooks`; never install a per-lane hook.
- A wave orchestrator's session is one wave; rotate by starting a fresh session from the packet
  (or `handoff`).
- This file is loaded by the one-line pointer in the user-level `~/.claude/CLAUDE.md` (created
  2026-09-10), read at the start of every Claude Code session on this machine, plus the repo's own
  `CLAUDE.md` for project specifics.
