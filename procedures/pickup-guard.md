# Capability guard at pickup

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27; "above" and "below" in it refer to the agreement section it implements.

**Trigger:** Pickup of any delivery: before the first commit on a checkout, and again for each
repository a session delivers to.

**Owner:** The delivery owner, per checkout and per repository.

**Implements:** B0 — Choosing the mode: the five guard items.

**Stop:** A failed item downgrades that delivery to attended with a one-line reason, except item 4
(recorded) and OpenClaw (B0's exception; stop-list item 5).

---

**Capability guard (every item that applies must hold):**

1. Native git on a real checkout — git executes hooks (so whatever the repo installs, e.g. husky,
   fires on commit); `rm`, worktrees, and `git branch -d` work. **Prove the hooks exist in the
   checkout you will push from:**
   `git push --dry-run <remote> <branch>`, usually `origin HEAD` — name both, because a fresh lane
   branch has no upstream and a bare `git push` dies before the hook. It sends no objects (git's
   own behaviour) but still contacts the remote, and must run the repo's `pre-push` hook **and
   show it**: the hook's own output, or for a silent hook the `run_command: …pre-push` line under
   `GIT_TRACE=1`. **The hook runs exactly as on a real push, with no dry-run signal** [measured
   2026-09-30, git 2.46.0, scratch repos: the same arguments, stdin and environment, and the hook's
   own side effect happened], so read it before probing and, where it would send data, neutralise
   that part for the probe while keeping its invocation visible under `GIT_TRACE=1` — for Git LFS,
   `GIT_LFS_SKIP_PUSH=1` [source: `git-lfs-pre-push(1)` uploads the LFS objects of the pushed
   range; `git-lfs-config(5)` documents `GIT_LFS_SKIP_PUSH`].
   **A dry run that dies before reaching the hook is no result, not a FAIL** — a bare push with no
   upstream, an unreachable host (both exit 128), or a remote or refspec that does not resolve (a
   remote not named `origin`; `HEAD` while detached, exit 1): fix the invocation or the route and
   probe again, and until the probe has run, item 1 has not held.
   A dry run that shows neither is a **FAIL** for that checkout, not a pass — it needs the repo's
   install step first, then the probe again. A repo that installs no `pre-push` hook has nothing
   to prove; record that instead. Worktrees share the main checkout's `.git/hooks`, so one probe
   covers them — unless `core.hooksPath` is relative (husky's `.husky/_`, a tracked `.githooks/`):
   that resolves inside each worktree, and the probe is per worktree.
   [measured 2026-09-17 and 2026-09-18, git 2.46.0, scratch repos]
2. The full CI gate (A5) can be run locally by the agent — *actually run it once at pickup*; the
   local shell is not the CI runner, and the project's agent docs name the exports it needs.
   **This probe is always permitted**, in either mode: it is how the mode gets decided, so B1's
   "Brandon runs the suites" governs routine runs afterward, not this one.
3. Feature work lands on an initiative branch no other initiative is using — its wave branch or a
   lane branch off it — or, for work with no initiative, on a branch of its own off `develop` for
   that piece of work (B2), with no other work on it, or a lane branch off that branch; never on a
   base branch. Scored when a commit would land, not by the checkout's current branch: a session
   that commits none does not fail it.
   What may be pushed to `develop` is B2's, not this item's.
4. The base branches are protected on GitHub **by role**:
   - **Integration branch (`develop`)** — force pushes and deletions blocked, no bypass actors, and
     **deliberately no pull-request rule and no required check**. `develop` is the *head* of the
     `develop → master` PR, so working that PR's review findings means pushing to `develop`; a PR
     rule there makes the CodeRabbit ritual impossible on every repo (Brandon, 2026-09-12).
   - **Release branch (`master`)** — a pull request is required, the CI gate is a required status
     check, force pushes and deletions blocked, no bypass actors.
   **A required approving review is not part of either profile**: agents open PRs as Brandon, GitHub
   forbids approving your own PR, and no bot here submits approvals, so a required approval enforces
   "nobody merges", never "only Brandon merges". Audit with the `branch-protection` skill, not by
   reading a settings page; a 404 on the classic endpoint is not "unprotected" when a ruleset covers
   the branch. **Until protection exists on a repo, a failed item 4 is *recorded* in MPD §0, or
   in the PR body for work with no initiative (B2; in attended mode, its one-off review record
   until a PR exists, B1), not a downgrade.**
   **What protection cannot enforce here.** Nothing in the repo settings stops an agent pushing
   straight to `develop`, or merging its own PR into `master` once the gate is green `[inference —
   untested, since testing it means merging into a protected branch]`. **Feature work never lands
   on a base branch, and only Brandon merges** are therefore rules of this agreement, not repo settings.
   Brandon explicitly accepts the shared-identity risk for now (2026-10-31). Separate agent
   identities remain a future goal; this agreement does not initiate that migration. Preserve the
   branch protections and Git ritual, and report a measured breach. A settings PASS is never proof
   that agents cannot act as the owner or that the human-merge boundary is mechanically enforced.
5. Brandon has not overridden the mode to attended for this session.

By environment: each client's appendix records how that client scores against these items and
what has been measured there; none is assumed from the client's name.
