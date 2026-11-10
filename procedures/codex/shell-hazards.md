# Codex local-shell hazards

This procedure carries mechanics for `clients/codex.md` and the rules it implements in
[`../../AGENT-WORKING-AGREEMENTS.md`](../../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts
A–B, and a rule here that contradicts one there is the rule that is wrong. The text below moved out
of the appendix on 2026-11-10 with its rules unchanged; the measurements behind it stay dated in
[`../../history/openclaw.md#codex`](../../history/openclaw.md#codex). Re-measure on your machine.

**Trigger:** In a Codex session with local shell tools, in the desktop app or through T3: you edit
the Codex instructions field or `~/.codex/AGENTS.md` (desktop app); a call is denied, fails DNS or hangs inside the sandbox; a shell command
carries a URL query string or fails with `no matches found`; the installed skills plugin is behind
the remote manifest; you changed MCP or app configuration; you dispatch a worker and close the app
window (desktop app).

**Owner:** The Codex session that meets the event; the delivery owner for gate steps.

**Implements:** `clients/codex.md` *Hazards*; A2 (claims keep their execution boundary) and B0
(capability is measured, not assumed).

**Stop:** A required operation with no permitted route: B2 item 5, naming the capability and its
restoration owner. A sandbox denial alone is never that.

---

## Editing the instruction pointer (desktop app)

The ChatGPT desktop **Personalization → Codex instructions** field and `~/.codex/AGENTS.md` are
**the same surface** — keep exactly one copy of the pointer and of these rules. It round-trips
**asymmetrically**: a field edit rewrites the file immediately, while a file edit reaches the field
**only after an app restart**, and a file edit made while the app runs can be discarded by the next
field save. So quit the app, edit the file, then start it. Whether a cloud Codex task without this
filesystem gets the same text is **measure and record**.

## Sandbox denials and hangs

- **A sandbox denial looks exactly like a missing capability** — preserve the execution boundary
  in the claim, and never report "this machine can't" from inside a restricted call. B0 item 1's
  dry run sends no objects but contacts the remote, so it can be denied the same way; one that dies
  before the hook is no result ([pickup guard](../pickup-guard.md)).
- **`claude plugin validate .` stalls inside the sandbox** and completes through approved
  execution. It is part of the CI gate: run it there and let it pass before calling the gate
  green. A hang on the permitted route is a real failure, not the boundary.

## Shell quoting

**Unquoted URL query strings die to zsh globbing** (`no matches found: …?ref=master`) — quote the
endpoint.

## Installed skills plugin behind the manifest

Refresh is `codex plugin marketplace upgrade <marketplace>` then `codex plugin add
<plugin>@<marketplace>`; whether that replaces the cache in place or needs an app restart is
**measure and record**.

## Stale MCP catalog

**A task can keep a stale MCP catalog after a config change, even across an app restart** — start
a fresh task rather than trusting the old one.

## Open measurements (desktop app)

Whether a dispatched worker keeps issuing tool calls while the app window is closed (distinct from
window-close, app-quit and sleep) is **measure and record**.
