# Claude Code

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B, then
[`../profiles/sansfaux.md`](../profiles/sansfaux.md), then this file — all three, even when your
pointer names only the core and this file.** This appendix adds only what is specific to this
client; it never overrides Parts A–B, and a rule here that contradicts one there is the rule that
is wrong. **Name all three when you acknowledge your reading** — "read the agreements,
`profiles/sansfaux.md` and `clients/claude-code.md`".

**Default mode: autonomous**, where B0's guard starts; attended (B1) if the profile is unreadable.

---

## Evidence store

On the desktop, this client's store is `~/dev/sansfaux/_agent/`. Use its `evidence/` and
`analysis/` subdirectories per A2 and A6; the store is working state, not repository content. A
cloud checkout uses its active workspace's durable `_agent/` store and records that location with
the capture.

The native shell supports `rm`, worktrees, `git branch -d` and hook execution; none of the Cowork
hazards (`cowork.md`) apply. So B0 item 1 passes by construction but for its hook probe. **Still
check at pickup:** item 1's hook probe (`git push --dry-run origin HEAD` from the checkout you will
push from), item 2 (the proportionate pickup check — the local shell's locale/env differs from the
CI runner; the project docs name the exports), item 3 before **every** feature commit, not only the
first, item 4 (branch protection — query it, never assume it), item 5 (the override in the prompt,
recorded in MPD §0 for initiative work, or with the delivery's decisions for work with no
initiative, B1 or B2, by mode). Whether the repo carries any hooks at all is a repo fact, not a
Claude Code fact.

- Lane isolation and retirement follow [worktree lifecycle](../procedures/worktree-lifecycle.md):
  Shell lanes use `manual/`; retain native T3 ownership. Do not use `EnterWorktree` (#101).
  Branch from the delivery branch using flat lane names: `wave-<n>-<lane>` avoids a Git ref-prefix
  collision with `wave-<n>`. In T3 also read [its adapter](../procedures/t3-adapter.md).
- **Lane worktrees and hooks:** a worktree made by `git worktree add` shares the main checkout's
  `.git/hooks`, so item 1's probe there covers it. Read `git config core.hooksPath` before
  dispatching lanes: where item 1 makes the probe per worktree, run it in each lane's, naming
  remote and branch as item 1 does — `git worktree add -b` sets no upstream. A lane never installs
  a hook of its own — the repo's install step is the only source of hooks.
- **Scratch clones (A6, "Clones"):** a scratch clone goes in the scratchpad directory the
  session's environment names, never under `_agent/`. Whether every dispatch shares it is
  unmeasured, so a dispatch names one subdirectory of it per sub-agent.
- **Agent-tool dispatches in one message run concurrently**; the ceiling is unmeasured.
- **Model and effort (A4):** per [orchestration seats](../procedures/orchestration-seats.md), and
  in T3 [its adapter](../procedures/t3-adapter.md); old role-to-selector maps restrict no task choice.
- **CodeRabbit CLI, for B2's preflight:** `coderabbit-preflight` checks the CLI on every run; a
  recorded install is a record, not a guarantee.
- **Kody tool names (A7):** the same Kody connector is named differently per client. A permission
  rule or a reference to a Kody tool uses the name the session reports, read before it is written,
  because a name taken from another client or inferred from a listing matches nothing here.
- **Attribution (RULE ZERO):** this environment injects `Co-Authored-By`/`Claude-Session` trailers,
  a "Generated with Claude Code" PR-body footer and, with Auto-fix on, a crediting line on replies.
  The installed hooks refuse the commit forms; remove the footer and reply lines before writing
  them, reading each as [`rule-zero-check.md`](../procedures/rule-zero-check.md) says.
- Rotate at a context-driven clean pause through the supported session route, using A4's packet
  (or `handoff`); verify successor capability, receipt, acceptance and advancement before retirement.
- Reached from the one-line pointer in `~/.claude/CLAUDE.md`; this opener completes the binding.

## History

Dated measurements behind these rules, in the shared client history archive; none required
reading: [`../history/openclaw.md#claude-code`](../history/openclaw.md#claude-code).
