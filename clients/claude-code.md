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

On the desktop the store is `~/dev/sansfaux/_agent/` (`evidence/`, `analysis/`; A2, A6): working
state, not repository content; a cloud checkout uses, and records, its workspace's durable `_agent/`.

The native shell supports `rm`, worktrees, `git branch -d` and hook execution; none of the Cowork
hazards (`cowork.md`) apply. **Still check at pickup:** item 1's hook probe (`git push --dry-run
origin HEAD` from the checkout you will push from), item 2 (the proportionate pickup check — the
local shell's locale/env differs from the CI runner; the project docs name the exports), item 3
before **every** feature commit, not only the first, item 4 (branch protection — query it, never
assume it), item 5 (the override in the prompt, recorded in MPD §0 for initiative work, or with the
delivery's decisions for work with no initiative, B1 or B2, by mode).

- Lane isolation and retirement follow [worktree lifecycle](../procedures/worktree-lifecycle.md):
  Shell lanes use `manual/`; retain native T3 ownership. Do not use `EnterWorktree` (#101).
  Branch from the delivery branch using flat lane names: `wave-<n>-<lane>` avoids a Git ref-prefix
  collision with `wave-<n>`. In T3 also read [its adapter](../procedures/t3-adapter.md).
- **Lane worktrees and hooks:** a worktree made by `git worktree add` shares the main checkout's
  `.git/hooks`, so item 1's probe there covers it. Read `git config core.hooksPath` before
  dispatching lanes: where item 1 makes the probe per worktree, run it in each lane's, naming
  remote and branch as item 1 does — `git worktree add -b` sets no upstream. A lane never installs
  a hook of its own — the repo's install step is the only source of hooks.
- **Scratch clones and installs (A6, "Clones"):** they go in the scratchpad directory the
  session's environment names, never under `_agent/`. Whether every dispatch shares it is
  unmeasured, so a dispatch names one subdirectory of it per sub-agent.
- **Agent-tool dispatches in one message run concurrently**; the ceiling is unmeasured.
- **Model and effort (A4):** per [orchestration seats](../procedures/orchestration-seats.md), and
  in T3 [its adapter](../procedures/t3-adapter.md); old role-to-selector maps restrict no task choice.
- **Long gates (Bash):** `run_in_background: true` and `timeout: 7200000`; the 30-minute default
  silently stops gate and watcher, and T3 messages or idle do not. One that can pass 2 hours or the
  session starts detached in a fresh `<d>` (`nohup perl -MPOSIX -e 'setsid;exec @ARGV' bash -c
  '(<gate>); echo $? > <d>/exit' & echo $! > <d>/pgid`, `$!` being its group); wait for `<d>/exit`
  or the group's end. Stop only your group, `kill -TERM -$(cat <d>/pgid)`, never `pkill -f`.
- **CodeRabbit CLI, for B2's preflight:** `coderabbit-preflight` checks the CLI on every run; a
  recorded install is a record, not a guarantee.
- **Kody tool names (A7):** the same Kody connector is named differently per client. A permission
  rule or a reference to a Kody tool uses the name the session reports, read before it is written,
  because a name taken from another client or inferred from a listing matches nothing here.
- **Attribution (RULE ZERO):** this environment injects `Co-Authored-By`/`Claude-Session` trailers,
  a "Generated with Claude Code" PR-body footer and, with Auto-fix on, a crediting line on replies;
  put one `Agent: Claude Code · <model id> · <effort>` line in their place, as the session reports.
  The installed hooks refuse the commit forms where they run; where none does (husky before
  install), fix the message by hand ([`rule-zero-check.md`](../procedures/rule-zero-check.md)).
- Rotate at a context-driven clean pause through the supported session route, using A4's packet
  (or `handoff`); verify successor capability, receipt, acceptance and advancement before retirement.

## History

Dated measurements behind these rules, in the shared client history archive; none required
reading: [`../history/openclaw.md#claude-code`](../history/openclaw.md#claude-code).
