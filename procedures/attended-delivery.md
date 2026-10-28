# Attended delivery

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27; "above" and "below" in it refer to the agreement section it implements.

**Trigger:** B0 selected attended mode for this delivery, or Brandon said so in the prompt.

**Owner:** The delivery owner stages and commits after Brandon's batch approval; Brandon pushes and
runs builds, suites and installs.

**Implements:** B1 — Attended mode.

**Stop:** Every commit and push waits for Brandon's approval of that batch.

---

Brandon is the verification step, on purpose.

**Feature work with no initiative** has no wave orchestrator, MPD or initiative folder, so the
session doing the work holds the orchestrator's duties, and the delivery owner's where no
specialist is assigned (A4, which lists both; this section carries their procedure); its review
verdicts and other
records go under the `_agent/` root's one-off folders (A6's tree), and its decisions and a failed
item 4 (B0) are recorded in its one-off review record under `_agent/reviews/`, which Brandon reads
at each batch approval, and copied into the PR body once a PR exists. A6 and
`clients/claude-code.md` point such work here, and in attended mode no PR exists when a batch is
reviewed (A7), so without this the pointers would land on nothing and the decisions would have no
place (Brandon, 2026-10-20).

- **You never commit or push without explicit approval, per batch, every single time.** Approval
  never carries to the next batch; no `--amend`; no routing around it with API/MCP writes or
  another client. Shape: write the change → show the **staged diff** → Brandon reviews in his IDE →
  he says commit → you commit. He pushes himself.
- **Dispatched lane sub-agents never commit, stage, push, or run any other git in the shared
  checkout.** A lane takes one of two shapes: it commits only in its own isolated clone and
  delivers an mbox / format-patch series in the initiative's `mboxes/`, or it edits its named files
  in the shared checkout and delivers them uncommitted, running no git there; either way it also
  delivers a **written report**. The delivery owner (A4) alone controls the shared checkout's git
  state — so too where it is a specialist dispatched as a sub-agent, which is not a lane: it stages
  uncommitted work, shows the staged diff, and commits after Brandon's batch approval; an mbox
  series it applies with `git am` only after that approval, since `git am` is the commit (below).
  Brandon pushes. This binds dispatched lanes only: a delivery owner that dispatches no lanes, and
  so counts as that lane (below), keeps its A4 duties in the shared checkout. **Lanes never write
  tickets; the orchestrator owns tickets and any live/browser verification.**
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
  orchestrator's own hands, except where the session dispatches no lanes: that session counts as
  that lane (A4), approved per batch as every attended fix is, so both modes say the same thing of
  a session with no lanes (Brandon, 2026-10-20). Until the PR that carries it merges, a small fix
  (A4) to work already committed is a new commit from that lane, approved per batch like any
  other; a fresh ticket is for real work (A4), and for work found after that PR has merged.
