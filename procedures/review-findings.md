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
allowance holds the paid review, never the push (B2); a delegated merge with any condition unmet
is not made, and the owner merges.

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

The internal review and its fixes come first, except under A4's no-reviewer exception, which
pushes before independent review. The required bot preflight then runs under B2's triggers; its
accepted findings are fixed, and the review or gate evidence they affect renewed, before the PR bot
round, which still runs. The two stages keep separate allowances; neither is
skipped for a routine change, and no paid fallback replaces either.

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

The owner merges base branches. An integration-branch merge may be delegated to the delivery
owner only through a route the binding names as qualified; with none named, the owner merges.
Installing a skill or passing a source scenario names no route.

**Eligible work** — the independent reviewer confirms it in the verdict at the exact head; the
producer's own label never suffices: already-approved scope, predictable localized effects,
adequate proof, inexpensive recovery, a Spec conclusion against an actual spec (a missing spec is
an evidence gap, never a pass), no escalation trigger above, and an integration merge that deploys,
publishes or notifies nothing outside the repository, read from the repository's actual workflows
and hosting, not inferred from the branch name; an unknown effect is ineligible, and a text revert
is no proof of recovery from deployment, data or notifications. Work integrated under A4's
no-reviewer exception is never eligible. Changes to authority, review or merge controls
(an agreement, a review or merge skill, branch protection, the CI gate) are never eligible. File
count and Markdown-only status are no evidence. The release branch is never delegated; the owner
approves and merges every release.

**A qualified route establishes, at the moment of merging and on the platform's current state:**
the PR's head is the accepted SHA; its base is the integration branch at an expected SHA, so the
merge result is the reviewed result; required checks passed and findings are dispositioned on
that head; the merge commit carries the bound author identity; and the actual repository effects
are as checked. A head pin alone does not guard a moving base, a locally pinned commit does not
prove the PR's head stayed unchanged, and a normal non-force push only refuses a push that is not
a descendant of the remote tip: an ancestry check, not a compare-and-swap against an expected base
SHA. Required checks, protections and hooks stay as they are; a guard that refuses an operation is
not routed around with another command. Qualification uses disposable fixtures for its positive
and refusal cases, never an otherwise unauthorized real merge. Any unmet condition or refusal ends
the attempt, without a retry under other arguments, and the owner merges.
