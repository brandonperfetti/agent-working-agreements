# Review, review-bot findings and merges

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The core links it directly,
so it reads with or without a profile. Without one, follow only the portable mechanics here, with
the owner's and repository's actual conventions (core *Composition*): a studio name stands for the
core term it binds — Brandon the owner, `code-review` the review route, `develop` and `master` the
integration and release branches, `_agent/` the artifact store, a ticket the tracker the
repository uses — and a passage opening **Selected studio profile only** binds only when
`profiles/sansfaux.md` is selected, through the end of its paragraph and any list under it.

**Trigger:** A delivery, fix, lane merge, conflict resolution or release is ready for review; a
review-bot finding (with the studio profile, CodeRabbit's CLI or PR bot) has been posted; a
reviewer's note needs an outcome; a PR is about to merge.

**Owner:** The independent reviewer for the verdict and merge eligibility; the delivery owner for
working the findings; the orchestrator for routing fixes to lanes.

**Implements:** A4 — independent review and its escalation, acceptance and staleness, the harm
threshold and its three outcomes, base merges.

**Stop:** A verified harmful finding holds the merge until fixed; spending outside an approved
allowance holds the paid review, never the push (B2); a delegated merge with a condition unmet
is not made — the delivery owner repairs a repairable one, and a control's denial stops that
operation with its restoring owner named (*Base merges*).

---

## Who reviews

- **Every delivery is reviewed before acceptance** — riders, review-fix lanes and merge-conflict
  resolutions (scoped to the resolution, B2) included, no size exemption. The producer's own
  report is never the review; the verdict is recorded where the artifact store keeps review
  records (B1 or B2, by mode).
- **One independent reviewer, two conclusions.** Ordinary work needs one reviewer that did not
  produce it, recording a **Standards** conclusion (does it follow the repository's documented
  standards?) and a **Spec** conclusion (does it do what the governing brief asked?) separately,
  each with its own verdict. Two separate reviewers, one per axis, also satisfy this.
- **A second, focused reviewer joins** when the change touches security or authorization, a
  destructive or difficult data migration, a public contract, difficult cross-system behaviour, or
  authority, review or merge controls; when verification is insufficient; when material
  uncertainty remains; or when producer and reviewer disagree unresolved. The first reviewer, the
  delivery owner or the orchestrator may call it; it examines the risk that called it, not a
  repeat of the whole review. A policy change is reviewed under the rules in force before it
  merges, never under its own new text.
- **An orchestrator's hand-back is never the review of its wave:** it names the claims to
  re-measure, and before a merge a reader outside the wave reads them against the repository. The
  seat follows the situation (a session supervising dispatched agents), not the client. In attended
  mode Brandon's per-batch review is that reader (Brandon, 2026-10-12).

**Selected studio profile only:** the verdict is recorded under the initiative's `reviews/`, or
for work with no initiative under the `_agent/` root's one-off `reviews/`.
[learnings: 2026-09-06 wave-6 §5; 2026-09-04 wave-5 §7]

## Acceptance and staleness

- **Before any base merge, the whole branch is accepted** — its full diff against the base, not
  only the latest change — **at an exact head SHA** the verdict names; close-out review precedes
  promotion. Each later fix gets its own independent review scoped to it, naming its SHA, the prior
  acceptance's head, base and spec, the delta between them and which conclusions it affects.
- **The whole-branch acceptance is renewed only when a fix or a base move materially stales it:**
  observable scope or behaviour changed, reviewed logic was substantially rewritten, a conflict
  resolution changed semantics, the base moved the reviewed surface, or the verification basis
  changed. Otherwise the
  acceptance carries forward on that short confirmation, never on a prior PASS label alone, and
  the presentation names its SHA and each later fix SHA (Brandon, 2026-10-27, #193). A client's
  own documents point here and set no stricter timing.
- **A release carries feature acceptance forward only after a check of:** the complete release
  composition (every change it ships, each accepted or reviewed now), source identity (the shipped
  content is the accepted content), base compatibility, release metadata (version, changelog, built
  artifacts), the verification basis, and what the release merge deploys or publishes. Release-cut
  work and new release risk are reviewed as any change. The release record names each carried
  acceptance's head, base and spec, the delta since (zero, stated, when none) and the conclusions it
  affects. A matching patch-id alone never establishes acceptance; a second PR alone never
  invalidates it. Required CI and behaviour proof still run.

## Bot stages

The order of internal review, bot preflight and the PR bot round, with the preflight's triggers
and exceptions, is B2's: the preflight bullet of
[`autonomous-delivery.md`](autonomous-delivery.md)'s Git contract.

## Findings

- **A finding is fixed before the merge when it is verified and does real harm:** wrong behaviour,
  a result reported as clean that was not, a leak, a signal or write to something not identified, a
  held push or a hang. One the code disproves is declined. One that holds but does no such harm has
  three outcomes, by size; they govern a reviewer's notes as well as the bot's, and the verdict
  rests on verification, not on a severity label, release PRs included (Brandon, 2026-10-18):
  - **Small, fixed in the PR:** inside the files the PR already changes, or a line elsewhere that
    the PR's own change makes untrue, needing no new decision (a clause, a word, a test pin). It
    goes to the lane that owns the file, with a review scoped to the fix. A session that dispatches
    no lanes is the file's lane, the scoped review still required. Where lanes exist and none owns
    the file, on a wave or feature PR the orchestrator extends one lane's fence to it for one
    addendum, recorded; on a release PR the fix goes to the owning lane or a review-fix lane the
    orchestrator dispatches (Brandon, 2026-10-20).
  - **Not worth a change, noted:** recorded in the review record with a one-line reason; no ticket.
  - **Real work, a ticket:** outside the PR's files and the lines it makes untrue, a new decision,
    or more than a small fix.
- **A re-review round continues only while it surfaces a new, verified, harmful finding;** a round
  that surfaces none closes the loop, which is what "clean" means (Brandon, 2026-10-27, #193).
  Diff growth after the first review is evidence to investigate, never a target (#242). When three
  rounds in a row find harm in the mechanism the change itself adds, the delivery owner stops
  fixing and asks the owner whether to move the check to another layer or narrow its claim, a
  strategy change under B2 item 2; other work continues (Brandon, 2026-11-07, #243).

**Selected studio profile only:** the bot is CodeRabbit, by CLI or on the PR, and it keeps
reviewing release PRs (Brandon, 2026-09-29). An accepted finding's thread gets "Fixed in `<sha>`";
a noted one's its one-line reason; a ticketed one a short reply where it has a thread; a closing
round's remaining threads are answered the same way. **Declines are argued per thread with cited
receipts** (file, test name, documented ops order); bare declines teach the bot nothing
[learnings: 2026-09-06 wave-6 §6]. **When a re-raise names a vector the decline missed, concede the
vector and re-argue the trade on purpose and cost**, never by repeating evidence the bot has
weighed [learnings: 2026-09-12 wave-8 §22]. **Use only an approved funded allowance** for paid
reviews; an exhausted allowance or unapproved charge holds that paid review, never the push (B2).

## Base merges

The owner merges every release. An integration-branch merge is the delivery owner's only through a
route the binding names and records as **active**, for the repositories and clients it names;
otherwise, a dormant or missing route included, the owner merges. Merging this procedure, a
skill, a guard or a passing source scenario activates nothing: a route is activated by a reviewed
change to the binding after its qualification on a disposable fixture (positive and refusal cases
on the server and on each client named), never by an otherwise unauthorized real merge. Later
real merges are observations, not qualification.

**Eligible work** — routine work in the binding's scope, confirmed by the independent reviewer at
the exact head; the producer's own label never suffices. Already-approved scope; whole-branch
Standards and Spec acceptance at head `H` against an actual spec (a missing spec is an evidence
gap, never a pass); no open escalation trigger; every effect of the merge known and inside the
repository's recorded effects — workflows on the base, hosting (deploy matchers, build hooks),
environments, webhooks and integrations; a surface that could not be read is recorded as
uninspected, never as no effect, and "no workflow" is never "no effect". An unknown effect is
investigation before the merge. **Never delegated:** a release; a change to authority, review or
merge controls (an agreement, a review or merge skill, a guard hook, branch protection, the CI
gate), which stays the owner's merge with its focused reviewer; work integrated under A4's
no-reviewer exception. File count and Markdown-only status are no evidence.

**Before the merge.** The expected checks are named by context and source from the repository's gate
and its PR-triggered workflows; on `H` each is present, completed, the latest run, and a success —
skipped or neutral only where that workflow's own conditions explain it. An absent check fails; a
repository with no expected PR check records its disposition (the full gate on the merge result,
seen by the reviewer). Commits in the base-to-`H` range pass the author and attribution read. The
repository has no open issue labelled `route-suspended`; a check that cannot be read counts as
suspended, and a suspension opened after that read does not stop a merge already under way. If the
base has moved since acceptance, the delivery owner gathers what the movement changes — behaviour,
workflows, effects, the verification basis, not only paths — and the independent reviewer carries
the acceptance forward or renews it (*Acceptance and staleness*); the producer never issues it. A
moved head, conflict, failing, pending or absent check, stale review or open finding is the delivery
owner's to repair, within the existing bounds: the conflict procedure's progress rule, the
three-round stop above, and B2's restoration rule.

**The operation** is one command, alone: `gh pr merge <N> --repo <owner/name> --merge
--match-head-commit <H> --author-email <bound author>` — never `--admin`, `--auto`, a squash, a
rebase, branch deletion or a custom message. No API call is an equivalent route; one may qualify
later under this procedure, and none is switched to after a refusal. The response is read, not
its status code alone: a repairable state goes back to repair; an ambiguous or failed transport is
followed by reading the PR, the branch and the commit before any fresh attempt, and a still
unknown outcome is reconciled, never assumed failed or repeated. A denial by a permission, ruleset
or hook stops that operation — no other flag, API, account or hook edit — and names the control's
owner, who restores an authorized route if one is intended.

**After the merge,** the merge commit's parents, author, committer and message are read. A wrong
accepted head, a wrong author or a prohibited attribution, or another merge shape suspends the route
in that repository: whoever finds the fault opens an issue there labelled `route-suspended` (one
that cannot be opened is reported to the owner, and no delegated merge runs there until it is),
history is kept, the restoration and incident owner is named, and no direct push or unapproved
rollback follows; the owner closing that issue restores the route. A red result or a material base
interaction is corrected by a normal reviewed PR into the integration branch.

**What the route does not guarantee.** The platform pins the head, not the base; checks, findings
and effects are read, not bound by the server. A base can move between the last read and the
merge, and the merged result can run its effects before anyone looks. A post-merge gate detects
some faults; it bounds no other consequence and reverses no deployment or data effect. The owner
accepted this for the binding's scope (Brandon, 2026-11-12, #264); a repository whose effects
need more uses a stronger pre-merge control, and the release branch is never delegated.
