# Amendment log — AGENT-WORKING-AGREEMENTS.md

Newest first; each entry says what changed and what produced it. Git history records *what*
changed — this records *why*, which a diff cannot. A rule's own `[learnings: …]` citation is its
receipt; this is the provenance of the *edit*. Moved out of the agreement 2026-09-13 to keep that
file to its rules; moved into this repo 2026-09-13 when the agreement stopped being machine-local.
Several amendments can share a date. Entries that carry a `(#n)` are same-day amendments in order,
highest first; entries written before that convention (2026-09-12 and earlier) do not, and are
simply in order. A bare `(n)` after a source — "CodeRabbit on claude-skills #62 (2)" — is a **count
of amendments in that batch**, not an ordinal; the two notations predate each other and neither is
being retrofitted onto the other.

- **2026-09-13 (#12) — B2: every commit runs the repo's hooks (#6).** Guard item 1 checked that
  hooks *fire*; nothing forbade turning them off. Every commit on #3 was made with
  `git -c core.hooksPath=/dev/null commit`, a Cowork device-bridge habit that would have skipped a
  `pre-commit` hook in any repo that had one. Surfaced while scoping #4 to CI only. Same principle
  as the override rule on claude-skills #73. B1 is not amended: the bridge fails item 1, and
  whether a bridge commit can run hooks at all is unmeasured.
- **2026-09-13 (#11) — the rules stop carrying their own biography.** Brandon: this repo states the
  agreements, it is not a running log of why they are that way — and several review findings were
  about prose that existed only to justify a rule. Item 3 went from nine lines (tri-state
  vocabulary, a ritual-step citation, carve-outs for lane commits and release-cut work) back to
  three: feature work lands on an initiative branch, scored when a commit would land, and what may
  be pushed to `develop` is B2's. The Codex gate hazard went from seven lines to three. The
  `[measured]` claim there no longer cites `_agent/evidence/…`: **a path outside this repo does not
  resolve in a clone**, so a citation to one is unreadable by the agent the rule is written for —
  provenance belongs here, in the changelog, not beside the rule. The evidence for that measurement
  is `_agent/evidence/2026-09-13-codex-standing-instructions-audit-01a09c32/` on Brandon's fleet.
  Two open review findings (how item 3 applies to lane commits; scoping the sandbox
  classification) were answered by deletion rather than by more prose: the surface they pointed at
  no longer exists. Every clause added to a rule is surface for the next finding.
- **2026-09-13 (#10) — three precision fixes from the release PR's review.** The `develop → master`
  PR (#5) reads the whole diff against the release branch rather than one commit at a time, and
  caught three things #3's incremental passes did not. B0's by-environment line said item 3 is
  checked "at its first feature commit", which licenses every later commit to skip the branch and
  ownership check — it is now checked before **every** feature commit. The same line claimed item 4
  was "measured" for Codex; `clients/codex.md` records only that it is **queryable** there (`gh`
  authenticated with the right scopes), which is not a repo's branches having been scored against
  their profiles — an evidence overclaim, corrected, with 4 still checked per repo. And
  `clients/codex.md` said a gate could be reported green if you disclosed which steps ran where;
  A5's bar is every named command succeeding, so the stalled step must be **run and pass** through
  the permitted route, with split execution allowed and disclosure still required.
  These pushed straight to `develop` as release-cut work under B2's review-not-branch rule —
  the first time this repo has exercised it.
- **2026-09-13 (#9) — an evidence claim retracted, twice.** Answering a review finding on #3, the
  Codex sandbox-stall hazard was relabelled from `[measured]` to "no raw capture retained" — a
  claim made **without looking**. The capture existed the whole time, 70 files under
  `_agent/evidence/2026-09-13-codex-standing-instructions-audit-01a09c32/` with a
  `SHA256SUMS.json`. The `[measured]` label is restored and now cites the capture. Found by the
  two-axis `code-review` the agreements require **before** a push, run only after Brandon asked why
  it had not been. Asserting the absence of evidence without searching for it is the A2 failure
  performed while arguing A2.
- **2026-09-13 (#8) — guard item 3 scores at the moment a commit lands, and can be *n/a*.** Two
  clients read the same item two ways on the same day: a Claude Code session scored it "doesn't
  apply: this session commits nothing"; a Codex session on the same kind of read-only pass scored
  it "not satisfied: checkout is on `master`" and downgraded itself to attended partly on that
  basis. The item was written as a flat condition, so both readings were defensible — and the
  stricter one is the harmful one, since a session that downgrades because it has not cut a branch
  *yet* puts Brandon back in the loop for exactly the work autonomous mode exists to hand off. Item
  3 now names the ritual step it governs (step 1), is scored at the moment a commit would land
  rather than by the checkout's current branch, and is *n/a* — neither holding nor failing — for a
  session that has not cut its branch yet or will commit nothing. The guard header and the
  by-environment line were reconciled to admit that third score. The change is **both** a tri-state
  score and a move of when the item is evaluated — from the checkout's current branch at pickup to
  the moment a feature commit would land. The branch name `fix/guard-item-3-timing` names only the
  second half. Also added to `clients/codex.md`: `claude plugin validate .` stalls inside the
  sandbox and completes outside it `[measured]`, its raw capture cited. A named instance of the
  sandbox-denial hazard already in that file, mattering here because that command is part of the CI
  gate item 2 requires.
- **2026-09-13 (#7) — the agreement became a repo, and Part C became four files.** It had
  been machine-local and uncommitted, instantiated per runtime from the `agent-workspace` template,
  which meant three clients could silently drift apart and the only history was this log. It is now
  `sansfaux/agent-working-agreements/`, and the environment appendices C1–C4 are
  `clients/{cowork,claude-code,codex,openclaw}.md`, reached through an index at the foot of the root
  file. **Parts A and B were not split and must never be**: they are what every client is judged
  against, and a rule behind an unfollowed link is a rule broken silently — the same failure mode
  already measured for the pointer itself. The appendices are the one part where exactly one file is
  ever relevant, which is what makes them safe to disclose progressively; the detail they can now
  carry without bloating the shared read is the actual gain. `scripts/check-index.sh` fails CI if the
  index and `clients/` disagree (verified against a deliberately unindexed file). A6 amended: the
  `sansfaux/` root now holds the clone rather than the loose file. `organize.sh` **stays at the
  `sansfaux/` root** — it derives the fleet root from its own location, so moving it into the repo
  would silently retarget every path it touches.
- **2026-09-13 (#6) — the Codex surface round-trips, on restart.** Following the previous
  entry, Brandon appended a line to `~/.codex/AGENTS.md` in his editor; it appeared in the
  Personalization field only after restarting the ChatGPT desktop app, while removing it in the
  field deleted it from the file immediately `[measured]`. C3 now records the asymmetry and its
  hazard — a file edit made while the app runs is invisible to it and can be discarded by the next
  field save. The pointer is script-editable with a restart, which is what the AWA repo migration
  needs; the cloud-Codex question stays open.
- **2026-09-13 (#5) — one Codex surface, not two.** C3 said the pointer lived on line 1 of
  `~/.codex/AGENTS.md`, and the day's guidance treated the desktop Personalization field as a
  separate place. Brandon's edit in the UI rewrote that file's entire contents `[measured]`, so they
  are one surface; C3's "how this file reaches you" bullet now records that, plus two open
  measurements (does a file edit propagate back to the field; what does a cloud Codex task get).
- **2026-09-13 (#4) — Codex moved from attended to autonomous.** C3's heading and its
  default-mode bullet said "attended **by instruction**, not by incapability"; Brandon lifted that
  standing instruction, so mode there is now decided by the capability guard alone, as in C2 (items
  1 and 4 measured passing 2026-09-13; item 2 stays a per-repo probe at pickup). B0's
  by-environment line updated to match. A scope bullet was added to C3 because that client's
  instruction field is wider than the others': it reaches every ChatGPT/Codex chat, so Part B and
  C3 apply only to a session with a local shell working a repo under `~/dev/sansfaux`, and
  elsewhere only Part A's honesty rules carry.
- **2026-09-13 (#3) — two stale sentences brought in line with the review-not-branch rule.**
  B2's first bullet said "never `develop` to land work" and B0 item 4's summary said "Agents never
  push a base branch" — both survived the 2026-09-13 rewrite and still forbade the release-cut
  pushes that rewrite had just permitted. Found by the #68 reviewer in the shipped template, which
  the #56 session corrected there and correctly declined to touch here. Fifth correction to this
  one rule; the ritual section at the head of Part B exists to stop a sixth.
- **2026-09-13 (#2) — the ritual itself is written down, at the head of Part B.** The file
  carried many rules *about* agents and no description of the release flow they serve, so each time
  the subject came up it was re-derived from principle — three times in two days, each derivation
  re-imposing a constraint the previous correction had lifted (a PR rule on `develop`; then a prose
  ban; then a narrow exception that still forced a PR for a version bump). Brandon named the
  pattern. Any rule touching a push, branch or merge must now name the ritual step it applies to.
- **2026-09-13 (#1) — B2's exception widened to all release-cut work, on the right principle.**
  Written the day before as "review findings only", it re-imposed in prose exactly what removing
  the PR rule from `develop` had just lifted, and would have forced a separate PR to land a version
  bump. Brandon caught it. The rule is now about **review, not branch**: release-cut work (bump,
  CHANGELOG, `dist/`, review fixes) pushes straight to `develop` because the release PR reviews it;
  feature work takes a PR because nothing else would.
- **2026-09-12 (third pass) — B2's push rule corrected, and the release-PR exception written.**
  B2 claimed "the protection rules enforce" the never-`develop` rule; after the two-profile split
  that is true only of `master`, so the claim was retired and the rule kept as a rule. The gap the
  #56 reviewer found is now closed rather than improvised: working a `develop → master` PR's review
  findings means pushing its head, which *is* `develop`, so autonomous orchestrators may push those
  fix commits and nothing else; attended mode keeps the mbox-and-Brandon-pushes shape it already had.
- **2026-09-12 (second pass) — B0 item 4 split into two profiles by branch role.** The single
  standard (PR + required check on both base branches) was wrong for the way every repo here works:
  `develop` is the head of the `develop → master` PR, so a PR rule on it makes working that PR's
  review findings impossible. Brandon named it after the first rewrite still got it wrong. The
  integration profile blocks only force-push and deletion; the release profile carries the PR gate.
  bp-portfolio's hand-built configuration was this shape all along and was twice mis-scored as a gap
  — correction recorded on #56 and in the skill's analysis. claude-skills re-applied to match
  `[measured: plain push to develop accepted, force-push rejected, direct push to master rejected]`.
- **2026-09-12 — B0 item 4 rewritten (the guard's own bar was wrong).** It required "Brandon's
  review"; applied to a single-account repo by the `branch-protection` skill (claude-skills #56),
  that froze every PR into `develop` and `master`, including the PR shipping the skill `[measured:
  #66 `mergeable_state` blocked → clean after re-applying at 0 approvals]`. Approvals are out of the
  guard; the PR rule, required checks, force-push/deletion blocks and the absence of bypass actors
  are in. Added the honest limit: at 0 approvals nothing mechanically stops an agent merging its own
  PR, so "only Brandon merges" is prose here. Surfaced by the #56 session and its independent
  reviewer; the ticket's acceptance criteria were amended in place the same day.
- **2026-09-12 — wave-8 amendments (5).** A4 gains the concede-the-vector clause; A7 gains the
  create-then-link retry rule; B1's apply-block gains rider-is-a-delta; C1's overwrite and
  re-staging bullets gain the shrinking-rewrite and `stagedPath` re-commit traps. Proposed by the
  bp-portfolio wave-8 orchestrator (`_agent/handoffs/2026-09-12-awa-v2-amendment-proposals-handoff.md`),
  reviewed here: one proposed drop (amend-vs-delta) was partly restored, one proposed clause was
  cut as a retelling of wave-6 §6 and as overclaiming, and all citations were re-pointed from
  initiative to promoted numbering.
- **2026-09-11 — CodeRabbit on claude-skills #62 (2).** B1: `git am` *is* the commit step and runs
  the applypatch hooks (the earlier "skips husky" shorthand over-claimed); the attended lane cap
  reads "two by default; three is earned" rather than contradicting itself.
- **2026-09-11 — claude-skills wave-1 close-out (5).** C2's lane branches take the flat
  `wave-<n>-<lane>` form (git refuses a ref that is a path prefix of another); A6's index gains a
  mode column; B1 scopes the sub-agent ban to the shared checkout and restores v1's
  tickets/live-verification clause, dropped in the v2 rewrite; B2 gains the addenda rule; B0/C2
  record Claude Code's measured guard results and ≥ 3 lane concurrency.
- **2026-09-11 — Brandon (3).** A1: the agreement governs every session on any of his repos —
  initiatives organise orchestrated work, they do not gate applicability. B0: the environment picks
  the mode, never a start-of-session question; the guard runs silently and only downgrades. B0
  item 4: a missing branch protection is recorded, not a downgrade, until claude-skills #56 lands.
- **2026-09-10 — v2 authored** with Brandon (Parts A/B/C; attended and autonomous modes; the
  capability guard). v1 quarantined at `_agent/quarantine/2026-09-10-AGENT-WORKING-AGREEMENTS-v1.md`.
