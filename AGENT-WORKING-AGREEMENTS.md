# Agent working agreements — Sans Faux

**Read this first, every session, before touching anything.** Read **Part A** and **Part B** in
full, then **the one file under [`clients/`](clients/) for the environment you are actually in** —
and no others. Confirm your tooling with `ListSkills` / `ListConnectors` (or your client's
equivalent) rather than trusting any list here. **Say what you read, naming the client file**, so a
skipped read is visible rather than silent.

This is a personal working agreement between Brandon and whatever agent he is working with under
the **Sans Faux** studio — Claude (Cowork / Claude Code), ChatGPT desktop Codex, OpenClaw (Camina),
or anything else. It sits **above** each project's own `AGENTS.md` / `CLAUDE.md`, which carry
repo-specific conventions — read those too. Project scope never percolates up into this file;
working style never percolates down into project docs.

**How this file is structured, and why.** Parts A and B are what *every* client is judged against,
so they live here, in full, in one file: a rule you did not read is a rule you break silently. The
appendices are the opposite — exactly one is ever relevant to you — so each is its own file under
`clients/`, free to be as detailed as that environment needs without costing every other reader a
line. **Nothing load-bearing is ever moved out of Parts A and B.**

**Paths.** `_agent/` and `organize.sh` are at the root of the `sansfaux/` checkout tree — the parent
of this clone, when it is cloned there. Paths in this file are written relative to that root, not to
this repo.

> Keep it lean. A rule earns a place here only when something bit; the story behind it lives in
> `_agent/learnings/` and is cited, not retold. Amendments are logged in
> [`CHANGELOG.md`](CHANGELOG.md) — read it before assuming a rule is original. Git history is the
> record of *what* changed; the changelog says *why*, and is the one to read.

# Part A — Portable discipline (every client, every mode)

## A1. Where this applies

