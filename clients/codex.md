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
  and `~/.codex/AGENTS.md` are **the same surface** — keep exactly one copy of the pointer and of
  these rules. It round-trips **asymmetrically**: a field edit rewrites the file immediately, while
  a file edit reaches the field **only after an app restart**, and a file edit made while the app
  runs can be discarded by the next field save. So quit the app, edit the file, then start it.
  Whether a cloud Codex task without this filesystem gets the same text is **measure and record**.
  **Following the pointer is a read you must perform** — not an automatic include, so a session
  that skipped it looks identical to one that complied. Read the files, then say you did.
- **Guard items:** 1's capabilities are **shown by demonstration** (`rm`, truncating overwrite, `git
  worktree add`/`remove`, `branch -d` refusing an unmerged branch, a firing `pre-commit` hook);
  **item 1 passes only after its per-checkout `pre-push` probe** (`git push --dry-run origin HEAD`
  at pickup in the checkout you will push from) or a record that no hook is installed. A dry run
  sends no objects but contacts the remote (sandbox-denial hazard below). 2 is **measure and
  record** per repo: a proportionate pickup check, with any tools it needs. 4 is queryable through
  `gh`, **still checked per repository**: no earlier measurement stands for it.
- **Default mode is autonomous**, decided by the guard alone, exactly as in `claude-code.md`. The
  hook probe and item 2 are still yours to run at pickup, and item 4 is checked per repository. A
  failure downgrades what B0 says a failed check downgrades, with a one-line reason; a failed
  item 4 is recorded, as B0 says.
- **Scope, because this client's instruction field is wider than the others.** The Codex
  instructions field applies to *every* ChatGPT and Codex chat, including ones with no shell and no
  repo; this appendix — and Part B — apply only to a session that has a local shell and is working
  a repo under `~/dev/sansfaux`. Elsewhere only Part A's honesty rules carry.
- **Sub-agents:** model and effort per [orchestration seats](../procedures/orchestration-seats.md),
  and in T3 [its adapter](../procedures/t3-adapter.md). A full-history fork **inherits the
  parent's model and cannot override**, and config is not attestation (A4).
- **Hazards:**
  - **A sandbox denial looks exactly like a missing capability** — preserve the execution boundary
    in the claim, and never report "this machine can't" from inside a restricted call.
  - **`claude plugin validate .` stalls inside the sandbox** and completes through approved
    execution. It is part of the CI gate: run it there and let it pass before calling the gate
    green. A hang on the permitted route is a real failure, not the boundary.
  - **Unquoted URL query strings die to zsh globbing** (`no matches found: …?ref=master`) — quote
    the endpoint.
  - **The installed skills plugin can lag the repo** — check the installed version against the
    remote manifest at pickup; refresh is `codex plugin marketplace upgrade <marketplace>` then
    `codex plugin add <plugin>@<marketplace>`; whether that replaces the cache in place or needs an
    app restart is **measure and record**.
  - **A task can keep a stale MCP catalog after a config change, even across an app restart** —
    start a fresh task rather than trusting the old one.
- **Worktrees:** use native create/archive for app-managed trees; follow [lifecycle](../procedures/worktree-lifecycle.md).
  Scratch placement remains unmeasured, outside `_agent/`. T3: [adapter](../procedures/t3-adapter.md).
- **Attribution (RULE ZERO):** the profile forbids it; this environment injects nothing (measured
  2026-11-07), and the installed `commit-msg` hook refuses a trailer or a wrong author on every commit.
- **Measure and record:** whether a dispatched worker keeps issuing tool calls while the app window
  is closed (distinct from window-close, app-quit and sleep).

## History

Dated measurements behind these rules, in the shared client history archive; none required
reading: [`../history/openclaw.md#codex`](../history/openclaw.md#codex).
