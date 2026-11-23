# The `_agent/` workspace

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27; "above" and "below" in it refer to the agreement section it implements.

**Trigger:** An agent is about to write any artifact (review, evidence, handoff, note, friction
record, plan), to clone or check out a repository for scratch work, or to install or build there.

**Owner:** The agent writing the artifact; the agent closing a delivery for its friction record.

**Implements:** A6 — Where things go.

**Stop:** B2 item 5 for an inaccessible required handoff; a file with no home goes to
`experiments/` and says so.

---

The `sansfaux/` root holds `_agent/`, project checkouts, `.worktrees/`, the agreement clone and
`organize.sh`. [Worktree lifecycle](worktree-lifecycle.md) defines placement and retirement.

An **on-fleet workspace** is one where walking upward from the working directory finds an
`_agent/` directory; the directory containing its first occurrence is the **agent root**, and
`AGENT-WORKING-AGREEMENTS.md` is not a marker because this agreement is a repository whose file
appears at the root of every clone and worktree.

**Artifact placement precedence** is one case of A1's rule that a skill never overrides Parts
A–B: on an on-fleet workspace, where agent artifacts are written is this section's to decide (the
`agent-workspace` convention carries it out), not a skill's default; off-fleet fallbacks remain
the skill's to define.

**Artifact store.** `_agent/` names an artifact-location class, not a synchronization or cutover
mechanism. At session start, the applicable store policy selects one concrete artifact store; the
session records that location and does not switch stores or write the same artifact to another
store mid-session. Each execution machine keeps receipts for its work. Agents share
relevant receipt pointers with roles that can read the same store; verify access before relying
on them. Across stores, send a bounded handoff through an existing authorized, access-controlled
transfer route, naming the source machine, store, path and observation time. The recipient saves
that handoff in its already-selected store; the source receipt remains canonical, without store
mirroring or new access grants. Verify receipt and usable evidence before dependent work; if no
safe transfer route exists, apply B2 item 5 only to that dependency. Preserve privacy and access
boundaries; the owner need not relay receipts. Client appendices resolve discovery and limits.

On an on-fleet workspace, everything an agent produces goes under `_agent/` — a clone is not a
product (**Clones**, below):

```text
_agent/
├── initiatives/<project>-<slug>/   one self-contained folder per orchestrated initiative:
│     MASTER-PRIORITY-DOCUMENT.md   + nested handoffs/ analysis/ reviews/ evidence/ friction/
│                                   learnings/ mboxes/ pull-requests/ rationale/ (as needed)
├── learnings/     cross-initiative lessons promoted from initiatives' learnings/ — cited, durable
├── plans/         execution plans, initiative briefs, grill records
├── analysis/      cross-repo findings that belong to no initiative
├── evidence/      raw captures for cross-initiative claims
├── friction/      one-off delivery friction records — raw workflow cost before promotion
├── experiments/   the harness sources and scripts you write that fit nowhere else (not /tmp —
│                  the next session can't see it); what they install or build is scratch (Clones)
├── notes/         session scratch, decisions-in-progress
├── quarantine/    superseded docs kept for the trail (move, don't rewrite beyond recognition)
├── _trash/        staged for deletion — only Brandon empties this
└── handoffs/ mboxes/ pull-requests/ reviews/ rationale/   LEGACY + one-off only (pre-initiative
                   material lives here; new initiative work never does)
```

**Rules.** Deliverables are born in their initiative folder from the first write.
[learnings: 2026-08-30 §6] Initiative slugs carry the project prefix (`bp-portfolio-…`,
`claude-skills-…`, `fleet-…` for cross-repo work) and the MPD §7 names the repo and checkout path;
`initiatives/README.md` keeps the index (initiative → repo → mode → status), written at Genesis and
updated at wave close. Date-prefix files
`YYYY-MM-DD-`. Never a loose file at `_agent/` root or `sansfaux/` root; never a new top-level
folder (if nothing fits: `experiments/`, and say so). `./organize.sh` (dry-run by default) tidies
loose files and sweeps git locks; `--empty-trash --apply --yes` is **Brandon's command, not an agent's**.

