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

- **2026-10-25 — `clients/openclaw.md`: permit isolated delivery worktrees from the protected
  instruction-source repository.** Issue #180. Brandon clarified the topology: the canonical
  checkout stays protected and hosts disposable delivery worktrees, so delivery needs no duplicate
  clones. The #48 containment rule assumed that protecting the stable instruction checkout
  required a one-worktree topology; #24 supplied the measured failure that established the need to
  protect it. This narrows only that assumption: the protected root stays clean, on `master`, and
  equal to `origin/master` after refresh, and may serve as Git administration for isolated managed
  delivery worktrees; delivery cannot alter its branch, index, or checked-out files, and the root is
  never eligible for cleanup. No runtime project binding changes, no clone is deleted or migrated,
  and the successful-fetch, ancestry, cleanliness, uniqueness, and no-force cleanup safeguards
  stay. The appendix carries the procedure; review and revision on PR #181 identified the
  following defects in earlier wording. [source, commit `9669abf`] That wording named no
  worktree-creation route, so it did not require OpenClaw's managed facility and registered
  inventory or exclude plain `git worktree add`, and the earlier wording named no resolution of
  the managed root.
  [source, commits `c3d598d`, `37f83c9` and `428af38`] Cleanup removed managed worktrees with
  `git worktree remove`, root resolution read the probing shell rather than the Gateway service,
  the profile mechanism was misdescribed (a service's `OPENCLAW_PROFILE` alone selects no profile
  root), and the verification recipe passed `--profile`, which can replace the bound state and
  config paths; those commits carry the superseded wording and its replacement. A later correction,
  commit `979decd`, records that `openclaw gateway --dev` selects no profile. [source, CodeRabbit,
  PR #181 review comment `4372921615`] Creation passed `--base-ref origin/develop` without a
  fetch; fixed in `e56f1ff` and `6973c1a`. [inference] A stale ref could seed delivery, which
  would be verified if, with `origin/develop` left stale behind the remote's `develop`, a worktree
  created with that base had `HEAD` equal to the stale OID rather than the OID
  `git ls-remote origin refs/heads/develop` reports. [source, CodeRabbit, PR #181 review
  `5646215403`] Cleanup matched worktree paths without canonicalizing them; fixed in `a9f544f`.
  [source, commit `efff37b`; the reviewer is not recorded here] Cleanup did not confirm the paths
  exist, and the inventory-verification recipe for `openclaw worktrees list --json` checked only
  that a plain Git worktree was absent, which an empty or unreadable list also satisfies; it now
  also requires an OpenClaw-managed worktree of the same scratch repository to be present.
  [source, CodeRabbit, PR #181 reviews `5646925778` and `5646995554`] Nothing stopped the
  plain-Git route from selecting the protected root, which has no inventory record and lies outside
  the managed root (fixed in `3c04d73`), and then the fix guarded only the root, not every
  protected base worktree (fixed in `e2e926d`). [source, commit `3b4e257`; the reviewer is not
  recorded here] The inventory of protected base worktrees had no defined source. The inventory
  now comes from one `git worktree list --porcelain` read taken before any
  other cleanup step: the named root plus the main working tree and every `master`, `develop`,
  detached, or locked record. Cleanup compares `<path>` with each canonicalized inventory worktree
  before any route, retains on an unreadable or indeterminate inventory, including a record it
  cannot classify, and records every canonicalization and comparison outcome in its audit.
  [source, commits `70cd49b`, `a288d49` and `2900e68`] Those commits bound the appendix's
  `openclaw worktrees list --json` inventory evidence to a capture that records its bindings and
  labelled the former capture, which recorded none, superseded. That was an evidence correction,
  not a new policy amendment. [source, commit `ac42d29`] Cleanup already ran
  `git --no-optional-locks -C <path> status --porcelain --untracked-files=all` after the
  protected-worktree comparison and before the inventory query, retained and reported the worktree
  and branch unless that exited 0 with empty output, and recorded that check's exit status and
  output in its audit. That check now also passes `--ignored`, so the same clean-status
  enforcement and audit cover ignored files. [source, commit
  `ac42d296adae956a278960570dfb86ce0ea52183`] As first written, the check omitted `--ignored`.
  [measured 2026-10-25, Git 2.56.0] In a scratch repository, that form exited 0 with empty output
  for a worktree whose only local content was an ignored file, and `git worktree remove` without
  `--force` then deleted it. [measured 2026-10-25, Git 2.56.0] With `--ignored`, the check printed
  `!! .env`. [inference] Because `clients/openclaw.md`'s procedure lets cleanup continue only on
  exit 0 with empty output, that output would stop cleanup and retain the worktree and branch;
  running the procedure against such a worktree and observing it retained would verify this.

- **2026-10-24 — `clients/openclaw.md`: current wrapper-selector citation and a Claude-route
  exception record.** Issue #177. The appendix cited the wrapper-selector rule at lines 195–196 of
  `~/.openclaw/workspace/docs/team-operating-model.md` under a SHA-256 the reviewed, expanded file
  no longer has. It now cites lines 198–199 at SHA-256
  `1bf9bcef0f5f2b17273c9d14f3062f19ae51a5ffa5e0c017621055fa6b84f163`, read 2026-10-24, and quotes
  both lines exactly with their line break. A new **Claude routes and intentional exceptions**
  paragraph states its search boundary first — a case-insensitive `claude|wrapper` search of only
  each role's six top-level files `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`
  and `MEMORY.md`, with all other files and subdirectories excluded, among them `DREAMS.md`,
  `memory/`, `media/`, `avatars/`, `drafts/` and `_agent/` — then labels each claim [measured],
  [source], [inference] or **unmeasured**, re-verified 2026-10-24 against the role sources,
  `~/.openclaw/openclaw.json` (agent-entry and `toolsBySender` line ranges, under its read SHA-256)
  and the 2026-10-24 memory record (lines 121 and 131). `assistant` has only conditional
  future-wrapper text (`SOUL.md` lines 113–115); `finance` and `marketing` have no wrapper text
  within the boundary, their only `claude` match there being the `AGENTS.md` pointer;
  `openclaw-admin` has no match for either term there; and the `SOUL.md` files of all three do not
  name `claude-with-max.sh`, though `openclaw-admin`'s unsearched `_agent/` does contain matches.
  Each role entry records its [source]
  config: primary model, listed or allowed models (all `openai/`), and for all four a
  `tools.alsoAllow` of `memory_write` only. `finance` is an intentional GPT-only pilot; the
  `finance` and `marketing` sender rules cover the same two Slack senders and each both denies
  `group:runtime` and allows `gateway_exec`. Memory line 121 records `finance`'s `gateway_exec`
  allow as stale and its authenticated Slack canary as exposing no executable tools and making zero
  Claude calls; memory line 131 records that the class has no supported Claude route. The
  missing-route stop is marked [inference] from the stop rule at lines 204–206 applied to that
  source, not from the configured grants, with the canary that would verify it. Route status stays
  **unmeasured** for `assistant`, for `marketing` outside the Slack class, for `openclaw-admin`,
  and for any role outside the role-local wrapper contract beyond those four; no route is inferred
  from absence alone, and the list is not a census.
- **2026-10-23 — A4, A6, B0, B1, B2, Part C, the split rule and the client appendices: three distinct
  delivery seats, exact-final-head whole-branch review, and client detail moved to its
  appendices.** Issue #173; the clause-level reconciliation matrix is #173's existing comment at
  [this permalink](https://github.com/brandonperfetti/agent-working-agreements/issues/173#issuecomment-6378577766),
  and that comment, not this entry, records the exact reconciled head the matrix covers.
  Parts A–B had come to mix portable rules with client selectors, runtime measurements and
  roster names, and assigned branch, integration, pull-request and review-bot mechanics to the
  orchestrator, while the team model has the coordinating layer coordinate and a qualified
  specialist deliver. **Decision (Brandon, 2026-10-23,
  [#173 comment](https://github.com/brandonperfetti/agent-working-agreements/issues/173#issuecomment-6378320284)):
  three distinct seats — Camina coordinates and synthesizes; Judy, or the assigned delivery
  specialist, owns branch, reviewed child integration, pull-request and CodeRabbit mechanics, with
  the orchestrating session in that seat only when no specialist is assigned; and Amos, or the
  assigned independent reviewer, performs the Standards + Spec review against the exact delivery
  head. Brandon alone merges base branches.** The matrix records `NO_UNRESOLVED_POLICY_CHOICE`.
  **A4 is the one authority for the seats' duties:** it opens with the orchestrator, the delivery
  owner and the independent reviewer, lists every delivery-owner duty — but for the one-off close
  record, which A6 assigns to the agent closing a delivery with no initiative — and each seat's
  core boundary, and assigns supplemental orchestration and review duties in its other bullets,
  with "reviewed child integration" written as integration of reviewed lane work, in the glossary's
  term "lane". The orchestrator
  briefs, fences, dispatches and redispatches lanes, extends a lane's fence, holds tracker
  coordination (closing, relabelling and moving issues to In Review among it), owns attended
  live/browser verification, routes review evidence and writes the hand-back. The delivery owner
  alone controls the shared checkout's git state, even when it is a specialist dispatched as a
  sub-agent, and cuts the delivery branch; in B1 stages a batch and shows the staged diff, commits
  after Brandon's batch approval, and applies the reviewed mbox series that lanes delivered from
  their isolated clones with `git am` only after that approval, since `git am` is the commit, and
  Brandon pushes; in B2 integrates reviewed lanes and records their verdicts, runs the merged-tree
  gate, owns conflict-resolution mechanics, pushes, runs the `coderabbit-preflight` and
  `coderabbit-response` routines, opens and updates the feature pull request, and may draft the
  `develop → master` release pull request. B1 and B2 now say their no-initiative session holds
  those A4 duties and carry each duty's procedure, not a further duty list; B1's sub-agent bullet
  now binds dispatched lane sub-agents only and keeps both attended lane shapes — an mbox lane
  runs git only in its isolated clone, and a lane delivering uncommitted edits may edit its named
  files in the shared checkout but runs no git there — so a delivery-owner specialist dispatched as
  a sub-agent, and a delivery owner that dispatches no lanes and so counts as that lane, keep their
  A4 duties in the shared checkout. A4's lane-git bullet now gives the delivery owner the shared
  checkout's git state, not the checkout itself. A6's no-initiative friction paragraph now says A6
  itself assigns
  the one-off close record to the agent closing the delivery, and that all remaining seat authority
  for that delivery comes from A4, B1 or B2 carrying only its procedure; the 2026-10-20 provenance
  stays on the close-record and mode-pointer rule. Part C's OpenClaw line no longer points at a B0
  "autonomous-default rule" B0 no longer states: the default is the index's and the appendix's, the
  exception B0's. The glossary's "wave" is coordinated by the orchestrator on a branch its
  delivery owner cuts, its "delivery owner" alone controls the shared checkout's git state, and its
  "lane" names the autonomous lane's own worktree and both of B1's attended lane shapes and
  excludes a delivery owner dispatched as a sub-agent, which keeps its A4 git-state duties. B2's
  attended-mode sentence now names both B1 lane shapes and gives the delivery owner, not Brandon,
  the staging, commit and `git am` mechanics in B1's approval order; the OpenClaw appendix's B1
  deliveries sentence, its delivery-topology item and its migration disposition B name both
  shapes too, disposition B now dropping only a dispatched lane specialist's committing, staging
  or other git in the shared checkout and keeping the delivery owner's git control, a delivery
  owner dispatched as a sub-agent being no lane. The OpenClaw
  appendix's acceptance boundary is now Brandon's ready-PR acceptance and manual merge. The README,
  `docs/agents/domain.md` and `clients/openclaw.md` point at A4 rather than restating its duty
  lists; the OpenClaw appendix keeps what is its own — which role fills each seat, Camina's
  continuity and decision-ready hand-back, and Judy's implementation and diagnostics — and drops
  "The orchestrator handles the A4 two-axis review cycle", which contradicted the decision. Its
  "child branch" and "handoff" wording becomes "lane branch" and "hand-back"; "handoff" stays only
  for the handoff-file artifact. **Review timing:** A4's two-axis rule adds the decided invariant
  only — the independent reviewer reviews the whole branch at its exact final head SHA before the
  delivery is presented for Brandon's merge, and any later repository-changing change to the head —
  a fix, a lane merge, a base merge — needs its scoped review and a renewed whole-branch verdict at
  the new exact head before presentation. The draft's "before the pull request is created" is
  removed: the decision and the issue's acceptance criterion name presentation for merge, and B2
  opens the pull request at the first push, so a generic pre-creation review would contradict B2.
  Stricter timing a client's own authority already established — its appendix or the client's own
  operating policy, as OpenClaw's operating documents do for a simple single-branch delivery — still
  applies for that client; it is not made portable and not set by #173. **This departs from the
  split rule as the agreement's header stated it** — "Nothing load-bearing is ever moved out of
  Parts A and B" — and clarifies it: Parts A and B keep every portable rule, and a client's own
  selectors and mechanics move to its appendix only once that destination carries them, is linked
  and has been reviewed. Moved under that test: A4's Claude model selectors (`opus`, `sonnet`) to
  `clients/claude-code.md` and `clients/cowork.md`, which now carry the selectors alone, the role
  routing staying in A4 — workhorse is `opus`, the careful tier is recorded there as unmeasured,
  and `sonnet` is only for a trivially mechanical dispatch, never the careful tier;
  `clients/codex.md` and `clients/openclaw.md` record their tier-to-selector
  mapping as unmeasured, OpenClaw's with its shared Claude Code wrapper, which takes no caller
  selector and pins its own model [source: `~/.openclaw/workspace/docs/team-operating-model.md`
  lines 195–196, read 2026-10-23, SHA-256
  `afd5812b86094920f41dc869673d09c9d59a0d0a8ca577cd6e3ddea8f04c1389`, which reads: "Invoke the
  wrapper without `--model` or `--fallback-model`; the wrapper pins the exact model and rejects
  caller-supplied model selection."], and a dispatch naming a
  selector only where the
  mechanism accepts one; B2's Claude Code concurrency measurement, which `clients/claude-code.md`
  already carried; B0's per-client default modes, which Part C's index and each appendix carry; B0
  item 1's "Claude Code on claude-skills" measurement label, and B0's per-client guard scoring —
  Claude Code's item 1, 3 and 4 notes, the claude-skills protection measurement among them, to
  `clients/claude-code.md`, Cowork's "fails 1 and usually 2" to `clients/cowork.md`, Codex's already
  in `clients/codex.md`, which now says outright that B0 item 4 is still checked per repository
  despite earlier measurements; the roster name Camina, from the agreement's opening paragraph (Part
  C's index and the appendix keep it); and A4's machine-specific author-name example, whose
  measurement the 2026-09-29 entry on #79 already records. **Retained, with the portability
  reason:** B0's
  OpenClaw exception — no downgrade to B1, stop at the first operation with no safe route, and stop
  rather than fall back to attended where this file is unreachable — stays in B0, because it
  modifies B0's portable downgrade rule and an appendix that contradicts Parts A–B is, by every
  appendix's own opener, the rule that is wrong; and A7's Kody bullet stays, because Kody serves
  more than one client and its rules are authority and credential boundaries — it never authors
  commits, its `confirm: true` is not B1's approval, and every call names its scoped token — that
  B1's no-routing-around rule relies on, while each client file already records how it names the
  tools. A6's `sansfaux/` root and `_agent/` tree and A7's tracker board stay too: they are
  root-relative fleet layout and the one board every client and repository shares, with each
  machine's absolute paths in its appendix. Rules whose replacement lives outside this repository
  stay in place until it exists; that work is linked follow-up:
  [claude-skills #342](https://github.com/brandonperfetti/claude-skills/issues/342) for the
  `orchestrate`, `coderabbit-preflight`, `coderabbit-response` and `writing-pull-requests` skills,
  to be reconciled with the three seats, and
  [#174](https://github.com/brandonperfetti/agent-working-agreements/issues/174) for the OpenClaw
  team operating documentation, CodeRabbit review workflow and role configuration.

- **2026-10-22 — OpenClaw: name the native agent root, session-stable artifact-store selection,
  and fresh-session acceptance boundary.** The reviewed native-root P3 cutover package replaces
  the former host-specific workspace-store description with the configured native macOS mapping:
  `~/dev/sansfaux/agent-working-agreements` for instructions and `~/dev/sansfaux/_agent` for
  artifacts. A fresh role whose pointer has changed selects the target store provisionally at
  startup, keeps that store for the session whether acceptance later passes or fails, and declares
  the mapping operational only after exact instruction reporting and its ordinary create/readback
  canary pass. Existing sessions never switch or dual-write, partial pointer application affects
  only the changed subset's fresh sessions, and both former instruction/artifact roots remain
  independent rollback roots. Brandon approved the exact reviewed P3 package on 2026-10-22; the
  repository amendment changes policy text only and does not itself update a pointer or store.

- **2026-10-20 (#6) — B1: for feature work with no initiative, the session doing the work holds
  the orchestrator's duties, and its one-off review record holds its decisions until a PR
  exists.** Issue #165, from the review of the (#5) change: A6 **Friction** and
  `clients/claude-code.md`'s item 5 pointer now send attended work with no initiative to B1,
  which said nothing of it, and in attended mode no PR exists when a batch is reviewed (A7), so
  B2's "the PR body" had no counterpart. Under the (#4) entry's size test, that is a line the PR's
  own change makes untrue. B1 now opens with a paragraph mirroring B2's: the session holds the
  orchestrator's duties, its records go under the `_agent/` root's one-off folders, and its
  decisions and a failed item 4 go in its one-off review record under `_agent/reviews/` until a PR
  exists, then into the PR body. B0 item 4 and the item 5 pointer, which named the PR body alone
  for such work, now say so too, and A4's two-axis bullet names "B1 or B2, by mode" for the
  one-off `reviews/` location. **Decision (Brandon, 2026-10-20): "Decisions are recorded in the
  delivery's one-off review record under `_agent/reviews/`, which Brandon reads at each batch
  approval, and copied into the PR body once a PR exists."** Folded into the change for #165
  rather than ticketed. The per-batch approval, and who commits or pushes, are unchanged.

- **2026-10-20 (#5) — B1, A6 and the Claude Code appendix: attended work with no lanes gets the
  same fix owner as autonomous work, and no-initiative pointers name both modes.** Issue #165 (its
  first comment): B2's Addenda carry an exception for a session that dispatches no lanes, while
  B1's said a fix is "never done by the orchestrator's own hands" with none. A6 **Friction** said
  a no-initiative delivery's other orchestrator duties "are B2's to assign", and
  `clients/claude-code.md`'s item 5 pointer ended "for work with none, B2" — both the autonomous
  section, for work that may be attended. B1's Addenda now carry the same exception, approved per
  batch, and the two pointers say "B1 or B2, by mode", with the reason: both modes then say the
  same thing, and attended work with no initiative is not pointed at the autonomous section. **Decision
  (Brandon, 2026-10-20): "B1's Addenda gain the exception B2's have: a session that dispatches no
  lanes counts as that lane, approved per batch as every attended fix is. A6 *Friction* and the
  Claude Code appendix's item 5 pointer name 'B1 or B2, by mode' where they name B2."**

- **2026-10-20 (#4) — A4: a line elsewhere that the PR's own change makes untrue counts as a
  small fix.** Issue #165: A4's size test kept a small fix "inside the files the PR already
  changes", so a line in another file that the PR's change contradicts was real work and a ticket.
  The size test now reads "inside the files the PR already changes, or a line elsewhere that the
  PR's own change makes untrue", and the real-work outcome's "outside the PR's files" now excludes
  those lines too, since this change makes the old wording untrue. The reason is in the rule:
  otherwise a PR ships text that contradicts itself and leaves a ticket to fix it later, which is
  what the small-fix outcome exists to prevent. **Decision (Brandon, 2026-10-20): "A line
  elsewhere that the PR's own change makes untrue counts as small."**

- **2026-10-20 (#3) — A4 and B2: where the session dispatches lanes and none owns the file, the
  orchestrator extends one lane's fence for the fix.** Issue #165: after the (#1) entry, a small
  fix had an owner when the session dispatches no lanes and on a release PR, but not when the
  session dispatches lanes, on a wave or feature PR, and the file belongs to no lane: A4 sent the
  fix "back to the lane that owns the file" and B2's Addenda kept it out of "the orchestrator's own
  hands". A4's small-fix route and B2's Addenda now name the route, with the reason: a lane already
  working the change has its context, so this is the cheapest route that keeps the fix out of the
  orchestrator's own hands. B2's Addenda also name that lane beside the owning lane for a fix that
  rides an open wave PR. **Decision (Brandon, 2026-10-20): "The orchestrator extends one lane's
  fence to that file for one addendum, and that lane makes the fix, with the two-axis review
  scoped to the fix still required and the extension recorded."** Chosen over dispatching a
  review-fix lane, the ticket's other route. The harm list, the three outcomes, who merges, the
  two-axis review, and the no-lane and release-PR owners the (#1) entry set are unchanged.

- **2026-10-20 (#2) — B2: for work with no initiative, the stop-list's first two items name the
  ticket and the prompt in place of the MPD.** Issue #161: B2's stop-list stops on "A premise
  conflict with the MPD or a ticket" and on "A scope decision the MPD does not cover". Feature work
  with no initiative has no MPD, so read literally, item 2 stopped on every scope decision. One
  sentence under the list now gives both items as such work reads them — item 1 "A premise conflict
  with the ticket or the prompt" and item 2 "A scope decision neither the ticket nor the prompt
  covers" — with the reason: both exist for every piece of work. The items themselves are
  unchanged, so an initiative reads them as before. Writing the two readings out was chosen over a
  rule to put "the ticket and the prompt" where the items say "the MPD", which, substituted
  literally, makes item 2 "a scope decision the ticket and the prompt does not cover" and has item
  1 name the ticket twice. One sentence under the list was chosen over a second numbered list,
  which would read as more stop-list items, and over B2's opening paragraph, which is out of view
  where the list is read. **Decision (Brandon, 2026-10-20): for work with no initiative, stop-list
  items 1 and 2 read "the ticket and the prompt" where they say "the MPD"; read out, a conflict
  with either is a premise conflict, and a scope decision stops when neither covers it.** Chosen
  over the ticket alone and over the PR body's decisions. The stop-list's heading and its other
  items are unchanged.

- **2026-10-20 (#1) — A4 and B2: a session that dispatches no lanes counts as the file's lane for
  a fix, and a release PR's small fix goes to the owning lane or a review-fix lane.** Issue #161:
  since the 2026-10-18 (#6) entry, the session doing feature work with no initiative holds B2's
  orchestrator duties, while A4's small-fix outcome sent the fix "back to the lane that owns the
  file" and B2's Addenda said a fix is "never the orchestrator's own hands". A session that
  dispatches no lanes is both orchestrator and only author, so read together the two left its own
  small fix with no one allowed to make it. A4 applies the same threshold to release PRs, whose fix
  commits B2 pushes straight to `develop`, and the small-fix route named no owner there either.
  A4's small-fix sentence now says that a session that dispatches no lanes counts as the file's
  lane, the scoped review still required, and that on a release PR the fix goes to the lane that
  owns the file or to a review-fix lane the orchestrator dispatches for it, with the reason: the
  route assumes a lane exists. B2's Addenda say the same of a session with no lanes and point to
  A4 for a release PR. B2's release-cut bullet, which says where a release PR's fix commits are
  pushed, is unchanged: it covers every fix commit, not only a small one, and B2's review loop
  already sends the fixes A4 calls for to lanes. B1's Addenda are unchanged. **Decision (Brandon,
  2026-10-20): a session that dispatches no lanes counts as the file's lane for A4's small-fix
  route and B2's Addenda, with the scoped two-axis review still required; on a release PR, the fix
  goes to the lane that owns the file, or to a review-fix lane the orchestrator dispatches for
  it.** Chosen over always dispatching a lane and over letting the orchestrator fix with a scoped
  review. The harm list, the three outcomes, who merges and the two-axis review are unchanged.

- **2026-10-18 (#6) — B2: for feature work with no initiative, the session doing the work holds
  the orchestrator's duties, and the PR body holds its decisions.** Issue #145: since the
  2026-10-16 (#2) entry, feature work with no initiative has its own branch off `develop` and a PR
  into `develop`, while the rules around that path named only an initiative's seats and folders —
  B2's loop "the orchestrator", its stop-list "MPD §6 + PR body", B0 item 4 a failed item "in MPD
  §0", and A4's two-axis bullet the verdict "under the initiative's `reviews/`" — so an agent doing
  such work could follow each only by analogy. Two more places assumed an initiative: B0 item 3
  named a lane branch only for initiative work, so a lane's commit in a no-initiative session that
  dispatches lanes had no stated place, and `clients/claude-code.md` sent a session to "item 5
  (MPD §0)", a file such work does not have. **Decision (Brandon, 2026-10-18): for feature work
  with no initiative, the session doing the work holds B2's orchestrator duties; its review
  verdicts and other records go under the `_agent/` root's one-off folders (A6), and its decisions
  and a failed item 4 are recorded in the PR body.** B2 now says so once, under its opening, with
  the reason: such work has no wave orchestrator, MPD or initiative folder, and it always has a PR.
  A4's two-axis bullet names the `_agent/` root's one-off `reviews/` for such work; B0 item 4
  records a failed item 4 in the PR body for it; the stop-list heading records its decisions in
  the PR body alone; B0 item 3 adds a lane branch off the work's own branch, matching the
  initiative case's "or a lane branch off it"; B2's lane bullet names the same branch, and its
  merge bullet names that work's own branch as the one the lane merges into;
  `clients/claude-code.md`'s pickup check reads "item 5 (the override in the prompt, recorded
  in MPD §0 for initiative work, or with the delivery's decisions in the PR body for work with
  none, B2)", which keeps an initiative's override with the mode MPD §0 records, puts it in the PR
  body with the delivery's decisions for work with no initiative, and adds nothing to B2's
  paragraph; and the `orchestrator` row in `docs/agents/domain.md`, which named only an
  initiative's orchestrator, now reads "A4 and B2: the lead agent; for an initiative it runs one
  wave, then rotates to a fresh one through a packet; for work with no initiative, the session
  doing the work". A6 **Friction** said the agent
  closing a no-initiative delivery writes its close record and that "this does not assign any
  broader no-initiative delivery role"; with the role now assigned, that clause reads "the
  delivery's other orchestrator duties are B2's to assign", and the close-record writer is
  unchanged. This settles the ownership question the 2026-10-18 (#1) entry left open for #145;
  that entry stays as written. Who merges, the mode, the two-axis review and the stop-list's items
  are unchanged.

- **2026-10-18 (#5) — A6 Clones: a clone's remote, recorded commands and captured output lose their
  secrets before they reach `evidence/`.** Issue #154: A6 **Clones** says what persists from a
  scratch clone is the commands run and their output, under `evidence/`, with the remote and the
  commit needed to rebuild the clone. A remote URL can carry credentials, and the plain ways of
  reading a remote print them verbatim [measured 2026-10-17, git 2.46.0, a scratch repository with a
  fake credentialed remote: `git remote -v`, `git remote get-url origin` and `git config --get
  remote.origin.url` each printed the URL's userinfo], so following the rule as written could write
  a secret into the evidence store, a leak by A4's harm list. The commands run persist too, and a
  recorded command keeps a credential as typed (a `git clone` of a URL with a token in it), so the
  clause covers the command text as well as the remote and the output. A clone can also carry a
  credential that is neither userinfo nor a token — an authentication header set through
  `http.extraHeader` on the clone puts one in the recorded command — so the last part names any
  credential the clone uses, not only a token. One clause now says that before the remote, a command
  or its output is written under `evidence/`, the secret comes out, by the remote's form, wherever a
  remote appears: an http(s) URL loses its whole userinfo, since a token can stand where a user name
  does and the two cannot be told apart; an ssh remote keeps its user name and loses any password; a
  remote of any other form loses its whole userinfo; and any credential the clone uses, a token or
  an authentication header among them, is stripped from a captured command and its output. Keeping a
  bare user name on an http(s) URL was rejected because it can keep a token. The sentence keeps "the
  remote and the commit needed to rebuild the clone". The next sentence, which had read "That is how
  this sits beside the `experiments/` line's …" and would now have pointed at the new clause, opens
  "Keeping that evidence is how …", so it still means the kept evidence. This is not a general
  secrets policy, and the rest of **Clones** is unchanged.

- **2026-10-18 (#4) — B0: a failed check downgrades unless its item says otherwise, and the
  example names one that does.** Issue #147: B0's opening said a failed capability-guard check
  downgrades the delivery to attended, with a one-line reason, and gave "attended: `develop` is
  unprotected" as the example, while item 4 says that, until protection exists on a repository, a
  failed item 4 is recorded, not a downgrade. The example named the one case the item excludes,
  and the tension predates the 2026-10-16 (#1) change of unit from session to delivery. The
  opening now keeps the downgrade as the rule and names the exception: a failed check downgrades
  the delivery, with a one-line reason, never a question, unless its item says otherwise — a
  failed item 4 is recorded instead, until protection exists. Its example reason is an item 2
  failure, which does downgrade: "attended: the CI gate does not run locally". No item's own rule
  changes. The "capability guard" row in `docs/agents/domain.md` still named the session as the
  unit, "the checks, verified at pickup, that a session must pass to run autonomous", and the same
  file tells writers to word issues, rules and changelog entries in that table's terms, so the old
  unit could come back into new text; it now reads "the checks, verified at pickup for each
  checkout and repository delivery path, that a delivery must pass to run autonomous; a failed
  item 4 is recorded instead, until protection exists", which carries B0's unit since the
  2026-10-16 (#1) entry and the same exception as B0's opening, so the row says no more than B0.

- **2026-10-18 (#3) — B0 item 5 names the override it guards against.** Issue #158: B0 says
  Brandon can override the mode in either direction by saying so in the prompt, and that the
  override wins over the default, while item 5, which every autonomous delivery must pass, read
  "Brandon has not overridden it for this session". Read literally, an override toward autonomous
  failed item 5, so the override B0 promises in that direction could not select autonomous. Item 5
  now reads "Brandon has not overridden the mode to attended for this session": an override toward
  autonomous passes it, and one toward attended fails it, as B0's opening promises. **Decision
  (Brandon, 2026-10-18): item 5 names the override it guards against.** Items 1–4 and who may
  override are unchanged.

- **2026-10-18 (#2) — A4, B1 and B2: a verified finding that does no harm is fixed in the PR,
  noted, or ticketed, by size.** Issue #157: A4 sent every verified review-bot finding that does
  no harm to a ticket, B2's Addenda sent any fix to work already merged into the wave branch to a
  fresh ticket, B1's Addenda did the same for anything already committed, and B2's Issues bullet
  had agents file findings freely. A one-clause fix then cost a ticket and a later wave instead of
  a commit, and the backlog refilled about as fast as waves cleared it. A4's review-bot bullet
  keeps its two ends — what is verified and does real harm is fixed before the merge, and what the
  code disproves is declined — and drops the "only" that would have barred any other fix. Its
  middle case now has three outcomes: **small**, fixed in the PR, when the fix stays inside the
  files the PR already changes and needs no new decision, through the lane that owns the file with
  a scoped review, its thread getting "Fixed in `<sha>`"; **not worth a change**, noted in the
  review record with a one-line reason that its thread gets too, and no ticket; **real work** —
  outside the PR's files, a new decision, or more than a small fix — a ticket, as before. The same
  outcomes govern a reviewer's notes. B2's Addenda now lets a small fix to work already merged
  into the wave branch ride the open wave PR, through the owning lane, a scoped review and a push,
  and keeps a fresh ticket for real work and for work found after the wave PR has merged; B1's
  Addenda says the same in attended mode's shape, a new commit approved per batch until the PR
  that carries the work merges; B2's Issues bullet now files the findings that are real work; and
  B2's review loop redispatches "the fixes A4 calls for" in place of "the fixes A4's threshold
  calls for", since A4 now calls for small fixes as well as harmful ones. **Decision (Brandon,
  2026-10-18): quick fixes are done in the PR as they arise, and the backlog is not clogged with
  tickets to get a PR out faster.** The harm list, who merges, the two-axis review and the
  stop-list are unchanged, and no client file sent harmless findings to a ticket.

- **2026-10-18 (#1) — Friction capture is a raw, non-blocking delivery artifact.** Issue #155:
  A6 now names `friction/` inside an initiative and at the one-off artifact location, defines the
  bounded close record (`friction: none` or a dated entry with the delivery, affected step,
  labelled observation and locator where available, measured-only cost, workaround, recurrence and
  reproduction status, and proposed fix or `unknown`), and keeps that raw record distinct from A2
  evidence, independent-review findings, promoted learnings and GitHub issues. The record is
  corrected in place under A2 and promotes only through triage and deduplication to recurring,
  reproducible, repository-owned issue work, then to a resolved learning, rule, skill or software
  improvement. B2 points wave close at the A6 record. Capture is non-blocking unless the underlying
  condition independently reaches an existing gate, authority or stop boundary. `_agent/` is also
  stated as the artifact-location class selected once per session; client discovery stays in the
  appendices.
  In response to CodeRabbit, A6 now also gives no-initiative friction records a canonical
  delivery identifier (PR URL, otherwise origin plus full HEAD, otherwise branch plus full HEAD),
  a closing-agent writer, and a date-prefixed deterministic `_agent/friction/` filename mapping;
  the record starts with that exact identifier. Review correction: the initial mapping's lossy
  repository and branch slug normalization could collide. Each filename now includes a mandatory,
  full lowercase hexadecimal SHA-256 suffix over the UTF-8 bytes of the exact pre-normalization
  repository identity and, for branch-form records, the exact full branch ref. This is limited to
  friction capture: #145's unresolved broader no-initiative ownership boundaries, and #110's
  store, synchronization and cutover boundaries, remain unchanged. No B0, B1, B2 authority,
  branch, merge or stop boundary changes.

- **2026-10-18 — OpenClaw: B0 re-evaluation is capability evidence, not the mode selector.**
  Issue #152: [source, prior `clients/openclaw.md`] the Pickup guard's historical
  `claude-skills` receipt ended by saying “a future session's mode is still decided only by
  rerunning B0 for its exact checkout and path.” That sentence should not be relied on after the
  released OpenClaw autonomous-default amendment: [source, B0 and `clients/openclaw.md`, Startup
  and mode] OpenClaw defaults to autonomous, and a failed or unavailable B0 capability is evidence
  about the affected operation rather than a B1 downgrade. The sentence now says that future
  OpenClaw work re-evaluates B0 for its exact checkout and path as capability evidence, not as the
  B1/B2 mode selector. [measured 2026-09-20, current Gateway host] The historical receipt records
  that the gate could not pass because Ruby and `zip` were required, and that the session was
  attended. [source, current `clients/openclaw.md`] It links `claude-skills` #111 for the
  durable install and complete remeasurement. [source, this amendment] Those historical lines,
  B0, and every other client's mode are unchanged.

- **2026-10-18 — Receipt correction for the 2026-10-17 OpenClaw amendment.** Independent release
  review found that the original amendment's receipt trail did not give the new B0 OpenClaw
  autonomy/default and B2 bounded-recovery rules their required learning receipt, leaving the Part
  C index and `clients/openclaw.md` citation mirrors without a durable source to follow. The new
  learning receipt records the issue, PR, CodeRabbit review-thread, and commit representations with
  locators, SHA-256 values, and relevant excerpts; it adds no policy. It also makes the status
  boundary explicit: merge into `develop` is integration, a later `develop` → `master` release may
  make the policy binding, and neither proves observed adoption until fresh canonical-main and
  specialist-pickup evidence exists. The 2026-10-17 entry below retains that integration,
  release, and adoption distinction as the record of the original amendment.

- **2026-10-17 (#149; effective with this release; observed adoption pending) — Bounded recovery,
  OpenClaw delegation, and autonomous delivery.** This amendment replaces the single fix round in a
  merge-conflict resolution with an explicitly budgeted, evidence-led recovery
  for a red of the resolution's own, absent from both sides' pre-merge gate
  records: every in-scope action is recorded with its evidence and relevant
  re-check, which demonstrates recovery progress only; it stops at an exhausted
  budget, a disproved premise, no evidenced progress, or a
  scope/destructive/security/credential/merge boundary; unresolved recovery
  aborts; only a successful full CI gate on the resolved merged tree permits the
  merge commit; and scoped two-axis review remains required. It also lets
  OpenClaw use the supported native or OpenClaw delegation mechanism available
  to the session: `sessions_spawn` is one available OpenClaw mechanism, not a
  universal requirement. It also makes OpenClaw autonomous by default: the agent
  team owns installs, builds, tests, verification, and routine delivery through
  a ready B2 PR, while Brandon reviews and merges rather than running commands.
  A failed or unavailable OpenClaw capability is evidence about the affected
  operation only; under Brandon's 2026-10-17 direction, it stops there with the
  exact missing safe route and does not downgrade the delivery to B1 or make
  Brandon the command runner. The OpenClaw exception also applies when the
  instruction source is unreachable: stop the affected work and record that
  missing capability rather than automatically selecting B1. A confirmed
  breaker strike preserves the B0-selected mode, including an explicit
  owner-selected attended override; the historical no-mode-change rule remains
  the 2026-10-01/#94 decision. The existing feature-branch rules remain
  unchanged; the breaker still does not weaken sandbox controls or broaden
  system writes. This amendment was canonically reviewed in #149 and becomes
  binding when this release reaches `master`; fresh canonical-main and
  specialist-pickup verification remains pending, so #148 stays open and no
  deployed adoption is claimed. The instruction-source clone remains read-only.

- **2026-10-16 (#4) — Changelog: the 2026-10-12 (#2) entry claims no more than the Claude Code
  scratchpad measurement.** Issue #143: that entry said a Claude Code scratch clone takes "one
  subdirectory per sub-agent because sub-agents share it", while `clients/claude-code.md`, the
  file it describes, says two measured dispatches shared the directory and whether every dispatch
  does is unmeasured. The client file's sentence had been narrowed to its measurements in review
  and the entry kept the first wording, so the changelog carried a measurement past its boundary,
  which A2 keeps inside the claim. The entry's clause now says what the client file says,
  corrected in place, marked and dated there with the old text quoted, what was observed and what
  was concluded (A2), in the shape of the in-place notes this file already carries (the 2026-09-29
  and 2026-09-26 (#2) entries). The rule, one subdirectory per sub-agent, and the client file are
  unchanged.

- **2026-10-16 (#3) — B2: a wave branch that has moved since the lane merged is the same rule
  again.** Issue #140: B2's bullet "A lane merge that conflicts goes back to the lane" said the
  orchestrator's merge is clean against the tip the lane merged, and stopped there, so a reader
  whose wave branch had moved since — another lane landed in between — had to derive from the
  bullet's first sentence that a merge that conflicts on the new tip goes back to the lane too.
  The clause now says it: a wave branch that has moved since is the same rule again — a merge that
  conflicts goes back to the lane. The 2026-10-12 (#3) entry carried the same clause and was
  amended in place to match, marked and dated there (A2). No other rule changes: the rule held
  without the clause, which writes down a case the reader had to derive, as issue #123, which
  introduced the clause, had asked.

- **2026-10-16 (#2) — A1 and B0: B0 picks the mode with or without an MPD, and feature work with
  no initiative has a branch.** Issue #142: A1 said "with no MPD, you are in **attended mode**
  (B1)", while B0 says the environment picks the mode and an MPD records it without gating it, so
  an agent doing one-off work in a client whose default is autonomous read two answers. **Decision
  (Brandon, 2026-10-16, on the ticket): A1's clause goes; B0 decides, with or without an MPD**, as
  the "2026-09-11 — Brandon (3)" entry intended ("initiatives organise orchestrated work, they do
  not gate applicability"). A1 keeps the sentence's true half — initiatives organise orchestrated
  work and do not gate whether these rules apply — and now says they do not gate the mode either;
  B0's MPD sentence says work with no MPD has its mode picked the same way. The decision also asked
  which branch feature work with no initiative lands on, because B0 item 3 said "an initiative
  branch" and B2 named only `<initiative>/wave-<n>` as the branch an agent pushes, which left such
  work, now possibly autonomous, with no branch it could push. B0 item 3 keeps initiative work as
  it was — an initiative branch no other initiative is using, now named as its wave branch or a
  lane branch off it — and adds the other kind: feature work with no initiative lands on a branch
  of its own off `develop` for that piece of work, with no other work on it, the ritual's step 1
  ("one branch per wave or piece of work"). B2's first Git-contract bullet names each kind's only
  push branch — the wave branch for an initiative's feature work, the work's own branch for work
  with no initiative — and its feature-work sub-bullet sends feature work through its branch and a
  PR into `develop`, for the reason it already gives: pushed straight, it would reach `master`
  reviewed by nobody. A4's author check names the new branch among the deliveries whose added
  commits it reads, since each push of that branch is a delivery like the others. B0 item 4's
  decided-not-now paragraph listed "feature work goes through a wave branch and a PR into
  `develop`" among the conditions Brandon's 2026-10-12 decision rests on; it now says "through its
  branch (B2)". That is a conforming wording change, not a change to the decision: the condition
  always meant a branch and a PR into `develop`, never a push straight to a base branch, and that
  holds for both kinds of branch; the decision and its reopening conditions are unchanged.
  **Decision (the wave orchestrator, 2026-10-16, under B2's decide and record, reviewed on the
  wave's PR): the branch wording as it now stands in B0 item 3, B2's first Git-contract bullet, B0
  item 4's condition and A4's author check.** No naming scheme is added, and who merges, what may
  be pushed to `develop` and the rest of B2 are unchanged.

- **2026-10-16 (#1) — B0: a failed guard check downgrades the delivery, not the session.** Issue
  #141: B0 said a failed capability-guard check "downgrades that session to attended", and
  `clients/codex.md` repeated "this session", while `clients/openclaw.md` said the guard decides
  for each exact checkout and repository delivery path, not the conversation as a whole, and that
  a failure moves only the affected delivery to B1. One rule had two units, and the narrower one
  lived in a client file, which adds only what is specific to its client.
  **Decision (Brandon, 2026-10-16, on the ticket): option (a), the per-checkout, per-delivery-path
  reading.** B0 now says the guard is scored for each checkout and repository delivery path, not
  for the session as a whole, and that a failed check downgrades only that delivery to attended,
  with its one-line reason, so a session working two repositories is not moved to attended by a
  check that failed in one. It gives the reason where it states the unit: items 1, 2 and 4 are
  already scored that way — item 1's hook probe per checkout, items 2 and 4 per repository — so
  item 1's hook probe failing says nothing of a delivery from a checkout that probe does not cover
  — another clone, or another worktree where `core.hooksPath` is relative — and item 2 or 4 failing
  for one repository says nothing of a delivery to another repository. Item 3 is scored per commit,
  inside a delivery, and item 5 is Brandon's override, which reaches the whole session.
  `clients/openclaw.md`'s "Default mode" and "Staff operating model" sentences now point at B0 in
  place of stating the unit, keeping what is that client's own (Camina coordinating several
  deliveries, the specialist route); its "Lane capability" decision applies B0's unit to a lane
  and is unchanged. `clients/codex.md`'s "a failure downgrades this session" now points at B0 the
  same way. Item 5, Brandon's override for the session, is unchanged, and the Claude Code and
  Cowork appendices state no unit and are unchanged.

- **2026-10-14 (#1) — OpenClaw: row 1's bound points at the paragraph carrying its citation.**
  Issue #137: the paragraph "**Row 1's bound is the command's, not Gateway's.**" sent the reader to
  a paragraph below beginning "**Test runs deliberately have no route.**" for the measurement behind
  its `workdir` claim. The 2026-10-07 (#2) amendment replaced that paragraph with "**Executable
  checks are classified by behavior, not by name.**", which carries #67's canary and Camina's
  inference from it, and the pointer was not updated, so it led nowhere. It now names that opening,
  so a reader following the bound reaches the measurement it rests on. No rule changes.

- **2026-10-13 (#8) — A4: RULE ZERO's identity rule names whose commits it governs.** Issue
  #132: RULE ZERO said a commit carries Brandon's author identity, with no scope. Inside the fleet
  that names the identity an agent's commit carries when it works for him; read from outside, by a
  contributor's agent, it is an instruction to author a commit as the owner. [measured
  2026-10-13] One arrived that way: a pull request from a fork, by an account the owner does not
  know, carried one commit authored and committed under his name and email, which the hosting
  platform attributed to him; the owner asked for it to be re-authored. A4 now scopes the
  sentence: the identity rule governs commits made by agents working on Brandon's behalf inside
  this fleet; a contribution from anyone else carries its author's own identity; and a pull
  request whose commits carry his identity from another account is not merged until re-authored.
  The reason: B0 item 4's "one account has write access to each repository" does not reach a pull
  request from a fork, which needs no write access, so the merge is the only guard, and a
  maintainer merging on the content alone would record a stranger's commit as the owner's.
  **Decision (Brandon, 2026-10-13, on the ticket): the clause as the ticket words it.** RULE
  ZERO's attribution half, the author check on deliveries (the author email against his,
  exactly) and who merges are unchanged.

- **2026-10-13 (#7) — A4: an orchestrator's hand-back is never the review of its wave.** Issue #63:
  A4 said the lane's own report is never the review, and said nothing of the orchestrator's; when
  an orchestrator reported its own wave green, that report was the only attestation the delivery
  got, though the orchestrator had chosen, batched, dispatched and merged the work it attested to.
  In practice a session supervising the dispatched agents had been re-measuring their claims
  against the repository and the services before a merge, and that seat was written down nowhere
  [measured 2026-10-12: a case-insensitive search for "supervis" over the agreement and
  `clients/cowork.md` found nothing]. **Decision (Brandon, 2026-10-12, recorded on #63): write the
  seat down, as one sentence in A4 beside the lane rule.** A4's two-axis bullet now says an
  orchestrator's hand-back is never the review of its wave: the hand-back names the claims to
  re-measure, and before a merge a reader outside the wave reads them against the repository. Each
  sub-decision and its reason:
  - **The sentence:** the party that produced the work does not attest to it, and A4's rule was
    observed to stop one level too early, at the lane. Rotation does not close the gap: it changes
    who orchestrates the next wave and adds no reader before this wave's merge.
  - **The trigger is the situation, not the client:** the seat is a session supervising dispatched
    agents. Most sessions own their work and should, and a Genesis session is attended by design
    and builds the MPD with Brandon, so a rule keyed to a client would wrongly take ownership away
    from both.
  - **Attended mode gains nothing new:** Brandon's per-batch review (B1) is already a reader
    outside the work before anything is committed.

  The lane rule, the two-axis review and B2's review loop are unchanged. #63 closes when this
  lands.

- **2026-10-13 (#6) — A7: Kody's GitHub package is a third GitHub path.** Issue #109: A7 named two
  GitHub paths, the `gh` CLI and the GitHub MCP, and Kody's `@brandonperfetti/github` package had
  come into use as a GitHub API path for issues, PRs and checks with nothing in the agreement naming
  it or the approval rules that bind it. A7 gains a third bullet; the `gh` and GitHub MCP bullets
  are unchanged, and nothing is retired. **Decision (Brandon, 2026-10-12): the amendment lands with
  #63's A4 sentence, and per-client tool names go in `clients/`, not A7.** Each
  sub-decision and its reason:
  - **What it is for:** the GitHub REST/GraphQL API for issues, PRs, checks, PR status and merge
    previews, for any client with Kody connected — named so that the approval rules are visible
    before an agent uses it, not inferred from B1's general wording.
  - **It never authors commits**, in both modes, because like the GitHub MCP's write tools it
    bypasses the local clone, where the repository's hooks and gate run.
  - **`confirm: true` is per call and is not B1's per-batch approval:** it is the agent confirming
    its own call, not Brandon reviewing a batch, so in attended mode a Kody write falls under B1's
    "no routing around it with API/MCP writes or another client".
  - **A fine-grained token scoped per repository, one `secretName` per organisation:** a call
    reaches whatever its token reaches. [measured 2026-10-03] The token first used reached
    repositories beyond this account's own, and GitHub returned the `x-oauth-scopes` header on it;
    the token was then rotated, and on the new one the same call returned no scopes header — the
    instrument shows the header when GitHub sends it. [source: GitHub's REST docs on token scopes]
    GitHub sends that header for classic tokens only; [inference, from the header and that premise]
    the first token was classic and the rotated one fine-grained, scoped per repository, which the
    token's settings page verifies.
  - **`secretName` on every call:** the package defaults to an OAuth lane, and [measured 2026-10-03]
    with no OAuth integration connected a call that omits `secretName` fails (`Integration "github"
    was not found`). Connecting OAuth as well would make the default work, but two credentials could
    then serve the same call with nothing showing which one did.
  - **Fallback:** where Kody is not connected, `gh` or the GitHub MCP, as before.

  The 2026-10-03 measurements behind it, each with its reason for being recorded: the identity check
  — a read-only `get-viewer` call on the token lane resolved to Brandon's account, in a working
  session and in a fresh Claude Code session with no prior conversation, after the secret was set to
  allow the package (Kody refuses a secret a package is not allowed) — shows the path acts as
  Brandon, as `gh` and the GitHub MCP do. [measured 2026-10-03] Before that, the agent-side
  permission check blocked three early attempts that ran package code with the token, which shows
  that check sees a package run that uses a secret — the review the allow-rule decision below
  keeps; and the ticket itself was filed through the package after the GitHub MCP's create-issue
  call rendered a confirmation form that never reached Brandon.
  The write probe, on a private repository of Brandon's with no workflows or webhooks,
  opened a draft PR between two existing branches, created and deleted an issue comment and a
  pending review, and closed the PR unmerged; every write succeeded on both the
  first and the rotated token, and no commit was authored. It shows the PR surface is
  writable through the package, which is why the commit rule and the approval rule are stated rather
  than assumed. The decision against a permission allow rule for the Kody tools (Brandon,
  2026-10-03, on the ticket): a fresh session ran every Kody call it needed, reads and writes, in
  auto mode with no rule; [source: Claude Code's permission documentation] a call that matches an
  allow rule skips the auto-mode check, so a rule for the code-running tool would remove review from
  every Kody code run, including runs that use secrets, and no rule was added. The Kody tools are
  named differently per client (the server segment is the connector's id in the desktop app's Code
  tab and its display name in Cowork; the terminal CLI lists it by display name), so
  `clients/claude-code.md` and `clients/cowork.md` each say to use the name the session reports,
  read before it is written. **Decision (the wave-4 orchestrator, 2026-10-13, under B2's decide and
  record, reviewed on the wave's PR):** neither file carries the literal id, because this repository
  is public and the id is an account fact; `clients/codex.md` and `clients/openclaw.md` carry no
  note, because Kody is unmeasured in those clients.

- **2026-10-13 (#5) — B0 item 4: a separate agent identity is decided not now.** Issue #13: B0
  item 4 said that making "only Brandon merges" and "feature work never lands on a base branch"
  mechanical needs a separate agent identity, and called that "an identity change, open, not
  decided". **Decision (Brandon, 2026-10-12, recorded on #13, which closed as decided): not now.**
  The sentence now records it, with the decision's reason and what reopens it. The reason: the two
  rules stay rules of this agreement because one account has write access to each repository,
  every change reaches `master` through a pull request Brandon merges by hand, the CI gate is a
  required check on `master`, and feature work goes through a wave branch and a PR into
  `develop`; a separate identity would cost a secret, a token-switch step in every client and a
  new PR author, a cost not paid while those conditions hold. It reopens on a second account with
  write access to a repository this agreement governs, or on one measured breach of either rule,
  with a GitHub App as the recommended shape, so the condition that would change the answer is written
  where the question is asked. The sentence is edited, not left open, because "open, not decided"
  sent every reader who met the two rules to re-derive a question that has been answered, which is
  what #13 was filed to stop. The untested-inference sentence before it is unchanged.

- **2026-10-13 (#4) — A6's root names the lane worktrees a client file places there.** Issue
  #122: A6 said the `sansfaux/` root holds `_agent/`, project checkouts, the
  `agent-working-agreements/` clone and `organize.sh` — "nothing else" — while
  `clients/claude-code.md` cuts each lane's worktree at `../<repo>-<lane>`, which is in that root.
  Read charitably a lane worktree is a project checkout; read literally the two disagreed. A6's
  sentence now names, beside project checkouts, the lane worktrees a client file places beside
  them; the client file's command stands. **Decision (the wave-4 orchestrator, 2026-10-13, under
  B2's decide and record, reviewed on the wave's PR): the ticket's first option, the clause in
  A6.** The reason: the agreement is the file every client reads, and where a lane worktree goes
  is a client fact the agreement should not contradict; the other option, a client file declaring
  its worktrees project checkouts for A6's purposes, would be a client file carving an exception
  out of Part A, which a client file never does. Where lane worktrees live is still each client
  file's to name (A6, **Clones**); no worktree moves.

- **2026-10-13 (#3) — A conflict resolution's fix round starts on its own red.** Issue #126: B2's
  conflict bullet opened its bound with "One fix round on a red gate, then stop and report", and
  stop-list item 4 repeated "still red after one fix round — inside a merge-conflict resolution
  too"; which red counts arrived only a sentence later ("no red of its own") and in the next
  sub-bullet (a red a side's own gate record already shows is that side's). Read in order, any red
  started the fix round and the abort; read whole, only the resolution's own did. The fix-round
  sentence and stop-list item 4 now name the red where they state the action — one of the
  resolution's own, absent from both sides' pre-merge gate records — and the 2026-10-12 (#3)
  entry's "one fix round on a red gate" phrase says the same. The reason: a reader acts on the
  sentence that names the action, and the stop-list is read on its own, so a condition stated
  later lets a red that belongs to one side abort a resolution that the next sub-bullet says should
  report that red with the side's record instead. The text produced no wrong behaviour read whole;
  this is wording, raised by the review bot on the release PR. **Decision (the wave-4 orchestrator,
  2026-10-13, under B2's decide and record, reviewed on the wave's PR): the change as the ticket
  states it.** The sub-bullet on a side's own red, and the rule, are unchanged.

- **2026-10-13 (#2) — Release-cut work names the built artifact by role.** Issue #127: B2's Git
  contract listed "the `dist/` rebuild" among the release-cut work pushed straight to `develop`.
  A repository that publishes releases need not commit a built artifact at all, and one that has
  stopped committing it has no such step, so the sentence sent a reader cutting a release to
  rebuild something that may not exist. The sub-bullet now says "any built artifact the
  repository commits", the role the ritual's step 5 already uses ("any built artifact"), because
  a step named by what it is for stays true of every repository, where a step named by one
  repository's layout goes stale when that layout changes. The rule and its reason are unchanged:
  whatever a release cut touches is reviewed on the `develop → master` PR, whose head is
  `develop`. **Decision (Brandon, 2026-10-13): the change as drafted, approved in principle when
  he read the ticket before it was filed.** No other line of the agreement names `dist/`.

- **2026-10-13 (#1) — OpenClaw: scope mode and approvals to the delivery path.** Issue #128:
  live OpenClaw use exposed an ambiguity in the opening attended default: an attended parent
  conversation could be read as making every coordinated action attended, turning informational
  progress updates into approval pauses and spreading B1's per-batch ceremony beyond the delivery
  it governs. The appendix now says B0 decides for each exact checkout and repository delivery
  path, not the whole conversation; routine authorized reversible repository work defaults to an
  available B2-qualified specialist lane; and status updates are informational and non-blocking.
  It also names the ordinary authorized B2 work that needs no per-batch owner approval — commits,
  pushes, pull-request creation or updates, review responses, and reviewed child-branch
  integration — while retaining the B2 stop-list and Brandon's ready-PR/manual-merge boundary.
  When no qualified safe route exists, only that delivery follows B1 or stops with its exact
  capability boundary. B0, A4, B1/B2 mechanics, consequential-action stops, Brandon-only
  base-branch merges, and the Claude Code, Cowork, and Codex appendices are unchanged.

- **2026-10-12 (#3) — Who resolves a conflicting lane merge, and how its gate is read.** Issue #115:
  B2 had the orchestrator merge a lane after two-axis review, gate the merged tree and push, and
  said nothing of a merge that does not apply cleanly, so an agent guessed who resolves, how long to
  keep fixing, and which red is its own. **Decision (Brandon, 2026-10-12): the recommended option on
  each of the three questions.** A new Git-contract bullet in B2 says: the lane brings the wave
  branch into its own branch as a merge commit in its own worktree (not a rebase, which would
  rewrite commits it has already reported), resolves, re-runs the gate, and the resolution gets a
  scoped review; the orchestrator's merge is clean against the tip the lane merged, and a wave branch
  that has moved since is the same rule again — a merge that conflicts goes back to the lane. Where
  the lane is no longer available, the
  orchestrator resolves and the resolution gets a scoped two-axis review before the push. The
  reason: a resolution is new work, and no work reaches the wave branch unreviewed. Inside a
  resolution the bound is the general one — one fix round on a red of the resolution's own, one
  absent from both sides' pre-merge gate records, then stop and report — and
  the rule names the state the tree is left in: the pre-merge tip, with the resolution's diff and
  the red gate's output saved under `evidence/` before `git merge --abort`, because a branch left
  mid-merge holds unreviewed work where the next reader may not know a merge is in progress, and on
  the wave branch blocks every other merge. The merge is committed only once the gate shows no red
  of its own, so the abort is always available. Stop-list item 4 now says it reaches this case. A
  red that a side's own gate record already shows is that side's — reported with that record, not
  fixed inside the merge, because a lane may hand back with a gate step red by design, named in its
  handoff, and a fix to it inside the merge would be an unreviewed change to that side's work — and
  the orchestrator's merged-tree gate before the push is unchanged. A4's worktree and two-axis
  bullets and B2's Addenda point at the rule. What an agent does when `git am` of an approved series
  conflicts on the attended path is not decided here and has no rule. *(Amended 2026-10-16, issue
  #140: the clause "and a wave branch that has moved since is the same rule again — a merge that
  conflicts goes back to the lane" was added after "the orchestrator's merge is clean against the
  tip the lane merged", which until then ended the sentence; the earlier wording was not wrong,
  since the bullet's first sentence already sent any conflicting merge back to the lane, but left
  the moved-tip case for the reader to derive. The 2026-10-16 (#3) entry above.)*

- **2026-10-12 (#2) — No clone or worktree under `_agent/`.** Issue #114: A6 sent everything an
  agent produces under `_agent/` and named `experiments/` for scratch harnesses, saying nothing
  about clones, so scratch clones had been built there. A6 now carries a **Clones** rule: no clone
  of a repository, and no worktree, is written under `_agent/`; a scratch clone lives in the
  client's own scratch directory, outside `_agent/`; what persists is the evidence — the commands
  and their output under `evidence/`, with the remote and commit needed to rebuild. That is how it
  sits beside "never /tmp": a transcript has to survive the session, a clone can be made again. The
  reason, as written there: a clone under `_agent/` is a nested repository in a store meant to
  replicate, a second copy of a project's source with its licence, and the one rebuildable thing in
  the store. The `experiments/` line now reads as harnesses, scripts and files that fit nowhere else
  — never a clone or worktree — so the "if nothing fits: `experiments/`" rule stays true, and the
  sentence that sends every product under `_agent/` points at the rule. Each client file names where
  a scratch clone goes or records it unmeasured: Claude Code, the scratchpad directory the session's
  environment names, one subdirectory per sub-agent because the two dispatches measured shared it
  and whether every dispatch does is unmeasured; Codex and Cowork, unmeasured; OpenClaw,
  unmeasured, with its Gateway check's scratch root ruled out because it exists for one check and
  is removed after it. **Decision (Brandon, 2026-10-12): the rule as
  proposed.** Lane worktrees stay where they are, scratch repositories outside `_agent/` are not
  banned, and nothing is deleted by this amendment; what is already under `_agent/` is decided on
  the issue, not here. *(Corrected 2026-10-16, issue #143: the Claude Code clause read "one
  subdirectory per sub-agent because sub-agents share it", which should not be relied on. What was
  observed: two dispatches, a lane and its Spec reviewer, shared the directory [measured
  2026-10-12, as `clients/claude-code.md` records]. What was concluded from them, not measured:
  that every dispatch shares it. The client file had been narrowed to its two measurements in
  review, and this entry kept the first wording; the clause now says what the client file says.
  The rule, one subdirectory per sub-agent, is unchanged. The 2026-10-16 (#4) entry above.)*

- **2026-10-12 (#1) — A skill never overrides Parts A–B.** Issue #119: A1 said a repository's
  own `AGENTS.md` / `CLAUDE.md` never overrides Parts A–B, and A4 said RULE ZERO overrides any
  environment default, but nothing said which holds when a skill's instructions disagree with the
  agreement; A6's artifact-placement sentence covered that one case and nothing else. A1 now says
  it, beside the repository-docs sentence: where a skill's instructions and Parts A–B disagree,
  the agreement holds, and the agent says that it met the disagreement rather than choosing
  silently. The reporting half is kept on purpose: a disagreement never reported is never fixed
  at its source. A6's sentence now reads as one case of A1's rule instead of stating a precedence
  of its own, so the two cannot say different things; off-fleet fallbacks remain the skill's.
  **Decision (Brandon, 2026-10-12): adopt the clause as proposed.** No skill is named or changed,
  and two skills that disagree with each other are not ruled on.

- **2026-10-07 (#2) — OpenClaw: this amendment defines an inactive cross-session native-boundary
  record.** Issue #112: Once activated, fresh sessions may suppress a
  repeated, confirmed Bubblewrap prelaunch discovery only by consulting a valid
  Ashford/OpenClaw-owned durable record for the existing host and native-exec boundary. The record
  is metadata, not repository, `_agent/`, session, or new runtime state; Ashford alone owns and
  writes it, Bull supplies read-only change evidence, and Camina coordinates. Its non-secret
  boundary fingerprint and invalidators cover the effective host, executor, OCI, and security
  facts, not chats, processes, worktrees, models, commands, or time alone. A valid unavailable
  state follows only a reported exact confirmed strike and preserves the existing table and stop
  when no bounded route exists. Availability requires both separately authorized repair or a
  relevant boundary change and separately authorized execution of one evidence-bearing fixed
  no-write native canary through the recomputed boundary; it proves only prelaunch availability.
  Missing,
  invalid, or mismatched state preserves the one-strike-per-session behavior. Activation awaits
  Ashford designating both the supported resolver/writer and state location as active; after a
  restart, the resolver re-attests every keyed fact and the same deployment/container boundary or
  the record becomes unknown. This amendment authorizes neither maintenance, repair, lifecycle
  action, security weakening, nor canary execution. #58's signature-confirmation, #88's
  command-bounded inspection, and #94's no-mode-change remain unchanged. This batch narrows #67's
  categorical test no-route without making Gateway a general test runner: an unchanged,
  deterministic, source-audited executable check may run only when its complete
  repository-controlled execution path, identified host utilities and their relevant behavior,
  inputs, expected result, writes, exact scratch root, and absence of network, credentials,
  dynamic execution, and external effects are established before the run. Completion compares the
  observed exit, output, scratch-root removal, and candidate-diff hash with those recorded baselines.
  Every other test still has no Gateway route.

- **2026-10-07 (#1) — OpenClaw: staff-lane autonomy has separate boundaries.** Issue #111,
  from Brandon's 2026-10-06 direction: the OpenClaw appendix now separates staff authority, the
  selected lane's B0 capability, risk and reversibility, delivery topology, and the point of human
  approval. Camina defaults to coordination, briefing, boundary enforcement, continuity, review
  evidence, and synthesis; a B0-qualified specialist owns routine reversible work on its own path
  even when the parent cannot use that path. Child branches may compose beneath an assigned feature
  branch and return reviewed work to it, but Brandon remains the sole merger into `develop`,
  `master`, or `main`. Destructive, irreversible, production, credentialed, financial, and
  externally published actions remain stops. Review scales the packet and added scrutiny with risk
  and substance while preserving A4's two-axis verdict, gate evidence, diff, and Brandon's
  decision context; it does not waive A4. Independent Claude and Codex advisors received the same
  frozen evidence packet before this amendment's final wording; their reconciled advice informed
  the amendment as evidence and was not an approval gate. Agent Workspace PR #4 is the concrete
  pilot: its CodeRabbit finding on the committed control-file validation was corrected in
  `d6f917029168a89c01c0b94a6fa5fa1a530a8cb7`, and its later review reported no actionable
  comments. The amendment changes only `clients/openclaw.md`; Parts A–B and the Claude Code and
  Codex appendices remain unchanged.

- **2026-10-03 (#1) — OpenClaw: how row 3's added-file readback passes the path.** Issue #104,
  from the CodeRabbit CLI's review of the wave-4 branch and CodeRabbit on
  release PR #107 (thread `4173542541`): `--` ends option parsing but does not stop a shell
  interpreting a path spliced into a command string. The answer is Camina's (her comment on #104
  of 2026-10-03, posted under the owner's account; Brandon's instruction, fleet-coderabbit-preflight
  MPD D72), carried in her order, each clause under a label of the kind she gave it. In "Row 3's
  readback of a file the patch adds.", the two forms `cat -- <added-path>` and the `--no-index`
  form with `<added-path>` are replaced. [source, Camina's, issue #104] As the current Gateway tool
  contract describes it, Gateway execution takes one `command` described as a shell command,
  exposes no argv-array interface, and takes separate `env` overrides described as literal, with
  no expansion. Her `[source]` clause also states a conclusion (Gateway does not make a spliced
  path safe, but provides a separate literal-value channel); it is carried under the label she
  gave it. [inference/recommendation, Camina's, issue #104] Row 3 passes the exact,
  scope-validated added path as a literal `ADDED_PATH` override, supplied separately from the fixed
  command, and expands it quoted: `cat -- "$ADDED_PATH"` for a regular file, and
  `git --no-pager diff --no-index --no-ext-diff --no-textconv -- /dev/null "$ADDED_PATH"` for an
  added regular text file. The session must not splice the path into `command`, re-evaluate it
  with `eval`, or leave the expansion unquoted; the literal override plus the quoted expansion, not
  `--`, is what closes shell splitting, globbing, expansion and command-substitution vectors for
  the path value. For an added symlink, under the same override, `readlink -- "$ADDED_PATH"` (or an
  equivalent argv-based, non-dereferencing link-payload read if Gateway later provides one), then
  A2's complete-output checks. That form joins the paragraph's existing #103 sentence keeping `cat`
  from dereferencing an added symlink. Three of her sentences are not repeated, because the #103
  clauses beside them already say them: that exit 1 remains the expected result, that a symlink
  needs its own non-dereferencing form, and that the regular-file `cat` form is not repurposed for
  one. Two #103 sentences that introduced the old blocks now name "the `cat` form" and "the
  `--no-index` form" and end with a period; the new blocks follow under her #104 label. She ran no
  metacharacter-path or symlink-readback experiment, and none was run for this change: nothing it
  adds is measured, and the paragraph's one measurement is still the #103 gap, taken on the
  maintainer's machine, not the OpenClaw host. Her notes on her own session, and her line
  describing the paragraph at #107's head, stay on the issue. Unchanged: the rest of the paragraph
  under its #103 labels (the route and its bound, the generic-tool caution, exit 1 expected, the
  binary/truncation sentence, the measurement of the gap), rules 1–5, the table's rows (row 3's
  cell included), the whole #96 paragraph with its diff form, and row 1's eligible-set paragraph.

- **2026-10-02 (#2) — Claude Code: `EnterWorktree` is not the lane-isolation command.** Issue
  #101, from findings 4 and 5 of the two reviews of claude-skills#167. The lane-isolation line
  said the tool "does the same" as `git worktree add ../<repo>-<lane> -b
  <initiative>/wave-<n>-<lane>` from the wave branch. [measured interactive 2026-10-03, Brandon,
  Claude Code 2.1.91, scratch repository; recorded on #101] It made a worktree in a different
  directory, on a differently named branch, based on `origin/<default>` rather than the
  session's `HEAD`. **Decision (Brandon, 2026-10-03 UTC): drop the sentence; a one-line replacement
  saying lanes use the command is acceptable.** The line that stands in its place says a lane uses
  the command, not the `EnterWorktree` tool, and points to #101; nothing is claimed about any other
  version. The command, its flat-form note and the hooks bullet are unchanged; claude-skills#176
  item 2 is to mirror the change into the scaffold template.

- **2026-10-02 (#1) — OpenClaw: row 3's readback of a file the patch adds.** Issue #103, from
  CodeRabbit on claude-skills PR #177 (thread `4169652576`): `git apply` leaves an added file
  untracked, so row 3's index-based diff prints nothing for it. The answer is Camina's (her
  confirmation on #103 of 2026-10-02, carried clause by clause in her order, each under a label of
  the kind she gave it; Brandon's instruction, fleet-coderabbit-preflight MPD D68). A paragraph
  after "Row 3's readback form.": [inference/recommendation, Camina's, issue #103] after a confirmed
  strike, row 3 may read each added path directly through Gateway, provided that exact path is
  inside the session's original read scope and the complete command writes nothing outside the
  authorized paths (`cat -- <added-path>` for a regular file), and that exact-path read is the
  general rule; a generic/native read tool is not automatically a route after the strike; no `cat`
  to dereference an added symlink; for binary content, or whenever tool output can truncate, a
  bounded byte-for-byte read or a checksum/size comparison, verified complete under A2.
  [source, Camina's, issue #103] For an added regular text file,
  `git --no-pager diff --no-index --no-ext-diff --no-textconv -- /dev/null <added-path>` is also
  eligible, exit 1 expected. Two of her `[source]` clauses also state a conclusion (that a direct
  read invokes no Git index or helper; that the `--no-index` form is eligible); they are carried
  under the label she gave them. The one measurement the paragraph cites shows the gap, not either
  read: taken 2026-10-02 by the orchestrator that filed #103, on the maintainer's machine, not the
  OpenClaw host (git 2.46.0, a scratch repository), recorded on #103, which she cites and did not
  re-run; her notes on her own session stay on the issue. Rules 1–5, the table's rows (row 3's cell
  included), the whole #96 paragraph with its diff form, and row 1's eligible-set paragraph, which
  does not list the `--no-index` form, are unchanged.

- **2026-10-01 (#7) — OpenClaw: row 3's readback names its diff form.** Issue #96, from finding 7
  of the Spec review of wave 3b's `openclaw` lane; the clause is Camina's (her confirmation on #96
  of 2026-10-01; Brandon's instruction, fleet-coderabbit-preflight MPD D52 as corrected by D54). A
  paragraph after row 1's bound: [inference/recommendation, Camina's, issue #96] row 3's
  diff/readback is inspection, and when it uses Git diff it uses row 1's eligible form limited to
  the patched paths,
  `git -c diff.autoRefreshIndex=false diff --no-ext-diff --no-textconv -- <patched paths>`,
  bounded, as she bounds it, to the current OpenClaw host and breaker contract. Her recommendation
  clauses carry that label and her `[source]` clause is attributed to her; her notes on her own
  session stay on the issue. The measurement it rests on is the Spec reviewer's of 2026-10-01 on
  the maintainer's machine (git 2.46.0, scratch repos), recorded on #96, which she cites and did
  not re-run; that record names the form without the pathspec. Rules 1–5, the table's rows (row
  3's cell included) and what row 3 routes are unchanged.

- **2026-10-01 (#6) — B0 item 1: the dry-run probe runs `pre-push` as a real push would.** Issue
  #89, from the triage of claude-skills#144 (the CodeRabbit CLI's finding 5 against the scaffold
  template's copy). The hook probe's `git push --dry-run` "sends no objects", which is git's own
  behaviour; [measured 2026-09-30, git 2.46.0, scratch repos] the `pre-push` hook ran on the dry
  run with arguments, stdin and environment identical to a real push's, and its own side effect
  happened. Item 1 now says so and has the prober read the hook first and neutralise any part that
  sends data, keeping its invocation visible under `GIT_TRACE=1`; [source: `git-lfs-pre-push(1)`,
  `git-lfs-config(5)`] for Git LFS, whose hook uploads the pushed range's LFS objects, that is
  `GIT_LFS_SKIP_PUSH=1`. That the probe would upload LFS objects stays the ticket's unmeasured
  inference; no checkout on the maintainer's machine uses LFS [measured 2026-09-30]. What the
  probe proves, its FAIL and no-result cases and the per-worktree clause are unchanged.
- **2026-10-01 (#5) — OpenClaw: the breaker's closing paragraph names its subject.** Issue #90,
  from the Standards review of wave 3a's `openclaw` lane (not blocking): since #67 the paragraph
  "This is **not** a global switch…" follows the no-route paragraph, so its "This" read first as
  that rule. It now begins "The breaker is **not**…"; nothing else in the paragraph changes.
- **2026-10-01 (#4) — OpenClaw: a confirmed strike does not change the session's mode.** Issue
  #94, from CodeRabbit's question on PR #87 (thread `4150248351`). [decision 2026-10-01, Brandon,
  on Camina's recommendation; fleet-coderabbit-preflight MPD D36] One sentence beside the no-route
  paragraph: the strike marks the native sandbox unavailable and leaves the mode as B0 selected it;
  the session carries on by bounded routes and stops at the first required operation with none
  (attended, Brandon gets the exact command; autonomous, stop and report it); only Brandon's
  explicit override changes the mode after pickup; a strike during the pickup guard that stops the
  gate being demonstrated is an ordinary B0 attended start. B0 already gives that result (a guard
  item that fails at pickup starts the session attended) and is unchanged. Not a new mode, a new
  guard item or a change to the five rules.
- **2026-10-01 (#3) — OpenClaw: the prelaunch string, and what "confirmed" means.** Issue #91,
  carrying #67's two follow-ups (its comment of 2026-09-27, relaying Camina's of 2026-09-26).
  [measured on the OpenClaw Gateway host, as that comment gives it] The exact `bwrap` prelaunch
  string is quoted after the five rules. [source, Camina's, same comment] The `sysctl` remedy it
  names is not a route, since enabling unprivileged user namespaces would weaken the sandbox
  (#58's "Not" list); a failure is confirmed when the signature returns before the target produces
  any output or side effect, and a failure after the target starts is a target failure that does
  not trip the breaker. This entry leaves the five rules, the routing table and the no-route
  paragraph unchanged; row 1 changes under #88.
- **2026-10-01 (#2) — OpenClaw: row 1's bound is the command's, and the inspection commands that
  keep it are named.** Issue #88: the circuit breaker's row 1 routed read-only inspection to
  "narrowly scoped Gateway execution", putting the bound on Gateway, whose `workdir` does not
  confine writes on the measured host (#67: Camina's measurement and her inference from it).
  Camina's answer on the ticket (2026-10-01) is no, not by default: [source, Camina's] a linked
  worktree's index resolves to `.git/worktrees/<id>/index` in the main repository, and nothing in
  the breaker's contract implicitly expands a worktree-only grant to it; [inference, Camina's] a
  refresh there is outside that grant unless the exact path was granted. [measured 2026-09-30, git
  2.46.0, scratch repos, issue #88] With a stat-stale tracked file, `git status` and `git diff`
  rewrote that index, `--no-optional-locks` stopped `status`'s write but not `diff`'s, and
  `git log` wrote nothing. Row 1 now says the bound is the command's; a paragraph under the table
  names her eligible set and carries her recommendation — permit only commands established not to
  write outside authorized paths, default-deny the four forms she names, no route where that
  cannot be established — each clause under her own label (her "source-backed" items as
  `[source]`, attributed to her; her `[measured]` item with what its controls ran), with the bound
  she put on her answer. Rules 1–5, rows 2–5, the A7 sentence and the no-route paragraph are
  unchanged.
- **2026-10-01 — A provenance line names the initiative, the role and the mode, never the client
  or the product.** Issue #92, a revision made after option 1 shipped. On 2026-09-30, #85 was
  decided as option 1 and shipped in PR #87: a provenance line naming the filing agent is not a
  credit line. The line as the fleet filed it named the client the agent ran in, and the Spec
  review of that change had flagged the tension. [decision 2026-10-01, Brandon: option 3;
  fleet-coderabbit-preflight MPD D40] A4 now says what a provenance line names — the initiative,
  the role (e.g. wave orchestrator, lane) and the mode the filing agent worked in — and that it
  names no client and no product; it is still not a credit line, and still says who read the
  evidence, which A2 wants. The 2026-09-30 (#2) entry stands as the record of option 1 and is not
  rewritten. Forward-only: no Provenance line on an issue already filed is edited. Not a change to
  the grep or the author check. The claude-skills half (`writing-tickets`, `orchestrate` and its
  `HANDOFFS.md`, the scaffold template's mirror of A4) is claude-skills#161.
- **2026-09-30 (#3) — A4 carries the usage-credits rule, and three more wording items from the
  wave-2 review land.** Issue #84, from the two-axis review of PR #83, five findings labelled not
  blocking. [decision 2026-09-30, Brandon; fleet-coderabbit-preflight MPD D27, D28] "No agent spends
  usage credits: a billing prompt holds the paid review, never the push" moves from B2's stop-list
  item 3 to the end of A4's review-bot bullet, so it binds in attended mode too, where A8 already
  has the agent ask first; the stop-list keeps billing among its third-party writes and points back
  to A4 for the push. A4's author-check parenthesis says "a repository of Brandon's" in place of the
  repository and initiative it named, keeping `[measured 2026-09-26]`; the 2026-09-29 entry on #79
  keeps the locator. [decision 2026-09-30, the orchestrator; MPD D29, under D22] B2's merge bullet
  runs `coderabbit-preflight` when the push carries new work, pointing at the bullet that defines
  it, so it no longer reads as every lane merge; A4's short reply on a finding's thread, and its
  per-thread declines, apply where a thread exists, since a CLI finding has none. Item 3 (when the
  preflight runs is stated three times) is declined: the review loop's item 1 already ends "(Git
  contract above)", the pointer it asked for, and the merge bullet's restatement now points at the
  definition. Items 1, 2 and 5 change no rule's meaning; item 4 widens the credits rule to attended
  mode, where A8 already asked first. *(Marked 2026-10-01: the 2026-09-29 entry on #79 no longer
  keeps the locator; issue #93 removed it.)*
- **2026-09-30 (#2) — A provenance line is not a credit line.** Issue #85, from the Spec review of
  PR #83: since 2026-09-29 (#2) RULE ZERO covers what an agent posts under Brandon's name on an
  issue, and every issue the fleet's agents file ends with a Provenance line naming the filing
  agent. [decision 2026-09-30, Brandon: option 1; fleet-coderabbit-preflight MPD D26] A4 now says
  a provenance line naming the filing agent is not a credit line: it says who read the evidence,
  which A2 wants, and credits no product. The practice stays; `writing-tickets` is unchanged. Not
  a change to the grep or the author check.
- **2026-09-30 — OpenClaw: test runs deliberately have no route after the breaker trips.**
  Issue #67: the circuit breaker's routing table had no row for test runs, and the skill that
  applies it had to declare them unrouted in its own text. The decision was Camina's (her comment
  of 2026-09-30 on the ticket), accepted by Brandon the same day (fleet-coderabbit-preflight MPD
  D30): no row, a stated no-route rule. [source, issue #67, measured there 2026-09-30] The live
  Gateway execution surface takes a host command and a `workdir` and exposes no filesystem-root
  or path allowlist, mount namespace, UID remap or read-only-filesystem control, and a sibling
  write from a probe worktree succeeded. [inference, Camina's, issue #67] `workdir` does not
  confine writes on the measured host, so no command and `workdir` pair keeps a test run inside
  the worktree as rule 4 requires, and rule 5 applies. The appendix now says so beside the table,
  for any repository's suite: attended, Brandon runs it from the exact command (B1); autonomous,
  the session stops and reports the command as having no bounded route and does not run it
  through Gateway. This repository's `./scripts/check-index.sh && ./scripts/check-index.test.sh`
  is named as an example, not the rule. Not a change to the five rules, the five rows, the A7
  sentence or the "not a global switch" paragraph; the ticket's two follow-ups (the literal
  prelaunch string, the definition of "confirmed") stay open there.
- **2026-09-29 (#3) — B2 names `coderabbit-preflight`, and A4 says which review findings are
  fixed.** Issue #81, from the `fleet-coderabbit-preflight` initiative (MPD §6): Brandon adopted
  the CodeRabbit CLI as a pass before the push, run by the orchestrator through its own skill
  (D1–D3, D7), degrading on any client where the CLI cannot run (D8), never spending usage credits
  (D5, D9).
  After the claude-skills 1.19.0 release PR (claude-skills#145) took three PR rounds and seven CLI
  runs [measured 2026-09-29, MPD update log], he set when it runs and which findings are acted on
  (D14–D16, the ticket's comment of 2026-09-29). B2's git contract now runs `coderabbit-preflight`
  between the gate on the merged tree and the push, where the CLI is available to that client:
  once before each push that carries new work, a lane landing or a release cut, never before one
  that only answers review findings, and never re-run. An unavailable CLI never holds a push and
  never downgrades the mode; B0 is unchanged, the CLI is not a guard item. The review loop gains
  the step before the PR round as item 1 (old items 1–4 are now 2–5), and its fix step
  redispatches only the fixes A4's threshold calls for. A4's review-bot bullet now leads with the
  threshold, for the CLI and the PR bot alike and on release PRs: a finding is fixed before the
  merge only when verified and doing real harm; one that holds without such harm becomes a ticket
  with a short reply; one the code disproves is declined with receipts, as before. Stop-list item
  3 says no agent spends usage credits: a billing prompt holds the paid review, never the push. A1
  lists the skill; `clients/claude-code.md` records the CLI measured there (0.8.2, org
  `brandonperfetti`). The skill carries the rules of a run; this file carries the step, the
  condition and the law. Not a change to when the PR opens (B2's PR-open sentence is unchanged),
  to who merges, or to the two-axis review.
- **2026-09-29 (#2) — RULE ZERO covers thread replies and comments.** Issue #82: with Auto-fix on,
  Claude's desktop app asked the agent to end each PR thread reply with a line crediting Claude
  Code [measured 2026-09-29, claude-skills#139]; the orchestrator left it off, and A4 named only
  commits and PR bodies. [decision 2026-09-29, Brandon; fleet-coderabbit-preflight MPD D11] What an
  agent posts under his name on a PR thread, a PR or an issue carries no credit line. A4 now says
  so, and `clients/claude-code.md` records the Auto-fix request and that the agreement declines it.
  Not a change to the grep or the author check.
- **2026-09-29 — A4's author check reads the email, not the name.** Issue #79: since 2026-09-26
  (#2) A4 compared every added commit against `Brandon Perfetti <brandon@brandonperfetti.com>`
  exactly, as "the only author on either base branch [measured 2026-09-26]" — true of this
  repository, which sets a repo-local `user.name`, and false on a repository of Brandon's, whose
  `origin/develop` holds `brandonperfetti` ×51, `brandonperfeti` ×24 and `Brandon Perfetti` ×16,
  all at that email [measured 2026-09-26]. Every lane commit there, all at his email, failed the
  literal check, and merges held until an exception was made for that repository. [decision
  2026-09-29: option 1, in the wave-2 packet Brandon agreed under fleet-coderabbit-preflight MPD
  D18] A4 now compares the author email alone (`%ae` on the branch, the `From:` address in an
  mbox); the name is not compared, and the unscoped measurement is removed. #69's case is still
  caught wherever a lane clone's email differs; one differing only in name now passes, by design.
  Written from the draft kept at `evidence/2026-09-29-awa-79-draft/` in that initiative, less its
  sentence on the global `user.name`, which had since changed. Not a change to the trailer grep,
  to who applies an mbox, or to the forward-only rule. *(Corrected 2026-10-01, issue #93: the
  repository's name removed, with the entry locator and decision number from that repository's
  own initiative; the measurement and its counts stand.)*
- **2026-09-26 (#2) — RULE ZERO's check reads the author, not only the trailers.** Issue #69, from
  CodeRabbit on claude-skills PR #128 (thread 4108126735, 2026-09-25): A4 stated the rule as an
  identity ("a commit carries Brandon's author identity") but named only a text check, the grep for
  attribution trailers; B1's attended mbox path applies a lane's series with `git am`, which
  reproduces each patch's `From:` line as the commit author [source: git-am docs], so an mbox whose
  commits carry the lane's own identity would pass the grep and land a commit that breaks the rule.
  [measured, claude-skills-fleet-alignment waves 1–2] Orchestrators had been reading
  `git log --format='%an <%ae>'` on every delivery beside the grep, and on this fleet the lane
  clones share the machine's git identity, so it had not bitten; it bites on a machine where a lane
  clone's `user.name`/`user.email` differ from the human's — a fresh-machine template's case. A4
  now names the author read beside the grep, for both delivery shapes, with the send-back, and the
  one value both compare against — `Brandon Perfetti <brandon@brandonperfetti.com>`, the only author
  on either base branch — so operators do not each decide what "authored as Brandon" means
  (CodeRabbit on #77, thread 4112345800); B1's apply-block bullet says `git am` preserves the patch
  author, so the check precedes the apply. Not a change to the grep, to who applies, or to the
  forward-only rule for inherited commits. The skill and template halves are claude-skills #133,
  blocked on this entry (1.18.0 `### Known`, item 2). *(Marked 2026-09-29: the compared value is
  now the author email alone — the 2026-09-29 entry above; "the only author on either base
  branch" was true of this repository only.)*
- **2026-09-26 — A7's "In Review" move is qualified by mode.** Issue #68: A7's Tracker bullet said
  the orchestrator moves an issue to "In Review" "by hand at PR time" with no mode qualifier, but
  the only "PR time" a wave has is B2's autonomous review loop; in attended mode there is no PR when
  a delivery is reviewed (the human pushes, the orchestrator commits per batch), so the move happens
  at commit time. [decision 2026-09-25, Brandon, claude-skills MPD O3] No conflict in substance:
  the `orchestrate` skill's split ("commit time attended, PR time autonomous") stands and the skill
  does not change; A7's sentence was the one that read unqualified. A7 now says "at PR time in
  autonomous mode (B2's review loop), and at commit time in attended mode, where no PR exists when
  a delivery is reviewed". B2's review loop item 3 is unchanged. Recorded in claude-skills 1.18.0's
  `### Known` (item 3) as this repository's half.
- **2026-09-24 (#4) — B1's "never touch git" names the shared checkout.** Release review of the
  #51 → #58 queue (CodeRabbit on PR #65): the new A4 worktree bullet lets an attended lane commit
  in its own isolated clone, which B1's mbox shape already required, while B1's closing sentence
  said sub-agents "never … touch git" with no qualifier. The two disagreed on whether an attended
  lane may run git at all. B1 now says sub-agents never touch git **in the shared checkout**,
  which is what its own parenthetical meant; the isolated-clone commit stays as it was.
- **2026-09-24 (#3) — OpenClaw gets a one-strike Bubblewrap circuit breaker.** Issue #58 is
  Camina's measured specification, transcribed: [source, issue #58] the agent-working-agreements
  delivery cycle of 2026-09-23 retried native shell and patch paths after the same prelaunch
  error — Bubblewrap could not create a namespace inside the Docker/AppArmor boundary — while the
  bounded Gateway equivalents reached the target, and OpenClaw has no supported sticky per-session
  failover to make the switch for it. The appendix now carries the breaker every session reads at
  bootstrap: one confirmed prelaunch failure marks the native sandbox unavailable for the session,
  equivalent native retries are prohibited, a five-row routing table names the bounded fallback
  per operation, AppArmor/seccomp and the task's authority are preserved, and a missing fallback
  is a stop-and-report. Not a global Gateway switch, not a sandbox weakening, not a rule for
  failures after the target starts. The Migration dispositions sentence that sent all Bubblewrap
  guidance to the fleet documents is reconciled: the fuller five-step pattern stays in the fleet
  operating model (`docs/team-operating-model.md` on the OpenClaw host); the in-session breaker
  lives here. Release review of 2026-09-24 added, beside the table rather than in it, that A7
  still governs the GitHub row: the GitHub MCP's write tools never author commits.
- **2026-09-24 (#2) — OpenClaw removes a delivery worktree once its PR has merged.** Issue #48
  made the delivery checkout host the only place delivery worktrees are cut, but nothing ended a
  worktree's life: [measured 2026-09-23, issue #57] the host went from 13 to 16 registered
  worktrees in one delivery cycle, and the recorded cleanup then removed 14 merged ones without
  forcing a dirty removal. The OpenClaw appendix now names the end of the lifecycle: a
  merge-gated (`git merge-base --is-ancestor` against a fresh `origin/develop`), non-forced
  removal from the delivery host, the branch deleted only after the worktree, and anything
  protected, dirty, unmerged, or otherwise refused left intact and reported. The rule is durable
  client text only; it authorises no cleanup run and no change to the instruction-source clone.
  Release review of 2026-09-24 moved the cleanup's evidence-file path out of the rule, per
  2026-09-13 (#11): the dry-run and live cleanup are recorded on the OpenClaw host at
  `_agent/evidence/2026-09-23-agent-working-agreements-delivery-host-worktree-cleanup.md`.
- **2026-09-24 — OpenClaw's appendix describes the completed cutover, not a pending one.** Issue
  #54: after the canonical-source cutover, `clients/openclaw.md` still said the workspace-root
  `AGENTS.md` pointed at the full machine-local agreement and still carried the Quiet cutover
  contract, whose own step 5 named a later reviewed cleanup to remove it and condense Migration
  dispositions. [measured 2026-09-22, issue #44] The live workspace-root `AGENTS.md` routes
  Parts A–B and the appendix through the instruction-source clone, and the former path is a
  non-authoritative stale-reader stub. This amendment is the text half of that cleanup; the
  stub's removal is a host-side step the appendix now names, since a repository PR cannot perform
  it, and the removed steps stay readable at `29b6360:clients/openclaw.md` lines 104–130. The
  accepted `OpenClaw → autonomous` target moved from the contract into Startup and mode because
  it is standing mode status, not migration scaffolding. Review of the first draft narrowed the
  `[measured]` label to what #44 observed and replaced a citation to the deleted contract with
  that locator. The #48 section and the pickup guard are untouched. Release review of 2026-09-24
  dated the "until this amendment" locator to this entry's issue and put the pickup guard's "does
  not block … the pointer cutover" into the past tense, the one pre-cutover sentence the sweep
  found.
- **2026-09-23 (#4) — A4 names the worktree boundary beside the file fence.** Issue #51 records
  a sans-faux-studios maintenance wave-1 lane (2026-09-23) that ran git against the orchestrator's
  checkout and switched its branch mid-wave; the orchestrator's next merge landed on local
  `develop` instead of the wave branch, never reached origin, and was caught only by a "no commits
  between" error at PR time, not by any check. Read against that event, "Lanes work their named
  files only" governs which files a lane edits and says nothing about which working tree it stands
  in, so the switch crossed no fence as written. A4 now carries the worktree boundary as its own
  invariant, distinct from the file fence: a lane runs git only in its own worktree or isolated
  clone, and the orchestrator's checkout is out of bounds for any lane git operation, branch
  change, or git-state change, with the reason in the sentence. Two-axis review of the first
  draft found it outlawed B1's attended shape, uncommitted edits to named files in the shared
  checkout, which A4 governs too ("These hold in both modes"); the bullet scopes the boundary to
  git so that shape crosses neither fence. The `orchestrate` skill keeps the loop; the agreement
  holds the law.
- **2026-09-23 (#3) — OpenClaw keeps its instruction source isolated and current.** Issue #48
  records two measured failures after the canonical-source cutover: delivery commands explicitly
  selected the instruction-source clone as the Git host and created three worktrees under it, and
  PR #41 merged to `master` at `b733b59982736285d078ee9f67209bcce2fea957` on
  2026-09-22T20:18:10Z while that clone remained six commits behind until the next day. The
  OpenClaw appendix now requires delivery worktrees to come only from the delivery checkout host
  and requires a fetch plus fast-forward after every `develop → master` merge, before further
  work, with the next report naming the exact served SHA.
- **2026-09-23 (#2) — feature PRs open ready and finish CodeRabbit before hand-back.**
  [decision 2026-09-23, Brandon] Issue #46 records the ratified practice: agents open feature PRs
  into `develop` ready for review, complete the CodeRabbit round before hand-back, and leave every
  merge to Brandon. The earlier pre-bot read moved to Brandon's external verification of the
  completed report, so the additional draft-to-ready relay bought nothing. Drafts had controlled
  CodeRabbit's measured 5-reviews/hour allowance. For the authorized release queue that prompted
  this amendment, one-PR-at-a-time pacing covers that cost without treating the current allowance
  as a permanent guarantee or adding a global scheduling rule.
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
  `_agent/evidence/2026-09-23-pr47-agent-root-marker-audit.md`. Release review in
  `8ad6ebc` also corrected A6's
  root inventory to name `_agent/`, matching the preamble and the marker rule.
- **2026-09-22 (#2) — on-fleet artifact placement outranks generic skill defaults.** Issue #39
  makes explicit that the `agent-workspace` convention governs artifact destinations on an
  on-fleet workspace ahead of a generic skill default. A1 already identifies the skills plugin as
  a mirror of `mattpocock/skills` plus Brandon's own skills, while A6 already owns workspace
  destinations and keeps experiments out of `/tmp`; those neighboring rules make the canonical
  agreement, rather than a patch to one mirrored skill, the durable place to settle precedence.
  Off-fleet fallbacks remain the skill's to define. This supersedes
  claude-skills #113.
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
  failed; claude-skills #111
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
