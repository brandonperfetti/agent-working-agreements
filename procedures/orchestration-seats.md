# Orchestration seats and dispatch

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27; "above" and "below" in it refer to the agreement section it implements.

**Trigger:** A session dispatches a lane or sub-agent, holds more than one seat, or runs an
initiative (an MPD exists or is being born).

**Owner:** The orchestrator.

**Implements:** A4 — the three seats, the MPD, handoffs, lane fences, model tiers.

**Stop:** Stop-list items 1 and 2 (B2) when a premise or scope conflict appears.

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
    only one there is — the review bot's round on the PR plus Brandon's merge review is the
    independent review for routine, reversible work, and the PR body says so. An empty seat holds
    no push (Brandon, 2026-10-27, #194).

  A session holding both the orchestrator and delivery-owner seats holds both sets of duties;
  neither seat makes it the reviewer of its own work, and neither merges a base branch — only
  Brandon does (Part B ritual, step 6). A client appendix may name who fills each seat there
  (Brandon, 2026-10-23, #173).
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
  (on the attended mbox path, its own isolated clone), and the shared checkout's git state is the
  delivery owner's alone — no lane runs git against it, changes its branch, or alters its git
  state — because that isolation is what makes concurrent lanes safe at all, and a lane that has
  run git in the shared checkout has left that isolation, whatever files it edited. B1's attended
  lane delivering uncommitted edits edits its named files in the shared checkout, runs no git
  there, and so crosses neither fence.
  A lane whose merge into the wave branch conflicts resolves it in its own worktree too (B2).
  [learnings: 2026-09-23 sfs-wave-1 §1]
- **Every lane report states the model it ran on, and how it knows.** Requested, inherited,
  configured and backend-attested are four different claims; a dispatched tier resolves to whatever
  the account serves, and config is not attestation. Say which you have. [learnings: 2026-08-30 §5]
- **Explicit model tier on every dispatch — never omitted, never the orchestrator's premium tier.**
  Tiers are named by *role* (workhorse for lanes, careful for verify/aggregate); each client file
  records its own selector for each tier, or that the mapping is unmeasured, and a client whose
  dispatch tool cannot select records that instead of pretending. This applies to skills that fan
  out their own sub-agents. Route by role per `agent-workspace/references/subagent-model-routing.md`.
  [learnings: 2026-08-30 §5]
