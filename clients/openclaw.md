# OpenClaw (studio staff)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first, then
the target repository's instructions.** This appendix adds client mechanics only; it never overrides
Parts A–B, and a rule here that contradicts one there is the rule that is wrong. **Name this file
when you acknowledge your reading** — "read the agreements and
`clients/openclaw.md`" — so a skipped read is visible.

## Host and startup

- **Host:** Brandon's Mac mini, native macOS, user `brandonperfetti`, since 2026-10-21
  [measured 2026-10-27, #186: no Bubblewrap or AppArmor on PATH; Docker present, use unresolved].
  The former VPS and its sandbox are history; their recovery procedure is dormant (below).
- **Agent root** `~/dev/sansfaux`, set here: A6's upward walk from a role workspace finds its own
  `_agent/` or none. **Protected instruction-source root** `$AGENT_ROOT/agent-working-agreements/`:
  clean, on `master`, equal to `origin/master` after the post-release refresh, never a delivery
  checkout; its Git administration hosts isolated managed delivery worktrees. **Artifact store**
  `$AGENT_ROOT/_agent/`, the one store for every role and for Claude Code, named by absolute path;
  kept for the session, never switched or dual-written (A6). Each `~/.openclaw/workspace*/_agent/`
  and the former workspace checkout are rollback roots gaining only a pointer; never merged,
  mirrored, symlinked, moved, deleted or otherwise rewritten. A role on a changed pointer holds the
  store provisionally, runs the create/readback canary on its supported route and reports its exact
  instruction paths, hashes and store before acceptance. Paths are this host's.
- **If the pointer, Parts A–B or this file is unreachable,** stop the affected work with the
  missing instruction source recorded (B0); do not downgrade to B1.
- **Default mode: autonomous.** B0's guard is scored per exact checkout and delivery path, and
  that Camina coordinates several deliveries in one conversation widens nothing. An unavailable
  capability is evidence about that operation, not a switch of the delivery or team to B1: the
  team continues on its supported routes and stops at the first operation with no safe route,
  naming the capability and its restoration owner (B2 stop-list item 5). A role with no supported
  execution route stops only the affected operation, naming its restoration owner. Use approved
  fallback routes below; Brandon is never the command runner and alone merges base-branch PRs.
  [learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]
- **Resolve the active workspace and target checkout from live inventory**; do not assume every
  specialist shares main's working directory.

## Seats and routes

| A4 seat | OpenClaw role |
| --- | --- |
| Orchestrator | **Camina** (`main`), chief of staff, assigns the accountable lead; every staff member may orchestrate work in their domain |
| Delivery owner | **Judy** (`coder`), or the assigned delivery specialist |
| Independent reviewer | **Amos** (`reviewer`), or the assigned reviewer; where no reviewer can be seated, A4's bot-plus-merge rule applies and the PR body says so |
| Merge | **Brandon**, by hand, into `develop`, `master` or `main` |

The roster and route mechanics live in `~/.openclaw/workspace/docs/team-operating-model.md`.
Brandon may instruct any staff member directly; staff reconcile relevant operational context with
Camina and affected colleagues without reapproval. Initiative receipts share the store above.
Camina consolidates daily updates and weekly outcome/priority reviews; urgent material issues go
through promptly. Marketing may publish within approved strategy, channels and boundaries; website
code follows the Git ritual. B2 governs financial commitments and other scope boundaries.
Authorized execution proceeds without per-wave or per-batch approval in B2. Status is informational;
deliveries still carry independent review, verification and the owner's decision context.

- **Delegation:** canonical role IDs through the session's supported mechanism (`sessions_spawn`
  is one, not a requirement). RULE ZERO first; role, deliverable, mode, fence, model and effort follow.
- **Rotation (A4):** reported used context / capacity: checkpoint at 30%, prepare at 40%, rotate at
  a clean pause; at 60% take the next safe stop. Heuristics, not cliffs; unknown is not zero. Record
  session ID/time; verify successor root tools, provenance, receipt, acceptance and advancement per
  [`session-rotation.md`](../procedures/openclaw/session-rotation.md) before retiring the old session.
- **Models and routes:** Codex OAuth for thinking; the established Claude Code wrapper for coding.
  Leads choose model/effort within approved routes; respect wrapper pins rather than bypass them.
  On exhaustion, coding falls back from Claude to Codex OAuth, then to an approved API model within
  an existing funded allowance (B2). No automatic top-up; report an unavailable selector honestly.
- **Restoration owners (B2 stop-list item 5)** [decision 2026-10-27, Brandon, #194]: **Ashford** for
OpenClaw control-plane capability (dispatch allow-lists, tool exposure, routes, configuration, the
instruction-source pointer and its reachability); **Bull** for host and runtime capability; the
**delivery owner** for repository and worktree capability, the protected root's post-release refresh
included. Camina routes the stop and keeps continuity; a stop naming its owner needs no packet.

## Delivery topology

Autonomous specialists use B2's dedicated-worktree shape; attended lanes use B1's two shapes. For
this agreement repository, an amendment uses one isolated feature worktree off `develop`, never a
wave. A delivery worktree is created only through OpenClaw's managed worktree facility, from a
freshly fetched `develop` OID verified against `ls-remote`, bound explicitly to the Gateway
service's state directory, config and profile, placed per [lifecycle](../procedures/worktree-lifecycle.md),
outside `_agent/` and the protected root. Post-merge cleanup follows lifecycle checks; the root is
fast-forwarded to `origin/master` after each release. Commands, checks and the audit fields:
[`../procedures/openclaw/managed-worktrees.md`](../procedures/openclaw/managed-worktrees.md),
read at pickup; any overlap of those paths stops the delivery.

**Pickup audit.** Record the checkout and HEAD, author identity, `core.hooksPath` and hook
presence, the dry-run probe (or N/A), the full gate result, branch ownership, target protection,
and the worktree bindings the procedure lists. Reset is unmeasured; require a delivery audit.

## Evidence store

Use the selected store's `evidence/` and `analysis/` per A2 and A6; date-name artifacts and label
claims. The Gateway executable-check scratch root takes no scratch clone; where one goes on this
host, and whether specialists share that space, is **unmeasured** — measure and record.

## Dormant: the native sandbox breaker

The former host's one-strike Bubblewrap breaker and its Gateway routing table apply only when a
native shell returns this exact prelaunch signature before the target produces any output. This
host has none; the procedure is kept, not loaded:
[`../procedures/openclaw/native-sandbox-breaker.md`](../procedures/openclaw/native-sandbox-breaker.md).

```text
bwrap: No permissions to create a new namespace, likely because the kernel does not allow non-privileged user namespaces. On e.g. debian this can be enabled with 'sysctl kernel.unprivileged_userns_clone=1'.
```

## History

Measurements, source readings with their hashes, the route census, superseded claims and the
migration dispositions; none required reading: [`../history/openclaw.md`](../history/openclaw.md).
