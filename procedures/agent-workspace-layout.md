# The `_agent/` workspace

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27; "above" and "below" in it refer to the agreement section it implements.

**Trigger:** An agent is about to write any artifact (review, evidence, handoff, note, friction
record, plan) or to clone or check out a repository for scratch work.

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
├── experiments/   harnesses, scripts, and files you write that fit nowhere else (never /tmp —
│                  the next session can't see it); never a clone or worktree
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
findings (`reviews/`), learnings (`what-did-we-learn`) and issues (filed after triage); it may link
to any of them. Preserve the raw record; correct it in place under A2, quoting the old text,
marked and dated. Its promotion path is friction → triage → a
recurring, reproducible issue → a durable learning, rule, skill or script. Capture is
non-blocking: it creates no checkpoint and stops nothing.

**Clones.** No clone of a repository, and no worktree, is written under `_agent/`. A scratch clone
lives in the client's own scratch directory, outside `_agent/` — your client file names that
directory, or records that it is unmeasured. What persists is the evidence: the commands run and
their output, under `evidence/`, with the remote and the commit needed to rebuild the clone.
Before the remote, a command or its output is written under `evidence/`, the secret comes out, by
the remote's form, wherever a remote appears, because a remote can carry credentials, a command
records one as typed (a `git clone` of a URL with a token in it), and the plain ways of reading a
remote print them verbatim: an http(s) URL loses its whole userinfo, since a token can stand where
a user name does and the two cannot be told apart; an ssh remote keeps its user name and loses any
password; a remote of any other form loses its whole userinfo; and any credential the clone uses,
a token or an authentication header among them, is stripped from a captured command and its
output.
Keeping that evidence is how this sits beside the `experiments/` line's "never /tmp": a
transcript has to survive the session, a clone can be made again. The reason: a clone under
`_agent/` is a nested repository in a store meant to replicate, a second copy of a project's
source with its license, and the one thing in `_agent/` that is rebuildable (Brandon, 2026-10-12).
Scratch-clone rules move no existing lane tree; [worktree lifecycle](worktree-lifecycle.md) governs
new placement and retirement through the owning manager.
