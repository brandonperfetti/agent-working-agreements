# OpenClaw (studio staff)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B, then
[`../profiles/sansfaux.md`](../profiles/sansfaux.md), then this file — all three, even when your
pointer names only the core and this file — then the target repository's instructions.** This
appendix adds client mechanics only; it never overrides Parts A–B, and a rule here that contradicts
one there is the rule that is wrong. **Name all three when you acknowledge your reading** — "read
the agreements, `profiles/sansfaux.md` and `clients/openclaw.md`".

## Host and startup

- **Host:** Brandon's Mac mini, native macOS, user `brandonperfetti` (#186).
- **Agent root** `~/dev/sansfaux`. **Protected instruction-source root**
  `$AGENT_ROOT/agent-working-agreements/`: clean, on `master`, equal to `origin/master` after each
  release's refresh, never a delivery checkout. **Artifact store** `$AGENT_ROOT/_agent/`, the one
  store for every role and for Claude Code, named by absolute path (A6). Each
  `~/.openclaw/workspace*/_agent/` and the former workspace checkout are rollback roots: leave them
  as they are.
- **If the pointer, the core, the profile or this file is unreachable,** stop the affected work
  with the missing instruction source recorded (B0); do not downgrade to B1.
- **Default mode: autonomous.** B0's guard is scored per checkout and delivery path. An unavailable
  capability limits that operation, not the delivery or the team: continue on supported routes and
  stop only where no safe route remains, naming the capability and its restoration owner (B2 item
  5). Brandon is never the command runner; he merges what no active route covers.
  [learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]
- **Resolve the active workspace and target checkout from live inventory**; specialists do not all
  share main's working directory.

## Seats and routes

| A4 seat | OpenClaw role |
| --- | --- |
| Orchestrator | **Camina** (`main`), chief of staff, assigns the accountable lead; every staff member may orchestrate work in their domain |
| Delivery owner | **Judy** (`coder`), or the assigned delivery specialist |
| Independent reviewer | **Amos** (`reviewer`), or the assigned reviewer; where no reviewer can be seated, A4's bot-plus-merge rule applies and the PR body says so |
| Merge | **Brandon**, by hand, into `master` or `main`, and into `develop` except a merge the profile's delegated route covers: that one is the delivery owner's, in an OpenClaw-runtime turn's Code Mode `exec`, a claude-cli turn's `mcp__openclaw__exec` or a Codex-harness turn's `gateway_exec`, once `gh pr merge --help`, run alone through the merge's own tool right before that merge, is refused with a reason carrying `awa-guard-git:` ([`../hooks/openclaw/`](../hooks/openclaw/README.md)). Printed help text, or a missing or ambiguous refusal, stops the merge and hands it to Brandon; a refusal never carries across a handoff or a tool, runtime or config change. A Codex-harness turn's native shell is never the merge tool, though it still does the turn's ordinary git work. A delivery owner whose Codex-harness turn has no `gateway_exec` may make the merge step from one of those three turns, through its named tool, which runs its own canary, re-reads the PR to confirm its head is the accepted head and its base is `develop`, and meets every route condition; where none is available, the canary fails or a route condition cannot be met, the merge goes to Brandon |

The roster and route mechanics live in `~/.openclaw/workspace/docs/team-operating-model.md`.
Brandon may instruct any staff member directly; staff bring Camina and affected colleagues up to
date without asking again. Marketing may publish within approved strategy, channels and boundaries;
website code follows the Git ritual. Authorized work proceeds without per-wave approval; B2 governs
spending and scope.

- **Delegation:** give one accountable owner, by canonical role ID, the outcome, mode, fence, model
  and effort, through the session's supported mechanism.
- **Continuity (A4):** keep the conversation Brandon is using, with its checkpoint on disk; open a
  new topic or recover one per [continuity](../procedures/openclaw/session-rotation.md).
- **Models and routes:** choose a task-fit model and effort for each conversation and worker,
  through normal sessions and subagents, Anthropic models included; use Claude Code when it helps.
  Respect owner pins and the approved subscription, account and tool boundaries; B2 governs
  spending.
- **Restoration owners (B2 stop-list item 5)** (#194): **Ashford** for OpenClaw control-plane
  capability (dispatch, tool exposure, routes, configuration, the instruction-source pointer);
  **Bull** for host and runtime; the **delivery owner** for repository and worktree capability,
  the protected root's refresh included. Camina routes the stop and keeps continuity.

## Delivery topology

An agreement amendment uses one feature worktree off `develop`, never a wave. Create delivery
worktrees only through OpenClaw's managed facility, from a captured `develop` OID, bound to the
Gateway service's context, outside `_agent/` and the protected root; refresh the root after each
release and clean up after merge without force. Read
[`managed-worktrees.md`](../procedures/openclaw/managed-worktrees.md) at pickup; it carries the
commands and the pickup audit.

## Evidence store

Use the store's `evidence/` and `analysis/` per A2 and A6; date-name artifacts and label material
findings. Where a scratch clone goes on this host is **unmeasured**: measure and record it.

## History

Measurements, source readings, route census, superseded claims and migration dispositions, in the
shared client archive; none required: [`../history/openclaw.md#openclaw`](../history/openclaw.md#openclaw).
