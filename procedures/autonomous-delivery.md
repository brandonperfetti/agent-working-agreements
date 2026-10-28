# Autonomous delivery

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27; "above" and "below" in it refer to the agreement section it implements.

**Trigger:** B0 selected autonomous mode for this delivery.

**Owner:** The delivery owner owns the branch until Brandon merges; the orchestrator dispatches and
routes; the independent reviewer verdicts.

**Implements:** B2 — Autonomous mode: the git contract, addenda, the review loop.

**Stop:** The B2 stop-list in the agreement, which this file does not restate.

---

Brandon's review moves to the pull request. The delivery owner (A4) owns the branch until then.

**Feature work with no initiative** has no wave orchestrator, MPD or initiative folder, so the
session doing the work holds the orchestrator's duties, and the delivery owner's where no
specialist is assigned (A4, which lists both; this section carries their procedure); its review
verdicts and other
records go under the `_agent/` root's one-off folders (A6's tree), and its decisions and a failed
item 4 (B0) are recorded in the PR body, which such work always has (Brandon, 2026-10-18).

**Git contract**

- The wave's delivery owner cuts **one branch per wave off `develop`**
  (`<initiative>/wave-<n>`), and that is the **only** branch an agent pushes to land an
  initiative's **feature** work. Feature
  work with no initiative has no wave: it gets **one branch of its own off `develop`** for that
  piece of work (the ritual's step 1), with no other work on it, and that is the **only** branch an
  agent pushes to land it. **Never `master`, never a force-push, and never feature work pushed
  onto `develop`.** Protection enforces this only on `master`; `develop` blocks force-pushes and
  deletions but accepts pushes by design (step 4 of the ritual), so it is a rule you keep, not a
  wall you hit.
- **What decides is review, not the branch name.** `develop` accepts pushes by design; the question
  for any commit is whether it will be **reviewed before it reaches `master`**.
  - **Release-cut work pushes straight to `develop`** — the version bump, the CHANGELOG section
    rename, any built artifact the repository commits, and every fix commit answering the
    release PR's review. All of it
    is reviewed *on the `develop → master` PR itself*, whose head is `develop`; there is no other
    branch to push and no second review to wait for. Same gate, same two-axis review before the
    push, never a force-push.
  - **Feature work always goes through its branch (above) and a PR into `develop`** — pushed
    straight, it would reach `master` having been reviewed by nobody. That, not the branch, is the
    reason.
  In **attended** mode the shape is B1's: a lane delivers either an mbox series from its isolated
  clone or uncommitted edits to its named files in the shared checkout. For uncommitted edits the
  delivery owner (A4) stages them and shows the staged diff before Brandon's batch approval, then
  commits after it; an mbox series the delivery owner applies with `git am` only after that
  approval, since `git am` is the commit. Brandon pushes.
- **Each lane works in its own git worktree on a branch off the wave branch** (for work with no
  initiative, off that work's own branch, B0 item 3) and commits there with the repo's hooks
  firing (this replaces mboxes + `git am`). Lane commits keep RULE ZERO
  (A4); the lane still writes its **on-disk handoff doc** (premise, files, tests, gate line
  with the repro named, model it ran on).
- **The delivery owner merges a lane into the wave branch** (for work with no initiative, into that
  work's own branch) **only after two-axis review passes** (A4), records the verdict in
  `reviews/`, **re-runs the full CI gate on the merged branch, runs `coderabbit-preflight` when the
  push carries new work (below) and the CodeRabbit CLI is available to that client, then
  pushes.**
  Push after every lane merge — the remote is the backup and CI runs per merge so flakes surface early.
- **A lane merge that conflicts goes back to the lane.** The lane merges the wave
  branch into its own branch in its own worktree — a merge commit, never a rebase, which would
  rewrite commits it has already reported — resolves there and re-runs the gate; the resolution
  gets a scoped review, as an addendum's fix does; the delivery owner's merge is clean against
  the tip the lane merged, and a wave branch that has moved since is the same rule again — a
  merge that
  conflicts goes back to the lane. Only
  where the lane is no longer available does the delivery owner resolve, and its resolution gets a
  scoped two-axis review before the push. A resolution is new work, and no work reaches the wave
  branch unreviewed (Brandon, 2026-10-12). Inside a resolution, whoever resolves:
  - **Bounded evidence-led recovery when the gate shows a red of the resolution's own — one absent
    from both sides' pre-merge gate records:** take multiple causally supported, in-scope corrective
    actions only within a finite recovery budget recorded before the first corrective action and
    left unchanged throughout recovery. After each action, save the action, its evidence, and a
    relevant re-check under `evidence/`; the re-check demonstrates recovery
    progress only and does not permit the merge commit. Continue only while the trail shows
    evidenced progress. Stop and reassess when the budget is exhausted, the premise is disproved,
    the next action expands scope or crosses a destructive, security, credential, or merge
    boundary, or a re-check makes no evidenced progress. If recovery ends unresolved, save the
    resolution diff and gate output, then `git merge --abort` back to the pre-merge tip. Only a
    successful full CI gate on the resolved merged tree permits the merge commit; the resolution's
    scoped two-axis review remains required. A branch left mid-merge holds unreviewed work where
    the next reader may not know a merge is in progress, and on the wave branch it blocks every
    other lane's merge; the pre-merge tip was reviewed, and the record keeps what the attempt
    learned. [learnings: 2026-10-18 openclaw-autonomy-and-recovery §2]
  - **A red that a side's own gate record already shows is that side's, not the merge's:**
    reported with that record, not fixed inside the merge — a lane may hand back with a gate step
    red by design, named in its handoff, and a fix to it inside the merge would be an unreviewed
    change to that side's work. The delivery owner's merged-tree gate before the push is unchanged.
- **The preflight runs once before each push that carries new work** — a lane landing, a release
  cut — and never before a push that only answers review findings, which the PR's own review
  covers; there is no re-run. An unavailable CLI never holds a push and never downgrades the mode:
  the round is recorded as not run, and the PR round is the review. The skill carries the rules of
  a run, the checks that decide whether the CLI is available among them.
- **Open the ready-for-review PR against `develop` at the first push. CodeRabbit runs on that ready
  PR, and the delivery owner completes the round before hand-back.** The PR uses the
  `writing-pull-requests` shape; its body is seeded under the initiative's `pull-requests/` and
  grown as lanes land.
- **File-disjoint lanes may run in parallel up to the measured cap**, which each client file
  records where it has been measured. A client without one measures its own Agent tool before
  assuming concurrency and records the number in the MPD.
- **Agents run the full CI gate themselves** — every lane before handing back; the delivery owner
  on every merged tree before every push. CI on the PR is the arbiter for flakes.
- **Issues:** agents file the findings that are real work (A4) freely via `writing-tickets`,
  labelled **`agent-filed`**, so Brandon can sweep them. Closing or relabelling existing issues is
  orchestrator-only and cited. Board intake is a repository's own `add-to-project` workflow,
  issues only ([`github-paths.md`](github-paths.md)).

Non-blocking questions batch at the wave boundary. Rotation stays per wave with a packet.

**Addenda:** a defect found in review goes back to the **same lane, in its worktree, as a new
commit**, and is re-reviewed (scoped to the fix) before merge — never a fresh session, never the
orchestrator's own hands, except where the session dispatches no lanes: that session counts as
that lane, the scoped two-axis review still required (A4). Where the session dispatches lanes and
none owns the file, the orchestrator extends one lane's fence to that file for one addendum, and
that lane makes the fix, the scoped review still required and the extension recorded (A4). While
the wave PR is open, a small fix (A4) to work already merged into the wave branch rides it,
through the owning lane or the lane whose fence was extended to the file, a scoped review and a
push; a fresh ticket is for real work (A4), and for work found after the wave PR has
merged. On a release PR, A4 names who makes a small fix.
A lane merge that conflicts goes back to the lane the same way (Git contract above).

**The review loop (Brandon, the delivery owner and the orchestrator)**

1. **Before each push that carries new work, the delivery owner runs `coderabbit-preflight`** where
   the CodeRabbit CLI is available (Git contract above).
2. **The delivery owner opens the feature PR ready for review; CodeRabbit runs; the delivery owner
   completes the round before hand-back.**
3. The delivery owner works the review end-to-end with `coderabbit-response`: verifies every
   finding, has the orchestrator redispatch the fixes A4 calls for to lanes (worktrees, review,
   merge, push as above), replies per thread with receipts, monitors re-reviews to clean.
   Brandon's review is the PR's final state, not the threads.
4. **Brandon alone merges, manually, in the GitHub UI** — wave PRs into `develop`, and the release
   PR `develop → master`, which the delivery owner may open as a draft with a changelog. Closing
   keywords fire on the default branch; the orchestrator moves issues to In Review at PR time.
5. `what-did-we-learn` runs at wave close; promoted lessons go to `_agent/learnings/`, and
   any friction the wave met goes to its `friction/` (A6).