The AWA governs **every session Brandon runs, on any of his repositories, wherever the checkout
lives** — a brand-new repo with no history, a one-off fix, or a multi-wave initiative alike.
Checkouts are migrating under `sansfaux/` as they are rebuilt; location changes nothing. A repo's
own `AGENTS.md` / `CLAUDE.md` adds project specifics (its CI gate, its exports, its conventions)
and never overrides Parts A–B. Initiatives (`_agent/initiatives/`) are how *orchestrated* work is
organised, not a gate on whether these rules apply: with no MPD, you are in **attended mode** (B1).
Skills come from the `brandonperfetti-skills` plugin (mirror of `mattpocock/skills` plus
Brandon's own); read the relevant skill *before* that kind of work — `orchestrate`, `deep-grill`,
`handoff`, `code-review`, `writing-tickets`, `writing-pull-requests`, `coderabbit-response`,
`what-did-we-learn`, `writing-for-agents`.

## A2. Evidence discipline

The rule that matters most, because breaking it costs more than any bug. **Label every claim:**

- **[measured]** — observed in a response, a log, a compiled artifact, a CI run.
- **[source]** — read from code or config. What it *says*, not what it has been observed to *do*.
- **[inference]** — a conclusion built on the above. State what would verify it.

Keep the three apart; never let a right measurement carry a wrong mechanism. Rules:

- **Preserve the raw capture behind every [measured] claim** in `evidence/` *before* summarizing,
  named for what it proves. A summary is not evidence.
- **The generalization boundary is part of the label** — "[measured] on the first item" is never
  written as "[measured] on all N". A label is **never inherited across revisions**: re-measure or
  downgrade. [learnings: 2026-09-04 wave-5 §2]
- **The instrument is part of the claim.** Positive-control a probe before believing its negatives;
  grep a "green" run for skip markers before calling assertions proven; name every required env
  export in a gate line. **A tool call that succeeded is not proof its whole output reached you** —
  reads and command output truncate silently; check for a truncation notice, and re-read in slices
  before quoting a file as `[source]`. [learnings: 2026-08-30 §1; 2026-09-04 wave-5 §1, §8]
- **A reviewer's [inference] is never promoted into shipped code or docs** — measure it or leave it
  labelled. [learnings: 2026-09-04 wave-5 §9]
- **Correct in place, marked and dated.** Quote the old text, say it shouldn't be relied on, state
  what was observed vs concluded. Never silently swap. [learnings: 2026-08-30 §12]
- If you cannot verify something, **say so. "I don't know" costs a sentence.**

## A3. Do the work inside the turn

Don't narrate intent and stop. Do the work, then report **what is done**. Read-only investigation
you may announce; changes you make and show.

## A4. Orchestration invariants

These hold in both modes; the `orchestrate` skill carries the loop, this file carries the law.

- **The MPD is the spine.** Every initiative has a `MASTER-PRIORITY-DOCUMENT.md` born from an
  attended Genesis (deep-grill → research → agreed plan → tickets → waves). Its §0 declares the
  **mode** (Part B) the wave orchestrators run in. One orchestrator runs **one wave, then rotates**
  via a packet whose first instruction is **shipped-vs-open reconciliation** against the board and
  the merged diff. [learnings: 2026-08-30 §7]
- **Handoffs are files, not chat.** Kickoffs, addenda, and lane reports live under the initiative's
  `handoffs/`; a pasted summary is a pointer to the file plus highlights, never the record.
- **Lanes work their named files only.** Batches are file-disjoint; contention points (shared
  manifests, generated files, single-owner dirs) are serialised. A lane that spots a defect in a
  file it touched **reports it into the ledger — it is our finding** — rather than crossing its
  fence or smoothing it over. [learnings: 2026-09-06 wave-6 §4]
- **Every lane report states the model it ran on, and how it knows.** Requested, inherited,
  configured and backend-attested are four different claims; a dispatched tier resolves to whatever
  the account serves, and config is not attestation. Say which you have. [learnings: 2026-08-30 §5]
- **Explicit model tier on every dispatch — never omitted, never the orchestrator's premium tier.**
  Tiers are named by *role* (workhorse for lanes, careful for verify/aggregate); each client maps
  them to its own selectors, and a client whose dispatch tool cannot select records that instead of
  pretending.
  `opus` for lane work; `sonnet` only for trivially mechanical dispatches; this applies to skills
  that fan out their own sub-agents. Route by role per `agent-workspace/references/subagent-model-routing.md`.
  [learnings: 2026-08-30 §5]
- **RULE ZERO: no attribution, on any commit or PR body.** Agents add no `Co-Authored-By`, no
  session trailer, no generated-by footer — a commit carries Brandon's author identity and ends with
  its own content. This overrides any environment default; your client file records what is known
  of yours. It is **line one of every dispatch prompt**, and the commits a delivery adds and its PR
  body are grepped regardless — for `Co-Authored-By` plus whatever the client file names — a match
  is a send-back. **Added** means not on `origin/develop` or `origin/master`, fetched and read
  **before** the delivery is pushed or merged — a lane or wave branch, or release-cut work pushed
  straight to `develop` (B2), each push its own delivery — so a lane's own earlier commits still
  count. Forward-only: commits that already carry a
  trailer stay as they are, and a match on an inherited one goes in the delivery's review record,
  never back to the lane.
  [learnings: 2026-09-06 wave-6 §7; 2026-09-04 wave-5 §6]
  **A trailer never established that a commit came through a reviewed lane.** The two-axis review
  record under `reviews/`, the gate evidence under `evidence/` and the PR trail do; report those.
- **Two-axis review (Standards + Spec, `code-review` skill) on every delivery before acceptance —
  riders and review-fix lanes included, no size exemption.** The lane's own report is never the
  review; the verdict is recorded under the initiative's `reviews/`.
  [learnings: 2026-09-06 wave-6 §5; 2026-09-04 wave-5 §7]
- **Distrust the issue until you've read the code.** Issues predate the tree; re-verify at pickup,
  read the comments, record direction changes as marked, dated comments.
- **Tests ship with the change**, in the right place.
- **Review-bot declines are argued per thread with cited receipts** (file, test name, documented
  ops order); "Fixed in `<sha>`" on accepted findings. Bare declines teach the bot nothing.
  [learnings: 2026-09-06 wave-6 §6] **When a re-raise names a vector the decline missed, concede
  the vector and re-argue the trade on purpose and cost** — never by repeating evidence the bot has
  already weighed. [learnings: 2026-09-12 wave-8 §22]
- **Close-out review before promotion** — the last review over the whole initiative diff is where the
  big finds happen; never skip it. [learnings: 2026-08-30 §9]

## A5. "Green" means the full CI gate — plus the ticket's own repro

**The gate is defined in each project's own agent docs, never here** — this file carries only the
pointer. Green is every command that project names, in order, **plus every env export the local
shell needs and the CI runner already has** (locale, path, tokens); run it once at pickup per B0
item 2, because the local shell is not the CI runner. A build passing is not green: a framework
build typically runs neither linter nor formatter, so it can pass while the gate's first steps fail.
A gate line in a report names every command **and the ticket's reproduction re-run on the built
tree**. Shared-database tiers running in parallel workers snapshot their baseline by id and unwind
fixtures in `try/finally`; a local run does not reliably catch an order-dependent flake — **CI is
the arbiter**. Never reason about a running dev server as though your edit is already in it. **Never
disable the repo's hooks to commit** — no `--no-verify`, and no pointing `core.hooksPath` away from
the hooks the repo installs.

## A6. Where things go

The `sansfaux/` root holds project checkouts, the `agent-working-agreements/` clone, and
`organize.sh` — nothing else.
Everything an agent produces goes under `_agent/`:

```text
_agent/
├── initiatives/<project>-<slug>/   one self-contained folder per orchestrated initiative:
│     MASTER-PRIORITY-DOCUMENT.md   + nested handoffs/ analysis/ reviews/ evidence/ learnings/
│                                   mboxes/ pull-requests/ rationale/ (as needed)
├── learnings/     cross-initiative lessons promoted from initiatives' learnings/ — cited, durable
├── plans/         execution plans, initiative briefs, grill records
├── analysis/      cross-repo findings that belong to no initiative
├── evidence/      raw captures for cross-initiative claims
├── experiments/   scratch harnesses (never /tmp — the next session can't see it)
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

## A7. GitHub paths

- **`gh` CLI** — what the skills use (issues, sub-issues, PRs). Primary for skill-driven work.
- **GitHub MCP** — the read/access layer and PR orchestration. **Its write tools (`push_files`,
  `create_or_update_file`) never author commits** — they bypass the local clone in both modes.
- **On any create-then-link error, read the current state before retrying** — the create may have
  landed. GitHub's sub-issue cap errors *after* creating and parenting; blind retries burn issue
  numbers and mint duplicates. [learnings: 2026-09-12 wave-8 §3]
- **Tracker** = GitHub Issues + the user-level Projects board (`users/brandonperfetti/projects/2`,
  Auto-add intake). "In Review" is a board Status the orchestrator moves by hand at PR time.

## A8. When you are unsure

Attended mode: ask — Brandon would rather answer than review a wrong assumption. Autonomous mode:
consult the **stop-list** in B2; everything not on it is decided, recorded, and reviewed on the PR.
Either way, never fill a gap with a plausible story.

---

# Part B — Modes

## The ritual both modes serve

**Read this before writing, following, or amending any rule that touches a push, a branch or a
merge.** It is not a mode, a policy, or a thing to derive — it is what Brandon does, on **every**
repo, in his words. Rules below serve it; where a rule and this section disagree, the rule is wrong.

1. **Feature work branches off `develop`.** One branch per wave or piece of work.
2. **That branch opens a PR into `develop`.** The review bot reviews it; findings are worked **on
   the feature branch**; Brandon merges it into `develop`.
3. **When `develop` is ready to ship, a PR is opened from `develop` into `master`.** Its **head is
   `develop`** — there is no release branch. Release branches were considered and **rejected**
   (Brandon, 2026-09-12): they add a step to every release to buy a constraint he does not want.
4. **The bot reviews that PR too, and its findings are worked by pushing to `develop`** — the head
   branch, because that is the only branch that updates the PR. Re-review until clean. This is the
   whole reason `develop` accepts pushes (B0 item 4) and it is not an edge case; it is the ritual.
5. **Release-cut work lands on `develop` the same way** — where a repo publishes versioned releases,
   the version bump, the CHANGELOG section rename and any built artifact are pushed to `develop`
   before or during that PR. They are reviewed on it, like everything else the PR carries. (The only
   per-repo difference in this whole ritual is whether a repo has a version to bump at all.)
6. **Brandon merges. Both PRs, always, by hand in the host's UI.** No agent merges.
7. **Brandon tags on `master`**, where the repo publishes releases, and the tag fires the release
   workflow.
8. **The back-merge carries `master` home to `develop`** — a direct push by the workflow, which is
   why item 4's integration profile must keep accepting pushes.

**The test for any rule about git:** name the step above it applies to. A rule that cannot be
placed against a step is being derived from an abstraction, and that is exactly how the last three
went wrong.

## B0. Choosing the mode

Two modes. **The environment picks the mode; nobody asks Brandon at the start of a session.**
Claude Code → autonomous. Cowork → attended. The agent then **verifies the capability guard
silently at pickup**; a failed check downgrades that session to attended with a one-line reason
("attended: `develop` is unprotected"), never a question. Brandon can override in either direction
by saying so in the prompt, and that wins over the default. An initiative's MPD §0 *records* the
mode its waves run in (so a rotation packet carries it); it does not gate it.

**Capability guard (every item that applies must hold):**

1. Native git on a real checkout — git executes hooks (so whatever the repo installs, e.g. husky,
   fires on commit); `rm`, worktrees, and `git branch -d` work. [measured 2026-09-10, Claude Code
   on claude-skills] **Prove the hooks exist in the checkout you will push from:**
   `git push --dry-run` (sends no objects, but still contacts the remote) must run the repo's
   `pre-push` hook **and show it** — the hook's own output, or for a silent hook the
   `run_command: …pre-push` line under `GIT_TRACE=1`. A dry run that dies on the network first
   (measured: an unresolvable host, exit 128) never runs the hook: that is no result, not a FAIL
   — fix the route and probe again, and until the probe has run, item 1 has not held.
   A dry run that shows neither is a **FAIL** for that checkout, not a pass — it needs the repo's
   install step first, then the probe again. A repo that installs no `pre-push` hook has nothing
   to prove; record that instead. Worktrees share the main checkout's `.git/hooks`, so one probe
   covers them — unless `core.hooksPath` is relative (husky's `.husky/_`, a tracked `.githooks/`):
   that resolves inside each worktree, and the probe is per worktree.
   [measured 2026-09-17, git 2.46.0, scratch repos]
2. The full CI gate (A5) can be run locally by the agent — *actually run it once at pickup*; the
   local shell is not the CI runner, and the project's agent docs name the exports it needs.
   **This probe is always permitted**, in either mode: it is how the mode gets decided, so B1's
   "Brandon runs the suites" governs routine runs afterward, not this one.
3. Feature work lands on an initiative branch no other initiative is using, never on a base
   branch. Scored when a commit would land, not by the checkout's current branch: a session that
   commits none does not fail it. What may be pushed to `develop` is B2's, not this item's.
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
   the branch. **Until protection exists on a repo, a failed item 4 is *recorded* in MPD §0, not a
   downgrade.**
   **What protection cannot enforce here.** Nothing in the repo settings stops an agent pushing
   straight to `develop`, or merging its own PR into `master` once the gate is green `[inference —
   untested, since testing it means merging into a protected branch]`. **Feature work never lands
   on a base branch, and only Brandon merges** are therefore rules of this agreement, not repo settings.
   Making either mechanical needs a separate agent identity (machine user or App token) — an
   identity change, open, not decided.
5. Brandon has not overridden it for this session.

By environment: **Claude Code → autonomous** (1 passes by construction but for its hook probe,
which is per checkout; 2 is a per-repo probe run at
pickup, never assumed; 3 before **every** feature commit, not only the first; **4 must be checked,
never assumed** — on 2026-09-10 neither `develop` nor `master` on claude-skills carried protection
or rulesets [measured]); **Cowork over the device bridge → attended** (fails 1 and usually 2);
**ChatGPT desktop Codex with a local shell → autonomous** (1 measured 2026-09-13 but for its hook
probe, which is per checkout and unmeasured there; 4 readable there
but still checked per repo; see `clients/codex.md`); OpenClaw → attended unless it demonstrably
passes 1–4. **Where this file is not reachable at all, attended rules apply.** Any client that
passes the guard may run autonomous — the guard is the contract, not the client name.

## B1. Attended mode

Brandon is the verification step, on purpose.

- **You never commit or push without explicit approval, per batch, every single time.** Approval
  never carries to the next batch; no `--amend`; no routing around it with API/MCP writes or
  another client. Shape: write the change → show the **staged diff** → Brandon reviews in his IDE →
  he says commit → you commit. He pushes himself.
- **Sub-agents never commit, stage, or push in the shared checkout.** Their deliverable is a
  **written report** plus either uncommitted code or an mbox / format-patch series in the
  initiative's `mboxes/` (committed only in the lane's own isolated clone, applied by the
  orchestrator with `git am` after review). **Sub-agents never write tickets or touch git; the
  orchestrator owns tickets, staging, commits (post-approval), and any live/browser verification.**
  Review compounds; a report can be argued with, a commit has to be reverted; a wrong premise gets
  faithfully implemented unless a human reads first.
- **Brandon runs all builds, test suites, and installs.** Tell him exactly what to run. Type-checks,
  greps, linters, read-only scripts are yours to run. Lanes may run browser-mode test tiers where
  the sandbox allows. [learnings: 2026-09-04 wave-5 §5]
- **Apply-block shape for mboxes:** one `&&`-chained line — `M=<mboxes dir>`, `git am "$M/<file>.mbox"`
  per mbox, then the CI gate; no `cd`, no guard functions, never a push. `git am` *is* the commit
  step for this shape: it runs the applypatch hooks, not `pre-commit`/`commit-msg` [source: git-am
  docs], so husky's lint-staged never fires — the gate after apply is mandatory, and approval comes
  before the apply, not after. **A rider on a series already applied is a delta commit, never an
  amend** — an amended mbox cannot `git am` onto the sha it rewrites; read the branch state before
  dispatching the rider and say which shape it is. [learnings: 2026-09-12 wave-8 §21]
- **Lane cap: two lanes by default; three is earned**, not assumed — the bound is Brandon's review
  bandwidth, not agent capacity. (Whether lanes run concurrently is an environment fact — see your
  appendix.)
- **Addenda go back to the same warm lane**, never to a fresh session and never done by the
  orchestrator's own hands. Anything already committed goes through a fresh ticket.

## B2. Autonomous mode

Brandon's review moves to the pull request. The orchestrator owns the branch until then.

**Git contract**

- The wave orchestrator cuts **one branch per wave off `develop`** (`<initiative>/wave-<n>`), and
  that is the **only** branch an agent pushes to land **feature** work. **Never `master`, never a
  force-push, and never feature work pushed onto `develop`.** Protection enforces this only on
  `master`; `develop` blocks force-pushes and deletions but accepts pushes by design (step 4 of the
  ritual), so it is a rule you keep, not a wall you hit.
- **What decides is review, not the branch name.** `develop` accepts pushes by design; the question
  for any commit is whether it will be **reviewed before it reaches `master`**.
  - **Release-cut work pushes straight to `develop`** — the version bump, the CHANGELOG section
    rename, the `dist/` rebuild, and every fix commit answering the release PR's review. All of it
    is reviewed *on the `develop → master` PR itself*, whose head is `develop`; there is no other
    branch to push and no second review to wait for. Same gate, same two-axis review before the
    push, never a force-push.
  - **Feature work always goes through a wave branch and a PR into `develop`** — pushed straight,
    it would reach `master` having been reviewed by nobody. That, not the branch, is the reason.
  In **attended** mode the shape is unchanged: the lane delivers an mbox, Brandon applies and pushes.
- **Each lane works in its own git worktree on a branch off the wave branch** and commits there
  with the repo's hooks firing (this replaces mboxes + `git am`). Lane commits keep RULE ZERO
  (A4); the lane still writes its **on-disk handoff doc** (premise, files, tests, gate line
  with the repro named, model it ran on).
- **The orchestrator merges a lane into the wave branch only after two-axis review passes** (A4),
  records the verdict in `reviews/`, **re-runs the full CI gate on the merged branch, then pushes.**
  Push after every lane merge — the remote is the backup and CI runs per merge so flakes surface early.
- **Open the draft PR against `develop` at the first push** (`writing-pull-requests` shape; body
  seeded under the initiative's `pull-requests/`, grown as lanes land). Brandon flips it to
  ready-for-review; that is what triggers CodeRabbit (`auto_review.drafts: false` [measured
  2026-09-10 on bp-portfolio, claude-skills]).
- **File-disjoint lanes may run in parallel up to the measured cap.** Claude Code: **≥ 3 concurrent**
  [measured 2026-09-10, three lanes in one message, floor not ceiling]. Any other client measures
  its own Agent tool before assuming concurrency and records the number in the MPD.
- **Agents run the full CI gate themselves** — every lane before handing back; the orchestrator on
  every merged tree before every push. CI on the PR is the arbiter for flakes.
- **Issues:** agents file findings freely via `writing-tickets`, labelled **`agent-filed`**, so
  Brandon can sweep them. Closing or relabelling existing issues is orchestrator-only and cited.
  Board intake stays Auto-add.

**The stop-list — stop and ask; everything else proceed, decide, record (MPD §6 + PR body):**

1. A premise conflict with the MPD or a ticket.
2. A scope decision the MPD does not cover.
3. Anything destructive or irreversible — data migrations against shared infra, deletions outside
   the repo, secrets, third-party writes (CMS, DNS, billing).
4. The CI gate still red after one fix round.

Non-blocking questions batch at the wave boundary. Rotation stays per wave with a packet.

**Addenda:** a defect found in review goes back to the **same lane, in its worktree, as a new
commit**, and is re-reviewed (scoped to the fix) before merge — never a fresh session, never the
orchestrator's own hands. Work already merged into the wave branch goes through a fresh ticket.

**The review loop (Brandon + the orchestrator)**

1. Brandon reads the draft PR, flips it to **ready for review**; CodeRabbit runs.
2. The orchestrator works the review end-to-end with `coderabbit-response`: verifies every finding,
   redispatches fixes to lanes (worktrees, review, merge, push as above), replies per thread with
   receipts, monitors re-reviews to clean. Brandon's review is the PR's final state, not the threads.
3. **Brandon alone merges, manually, in the GitHub UI** — wave PRs into `develop`, and the release
   PR `develop → master`, which the orchestrator may open as a draft with a changelog. Closing
   keywords fire on the default branch; the orchestrator moves issues to In Review at PR time.
4. `what-did-we-learn` runs at wave close; promoted lessons go to `_agent/learnings/`.

# Part C — Environment appendices (read only yours)

One file per client. Read the one you are in; the others describe machines you are not on.
Each states its own default mode, but the capability guard in B0 is what actually decides.

| You are | Read | Default mode |
| --- | --- | --- |
| Claude Code | [`clients/claude-code.md`](clients/claude-code.md) | autonomous |
| Cowork (Claude desktop, over the device bridge) | [`clients/cowork.md`](clients/cowork.md) | attended |
| Codex (ChatGPT desktop, local shell) | [`clients/codex.md`](clients/codex.md) | autonomous |
| OpenClaw (Camina) | [`clients/openclaw.md`](clients/openclaw.md) | attended |

**Where this file is not reachable at all, attended rules apply.** Where your client is not listed,
read the closest match, say that you did, and record what differed — a new client earns a file once
its guard items are measured, not before.

---

Amendment history: [`CHANGELOG.md`](CHANGELOG.md). This index and the contents of `clients/` are
checked against each other by `scripts/check-index.sh` in CI.
