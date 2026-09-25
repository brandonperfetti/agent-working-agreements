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
it, and a rule earns its place only after something bit.

## Layout

```text
AGENTS.md                            repository-specific agent instructions
AGENT-WORKING-AGREEMENTS.md          Parts A (portable discipline) + B (modes) + the Part C index
clients/<client>.md                  one appendix per environment — read only your own
docs/agents/issue-tracker.md         repository-specific issue/spec fetch and PR-linkage rules
docs/agents/commit-subject-audit.md  the 2026-09-23 audit of commit-subject conventions across active repositories
CHANGELOG.md                         why each rule changed, newest first
LICENSE                              CC BY 4.0, the whole repository: reuse with attribution
scripts/check-index.sh               CI: the index and clients/ must correspond
.markdownlint-cli2.jsonc             CI: markdown lint rules, each exception with its reason
```

**The split rule:** anything every client is judged against stays in the root file, in full.
Only the environment appendices are disclosed progressively. A rule moved out of Parts A or B is a
rule that gets broken silently by whoever did not follow the link.

## How this reaches each client

Each client is pointed at the agreement by one line it loads at startup. The pointer is the only
per-client configuration; the agreement itself is identical for all of them.

| Client | Pointer lives in | Notes |
| --- | --- | --- |
| Claude Code | `~/.claude/CLAUDE.md` | plain file, read at session start |
| Cowork (Claude desktop) | the desktop **Instructions for Claude** field | applies to chats and Cowork only — it does *not* reach Claude Code |
| Codex (ChatGPT desktop) | **Personalization → Codex instructions**, which *is* `~/.codex/AGENTS.md` | one surface, not two — see below |
| OpenClaw (Camina) | workspace-root `AGENTS.md` | routes Parts A–B plus `clients/openclaw.md` to one read-only instruction-source clone on `master`, fast-forwarded after each release per #48; new/reset-session application must be verified |

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

Every amendment adds an entry at the top of `CHANGELOG.md`. Git history records *what* changed;
the changelog records *why*, and the agreement's own rules cite it.
