# Two-axis review and review-bot findings

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27 and split into portable and studio passages in #226; "above" and "below"
in it refer to the agreement section it implements. The core links it directly, so it reads with
or without a profile. Without one, follow only the portable mechanics here, with the owner's and
repository's actual conventions (core *Composition*): a studio name stands for the core term it
binds — Brandon the owner, `code-review` the review route, `develop` and `master` the integration
and release branches, `_agent/` the artifact store, a ticket the tracker the repository uses — and
a passage opening **Selected studio profile only** binds only when `profiles/sansfaux.md` is
selected, through the end of its paragraph.

**Trigger:** A delivery, fix, lane merge or conflict resolution is ready for review; a review-bot
finding (with the studio profile, CodeRabbit's CLI or PR bot) has been posted; a reviewer's note
needs an outcome.

**Owner:** The independent reviewer for the verdict; the delivery owner for working the findings;
the orchestrator for routing fixes to lanes.

**Implements:** A4 — two-axis review, material staleness, the harm threshold and its three outcomes.

**Stop:** A verified harmful finding holds the merge until fixed; spending outside an approved
allowance holds the paid review, never the push (B2).

---

- **Two-axis review (Standards + Spec, `code-review` skill) on every delivery before acceptance —
  riders, review-fix lanes and merge-conflict resolutions (scoped to the resolution, B2)
  included, no size exemption.** The lane's own report is never the review; the verdict is
  recorded where the artifact store keeps review records (B1 or B2, by mode).

  **Selected studio profile only:** the verdict is recorded under the initiative's `reviews/`, or
  for work with no initiative under the `_agent/` root's one-off `reviews/`.
  [learnings: 2026-09-06 wave-6 §5; 2026-09-04 wave-5 §7]

  **An orchestrator's hand-back is never the review of its wave either:** the hand-back names the
  claims to re-measure, and before a merge a reader outside the wave reads them against the
  repository, because the party that produced the work does not attest to it, and rotation changes
  who orchestrates the next wave without adding a reader before the merge. That reader's seat is
  set by the situation — a session supervising dispatched agents — not by the client, because most
  sessions own their work, as they should, and Genesis builds the MPD with Brandon by design. In
  attended mode Brandon's per-batch review is already that reader (Brandon, 2026-10-12).

  **Before a delivery is presented for Brandon's merge, the independent reviewer runs the two-axis
  review over the whole branch** — its full diff against the base, not only the latest change —
  **at an exact head SHA**, and the verdict names that SHA; close-out review precedes promotion
  (A4). Each later fix gets its own independent
  two-axis review scoped to it (above), naming its SHA. **The whole-branch verdict is renewed only
  when the fix materially stales it:** observable scope or behaviour changed, reviewed logic was
  substantially rewritten, a conflict resolution changed semantics, the base moved the reviewed
  surface, or the verification basis changed. A fix that stales none of these rides the existing
  verdict, and the presentation names the verdict's SHA and each later fix SHA (Brandon,
  2026-10-27, #193; this replaces the renewal-after-every-change rule of 2026-10-23, #173). A
  client's own documents point here and set no stricter timing.

- **A review-bot finding is fixed before the merge when it is verified and does real harm:** wrong
  behaviour, a result reported as clean that was not, a leak, a signal or write to something not
  identified, a held push or a hang. One the code disproves is declined. One that holds but does
  no such harm has three outcomes, by size.
  **Small, it is fixed in the PR:** the fix stays inside the files the PR already changes, or a
  line elsewhere that the PR's own change makes untrue, and needs no new decision (a clause, a
  word, a test pin); it goes back to the lane that owns the file, with a two-axis review scoped to
  the fix (above). The line elsewhere counts because
  otherwise a PR ships text that contradicts itself and leaves a ticket to fix it later, which is
  what the small-fix outcome exists to prevent (Brandon, 2026-10-20).
  A session that dispatches no lanes counts as the file's lane, the scoped review still required;
  on a release PR, the fix goes to the lane that owns the file or to a review-fix lane the
  orchestrator dispatches for it. The route assumes a lane exists, and without this a session that
  is both orchestrator and only author has no one allowed to make its own small fix, and a release
  PR's fix has no named owner (Brandon, 2026-10-20).
  Where the session dispatches lanes and none owns the file, on a wave or feature PR, the
  orchestrator extends one lane's fence to that file for one addendum, and that lane makes the
  fix, with the two-axis review scoped to the fix still required and the extension recorded: a
  lane already working the change has its context, so this is the cheapest route that keeps the
  fix out of the orchestrator's own hands (Brandon, 2026-10-20).
  **Not worth a change, it is noted:** recorded in the review record with a one-line reason, and
  no ticket. **Real work, it becomes a ticket** — outside both the PR's files and the lines its
  change makes untrue, a new decision, or more than a small fix.
  The same three outcomes govern a reviewer's notes, not only the bot's findings, because a ticket
  for a one-clause fix costs a later wave what a commit in the PR would have done, and a backlog
  that takes every harmless finding refills as fast as waves clear it (Brandon, 2026-10-18).
  The verdict rests on verification, not on the bot's severity label, and the same threshold holds
  on release PRs. **A re-review round continues only while it surfaces a new, verified finding
  that does real harm;** a round that surfaces none closes the loop, and that is what the ritual's
  "clean" means (Brandon, 2026-10-27, #193). Growth of the diff after the first review is
  evidence to investigate, never a target: the threshold above decides each finding, whatever its
  origin (#242). When three rounds in a row find harm in the mechanism the change itself adds, not
  in pre-existing code or wording, the delivery owner stops fixing and asks the owner whether to
  move the check to another layer or narrow its claim, a strategy change under B2 item 2; other
  work continues meanwhile (Brandon, 2026-11-07, #243).

  **Selected studio profile only:** the bot is CodeRabbit, by CLI or on the PR, and it keeps
  reviewing release PRs (Brandon, 2026-09-29). An accepted finding's thread gets "Fixed in
  `<sha>`"; a noted one's thread gets its one-line reason; a ticketed one gets a short reply on its
  thread where it has one; a closing round's remaining threads are answered the same way.
  **Declines are argued per thread, where there is one, with cited receipts** (file, test name,
  documented ops order). Bare declines teach the bot nothing.
  [learnings: 2026-09-06 wave-6 §6] **When a re-raise names a vector the decline missed, concede
  the vector and re-argue the trade on purpose and cost** — never by repeating evidence the bot has
  already weighed. [learnings: 2026-09-12 wave-8 §22] **Use only an approved funded allowance** for
  paid reviews; an exhausted allowance or unapproved charge holds that paid review, never the push
  (B2).
