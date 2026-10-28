# agent-working-agreements

The working agreement between Brandon Perfetti and every AI agent he works with — Claude Code,
Cowork, Codex, OpenClaw (Camina) — across the repositories he runs under Sans Faux. It is the
written form of deciding what gets built and holding agents to it: how orchestrated work is
specified (a grilling session, a master priority document, tickets, waves of agents), how every
claim is labelled as measured, read from source or inferred, which branch a change may land on
and who merges it, and what an agent must stop and ask about rather than decide. **The agreement
itself is [`AGENT-WORKING-AGREEMENTS.md`](AGENT-WORKING-AGREEMENTS.md)** — start there, not here.
This README is for a human reader: the maintainer, or someone arriving from outside.

## Reading this repo

These are one engineer's working agreements, running against a real fleet. The paths
(`~/dev/sansfaux/_agent/`), the client appendices and the initiatives named in the changelog are
his, and they stay as they are: agents read the agreement and their client file at the start of
every session, and a path an agent can follow is worth more than one a stranger finds tidy. What
is portable is the structure and the rules — the evidence labels, the two modes and the guard that
picks between them, the git ritual, the stop-list — not the layout. This is the real thing, not a
template. The changelog is the record of these rules being exercised: an entry names what produced
it, and a rule earns its place only after something bit. The documentation is licensed CC BY 4.0
(the text is in `LICENSE`); the shell scripts under `scripts/` and the GitHub workflows are MIT
(the text is in `LICENSE-MIT`), copyright 2026 Brandon Perfetti.

## Layout

```text
AGENTS.md                            repository-specific agent instructions
.github/copilot-instructions.md      a symlink to AGENTS.md, the name GitHub Copilot reads
.github/pull_request_template.md     the pull request template
AGENT-WORKING-AGREEMENTS.md          Parts A (portable discipline) + B (modes) + the Part C index
procedures/<name>.md                 the mechanics behind a rule, read when its trigger occurs
procedures/<client>/<name>.md        the same, for one client, linked from its appendix
history/<client>.md                  measurements, pinned source readings, superseded claims: never required reading
clients/<client>.md                  one appendix per environment — read only your own
docs/agents/issue-tracker.md         repository-specific issue/spec fetch and PR-linkage rules
docs/agents/triage-labels.md         the triage roles mapped to this repository's labels
docs/agents/domain.md                the agreement's terms, and GLOSSARY.md as where resolved ones go
docs/agents/commit-subject-audit.md  the 2026-09-23 audit of commit-subject conventions across active repositories
CHANGELOG.md                         why each rule changed, newest first
LICENSE                              the CC BY 4.0 legal code; it covers the documentation
LICENSE-MIT                          the MIT text; it covers scripts/ and the GitHub workflows
scripts/check-index.sh               CI: the index and clients/ must correspond
scripts/check-structure.sh           CI: the core and client ceilings, procedure fields and index, no pins
.markdownlint-cli2.jsonc             CI: markdown lint rules, each exception with its reason
```

**The split rule:** the rule every client is judged against stays in the root file — evidence
discipline, authority boundaries, stop conditions, the git ritual, the review invariant — short
enough to be read whole before a delivery. The mechanics that carry a rule out live in
`procedures/`, each behind a named trigger, read when that trigger occurs. What is specific to one
client — its selectors, its measured limits, who fills which seat — is in that client's appendix:
an agent reads Parts A and B, then the one appendix [Part C](AGENT-WORKING-AGREEMENTS.md#part-c--environment-appendices-read-only-yours)
indexes for its environment, and no other. A rule moves out of the root file only once its
destination carries it, is linked from where it stood and has been reviewed, because a rule moved
without a destination is broken silently by whoever did not follow the link. Repository gates and
conventions stay in each repository's own `AGENTS.md`, and workflow procedures in the skills Part A
names (#173).

**Who does what in a delivery** is A4's to say, in its three seats — the orchestrator, the
delivery owner and the independent reviewer — and only Brandon merges. A client appendix may name
who fills each seat there.

## How this reaches each client

Each client is pointed at the agreement by one line it loads at startup. The pointer is the only
per-client configuration; the agreement itself is identical for all of them.

| Client | Pointer lives in | Notes |
| --- | --- | --- |
| Claude Code | `~/.claude/CLAUDE.md` | plain file, read at session start |
| Cowork (Claude desktop) | the desktop **Instructions for Claude** field | applies to chats and Cowork only — it does *not* reach Claude Code |
| Codex (ChatGPT desktop) | **Personalization → Codex instructions**, which *is* `~/.codex/AGENTS.md` | one surface, not two — see below |
| OpenClaw (Camina) | workspace-root `AGENTS.md` | routes Parts A–B plus `clients/openclaw.md` to one protected instruction-source root working tree on `master` (its Git administration may host isolated managed delivery worktrees without altering the root tree), fast-forwarded after each release per #48; new/reset-session application must be verified |

**Codex writes both directions, asymmetrically** `[measured 2026-09-13]`: editing the field rewrites
`~/.codex/AGENTS.md` immediately, while editing the file reaches the field **only after restarting
the ChatGPT desktop app**. A file edit made while the app is running is invisible to it and will be
discarded by the next save from the field. **So: quit the app, edit the file, then start it** — not
"edit and restart later".

Following a pointer is a read the agent performs, not an automatic include: a session that skipped
it looks identical to one that complied. That is why the agreement asks every agent to *name* what
it read, including the client file.

## Amending it

Rules change by pull request against `develop`, the same as any repo here — with one exception worth
stating plainly: **this repo is exempt from the wave/initiative machinery its own Part B describes.**
An amendment is a branch, a PR, a review, and a merge. It does not get an MPD.

Every amendment adds a short entry at the top of `CHANGELOG.md`. Git history records *what*
changed; the changelog records *why*, and the agreement's own rules cite it. The rules that keep
the agreement from growing back — friction before amendment, one agreement PR at a time, replace
rather than layer, evidence out of the rule — are in [`AGENTS.md`](AGENTS.md), *Amending the
agreement*; an agent reads them before proposing a change here.
