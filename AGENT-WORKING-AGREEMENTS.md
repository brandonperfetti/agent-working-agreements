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
and never overrides Parts A–B. **Neither does a skill: where a skill's instructions and Parts A–B
disagree, the agreement holds, and you say that you met the disagreement** rather than choosing
silently — a disagreement never reported is never fixed at its source (Brandon, 2026-10-12).
Initiatives (`_agent/initiatives/`) are how *orchestrated* work is
organised, not a gate on whether these rules apply, nor on the mode: B0 picks the mode, MPD or not.
Skills come from the `brandonperfetti-skills` plugin (mirror of `mattpocock/skills` plus
Brandon's own); read the relevant skill *before* that kind of work — `orchestrate`, `deep-grill`,
`handoff`, `code-review`, `writing-tickets`, `writing-pull-requests`, `coderabbit-preflight`,
`coderabbit-response`, `what-did-we-learn`, `writing-for-agents`.

## A2. Evidence discipline

The rule that matters most, because breaking it costs more than any bug. **Label every claim:**

- **[measured]** — observed in a response, a log, a compiled artifact, a CI run.
- **[source]** — read from code or config. What it *says*, not what it has been observed to *do*.
- **[inference]** — a conclusion built on the above. State what would verify it.

Keep the three apart; never let a right measurement carry a wrong mechanism. Rules:

- **Preserve [measured] evidence — classified first.** Irreproducible bytes are preserved in
  `evidence/`, named for what they prove, before summarizing. Retrievable evidence gets a stable
  locator, SHA-256, and relevant excerpt — or the search terms plus absence; do not copy a
  retrievable artifact merely to prove a claim. A summary is not evidence.
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
- **Lanes keep their git in their own worktree.** The file fence says which files a lane edits;
  this says which working tree a lane may run git in. A lane runs git only in its own worktree
  (on the attended mbox path, its own isolated clone), and the orchestrator's checkout is the
  orchestrator's alone — no lane runs git against it, changes its branch, or alters its git
  state — because that isolation is what makes concurrent lanes safe at all, and a lane that has
  run git in the shared checkout has left that isolation, whatever files it edited. B1's attended
  delivery of uncommitted edits to named files runs no git there and crosses neither fence.
  A lane whose merge into the wave branch conflicts resolves it in its own worktree too (B2).
  [learnings: 2026-09-23 sfs-wave-1 §1]
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
- **RULE ZERO: no attribution, on any commit, PR body, reply or comment.** Agents add no
  `Co-Authored-By`, no session trailer, no generated-by footer — a commit carries Brandon's author
  identity and ends with its own content. That identity rule governs commits made by agents
  working on Brandon's behalf inside this fleet: a contribution from anyone else carries its
  author's own identity, and a pull request whose commits carry Brandon's identity from another
  account is not merged until re-authored, because a pull request from a fork needs no write
  access and the merge is then the only guard (Brandon, 2026-10-13). What an agent posts under his
  name on a PR thread, a PR
  or an issue carries no credit line either; a provenance line is not one: it names the initiative,
  the role (e.g. wave orchestrator, lane) and the mode the filing agent worked in — never the client
  or the product — and says who read the evidence, which A2 wants.
  RULE ZERO overrides any environment default; your client
  file records what is known of yours. It is **line one of every dispatch prompt**, and the commits
  a delivery adds and its PR body are grepped regardless — for `Co-Authored-By` plus whatever the
  client file names — a match is a send-back. **The author is read beside the grep**, because the
  grep checks text and the rule
  names an identity: `git log --format='%ae' <base>..HEAD` on the branch, or the address in each
  patch's `From:` line for an mbox series — before approval on the attended mbox path, before merge
  on the autonomous path. Both compare the **author email alone** against
  `brandon@brandonperfetti.com`, exactly. The name is not compared: it varies by machine and clone
  (a repository of Brandon's holds three spellings of it on its integration branch, all at that
  email [measured 2026-09-26]). A commit at any other email is a send-back like a trailer match:
  reject or regenerate, since `git am` preserves
  the patch author (B1). **Added** means not on `origin/develop` or `origin/master`,
  fetched and read
  **before** the delivery is pushed or merged — a lane or wave branch, the branch of feature work
  with no initiative, or release-cut work pushed straight to `develop` (B2), each push its own
  delivery — so a lane's own earlier commits still count. Forward-only: commits that already
  carry a trailer stay as they are, and a match on an inherited one goes in the delivery's review
  record, never back to the lane.
  [learnings: 2026-09-06 wave-6 §7; 2026-09-04 wave-5 §6]
  **A trailer never established that a commit came through a reviewed lane.** The two-axis review
  record under `reviews/`, the gate evidence under `evidence/` and the PR trail do; report those.
- **Two-axis review (Standards + Spec, `code-review` skill) on every delivery before acceptance —
  riders, review-fix lanes and merge-conflict resolutions (scoped to the resolution, B2)
  included, no size exemption.** The lane's own report is never the review; the verdict is
  recorded under the initiative's `reviews/`.
  [learnings: 2026-09-06 wave-6 §5; 2026-09-04 wave-5 §7]
  **An orchestrator's hand-back is never the review of its wave either:** the hand-back names the
  claims to re-measure, and before a merge a reader outside the wave reads them against the
  repository, because the party that produced the work does not attest to it, and rotation changes
  who orchestrates the next wave without adding a reader before the merge. That reader's seat is
  set by the situation — a session supervising dispatched agents — not by the client, because most
  sessions own their work, as they should, and Genesis builds the MPD with Brandon by design. In
  attended mode Brandon's per-batch review is already that reader (Brandon, 2026-10-12).
- **Distrust the issue until you've read the code.** Issues predate the tree; re-verify at pickup,
  read the comments, record direction changes as marked, dated comments.
- **Tests ship with the change**, in the right place.
- **A review-bot finding, the CodeRabbit CLI's or the PR bot's, is fixed before the merge when it
  is verified and does real harm:** wrong behaviour, a result reported as clean that was not, a
  leak, a signal or write to something not identified, a held push or a hang. One the code
  disproves is declined. One that holds but does no such harm has three outcomes, by size.
  **Small, it is fixed in the PR:** the fix stays inside the files the PR already changes and
  needs no new decision (a clause, a word, a test pin); it goes back to the lane that owns the
  file, with a two-axis review scoped to the fix (above), and its thread gets "Fixed in `<sha>`".
  **Not worth a change, it is noted:** recorded in the review record with a one-line reason, which
  its thread gets too, and no ticket. **Real work, it becomes a ticket** — outside the PR's files,
  a new decision, or more than a small fix — with a short reply on its thread where it has one.
  The same three outcomes govern a reviewer's notes, not only the bot's findings, because a ticket
  for a one-clause fix costs a later wave what a commit in the PR would have done, and a backlog
  that takes every harmless finding refills as fast as waves clear it (Brandon, 2026-10-18).
  The verdict rests on verification, not on the bot's severity label, and the same
  threshold holds on release PRs, which CodeRabbit keeps reviewing (Brandon, 2026-09-29).
  **Declines are argued per thread, where there is one, with cited receipts** (file, test name,
  documented ops order); "Fixed in `<sha>`" on accepted findings.
  Bare declines teach the bot nothing.
  [learnings: 2026-09-06 wave-6 §6] **When a re-raise names a vector the decline missed, concede
  the vector and re-argue the trade on purpose and cost** — never by repeating evidence the bot has
  already weighed. [learnings: 2026-09-12 wave-8 §22] **No agent spends usage credits:** a billing
  prompt holds the paid review, never the push (Brandon, 2026-09-29).
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

The `sansfaux/` root holds `_agent/`, project checkouts, the lane worktrees a client file places
beside them, the `agent-working-agreements/` clone, and `organize.sh` — nothing else.

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
store mid-session. Client appendices resolve discovery and client limits.

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

**Friction.** For a delivery with no initiative, define its canonical delivery identifier before
writing its close record: use its GitHub pull-request URL when it has one; otherwise use its
checkout's `origin` URL plus the delivery's full `HEAD` SHA; otherwise use its full branch ref plus
that full SHA. The agent closing that delivery owns and writes its one-off close record; this does
not assign any broader no-initiative delivery role. In `_agent/friction/`, that record is exactly
`YYYY-MM-DD-<repository-slug>--repo-<repository-hash>--pr-<number>.md` for the pull-request form,
or `YYYY-MM-DD-<repository-slug>--repo-<repository-hash>--branch-<branch-slug>--ref-<branch-hash>--<full-head-sha>.md`
otherwise. `repository-identity` is the exact remote host and path before normalization, or the
exact checkout basename when there is no remote; `repository-slug` is that identity lowercased with
non-alphanumerics replaced by `-`. `repository-hash` is the full lowercase hexadecimal SHA-256
digest of the UTF-8 bytes of `repository-identity`. `branch-slug` is the same normalization of the
full branch ref, and `branch-hash` is the full lowercase hexadecimal SHA-256 digest of the UTF-8
bytes of that exact full branch ref. The hashes are mandatory stable suffixes, so distinct inputs
that normalize to the same slug still produce distinct filenames. The record starts with the exact
canonical identifier, so the filename maps to that delivery without ambiguity. Initiative
deliveries keep their initiative `friction/` location and existing semantics.

At delivery close — and at each wave close for an initiative — record either `friction: none` or
one or more dated entries in that delivery's `friction/` location. An entry names the delivery and
affected workflow step; the observed behaviour, with A2 labels and evidence
locators where available; the cost or impact (human interruption, retries, rework, or elapsed time
only when measured); the workaround, if any; whether it is first-seen or recurring and how to
reproduce it; and the proposed durable fix, or `unknown`.

Friction is an observed workflow cost or obstacle while following the agreement. It is not
evidence: A2 evidence supports a labelled claim and keeps its own locator or preserved capture. It
is not a review finding: a review finding is a concern from the independent review that still needs
verification and its verdict belongs in `reviews/`. It is not a learning: a learning is a resolved,
cited durable lesson promoted through `what-did-we-learn`. It is not a GitHub issue: an issue is
repository-owned tracker work filed only after triage and deduplication. A friction record may link
to any of them without replacing its record.

Preserve the raw record. Correct it in place under A2: quote the old text, mark and date the
correction, and distinguish what was observed from what was concluded. The promotion path is raw
friction record → triage and deduplication → recurring, reproducible, repository-owned GitHub
issue → resolved durable learning, rule, skill or software improvement. Capture is non-blocking:
it creates no approval checkpoint and stops no delivery unless the underlying condition
independently reaches an existing gate failure, authority boundary, or B2 stop-list item.

**Clones.** No clone of a repository, and no worktree, is written under `_agent/`. A scratch clone
lives in the client's own scratch directory, outside `_agent/` — your client file names that
directory, or records that it is unmeasured. What persists is the evidence: the commands run and
their output, under `evidence/`, with the remote and the commit needed to rebuild the clone.
Before the remote or a command's output is written under `evidence/`, the secret comes out, by the
remote's form, because a remote can carry credentials and the plain ways of reading one print them
verbatim: an http(s) URL loses its whole userinfo, since a token can stand where a user name does
and the two cannot be told apart; an ssh remote keeps its user name and loses any password; a
remote of any other form loses its whole userinfo; and any token is stripped from captured output.
That is how this sits beside the `experiments/` line's "never /tmp": a transcript has to survive the
session, a clone can be made again. The reason: a clone under `_agent/` is a nested repository in a
store meant to replicate, a second copy of a project's source with its licence, and the one thing
in `_agent/` that is rebuildable. This moves no lane worktree: where those live is unchanged and is
each client file's to name. (Brandon, 2026-10-12)

## A7. GitHub paths

- **`gh` CLI** — what the skills use (issues, sub-issues, PRs). Primary for skill-driven work.
- **GitHub MCP** — the read/access layer and PR orchestration. **Its write tools (`push_files`,
  `create_or_update_file`) never author commits** — they bypass the local clone in both modes.
- **Kody's `@brandonperfetti/github` package** — the GitHub REST/GraphQL API for issues, PRs,
  checks, PR status and merge previews, for any client with Kody connected. **It never authors
  commits**, in both modes, for the GitHub MCP's reason: it bypasses the local clone. **Its
  `confirm: true` is per call and is not B1's per-batch approval** — it is the agent confirming
  its own call, not Brandon reviewing a batch — so in attended mode a Kody write is one of the
  API writes B1 allows no routing around. **The token it uses is fine-grained and scoped per
  repository, with one `secretName` per organisation**, because a call's reach is its token's, so
  the owner a call names matters as much as its `confirm: true`; **every call passes
  `secretName`**, because the package otherwise defaults to an OAuth lane, which may not be
  connected and, where it is, would leave two credentials able to serve one call with nothing
  showing which did. Where Kody is not connected, use `gh` or the GitHub MCP. How a client names
  the Kody tools is its client file's to record (Brandon, 2026-10-12).
- **On any create-then-link error, read the current state before retrying** — the create may have
  landed. GitHub's sub-issue cap errors *after* creating and parenting; blind retries burn issue
  numbers and mint duplicates. [learnings: 2026-09-12 wave-8 §3]
- **Tracker** = GitHub Issues + the user-level Projects board (`users/brandonperfetti/projects/2`,
  Auto-add intake). "In Review" is a board Status the orchestrator moves by hand — at PR time in
  autonomous mode (B2's review loop), and at commit time in attended mode, where no PR exists when
  a delivery is reviewed.

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
silently at pickup**, scored **for each checkout and repository delivery path**, not for the session
as a whole: outside the specific OpenClaw rule below, a failed check downgrades **only that
delivery** to attended where the item calls for it — item 4 records a failure instead, until
protection exists — with a one-line reason ("attended: the CI gate does not run locally"), never a
question, so a session working two repositories is not moved to attended by a check that failed in
one. The reason is in the items: items 1, 2 and 4
are already scored that way — item 1's hook probe per checkout, items 2 and 4 per repository — so
item 1's hook probe failing says nothing of a delivery from a checkout that probe does not cover —
another clone, or another worktree where `core.hooksPath` is relative — and item 2 or 4 failing for
one repository says nothing of a delivery to another repository. Brandon can override in either
direction by saying so in the prompt, and that wins over the default. An initiative's MPD §0
*records* the mode its waves run in (so a rotation packet carries it); it does not gate it, and work
with no MPD has its mode picked the same way.

**Capability guard (every item that applies must hold):**

1. Native git on a real checkout — git executes hooks (so whatever the repo installs, e.g. husky,
   fires on commit); `rm`, worktrees, and `git branch -d` work. [measured 2026-09-10, Claude Code
   on claude-skills] **Prove the hooks exist in the checkout you will push from:**
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
   that piece of work (B2), with no other work on it; never on a base branch. Scored when a commit
   would land, not by the checkout's current branch: a session that commits none does not fail it.
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
   the branch. **Until protection exists on a repo, a failed item 4 is *recorded* in MPD §0, not a
   downgrade.**
   **What protection cannot enforce here.** Nothing in the repo settings stops an agent pushing
   straight to `develop`, or merging its own PR into `master` once the gate is green `[inference —
   untested, since testing it means merging into a protected branch]`. **Feature work never lands
   on a base branch, and only Brandon merges** are therefore rules of this agreement, not repo settings.
   Making either mechanical needs a separate agent identity (machine user or App token), and that
   is decided not now (Brandon, 2026-10-12): the two stay rules of this agreement because one
   account has write access to each repository, every change reaches `master` through a pull
   request Brandon merges by hand, the CI gate is a required check on `master`, and feature work
   goes through its branch (B2) and a PR into `develop`; a separate identity costs a secret, a
   token-switch step in every client and a new PR author, a cost not paid while those conditions
   hold. It reopens on a second account with write access to a repository this agreement governs,
   or on one measured breach of either rule, with a GitHub App as the recommended shape.
5. Brandon has not overridden the mode to attended for this session.

By environment: **Claude Code → autonomous** (1 passes by construction but for its hook probe,
which is per checkout; 2 is a per-repo probe run at
pickup, never assumed; 3 before **every** feature commit, not only the first; **4 must be checked,
never assumed** — on 2026-09-10 neither `develop` nor `master` on claude-skills carried protection
or rulesets [measured]); **Cowork over the device bridge → attended** (fails 1 and usually 2);
**ChatGPT desktop Codex with a local shell → autonomous** (1 measured 2026-09-13 but for its hook
probe, which is per checkout and unmeasured there; 4 readable there
but still checked per repo; see `clients/codex.md`); **OpenClaw → autonomous.**
In OpenClaw, a failed or unavailable capability
check is evidence about the affected operation, not a B1 downgrade: the autonomous team continues
within its supported routes and stops at the first operation that has no safe route, recording the
exact missing capability. It does not make Brandon the command runner. **Where this file is not
reachable at all, attended rules apply, except in OpenClaw: stop the affected work with the missing
instruction-source capability recorded; do not automatically convert it to B1.** Any client that
passes the guard may run autonomous — the
guard is the contract, not the client name.
[learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]

## B1. Attended mode

Brandon is the verification step, on purpose.

- **You never commit or push without explicit approval, per batch, every single time.** Approval
  never carries to the next batch; no `--amend`; no routing around it with API/MCP writes or
  another client. Shape: write the change → show the **staged diff** → Brandon reviews in his IDE →
  he says commit → you commit. He pushes himself.
- **Sub-agents never commit, stage, or push in the shared checkout.** Their deliverable is a
  **written report** plus either uncommitted code or an mbox / format-patch series in the
  initiative's `mboxes/` (committed only in the lane's own isolated clone, applied by the
  orchestrator with `git am` after review). **Sub-agents never write tickets, and never touch git
  in the shared checkout; the orchestrator owns tickets, staging, commits (post-approval), and
  any live/browser verification.**
  Review compounds; a report can be argued with, a commit has to be reverted; a wrong premise gets
  faithfully implemented unless a human reads first.
- **Brandon runs all builds, test suites, and installs.** Tell him exactly what to run. Type-checks,
  greps, linters, read-only scripts are yours to run. Lanes may run browser-mode test tiers where
  the sandbox allows. [learnings: 2026-09-04 wave-5 §5]
- **Apply-block shape for mboxes:** one `&&`-chained line — `M=<mboxes dir>`, `git am "$M/<file>.mbox"`
  per mbox, then the CI gate; no `cd`, no guard functions, never a push. `git am` *is* the commit
  step for this shape: it runs the applypatch hooks, not `pre-commit`/`commit-msg` [source: git-am
  docs], so husky's lint-staged never fires — the gate after apply is mandatory, and approval comes
  before the apply, not after. `git am` also preserves each patch's author as the commit author, so
  A4's author check runs on the series' `From:` lines before approval, not on the branch after.
  **A rider on a series already applied is a delta commit, never an
  amend** — an amended mbox cannot `git am` onto the sha it rewrites; read the branch state before
  dispatching the rider and say which shape it is. [learnings: 2026-09-12 wave-8 §21]
- **Lane cap: two lanes by default; three is earned**, not assumed — the bound is Brandon's review
  bandwidth, not agent capacity. (Whether lanes run concurrently is an environment fact — see your
  appendix.)
- **Addenda go back to the same warm lane**, never to a fresh session and never done by the
  orchestrator's own hands. Until the PR that carries it merges, a small fix (A4) to work already
  committed is a new commit from that lane, approved per batch like any other; a fresh ticket is
  for real work (A4), and for work found after that PR has merged.

## B2. Autonomous mode

Brandon's review moves to the pull request. The orchestrator owns the branch until then.

**Git contract**

- The wave orchestrator cuts **one branch per wave off `develop`** (`<initiative>/wave-<n>`), and
  that is the **only** branch an agent pushes to land an initiative's **feature** work. Feature
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
  In **attended** mode the shape is unchanged: the lane delivers an mbox, Brandon applies and pushes.
- **Each lane works in its own git worktree on a branch off the wave branch** and commits there
  with the repo's hooks firing (this replaces mboxes + `git am`). Lane commits keep RULE ZERO
  (A4); the lane still writes its **on-disk handoff doc** (premise, files, tests, gate line
  with the repro named, model it ran on).
- **The orchestrator merges a lane into the wave branch only after two-axis review passes** (A4),
  records the verdict in `reviews/`, **re-runs the full CI gate on the merged branch, runs
  `coderabbit-preflight` when the push carries new work (below) and the CodeRabbit CLI is
  available to that client, then pushes.**
  Push after every lane merge — the remote is the backup and CI runs per merge so flakes surface early.
- **A lane merge that conflicts goes back to the lane.** The lane merges the wave
  branch into its own branch in its own worktree — a merge commit, never a rebase, which would
  rewrite commits it has already reported — resolves there and re-runs the gate; the resolution
  gets a scoped review, as an addendum's fix does; the orchestrator's merge is clean against the tip
  the lane merged, and a wave branch that has moved since is the same rule again — a merge that
  conflicts goes back to the lane. Only
  where the lane is no longer available does the orchestrator resolve, and its resolution gets a
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
    change to that side's work. The orchestrator's merged-tree gate before the push is unchanged.
- **The preflight runs once before each push that carries new work** — a lane landing, a release
  cut — and never before a push that only answers review findings, which the PR's own review
  covers; there is no re-run. An unavailable CLI never holds a push and never downgrades the mode:
  the round is recorded as not run, and the PR round is the review. The skill carries the rules of
  a run, the checks that decide whether the CLI is available among them.
- **Open the ready-for-review PR against `develop` at the first push. CodeRabbit runs on that ready
  PR, and the orchestrator completes the round before hand-back.** The PR uses the
  `writing-pull-requests` shape; its body is seeded under the initiative's `pull-requests/` and
  grown as lanes land.
- **File-disjoint lanes may run in parallel up to the measured cap.** Claude Code: **≥ 3 concurrent**
  [measured 2026-09-10, three lanes in one message, floor not ceiling]. Any other client measures
  its own Agent tool before assuming concurrency and records the number in the MPD.
- **Agents run the full CI gate themselves** — every lane before handing back; the orchestrator on
  every merged tree before every push. CI on the PR is the arbiter for flakes.
- **Issues:** agents file the findings that are real work (A4) freely via `writing-tickets`,
  labelled **`agent-filed`**, so Brandon can sweep them. Closing or relabelling existing issues is
  orchestrator-only and cited. Board intake stays Auto-add.

**The stop-list — stop and ask; everything else proceed, decide, record (MPD §6 + PR body):**

1. A premise conflict with the MPD or a ticket.
2. A scope decision the MPD does not cover.
3. Anything destructive or irreversible — data migrations against shared infra, deletions outside
   the repo, secrets, third-party writes (CMS, DNS, billing).
   A billing prompt holds the paid review, never the push (A4).
4. A CI gate remains red after bounded evidence-led recovery reaches its declared budget — inside a
   merge-conflict resolution, this applies only to a red of the resolution's own, one absent from
   both sides' pre-merge gate records; unresolved recovery leaves the branch at its pre-merge tip
   (Git contract above). [learnings: 2026-10-18 openclaw-autonomy-and-recovery §2]

Non-blocking questions batch at the wave boundary. Rotation stays per wave with a packet.

**Addenda:** a defect found in review goes back to the **same lane, in its worktree, as a new
commit**, and is re-reviewed (scoped to the fix) before merge — never a fresh session, never the
orchestrator's own hands. While the wave PR is open, a small fix (A4) to work already merged into
the wave branch rides it, through the owning lane, a scoped review and a push; a fresh ticket is
for real work (A4), and for work found after the wave PR has merged.
A lane merge that conflicts goes back to the lane the same way (Git contract above).

**The review loop (Brandon + the orchestrator)**

1. **Before each push that carries new work, the orchestrator runs `coderabbit-preflight`** where the
   CodeRabbit CLI is available (Git contract above).
2. **The agent opens the feature PR ready for review; CodeRabbit runs; the orchestrator completes
   the round before hand-back.**
3. The orchestrator works the review end-to-end with `coderabbit-response`: verifies every finding,
   redispatches the fixes A4 calls for to lanes (worktrees, review, merge, push as
   above), replies per thread with receipts, monitors re-reviews to clean. Brandon's review is the
   PR's final state, not the threads.
4. **Brandon alone merges, manually, in the GitHub UI** — wave PRs into `develop`, and the release
   PR `develop → master`, which the orchestrator may open as a draft with a changelog. Closing
   keywords fire on the default branch; the orchestrator moves issues to In Review at PR time.
5. `what-did-we-learn` runs at wave close; promoted lessons go to `_agent/learnings/`. The
   wave-close record also meets A6's friction-close requirement.

# Part C — Environment appendices (read only yours)

One file per client. Read the one you are in; the others describe machines you are not on.
Each states its own default mode, but the capability guard in B0 is what actually decides.

| You are | Read | Default mode |
| --- | --- | --- |
| Claude Code | [`clients/claude-code.md`](clients/claude-code.md) | autonomous |
| Cowork (Claude desktop, over the device bridge) | [`clients/cowork.md`](clients/cowork.md) | attended |
| Codex (ChatGPT desktop, local shell) | [`clients/codex.md`](clients/codex.md) | autonomous |
| OpenClaw (Camina) | [`clients/openclaw.md`](clients/openclaw.md) | autonomous |

**OpenClaw's mapping and exception follow B0's autonomous-default rule.**
[learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]
**Where this file is not reachable at all, attended rules apply. For OpenClaw, instead stop the
affected work with the missing instruction-source capability recorded; do not automatically convert
it to B1.** [learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]
Where your client is not listed, read the closest match, say that you did, and record what differed
— a new client earns a file once its guard items are measured, not before.

---

Amendment history: [`CHANGELOG.md`](CHANGELOG.md). This index and the contents of `clients/` are
checked against each other by `scripts/check-index.sh` in CI.
