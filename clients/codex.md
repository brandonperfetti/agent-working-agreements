# Codex (ChatGPT desktop, local shell)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B, then
[`../profiles/sansfaux.md`](../profiles/sansfaux.md), then this file — all three, even when your
pointer names only the core and this file.** This appendix adds only what is specific to this
client; it never overrides Parts A–B, and a rule here that contradicts one there is the rule that
is wrong. **Name all three when you acknowledge your reading** — "read the agreements,
`profiles/sansfaux.md` and `clients/codex.md`".

**Default mode: autonomous**, where B0's guard starts; attended (B1) if the profile is unreadable.

---

## Evidence store

On the desktop, Codex uses `~/dev/sansfaux/_agent/`, the store Claude Code uses; that location is
inferred, not measured in Codex. Use its `evidence/` and `analysis/` subdirectories per A2 and A6,
and measure the store location on another machine.

Scope: this describes a *Codex session with local shell tools*, not every ChatGPT conversation.
Measurements behind it are in the history file; **re-measure on yours**.

- **How this file reaches you:** the ChatGPT desktop **Personalization → Codex instructions** field
  and `~/.codex/AGENTS.md` are **the same surface**; keep one copy of the pointer and these rules.
  **Following the pointer is a read you must perform** — not an automatic include, so a session
  that skipped it looks identical to one that complied. Read the files, then say you did.
  Whether a cloud Codex task without this filesystem gets the same text is **measure and record**.
- **Guard (B0):** the mode is decided by the guard alone, exactly as in `claude-code.md`. Item 1's
  capabilities are **shown by demonstration** (`rm`, truncating overwrite, `git worktree
  add`/`remove`, `branch -d` refusing an unmerged branch, a firing `pre-commit` hook). At pickup
  run item 1's per-checkout `pre-push` probe (`git push --dry-run origin HEAD` in the checkout you
  will push from) or record that no hook is installed; item 2 is **measure and record** per repo,
  with any tools it needs; item 4 is queryable through `gh`, still checked per repository: no earlier
  measurement stands for it. At pickup, check the installed skills plugin's version against the
  remote manifest.
- **Scope, because this client's instruction field is wider than the others.** The Codex
  instructions field applies to *every* ChatGPT and Codex chat, including ones with no shell and no
  repo; this appendix — and Part B — apply only to a session that has a local shell and is working
  a repo under `~/dev/sansfaux`. Elsewhere only Part A's honesty rules carry.
- **Sub-agents:** model and effort per [orchestration seats](../procedures/orchestration-seats.md),
  and in T3 [its adapter](../procedures/t3-adapter.md). A full-history fork **inherits the
  parent's model and cannot override**, and config is not attestation (A4).
- **Hazards:** read [shell hazards](../procedures/codex/shell-hazards.md) before you edit the
  instructions field or `~/.codex/AGENTS.md`, before `claude plugin validate .`, when a call is
  denied, fails DNS or hangs in the sandbox, a command carries a URL query string, the plugin is
  behind, MCP or app config changed, or you are about to close the window on a dispatched worker.
- **Worktrees:** use native create/archive for app-managed trees; follow [lifecycle](../procedures/worktree-lifecycle.md).
  Scratch placement remains unmeasured, outside `_agent/`. T3: [adapter](../procedures/t3-adapter.md).
- **Attribution (RULE ZERO):** the profile forbids it; this environment injects nothing (measured
  2026-11-07); the `commit-msg` hook refuses a trailer or a wrong author, `--no-verify` aside.

## History

Dated measurements behind these rules, in the shared client history archive; none required
reading: [`../history/openclaw.md#codex`](../history/openclaw.md#codex).
