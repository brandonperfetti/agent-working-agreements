# Orchestration seats and dispatch

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong.

**Trigger:** A session dispatches a lane or sub-agent, holds more than one seat, or runs an
initiative (an MPD exists or is being born).

**Owner:** The orchestrator.

**Implements:** A4 — the three seats, the MPD, handoffs, lane fences, models and effort.

**Stop:** Stop-list items 1 and 2 (B2): unresolved conflicts in owner instructions or authorized
objectives, or expansion of the authorized scope.

---

- **Three seats, kept distinct.** This list is the authoritative, complete list of the delivery
  owner's duties, but for the one-off close record A6 assigns to the agent closing a delivery with
  no initiative, and sets the core boundary of each seat; other bullets of A4 assign supplemental
  portable orchestration and review duties (the rotation packet, the reading outside the wave), and
  B1 and B2 carry procedure only, not further duties.
  - The **orchestrator** coordinates and synthesizes: it briefs, fences, dispatches and
    redispatches lanes, extends a lane's fence where a fix needs it (below), holds tracker
    coordination (issues, closing and relabelling, board Status and moving issues to In Review,
    A7), owns any attended live/browser verification (B1), routes review evidence, and writes the
    decision-ready hand-back.
  - The **delivery owner** is the qualified specialist assigned to the delivery, or the
    orchestrator when no specialist is assigned, and alone controls the shared checkout's git
    state, so too when it is a specialist dispatched as a sub-agent; a lane delivering uncommitted
    edits may still edit its named files there (B1). It cuts the delivery branch; in attended mode
    (B1) it stages a batch and shows the staged diff, commits after Brandon's batch approval, and
    applies the reviewed mbox series that lanes delivered from their isolated clones with `git am`
    only after that approval, since `git am` is the commit; Brandon pushes. In autonomous mode (B2)
    it integrates reviewed lane work and records each verdict in `reviews/`, runs the full CI gate
    on the merged tree, owns conflict-resolution mechanics,
    pushes, runs the routine `coderabbit-preflight` and `coderabbit-response` mechanics, opens and
    updates the feature pull request and completes its review round, and may draft the
    `develop → master` release pull request.
  - The **independent reviewer** is a separate seat, independent of whoever produced the work
    under review, delivery owner included; it runs the two-axis review below. Where the client's
    supported routes cannot seat one — the dispatch tool refuses the role, or the session is the
    only one there is — A4 permits routine reversible work to integrate and push before independent
    review. The PR discloses the missing route; its bot round plus Brandon's review occur before
    base merge. This exception changes timing, not reviewer independence or the full gate.

  A session holding both the orchestrator and delivery-owner seats holds both sets of duties;
  neither seat makes it the reviewer of its own work, and neither merges a base branch — only
  Brandon does (Part B ritual, step 6). A client appendix may name who fills each seat there
  (Brandon, 2026-10-23, #173).
- **The MPD is the spine.** The owner conversation establishes the objective and decisions;
  `MASTER-PRIORITY-DOCUMENT.md` records them and §0's mode. The lead advances the next justified
  wave within that objective, reconciles outcomes and reprioritizes at wave close. Wave close is
  not an approval gate or mandatory session rotation. Rotate at a clean pause when context calls
  for it, using the client's supported route and the packet below.
- **Staff own outcomes in their domains.** The assigned lead may delegate bounded work and
  choose the next in-scope action. Direct owner instructions count without another agent's
  reapproval. Reconcile changed priorities, ownership, dependencies and blockers with affected
  colleagues; the owner is not the relay. Share relevant receipts and decisions, preserving
  privacy and task-specific holds.
- **Handoffs are files, not chat.** Save kickoffs, addenda and lane reports under `handoffs/`.
  A rotation packet begins with shipped-vs-open reconciliation and names decisions, owners,
  receipts, governing constraints and the next authorized action. Carry existing authority;
  a packet cannot invent approval gates or narrow the owner's objective. A pasted summary is a
  pointer plus highlights. Verify successor capability, receipt, acceptance and actual advancement
  before retiring the predecessor; preserve any still-active lanes, worktrees and unique decisions.
- **Lanes work their named files only.** Independent work runs in parallel within available
  resources and file ownership; shared manifests, generated files, applications and other
  contention points are serialized. A lane that spots a defect in a
  file it touched **reports it into the ledger — it is our finding** — rather than crossing its
  fence or smoothing it over. [learnings: 2026-09-06 wave-6 §4]
- **Lanes keep their git in their own worktree.** The file fence says which files a lane edits;
  this says which working tree a lane may run git in. A lane runs git only in its own worktree
  (on the attended mbox path, its own isolated clone), and the shared checkout's git state is the
  delivery owner's alone — no lane runs git against it, changes its branch, or alters its git
  state — because that isolation is what makes concurrent lanes safe at all, and a lane that has
  run git in the shared checkout has left that isolation, whatever files it edited. B1's attended
  lane delivering uncommitted edits edits its named files in the shared checkout, runs no git
  there, and so crosses neither fence.
  A lane whose merge into the wave branch conflicts resolves it in its own worktree too (B2).
  [learnings: 2026-09-23 sfs-wave-1 §1]
- **Every lane report states the model it ran on, and how it knows.** Requested, inherited,
  configured and backend-attested are four different claims. The task's chosen model and effort
  are requests, not evidence of what the account served. State which evidence you have.
  [learnings: 2026-08-30 §5]
- **Choose model and effort for the task.** The lead uses approved routes and allowances, adjusting
  to observed quality, cost and elapsed time. A dispatch names the chosen model/effort and reason,
  or records inheritance or a route's pinned setting. A client whose tool cannot select says so;
  it never claims a requested selector proves the served model. Approved subscription routes may
  fall back automatically; paid routes require an already-approved funded allowance (B2).
  Apply the same rule when a skill fans out helpers; client files carry route mechanics.
