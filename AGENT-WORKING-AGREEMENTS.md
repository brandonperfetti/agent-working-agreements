# Agent working agreements — Sans Faux

**Read this once, before a session's first delivery, dispatch, repository write or GitHub action:**
Parts A and B in full, then your [`clients/`](clients/) file, and no other. An answer from memory or
the bootstrap needs no read; a resumed step, a packet or a later turn pointing back here starts no
re-read. Confirm your tooling with `ListSkills` / `ListConnectors` or your client's equivalent, not
a list here. **Say what you read, naming the client file**, so a skipped read is visible.

This is the working agreement between Brandon and every agent he works with under the **Sans
Faux** studio — Claude Code, Cowork, Codex, OpenClaw, or anything else. It sits above each
project's own `AGENTS.md` / `CLAUDE.md`, which carry repo-specific conventions; read those too.
Project scope never percolates up into this file; working style never percolates down.

**How it is built.** Parts A and B are the rules every client is judged against, short and whole.
The mechanics live in [`procedures/`](procedures/), each behind the trigger named in the table at
the end of Part B, read when that trigger occurs. One client's specifics are in its appendix (Part
C). History and measurements live in [`CHANGELOG.md`](CHANGELOG.md) and `_agent/`, never here.
How this file changes is [`AGENTS.md`](AGENTS.md)'s to say: an agent that meets a rule's cost
records friction (A6) and amends nothing in that session. Paths are relative to the `sansfaux/`
root, the parent of this clone, where `_agent/` and `organize.sh` sit.

# Part A — Portable discipline (every client, every mode)

## A1. Where this applies

Every session Brandon runs, on any of his repositories, wherever the checkout lives: a one-off fix
and a multi-wave initiative alike. A repo's own `AGENTS.md` / `CLAUDE.md` adds project specifics and
never overrides Parts A–B. Neither does a skill: where a skill and this agreement disagree, the
agreement holds, and you say that you met the disagreement rather than choosing silently (Brandon,
2026-10-12). Initiatives (`_agent/initiatives/`) organise *orchestrated* work; they gate neither
these rules nor the mode. Skills come from the `brandonperfetti-skills` plugin; read the relevant
one before that kind of work: `orchestrate`, `deep-grill`, `handoff`, `code-review`,
`writing-tickets`, `writing-pull-requests`, `coderabbit-preflight`, `coderabbit-response`,
`what-did-we-learn`, `writing-for-agents`.

## A2. Evidence discipline

The rule that matters most, because breaking it costs more than any bug. **Label every claim:**

- **[measured]** — observed in a response, a log, a compiled artifact, a CI run.
- **[source]** — read from code or config. What it *says*, not what it has been observed to *do*.
- **[inference]** — a conclusion built on the above. State what would verify it.

