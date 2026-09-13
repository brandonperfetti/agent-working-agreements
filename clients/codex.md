# Codex (ChatGPT desktop, local shell)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first.**
This appendix adds only what is specific to this client; it never overrides Parts A–B, and a rule
here that contradicts one there is the rule that is wrong. **Name this file when you acknowledge
your reading** — "read the agreements and `clients/codex.md`" — so a skipped read is visible.

**Default mode: autonomous.** The capability guard (B0) still decides; this is where it starts.

---

Everything below is `[measured 2026-09-13]` on Brandon's Mac unless marked; **re-measure on yours**.
Note the scope: this describes a *Codex session with local shell tools*, not every ChatGPT
conversation.

- **How this file reaches you:** the ChatGPT desktop **Personalization → Codex instructions** field
  and `~/.codex/AGENTS.md` are **the same surface on this machine** — editing the field rewrote the
  file's whole contents `[measured 2026-09-13, Brandon]`. So there is exactly one copy of the
  pointer and one copy of these rules; never maintain a second. It round-trips, **asymmetrically**
  `[measured 2026-09-13, Brandon]`: an edit in the field rewrites the file **immediately**, while an
  edit to the file reaches the field **only after an app restart** — the running app does not re-read
  it. So a file edit made while the app is running is invisible to it and can be silently discarded
  by the next field save. So the pointer can be changed by script (the AWA
  repo migration included), as long as the app is restarted afterward. (No `AGENTS.override.md`,
  `CODEX_HOME` unset. Whether a cloud Codex task without this filesystem gets the same text is
  **measure and record**.) Codex
  loads it at startup; **following the pointer is still a read you must perform** — it is not an
  automatic include, so a session that skipped it looks identical to one that complied. Read the
  file, then say you did.
- **Guard items:** 1 **passes by demonstration** — `rm` succeeds, a truncating overwrite shrinks the
  file in place with no surviving tail, `git worktree add`/`remove` work, `branch -d` refuses an
  unmerged branch while `-D` takes it, and an executable `pre-commit` hook fires on commit (sentinel
  in the output). 2 is **measure and record** per repo: node, pnpm and python3 are present, but the
  gate also wants `zip`/`unzip`/`mktemp` and a vendor CLI — run it once. 4 is queryable (`gh` is
  authenticated; scopes include `repo` and `workflow`).
- **Default mode is autonomous** — Brandon lifted the standing attended instruction on 2026-09-13,
  so mode here is decided by the guard alone, exactly as in `claude-code.md`. Items 1 and 4 pass as measured
  above; **item 2 is still a per-repo probe you run at pickup**, and a failure downgrades this
  session to attended with a one-line reason, same as anywhere else.
- **Scope, because this client's instruction field is wider than the others.** The Codex
  instructions field applies to *every* ChatGPT and Codex chat, including ones with no shell and no
  repo; this appendix — and Part B — apply only to a session that has a local shell and is working
  a repo under `~/dev/sansfaux`. Elsewhere only Part A's honesty rules carry.
- **Sub-agents:** ≥ 2 workers ran concurrently alongside the parent (4 slots advertised, 3 workers
  unverified). Model selectors are **GPT tiers only** — A4's role-named tiers map to those; a
  full-history fork **inherits the parent's model and cannot override**, and config is not
  attestation (A4).
- **Hazards:**
  - **A sandbox denial looks exactly like a missing capability.** `ps` was denied and a sandboxed
    `curl` failed DNS while the permitted route returned HTTP 200 — preserve the execution boundary
    in the claim, and never report "this machine can't" from inside a restricted call.
  - **`claude plugin validate .` stalls inside the sandbox** and completes through approved
    execution outside it `[measured 2026-09-13]`. Raw capture:
    `_agent/evidence/2026-09-13-codex-standing-instructions-audit-01a09c32/` — the gate log at line
    793, return code 143 under SIGTERM inside the sandbox, return code 0 through permitted
    execution outside it, and `gate-interruption.txt`. It is part of the CI gate, so a
    gate run that reaches it and hangs is the sandbox boundary rather than a failing gate — but
    the step still has to be **run and pass** through the permitted route before the gate counts as
    green. A5's bar is every command the project names, in order, all succeeding; splitting the run
    across the sandbox boundary is allowed, reporting a stalled step as green is not. Say which
    steps ran where.
  - **Unquoted URL query strings die to zsh globbing** (`no matches found: …?ref=master`) — quote
    the endpoint.
  - **The installed skills plugin lags the repo** — `1.9.0` at `ea05754` while `master` was already
    `1.12.0`. Check the installed version against the remote manifest at pickup; refresh is
    `codex plugin marketplace upgrade <marketplace>` then `codex plugin add <plugin>@<marketplace>`
    `[source: --help]`, and whether that replaces the cache in place or needs an app restart is
    **measure and record**.
  - **A task can keep a stale MCP catalog after a config change, even across an app restart**
    `[source: 2026-09-06 setup record]` — start a fresh task rather than trusting the old one.
  - Truncated tool output is a general hazard, not a Codex one — see A2.
- **Measure and record:** whether a dispatched worker keeps issuing tool calls while the app window
  is closed (distinct from window-close, app-quit and sleep; a proposed experiment is in the
  2026-09-13 audit).
