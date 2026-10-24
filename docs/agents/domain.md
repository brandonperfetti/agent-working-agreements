# Domain Docs

What a skill reads for this repository's vocabulary before it explores, and where a term goes
once it is resolved.

**Layout: single-context.** This repository is documents, not an application: the agreement
([`AGENT-WORKING-AGREEMENTS.md`](../../AGENT-WORKING-AGREEMENTS.md)), one appendix per client
under `clients/`, the changelog, and the scripts that check them. There is no `src/` and no
monorepo signal, so there is no `GLOSSARY-MAP.md` and no per-context layout.

## Before exploring, read these

- **`GLOSSARY.md`** at the repository root, where resolved terms go.
- **`AGENT-WORKING-AGREEMENTS.md`**, which defines every term below in the section named
  beside it. Read the section before using the term; the table only points at it.
- **`CHANGELOG.md`**, newest first: why each rule changed. This repository keeps no
  `docs/adr/`; the changelog is its record of decisions and their reasons.

The agreement and the changelog are in every clone: read the agreement before working, as
`AGENTS.md` says, and the changelog before taking a rule for original, as the agreement's header
says. Only `GLOSSARY.md` may not exist yet. An unwritten one is the expected state, not a
finding; `/domain-modeling` writes it when it resolves the first term, and not before.

## The domain's terms

| Term | Defined in |
| --- | --- |
| attended mode | B1: Brandon is the verification step; no commit without his approval, per batch |
| autonomous mode | B2: Brandon's review moves to the pull request |
| capability guard | B0: the checks, verified at pickup for each checkout and repository delivery path, that a delivery must pass to run autonomous; a failed item 4 is recorded instead, until protection exists |
| the ritual | Part B, "The ritual both modes serve": the branch, PR and merge steps |
| MPD (master priority document) | A4: an initiative's spine; its §0 records the mode |
| wave | A4 and B2: one phase of an initiative, run by one orchestrator on one branch off `develop` |
| orchestrator | A4 and B2: the seat that coordinates and synthesizes, tracker coordination included; for an initiative it runs one wave, then rotates to a fresh one through a packet; for work with no initiative, the session doing the work |
| delivery owner | A4 and B2: the assigned qualified specialist, or the orchestrator when none is assigned; owns the branch, reviewed lane integration, the merged-tree gate, conflict resolution, pushes, the pull request and its CodeRabbit round |
| independent reviewer | A4: the seat, separate from whoever produced the work, that runs the two-axis review, and reviews the whole branch at its exact head before the pull request is created and again at each new head a later fix or push makes |
| lane | A4 and B2: one sub-agent's work on named files, in its own worktree |
| RULE ZERO | A4: no attribution on any commit, PR body, reply or comment; an agent's commits on Brandon's behalf carry his identity, anyone else's carry their own, and a PR carrying his identity from another account is not merged until re-authored |
| evidence labels | A2: `[measured]`, `[source]`, `[inference]` on every claim |
| stop-list | B2: what an agent in autonomous mode stops and asks about |

When a term is resolved further than its section says, it goes in `GLOSSARY.md`, which then
becomes the first place to look.

## File structure

```text
/
├── AGENTS.md                      ← this repository's agent instructions, its CI gate among them
├── GLOSSARY.md                    ← resolved terms (created when the first one is)
├── AGENT-WORKING-AGREEMENTS.md    ← the agreement: Parts A and B, the Part C index
├── CHANGELOG.md                   ← why each rule changed
├── clients/
└── docs/agents/                   ← agent docs, this file among them; README.md's layout lists each
```

## Use the glossary's vocabulary

Name a concept by the term `GLOSSARY.md` gives it, or the agreement's section the table names —
in an issue's title, a rule's wording, a changelog entry — and keep to that term; a synonym the
glossary has ruled out reads as a second concept.

A concept with no term in either place means one of two things. The word may be new to this
repository: find the one it already uses. Or the vocabulary has a gap: leave a note for
`/domain-modeling`.

## Flag decision conflicts

When your output goes against a reason the changelog records, the output itself says so, names
the entry and makes the case for reopening it:

> _This departs from the changelog's entry for #N; it is worth reopening because…_