**Friction.** Record friction when it happened, not to prove that none did. A delivery with no
initiative writes its record to `_agent/friction/YYYY-MM-DD-<repo>-<id>.md`, where `<repo>` is the
repository name and `<id>` is `pr-<number>` or, with no PR, the first twelve characters of the head
SHA; the record opens with the delivery's full identifier (its PR URL, or its `origin` URL plus the
full head SHA). An initiative delivery keeps its initiative `friction/`. The agent closing the
delivery writes it; B1 or B2, by mode, carries the delivery's procedure (Brandon, 2026-10-20),
and all seat authority comes from A4 (Brandon, 2026-10-23, #173). The plain filename replaces a
hashed one that exceeded the filesystem's 255-byte limit the first time a delivery had no PR
(Brandon, 2026-10-27, #185).

An entry names the delivery and the workflow step; what was observed, with A2 labels and evidence
locators where they exist; the cost (interruption, retries, rework, or elapsed time when
measured); the workaround, if any; first-seen or recurring, and how to reproduce; and the proposed
durable fix, or `unknown`. Friction is a workflow cost, kept apart from evidence (A2), review
findings (`reviews/`), learnings (`what-did-we-learn`) and issues (promoted below); it may link
to any of them. Preserve the raw record; correct it in place under A2, quoting the old text,
marked and dated. Whoever later acts on it adds a dated disposition to the same record: link the
fix, issue or receipt that already covers it; fix a confirmed defect the delivery's authority
covers, since one confirmed defect needs no recurrence (a claim that it recurs keeps
`recurring-error-analysis`'s evidence threshold); keep follow-up open with its reason and the role
that holds it under existing authority; or say why none is needed. A lesson or prevention it
verifies goes to its existing learning, rule, skill or script, by that home's owner. Capture is
non-blocking: it waits for no disposition, creates no checkpoint and stops nothing.

**Promotion, at delivery close.** The agent closing the delivery, never mid-task, makes each item
that meets the bar an issue in the repository that owns its fix. The bar: durable or recurring, one
owning repository, a reproducible gap, and actionable without this session; one confirmed defect is
enough. Search that repository's open `friction` issues first and comment on a match instead of
filing. A new issue follows the repository's friction form (`.github/ISSUE_TEMPLATE/friction.yml`,
title `Friction: …`) and is filed with both labels on the command (`gh issue create` with `--label
friction --label agent-filed`), or through the `file-friction` skill. The record stays the raw
capture and links each issue it spawned; an item below the bar stays in the record and is not swept.
The sweep skips an issue labelled `needs-brandon`.
For a recurring item, use `recurring-error-analysis`'s evidence threshold, mechanism/counterevidence
analysis, prevention selection and validation; keep this record and its existing owner. Determine
what is objective and mechanically detectable. Prefer the smallest effective existing enforcement
point: architecture/ownership, tool boundaries or repository structure; then types/lint, tests and
validation scripts. Use an existing reusable skill for repeatable guidance; skills and prose do not
themselves enforce a judgment. Keep human judgment and review for choices no mechanism can decide.

Before adopting a new control, safely demonstrate rejection of the original failure and acceptance
of legitimate boundary/default use. Adopt only when its interruption, runtime, maintenance and
false-positive costs are proportionate to the supported harm. Name its owning repository and owner,
rollback path, and evidence for revision or retirement: reproduced legitimate-use denial, a
workflow dead end, disproportionate measured cost, changed contracts or a verified replacement. The
owner repairs, rolls back or retires within existing authority and review, preserving failure
coverage or explicitly recording the remaining risk; an empty log or a quiet period alone proves
neither success nor redundancy. Governing agreements, SOUL files, authority and approval policy
change only through their normal owner-approved amendment and review route, never automatic
self-modification (#167).

**Clones.** No clone, worktree, package install, `node_modules` or build output is written under
`_agent/` (a `node_modules` in a captured `*.app` bundle is the app). That scratch, and any brief's
scratch location, is the client scratch directory your client file names or records as unmeasured;
"move, don't delete" never moves a tree into `_agent/`. What persists is the evidence under
`evidence/`: commands, output, receipts, logs and hashes, with the remote and commit to rebuild a
clone. `hooks/claude-code/store_check.py check` fails on any `node_modules` root or a top-level
store tree over 5 GB (#283).
Before the remote, a command or its output is written under `evidence/`, the secret comes out, by
the remote's form, wherever a remote appears, because a remote can carry credentials, a command
records one as typed (a `git clone` of a URL with a token in it), and the plain ways of reading a
remote print them verbatim: an http(s) URL loses its whole userinfo, since a token can stand where
a user name does and the two cannot be told apart; an ssh remote keeps its user name and loses any
password; a remote of any other form loses its whole userinfo; and any credential the clone uses,
a token or an authentication header among them, is stripped from a captured command and its
output.
Keeping that evidence is how this sits beside the `experiments/` line's "not /tmp": a
transcript has to survive the session, a clone or install can be made again. The reason: a clone
under `_agent/` is a nested repository in a store meant to replicate, a second copy of a project's
source with its license, and rebuildable (Brandon, 2026-10-12, 2026-11-16).
Scratch-clone rules move no existing lane tree; [worktree lifecycle](worktree-lifecycle.md) governs
new placement and retirement through the owning manager.
