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

- **2026-09-23 (#2) — feature PRs open ready and finish CodeRabbit before hand-back.**
  [decision 2026-09-23, Brandon] Issue #46 records the ratified practice: agents open feature PRs
  into `develop` ready for review, complete the CodeRabbit round before hand-back, and leave every
  merge to Brandon. The earlier pre-bot read moved to Brandon's external verification of the
  completed report, so the additional draft-to-ready relay bought nothing. Drafts had controlled
  CodeRabbit's measured 5-reviews/hour allowance; serial one-PR-at-a-time pacing now controls that
  cost without treating the current allowance as a permanent guarantee.
- **2026-09-23 — A6 defines an on-fleet workspace by its `_agent/` directory.** Issue #42 cited
  the installed `agent-workspace` convention
  (`skills/personal/agent-workspace/references/workspace-convention.md`, lines 7–10 at `366c84e`),
  which also treats `AGENT-WORKING-AGREEMENTS.md` as a nearest-wins marker. After the first draft
  transcribed that rule, a source read showed that it contradicts this agreement's preamble:
  “`_agent/` and `organize.sh` are at the root of the `sansfaux/` checkout tree — the parent of
  this clone, when it is cloned there” (lines 21–23). This agreement is itself a repository, so
  every clone and worktree carries the file at its own root and would resolve itself as the agent
  root. Following the 2026-09-17 (#2) precedent — “One departure from the ticket, on a
  measurement” — A6 deliberately departs from #42's cited convention: the directory containing
  the first `_agent/` found while walking upward is the agent root. A positive-controlled VPS
  audit of both live Git common directories found one resulting incident: the legacy delivery checkout
  contains an empty `_agent/notes/`; none of the other 15 registered roots contains `_agent/`.
  The incident was recorded and left intact at
  `_agent/evidence/2026-09-23-pr47-agent-root-marker-audit.md`.
- **2026-09-22 (#2) — on-fleet artifact placement outranks generic skill defaults.** Issue #39
  makes explicit that the `agent-workspace` convention governs artifact destinations on an
  on-fleet workspace ahead of a generic skill default. A1 already identifies the skills plugin as
  a mirror of `mattpocock/skills` plus Brandon's own skills, while A6 already owns workspace
  destinations and keeps experiments out of `/tmp`; those neighboring rules make the canonical
  agreement, rather than a patch to one mirrored skill, the durable place to settle precedence.
  Off-fleet fallbacks remain the skill's to define. This supersedes
  [claude-skills #113](https://github.com/brandonperfetti/claude-skills/issues/113).
  Release review clarified that the following `_agent/` layout sentence is on-fleet too, so an
  off-fleet fallback selected by a skill cannot conflict with a universal-sounding workspace
  destination.
- **2026-09-22 — every client resolves A2 to its evidence store.** Issue #11's remaining client
  mappings are now explicit: Claude Code uses the desktop's per-machine `_agent/` store; Codex
  records the same location as an inference that still needs separate measurement; Cowork uses the
  linked desktop store and takes no irreproducible measurement when no durable folder is linked.
  [measured 2026-09-22, current OpenClaw instance] OpenClaw's store resolves to the active
  workspace's `_agent/` tree. A2 remains the one portable source for the capture classification:
  preserve irreproducible bytes, but record a stable locator, SHA-256 and relevant excerpt (or
  searched terms plus absence) for retrievable evidence. The stores remain per-machine working
  state rather than repository content.
- **2026-09-21 — OpenClaw cutover names the rollback agreement.** PR #22 review found that the
  sentence after the workspace-root pointer used “that file,” which could identify `AGENTS.md`
  rather than the complete machine-local agreement. The appendix now names the complete
  machine-local agreement as the artifact preserved intact for rollback and still forbids editing
  it into a second canonical layer. This clarification changes no cutover state; Brandon still
  schedules the quiet window.
- **2026-09-20 (#2) — OpenClaw migration dispositions and cutover contract.** The appendix records
  which rules from the complete machine-local agreement are superseded by Parts A–B rather than
  carried forward: local autonomy, shared-checkout specialist delivery, unconditional build/test
  ownership, raw retention for every measured claim, remote-API commits, and the generic ask rule.
  It retains only OpenClaw mechanics already owned by the appendix and preserves B1/B2 topology.
  [measured 2026-09-20] This autonomous amendment used a dedicated worktree. The appendix also
  defines a Brandon-scheduled quiet window with an inventory, hash-and-quarantine rollback, a
  non-authoritative stale-reader stub, fresh or reset-session verification for adoption,
  fresh-session verification for rollback, and later reviewed cleanup.
  Merging this amendment does not change OpenClaw startup.
  [measured 2026-09-20, current Gateway host] The `claude-skills` route was attended after item 2
  failed; [claude-skills #111](https://github.com/brandonperfetti/claude-skills/issues/111)
  (private; repository access required) tracks durable Ruby and `zip` prerequisites plus
  remeasurement, but future mode decisions still come only from B0. That condition does not block
  pointer adoption. The OpenClaw B0 default remains
  unchanged until a separate post-cutover amendment can cite deployed main- and specialist-session
  evidence; its accepted target is autonomous with the per-session guard still deciding.
- **2026-09-20 — OpenClaw appendix promoted from stub; #11 advanced, not closed.** B0 already maps
  OpenClaw to attended; this amendment emphasizes that mapping, and the appendix now defers to that
  portable rule instead of restating it. [source 2026-09-20] The OpenClaw bootstrap still points to
  the complete machine-local agreement at `/data/.openclaw/workspace/AGENT-WORKING-AGREEMENTS.md`;
  the canonical pointer is a migration target, not current state. The appendix records that
  transition with a session-specific authority boundary, retains A4's RULE ZERO as the first line
  of every dispatch, and limits any retained workspace-local layer to client mechanics after Parts
  A–B supersede the complete local agreement; B2 still reserves merging to Brandon. A2 now
  classifies evidence before preservation:
  irreproducible bytes are retained, while retrievable evidence gets a stable locator, SHA-256,
  relevant excerpt, or searched terms plus absence. Named OpenClaw paths fall back to the active
  workspace's durable evidence store when unreachable, with its location recorded. This advances
  the portable portion of issue #11 without copying retrievable artifacts or closing the issue.
  Issue #13 remains unchanged and out of scope.
- **2026-09-18 — item 1's probe names its remote and refspec.** Issue #14's rule, corrected by the
  review on the release PR (#16). The probe was written as a bare `git push --dry-run`, which works
  only where the branch already has an upstream. A lane worktree is exactly where it does not:
  `git worktree add -b` sets none, and with git's default `push.default=simple` a bare push exits
  128 with "no upstream branch" **before** `pre-push` runs — so the probe reports no hook evidence
  in a checkout whose hooks are fine, and item 1 fails for the wrong reason. Round 2's carve-out
  does not cover it: that one is about dying on the *network*, this dies on configuration.
  `git push --dry-run origin HEAD` fires the hook in the same worktree
  [measured 2026-09-18, git 2.46.0, scratch repo: bare exit 128 and no sentinel; `origin HEAD` and
  a named refspec both fired it; `push.default=current` also fired it, which is why the rule names
  the refspec rather than relying on config]. `clients/claude-code.md` and `clients/codex.md` carry
  the same form. The two-axis review before the push then asked what the explicit form breaks that
  the bare one did not, and measured two: a remote not named `origin` (exit 128) and `HEAD` while
  detached (exit 1, "not a full refname") — both die before the hook as well. So the probe is
  written `<remote> <branch>` with `origin HEAD` as the usual case, and round 2's carve-out is
  generalised from "dies on the network first" to **dies before reaching the hook**, which is the
  property that makes all of these no result rather than a FAIL. Evidence, on Brandon's fleet:
  `_agent/evidence/2026-09-18-awa-pr16-cr/no-upstream-probe.{sh,out}` and
  `explicit-form-edge-probe.{sh,out}`.
- **2026-09-17 (#2) — guard item 1 proves the hooks exist, per checkout.** Issue #14, from
  sans-faux-studios wave 4 (learning 69 of its promoted learnings, 2026-09-17; MPD D28). Item 1
  asked whether git *would* run a hook, which is true of any native checkout; it never asked whether
  the hooks were there. A release-cut push to `develop` went out of a main checkout whose
  `node_modules` predated husky: `core.hooksPath` pointed at a `.husky/_` that only the install
  creates, so `pre-push` was absent rather than disabled — A5 does not cover it — and the push was
  harmless only because the sha had just passed the gate on a fresh clone
  `[measured 2026-09-17 by that wave's orchestrator]`. The probe is the one that caught it: after
  `pnpm install`, `git push --dry-run` ran the full gate line. **One departure from the ticket, on
  a measurement.** #14's Change section says worktrees inherit the main checkout's hooks, so the
  probe is per main checkout. That holds for `.git/hooks` and fails for the very configuration the
  ticket came from: git resolves a relative `core.hooksPath` inside each worktree, and `.husky/_`
  is untracked, so a fresh lane worktree has no hooks at all
  [measured 2026-09-17, git 2.46.0, scratch repos: a sentinel `pre-push` fired from main checkout
  and worktree under `.git/hooks`; from the main checkout only under `core.hooksPath=.husky/_`; a
  hookless control printed nothing]. Learning 69 itself says hooks are a per-checkout fact. Item 1
  states what was measured instead, and its older `[measured 2026-09-10]` label now stops short of
  the worktree sentence, which the 2026-09-17 probe re-measured. `clients/claude-code.md` points at
  item 1 rather than restating it, and its "never install a per-lane hook" became "a lane never
  installs a hook of its own", so running the repo's install in a worktree does not read as banned.
  Also not in the ticket: a repo that installs no `pre-push` hook has nothing to prove and records
  that — without it the probe fails this repo, which has no hooks and no install step
  `[measured 2026-09-17]` — and the by-environment line no longer says item 1 passes wholly by
  construction. *Review round 1 (PR #15):* the probe now names its positive evidence. A silent
  `pre-push` and a missing one print the same dry run; `GIT_TRACE=1` separates them — a
  `run_command` line naming the hook, absent with no hook [measured 2026-09-17, git 2.46.0, scratch
  repo, three cases: absent, silent, and present but not executable — a hint, no `run_command`].
  "Shows no hook having run" had left the instrument unnamed (A2: the
  instrument is part of the claim). And Codex's item 1 evidence is a `pre-commit` sentinel from
  2026-09-13, which says nothing about a per-checkout `pre-push` probe: B0's by-environment line
  and `clients/codex.md` now say the probe is unmeasured there and run at pickup. *Round 2:* the
  ticket's "(sends nothing)" became "sends no objects, but still contacts the remote", because the
  order matters: with an unreachable remote the dry run exits 128 before `pre-push` runs
  [measured 2026-09-17, git 2.46.0, scratch repo, loud sentinel hook], which item 1 would have
  scored as missing hooks and answered with an install. It is now no result, not a FAIL — and not
  a pass either: item 1 has not held until the probe has run. Only a DNS failure was measured; an
  auth refusal, which does reach the remote, was not. *Round 4:* the worktree exception had been
  narrowed to a relative `core.hooksPath` naming an **untracked** directory, because that was all
  the first probe measured. A tracked one is no safer: with `.githooks/` tracked, a worktree on a
  branch from before the directory existed ran no hook, and one whose branch had edited the hook
  ran the edited one [measured 2026-09-17, git 2.46.0, scratch repo] — the main checkout's probe
  speaks for neither. Any relative `core.hooksPath` now makes the probe per worktree; an absolute
  one is shared, and fired from main checkout and worktree alike [measured, same instrument].
  *Round 5:* `clients/cowork.md` had been left alone because #14 puts attended-mode installs out of
  scope, but its "item 1 fails here… not for hooks" rested on a `pre-commit` sentinel
  (2026-09-13 (#12)) and now read as covering the new `pre-push` half. It says what was measured,
  and that the probe is Brandon's: he pushes from his clone (B1), so it is his checkout the probe
  is about. No agent-run probe or install was added there. Evidence, on Brandon's fleet:
  `_agent/evidence/2026-09-17-awa-12-14-guard-and-worktree-hookspath-probe/` and, for the review
  rounds, `_agent/evidence/2026-09-17-awa-pr15-cr-round1/`, `…-cr-round2/` and `…-cr-round4/`.
- **2026-09-17 (#1) — RULE ZERO inverted: no attribution, and the audit that leaned on it named.**
  Issue #12, widened by its 2026-09-15 comment. The `Co-Authored-By` trailer was an environment
  default nobody chose; Brandon does not want it (Brandon, 2026-09-15), and said the same
  independently for sans-faux-studios (initiative `sans-faux-studios-template-upgrade`, MPD D11),
  one step further: no `Claude-Session` trailer and no "Generated with" PR-body footer either. A
  per-prompt override does not hold — each fresh agent inherits the default from whatever kickoff
  or environment it reads — so the rule is stated once, in A4, without naming a client, and each
  `clients/*.md` records whether its environment injects one, so the override has a named target:
  Claude Code does; Cowork's harness carries the same instruction, with no setting to switch it
  off [source: this session, 2026-09-17]; Codex and OpenClaw are recorded as unmeasured rather
  than guessed. RULE ZERO had been a *positive* check ("32 commits, all carrying the trailer" in
  the claude-skills branch-protection wave reports) and B2 told lanes to carry the trailers; it is
  now the negative check sans-faux-studios wave 1 ran — grep commits and PR body, a match is a
  send-back — under which that wave's PR #15 shipped clean
  `[measured 2026-09-17: its seven commits and its body, zero matches]`. The trailer had also
  drifted into standing for "this commit came through a reviewed lane", which it never established
  — a hand-made commit carries one as easily — so the same edit names what does: the two-axis
  review record, the gate evidence, the PR trail. Forward-only; nothing rewrites history. The
  sans-faux-studios MPD tracks this entry as its open item O5.
  *Review round 1 (PR #15):* the Cowork line first added "and nothing else writes to a commit
  message", a universal nobody measured (a `commit-msg` hook or a commit template could), so the
  delivery grep is named as the check instead.
  *Round 3:* the grep is scoped to the commits a delivery **adds**. "Every delivery's commits" plus
  "a match is a send-back" could send back history the same bullet says to leave alone: 195 of
  the 426 commits on claude-skills' `develop` already carry the trailer [measured 2026-09-17,
  `git log --format='%(trailers:key=Co-Authored-By)'` on `origin/develop` at `1201aa8`;
  sans-faux-studios, adopted after its own rule, had 0 of 64], so any range that reaches them — a
  release PR, a lane merging an old branch, a grep run without a base — would fail on commits
  nobody may rewrite. The first wording named no base, which would have let a lane's own commit
  from an earlier round pass as inherited; an inherited match also gained a destination, the
  review record.
  *Round 4:* that base was "when the delivery's branch was cut", and B2 lets release-cut work push
  straight to `develop` with no branch to cut. One definition now covers both: not already on
  `origin/develop` or `origin/master`, fetched and read before the delivery is pushed or merged.
  The review's proposal was a recorded baseline OID; the remote-tracking ref does that job only
  under the two conditions the rule now states — a stale ref moves the boundary, and after the
  push the added commits read as inherited — and with each release-cut push scored as its own
  delivery, before it goes. On the `develop → master` PR every commit was already on `develop`, so
  it is inherited there and was grepped when it arrived.
  *Round 5:* `clients/cowork.md` said "the grep on every delivery", which could be read without
  A4's boundary; it now points at A4's grep and scope rather than restating the rule, since a
  client file adds only what is client-specific. Captures:
  `_agent/evidence/2026-09-17-awa-pr15-cr-round3/` and `…-cr-round4/` on Brandon's fleet.
- **2026-09-13 (#12) — A5: never disable the repo's hooks to commit.** Issue #6. Guard item 1
  checked that hooks *fire*; nothing forbade turning them off. Every commit on #3 was made over the
  device bridge with `git -c core.hooksPath=/dev/null commit` [source: #4's decision comment]. Same
  principle as the override rule on claude-skills #73: a guard an agent can lift on its own is not a
  guard. First drafted for B2 alone, on the theory that bridge commits might not be able to run
  hooks; Brandon's probe the same day measured that they do
  `[measured 2026-09-13, Cowork over the bridge]` (a `pre-commit` sentinel printed and the commit
  landed through the usual lock-file noise), so disabling them there is a habit, not a necessity,
  and the rule moved to A5, beside the gate whose commit-time half hooks are. Evidence:
  `_agent/experiments/2026-09-13-bridge-hook-probe/` on Brandon's fleet. `clients/cowork.md` records
  the fact and its limit: a hook *firing* is not a hook *passing*, and one that needs `rm`, a
  worktree or a truncating write is unmeasured there.
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
  Two open review findings (how item 3 applies to lane commits; scoping the sandbox classification)
  were answered by deletion rather than by more prose: the surface they pointed at no longer exists.
  Every clause added to a rule is surface for the next finding. *Clarified 2026-09-13 (#12's PR):*
  the ban is on citing, in a rule, a specific artifact outside the repo (an evidence directory, an
  audit file, a dated capture); naming the workspace convention A6 defines, as A1 does with
  `_agent/initiatives/`, is not a dead reference, because an agent creates that tree.
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
  that froze every PR into `develop` and `master`, including the PR shipping the skill
  ``[measured: #66 `mergeable_state` blocked → clean after re-applying at 0 approvals]``. Approvals
  are out of the guard; the PR rule, required checks, force-push/deletion blocks and the absence of
  bypass actors are in. Added the honest limit: at 0 approvals nothing mechanically stops an agent
  merging its own PR, so "only Brandon merges" is prose here. Surfaced by the #56 session and its
  independent reviewer; the ticket's acceptance criteria were amended in place the same day.
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
