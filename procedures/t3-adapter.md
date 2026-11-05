# T3 provider adapter

**Trigger:** Working through T3 (local, delegated or linked-environment tasks), including each
delegate's model and effort.

**Owner:** The task lead; each delivery owner verifies its execution route and checkout.

**Implements:** A2 evidence, A3 continuation, A4 model and effort, A6 receipts and B0
capability-based mode selection.

**Stop:** Stop only an operation with no supported authorized route; name its restoration owner
under B2. Provider login or a successful fixture does not qualify every repository or remote route.

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong.

Read Parts A–B, the selected profile and the actual provider adapter: canonically
`clients/codex.md` or `clients/claude-code.md`; in a single-file scaffold, the corresponding
filled-in client appendix. Do not require files that scaffold does not ship. Use this adapter for
T3 mechanics and remeasure desktop-specific capability claims. Triggered procedures still apply,
including evidence capture and artifact placement when writing receipts.

1. Identify the execution environment, host, provider and repository before using paths. Keep
   each host's receipts in its selected store; use existing approved authentication and allowances.
2. Bind repository work to its T3 project. Use native isolated delegation from a repo-bound
   parent; an umbrella/non-Git parent may not select another local project for its child.
   Treat rejection as a scoped route limit and continue independent work. Placement and retirement
   follow [worktree lifecycle](worktree-lifecycle.md); inspect the created path and branch.
3. Discover skills through the actual provider surface: Codex may expose a catalog and file reads;
   Claude may expose a native Skill invocation. Record the source/version actually accessed.
   A direct-file fallback can demonstrate behavior without proving native discovery. Released
   installations and unreleased candidates are separate qualification targets.
4. Collect terminal results after completion wakes, read the receipt and advance the next action.
   For a waiting remote task, inspect supported remote activity when the parent status is
   incomplete; a null pending-approval field alone does not prove no approval is waiting.
   Surface a real approval request to Brandon through the supported UI. Preserve existing grants;
   do not self-approve, duplicate the task or revive an approval belonging to a cancelled run.
5. Persist a disk handoff for continuation. Inherited-history pickup does not prove blind pickup.
   Use supported cancellation for an owned run and check its terminal state; reconnect is distinct
   from resumed execution, desktop quit, sleep or reboot recovery. Keep unqualified routes and
   their available fallbacks explicit without blocking unrelated qualified local work.
6. **Route each delegated task.** Apply the model-and-effort rule of
   [orchestration seats](orchestration-seats.md), setting both through the host's current
   delegation options, whose schemas stay the host's. Start from the defaults below; a default
   row is reason enough. Depart where difficulty, uncertainty, consequence, verification or likely
   rework calls for it, saying why in the existing task result; escalate for a concrete risk or
   failed approach, not by habit. An owner-pinned or owner-named setting wins; routing asks no
   per-dispatch approval. A rejected route is a scoped limit (step 2): continue on a supported
   approved route, never a paid or API one, and draw no model conclusion from it.
7. **Delegate where it pays.** Do trivial work, or work whose delegation costs more than it
   saves, directly. Overlap independent fenced lanes while dependencies and host resources
   allow; shared integration and heavy runtime stay with the delivery owner. Batch and trial
   checkpoints are internal: carry the original objective onward under A3 and A4.
8. **Treat headroom as a task-fit signal.** Read the provider's normal usage display where
   exposed; an unexposed reading stays unknown. Cached and processed tokens, displayed or
   API-estimated cost and subscription allowance are different quantities, and percentages from
   different providers do not add or compare. Between equally fit routes, prefer the one with
   visible headroom. Headroom never supports a savings claim, a purchase, API fallback or passing
   an exhausted limit (B2 item 3).

**Starting defaults** — provisional, adjusted here as evidence accrues; steps 6–8 are the stable
rule. Names are the live T3 selectors when adopted; which rows have pilot use is recorded in
[#237](https://github.com/brandonperfetti/agent-working-agreements/issues/237). Equal effort names
do not imply equal compute.

| Task | Start | Raise to high for |
| --- | --- | --- |
| Lead and coordination | Sol 6.1 medium | consequential dependency or API choice, ambiguous acceptance, hard integration |
| Implementation from a clear brief | Claude Opus 5.5 medium | difficult bug, risky refactor, edge-case-heavy work |
| Routine bounded edits, small migrations | Claude Sonnet 5.5 medium | a demonstrated need |
| Narrow inventory, triage, extraction | deterministic tools first; Haiku 5.5 low or medium, or Luna low (untested) | — |
| Independent Standards + Spec review | high, preferring a family other than the producer's (Sol 6.1 for Claude-authored work) | — |
| Unresolved architecture, hard diagnosis | a bounded Astra high consultation, applied in the delivery lane | — |

Final architecture, security and acceptance review use the review row. Rows are starting points
for step 6, and model diversity fits the required review seats rather than adding reviewers.

The preliminary qualification and remaining probes are tracked in
[AWA #217](https://github.com/brandonperfetti/agent-working-agreements/issues/217). This adapter
records usable mechanics; it is not an exclusive-client readiness declaration or a new appendix.
