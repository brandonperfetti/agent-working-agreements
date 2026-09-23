# agent-working-agreements

The cross-project working agreement between Brandon and whatever agent he is working with under Sans
Faux. **The agreement itself is [`AGENT-WORKING-AGREEMENTS.md`](AGENT-WORKING-AGREEMENTS.md)** —
start there, not here. This README is for the human maintaining the repo.

## Layout

```text
AGENTS.md                      repository-specific agent instructions
AGENT-WORKING-AGREEMENTS.md   Parts A (portable discipline) + B (modes) + the Part C index
clients/<client>.md           one appendix per environment — read only your own
docs/agents/issue-tracker.md  repository-specific issue/spec fetch and PR-linkage rules
CHANGELOG.md                  why each rule changed, newest first
scripts/check-index.sh        CI: the index and clients/ must correspond
.markdownlint-cli2.jsonc      CI: markdown lint rules, each exception with its reason
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