Keep the three apart; never let a right measurement carry a wrong mechanism. A label names its
generalization boundary and is never inherited across revisions. A summary is not evidence; a
tool call that succeeded is not proof its whole output reached you. A reviewer's [inference] is
measured before it ships or stays labelled. Correct in place, marked and dated; never silently
swap. If you cannot verify something, say so: "I don't know" costs a sentence. **Evidence is
proportional to the claim:** a docs-only change needs its diff and a gate line; preserved
captures and hashes are for claims whose reversal would be costly (Brandon, 2026-10-27, #185).
Preserving and capturing: [`procedures/evidence-capture.md`](procedures/evidence-capture.md).

## A3. Do the work inside the turn

Don't narrate intent and stop. Do the work, then report **what is done**. Read-only investigation
you may announce; changes you make and show. Within the authorized objective, act, decide, record;
relevant read-only and scratch prerequisites are included. Direct owner instructions count wherever
received. Preserve explicit task holds, privacy and security constraints; reconcile affected staff.

**A status update is not a hand-back.** While safe, authorized work remains, keep going. A hand-back
is terminal when the requested outcome is complete, a named authority boundary needs Brandon, no
safe route exists for what remains and its restoration owner is named (B2 stop-list item 5), or only
Brandon's merge remains. It states what is complete, what remains, who acts next, and the one
decision Brandon has to make, if any (Brandon, 2026-10-27, #185).

## A4. Orchestration invariants

These hold in both modes; the `orchestrate` skill carries the loop, this file carries the law.

- **Three seats, kept distinct.** The **orchestrator** briefs and dispatches lanes, coordinates
  the tracker (A7), routes review and owns the hand-back. Qualified staff lead and delegate work
  in their domains. The **delivery owner** — assigned specialist, or orchestrator if none — owns
  the shared checkout's git state, integration, full gate, push, PR and review round; in attended
  mode Brandon pushes. The **independent reviewer** did not produce the work. One session may
  hold the first two seats, never its own review seat; only Brandon merges base branches (Part B).
  Where supported routes cannot seat a reviewer, routine reversible work may integrate and push
  before independent review (B2 exception); the PR bot and Brandon review before base merge.
  The PR discloses the missing reviewer route. Full duties, staff coordination and dispatch:
  [`procedures/orchestration-seats.md`](procedures/orchestration-seats.md).
- **The MPD is the spine.** Every initiative has a `MASTER-PRIORITY-DOCUMENT.md` born from an
  attended Genesis; its §0 records the mode. Leads advance approved work across waves and rotate
  at context-driven clean pauses; a packet starts with shipped-vs-open reconciliation.
- **Handoffs are files, not chat.** Kickoffs, addenda and lane reports live under the
  initiative's `handoffs/`; a pasted summary is a pointer plus highlights. They carry owner and
  governing constraints, never invent approval gates or reduce the authorized objective.
- **Lanes work their named files only, and run git only in their own worktree.** The shared
  checkout's git state is the delivery owner's alone. A lane that spots a defect in a file it
  touched reports it into the ledger rather than crossing its fence. [learnings: 2026-09-23
  sfs-wave-1 §1]
- **Leads choose models and effort per task** within approved routes and budgets, adapting to
  measured outcomes. Every dispatch records its choice or inherited setting; every lane report
  distinguishes requested, configured, inherited and backend-attested model claims.
- **RULE ZERO: a commit carries Brandon's author identity.** Every commit an agent makes on his
  behalf has the author email `brandon@brandonperfetti.com`, exactly; an outside contribution
  carries its author's own identity, and a PR whose commits carry Brandon's identity from another
  account is not merged until re-authored (Brandon, 2026-10-13). Attribution — a `Co-Authored-By`
  line, a footer, a session trailer — is allowed and never required; a client's default stands
  (Brandon, 2026-10-27). A provenance line on a PR or issue names the initiative, the role and the
  mode. RULE ZERO is line one of every dispatch prompt. The author check before every push, merge
  and presentation: [`procedures/rule-zero-check.md`](procedures/rule-zero-check.md).
- **Two-axis review before acceptance** (Standards + Spec, `code-review`), with A4's exception;
  fixes, riders and conflict resolutions included, no size exemption. The lane's own report is never
  the review; the verdict is recorded under `reviews/` and names the exact head SHA. A later fix
  gets a scoped review; the whole-branch verdict is renewed only when the fix materially stales it
  (Brandon, 2026-10-27, #193). **Close-out review before promotion**, over the whole initiative
  diff, is where the big finds happen; never skip it. [learnings: 2026-08-30 §9]
- **A review-bot finding is fixed before the merge when it is verified and does real harm.** One
  the code disproves is declined, with receipts, on its thread. One that holds but does no harm is
  fixed in the PR when small, noted when not worth a change, and ticketed when it is real work. A
  re-review round continues only while it surfaces a new, verified, harmful finding. Spending
  follows B2's financial boundary; an unfunded paid review never holds the push. The outcomes,
  routing and reply mechanics: [`procedures/review-findings.md`](procedures/review-findings.md).
- **Distrust the issue until you've read the code**; re-verify at pickup and record direction
  changes as marked, dated comments. **Tests ship with the change**, in the right place.

## A5. "Green" means the full CI gate — plus the ticket's own repro

The gate is defined in each project's own agent docs, never here. Green is every command that
project names, in order, plus every env export the local shell needs and the CI runner already
has; run it once at pickup. A build passing is not green. A gate line in a report names every
command and the ticket's reproduction re-run on the built tree. Shared-database tiers running in
parallel workers snapshot their baseline by id and unwind fixtures in `try/finally`; a local run
does not reliably catch an order-dependent flake, so CI is the arbiter.
Never reason about a running dev server as though your edit is already in it. **Never disable the
repo's hooks to commit**: no `--no-verify`, no re-pointed `core.hooksPath`.

## A6. Where things go

The `sansfaux/` root holds `_agent/`, project checkouts, `.worktrees/`, the agreement clone and
`organize.sh`. Worktree placement and retirement follow `procedures/worktree-lifecycle.md`.
An **on-fleet workspace** has `_agent/` above it; that directory's parent is the agent root.
Agent artifacts go under `_agent/`: initiative work in `initiatives/<project>-<slug>/`, one-off
work in `reviews/`, `evidence/`, `friction/`, `notes/` and `analysis/`, promoted lessons in
`learnings/`; never loose at either root, in a new top-level folder, or a clone/worktree in `_agent/`.
Each execution machine keeps receipts; select one store and share relevant pointers with staff.
Record friction when it happens, not to prove none did: `_agent/friction/YYYY-MM-DD-<repo>-<id>.md`
(`pr-<n>` or the first twelve head-SHA characters), opening with the delivery's full identifier
(Brandon, 2026-10-27, #185). Tree, index, friction fields and scratch-clone rules:
[`procedures/agent-workspace-layout.md`](procedures/agent-workspace-layout.md).

## A7. GitHub paths

`gh` is what the skills use and the primary surface. The GitHub MCP and Kody's
`@brandonperfetti/github` package read, orchestrate PRs and call the API; **neither authors
commits** — a commit comes from the local checkout, in both modes. On a create-then-link error, read
the current state before retrying. The tracker is GitHub Issues plus the user-level Projects board
(`users/brandonperfetti/projects/2`; intake is a repository's own `add-to-project` workflow, issues
only); "In Review" is a board status the orchestrator moves by hand. Credentials and call mechanics:
[`procedures/github-paths.md`](procedures/github-paths.md).

## A8. When you are unsure

Consult the **stop-list** in B2 in autonomous mode; otherwise decide, record and verify, on the PR
for repository work. In attended mode, ask. Never fill an evidence gap with a plausible story.

# Part B — Modes

## The ritual both modes serve

**Read this before writing, following, or amending any rule that touches a push, a branch or a
merge.** It is not a mode, a policy, or a thing to derive — it is what Brandon does, on **every**
repo, in his words. Rules below serve it; where a rule and this section disagree, the rule is wrong.

1. **Feature work branches off `develop`**, with nested feature, bugfix and lane branches as needed.
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
6. **Brandon merges both base-branch PRs, by hand in the host's UI.** The delivery owner merges
   reviewed lanes.
7. **Brandon tags on `master`**, where the repo publishes releases, and the tag fires the release
   workflow.
8. **The back-merge carries `master` home to `develop`** — a direct push by the workflow, which is
   why item 4's integration profile must keep accepting pushes.

**The test for any rule about git:** name the step above it applies to. A rule that cannot be
placed against a step is being derived from an abstraction, and that is exactly how the last three
went wrong.

## B0. Choosing the mode

Two modes. **The environment picks the mode; nobody asks Brandon at the start of a session.** Each
client's default is in Part C and its appendix. The agent verifies the capability guard silently at
pickup, scored for each checkout and repository delivery path, not for the session: a failed check
downgrades only that delivery to attended, with a one-line reason, never a question, except item 4,
which is recorded until protection exists. Brandon's word in the prompt wins over the default.

**Capability guard (every item that applies must hold):**

1. Native git on a real checkout, hooks firing: prove the `pre-push` hook with
   `git push --dry-run <remote> <branch>` from the checkout you will push from, or record that
   the repo installs none.
2. The full CI gate (A5) runs locally; run it once at pickup. This probe is always permitted.
3. Feature work lands on a branch of its own off `develop`, or a wave or lane branch, never on a
   base branch; scored when a commit would land.
4. The base branches are protected on GitHub by role: `develop` blocks force-pushes and deletions
   and carries no PR rule, because it is the head of the release PR; `master` requires a PR and
   the CI gate. A failed item 4 is recorded (MPD §0, the PR body, or the one-off review record).
5. Brandon has not overridden the mode to attended for this session.

Probe mechanics and measurements: [`procedures/pickup-guard.md`](procedures/pickup-guard.md).

**OpenClaw's exception stays here, because an appendix cannot override Parts A–B:** in OpenClaw
a failed or unavailable capability is evidence about the affected operation, not a B1 downgrade;
the team continues within its supported routes and stops at the first operation that has no safe
route, recording the missing capability and its restoration owner (B2 stop-list item 5). It does
not make Brandon the command runner. Where this file is not reachable at all, attended rules
apply; in OpenClaw, stop the affected work with the missing instruction source recorded. Any
client that passes the guard may run autonomous: the guard is the contract, not the client name.
[learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]

## B1. Attended mode

Brandon is the verification step, on purpose. **You never commit or push without his approval, per
batch, every time**; approval never carries to the next batch; no `--amend`; no routing around it
through API writes or another client. Shape: write the change → show the staged diff → Brandon
reviews → he says commit → you commit; he pushes. Brandon runs builds, suites and installs;
type-checks, greps, linters and read-only scripts are yours. Dispatched lanes run no git in the
shared checkout: they deliver an mbox series from an isolated clone, or uncommitted edits to their
named files. Two lanes by default; three is earned. Addenda go back to the same warm lane. Lane
shapes, the mbox apply block and the per-batch procedure:
[`procedures/attended-delivery.md`](procedures/attended-delivery.md).

## B2. Autonomous mode

Brandon's review moves to the pull request; the delivery owner owns the branch until then.

**Git contract.** Feature, bugfix, wave and lane branches descend from `develop`; lanes may branch
from the delivery branch and integrate reviewed work. Never push `master`, force-push, or push
feature work to `develop`. Release-cut work and release-PR review fixes push to `develop`, reviewed
on `develop → master`. Each lane has its own worktree, with hooks firing. The owner integrates lanes
after two-axis review (or A4's no-reviewer exception), re-runs the gate on the merged tree, runs
`coderabbit-preflight` when the push carries new work and the CLI is available, then pushes; a
lane merge that conflicts goes back to the lane. The ready-for-review PR opens against `develop`
at the first push; the delivery owner works the CodeRabbit round with `coderabbit-response`;
Brandon alone merges base PRs, by hand; `what-did-we-learn` runs at wave close. Addenda go back to the
same lane as a new commit, scoped-reviewed before merge. Agents file real-work findings as
`agent-filed` issues. The full contract, conflict recovery and the review loop:
[`procedures/autonomous-delivery.md`](procedures/autonomous-delivery.md).

**The stop-list — pause only the affected action and name its decision or restoration owner;
otherwise act, decide, record (MPD §6 and PR, or the task receipt when neither exists):**

1. An unresolved conflict in owner instructions or authorized objectives; current explicit owner
   direction settles older plans, tickets and handoffs. Reconcile the record and affected staff.
2. Expanding the authorized objective, strategy, channels or business commitments. Necessary
   prerequisites and ordinary nonfinancial execution, configuration and external writes within
   approved scope proceed with appropriate checks; uncertainty alone creates no approval gate.
3. Purchases or financial commitments/transactions without explicit approval or an approved budget
   covering the action. Read-only financial research, analysis and preparation proceed. Existing
   approved allowances may be used; budget increases, top-ups and unbudgeted commitments require approval.
4. A CI gate remains red after bounded evidence-led recovery reaches its declared budget — inside a
   merge-conflict resolution, this applies only to a red of the resolution's own, one absent from
   both sides' pre-merge gate records; unresolved recovery leaves the branch at its pre-merge tip
   (Git contract above). [learnings: 2026-10-18 openclaw-autonomy-and-recovery §2]
5. A required operation has no safe route on this client's supported routes. The stop names the
   exact missing capability and its **restoration owner** — the client file says who, and where it
   names none the owner is Brandon — and hands back per A3; work that does not depend on the
   operation continues, and Brandon is never made the command runner (Brandon, 2026-10-27, #194).

These boundaries apply with or without an initiative; an MPD or handoff is never extra authority.

## Triggers

| When | Read |
| --- | --- |
| You label a claim from irreproducible bytes, trust a probe, or quote a file | [`evidence-capture.md`](procedures/evidence-capture.md) |
| You dispatch a lane, hold more than one seat, or run an initiative | [`orchestration-seats.md`](procedures/orchestration-seats.md) |
| You are about to push, merge, present, or apply an mbox series | [`rule-zero-check.md`](procedures/rule-zero-check.md) |
| A delivery is ready for review, or a bot or reviewer finding needs an outcome | [`review-findings.md`](procedures/review-findings.md) |
| You create or retire a worktree | [`worktree-lifecycle.md`](procedures/worktree-lifecycle.md) |
| You work through T3 | [`t3-adapter.md`](procedures/t3-adapter.md) |
| You write any artifact, or need a scratch clone | [`agent-workspace-layout.md`](procedures/agent-workspace-layout.md) |
| You touch an issue, a PR, or the GitHub API | [`github-paths.md`](procedures/github-paths.md) |
| You pick up a delivery (first commit on a checkout, each repository) | [`pickup-guard.md`](procedures/pickup-guard.md) |
| The delivery is attended | [`attended-delivery.md`](procedures/attended-delivery.md) |
| The delivery is autonomous | [`autonomous-delivery.md`](procedures/autonomous-delivery.md) |

# Part C — Environment appendices (read only yours)

Read your client appendix; B0 decides the mode. In T3, use the actual provider appendix
plus `procedures/t3-adapter.md`; desktop-specific observations are not T3 guarantees.

| You are | Read | Default mode |
| --- | --- | --- |
| Claude Code | [`clients/claude-code.md`](clients/claude-code.md) | autonomous |
| Cowork (Claude desktop, over the device bridge) | [`clients/cowork.md`](clients/cowork.md) | attended |
| Codex (ChatGPT desktop, local shell) | [`clients/codex.md`](clients/codex.md) | autonomous |
| OpenClaw (Camina) | [`clients/openclaw.md`](clients/openclaw.md) | autonomous |

Where your client is not listed, read the closest match, say that you did, and record what differed
— a new client earns a file once its guard items are measured, not before.
