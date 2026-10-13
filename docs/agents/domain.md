# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring it.

**Layout: single-context.** This repository is documents, not an application: the agreement
([`AGENT-WORKING-AGREEMENTS.md`](../../AGENT-WORKING-AGREEMENTS.md)), one appendix per client
under `clients/`, the changelog, and the scripts that check them. There is no `src/` and no
monorepo signal, so there is no `GLOSSARY-MAP.md` and no per-context layout.

## Before exploring, read these

- **`GLOSSARY.md`** at the repo root, where resolved terms go. It does not exist yet.
- **`AGENT-WORKING-AGREEMENTS.md`**, which defines every term below in the section named
  beside it. Read the section before using the term; the table only points at it.
- **`CHANGELOG.md`**, newest first: why each rule changed. This repository keeps no
  `docs/adr/`; the changelog is its record of decisions and their reasons.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest
creating them upfront. The `/domain-modeling` skill creates `GLOSSARY.md` lazily, when a term
actually gets resolved.

## The domain's terms

| Term | Defined in |
| --- | --- |
| attended mode | B1: Brandon is the verification step; no commit without his approval, per batch |
| autonomous mode | B2: Brandon's review moves to the pull request |
| capability guard | B0: the checks, verified at pickup, that a session must pass to run autonomous |
| the ritual | Part B, "The ritual both modes serve": the branch, PR and merge steps |
| MPD (master priority document) | A4: an initiative's spine; its §0 records the mode |
| wave | A4 and B2: one phase of an initiative, run by one orchestrator on one branch off `develop` |
| orchestrator | A4: the lead agent; runs one wave, then rotates to a fresh one through a packet |
| lane | A4 and B2: one sub-agent's work on named files, in its own worktree |
| RULE ZERO | A4: no attribution on any commit, PR body, reply or comment |
| evidence labels | A2: `[measured]`, `[source]`, `[inference]` on every claim |
| stop-list | B2: what an agent in autonomous mode stops and asks about |

When a term is resolved further than its section says, it goes in `GLOSSARY.md`, which then
becomes the first place to look.

## File structure

```text
/
├── GLOSSARY.md                    ← resolved terms (created when the first one is)
├── AGENT-WORKING-AGREEMENTS.md    ← the agreement: Parts A and B, the Part C index
├── CHANGELOG.md                   ← why each rule changed
└── clients/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a rule's wording, a changelog entry),
use the term as defined in `GLOSSARY.md`, or in the agreement's section the table names. Don't
drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary or the agreement yet, that's a signal: either you're
inventing language the project doesn't use (reconsider) or there's a real gap (note it for
`/domain-modeling`).

## Flag decision conflicts

If your output contradicts a reason the changelog records, surface it explicitly rather than
silently overriding:

> _Contradicts the changelog's entry for #N, but worth reopening because…_
