# OpenClaw (Camina)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first, then
the target repository's instructions.** This appendix adds client mechanics only; it never overrides
Parts A–B, and a rule here that contradicts one there is the rule that is wrong. **Name this file
when you acknowledge your reading** — "read the agreements and
`clients/openclaw.md`" — so a skipped read is visible.

## Host and startup

- **Host:** Brandon's Mac mini, native macOS, user `brandonperfetti`, since 2026-10-21
  [measured 2026-10-27, #186: no Bubblewrap or AppArmor on PATH; Docker present, use unresolved].
  The former VPS and its sandbox are history; their recovery procedure is dormant (below).
- **Agent root** `~/dev/sansfaux`. **Protected instruction-source root**
  `$AGENT_ROOT/agent-working-agreements/`: clean, on `master`, equal to `origin/master` after the
  post-release refresh, never a delivery checkout; its Git administration hosts isolated managed
  delivery worktrees. **Artifact store** `$AGENT_ROOT/_agent/`, selected at session start and kept
  for the session (A6); a role started from a changed pointer selects it provisionally, runs the
  create/readback canary through its supported route, and reports the exact instruction paths
  before the pointer counts as accepted for that role.
- **If the pointer, Parts A–B or this file is unreachable,** stop the affected work with the
  missing instruction source recorded (B0); do not downgrade to B1.
- **Default mode: autonomous.** B0's guard is scored per exact checkout and delivery path, and
  that Camina coordinates several deliveries in one conversation widens nothing. An unavailable
  capability is evidence about that operation: the team continues on its supported routes and
  stops at the first operation with no safe route, naming the capability and its restoration owner
  (B2 stop-list item 5). Brandon is never the command runner, and only Brandon merges.
  [learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]

## Seats and routes

| A4 seat | OpenClaw role |
| --- | --- |
| Orchestrator | **Camina** (`main`): briefs, dispatches, routes, synthesizes the hand-back; runs no delivery mechanics while a specialist is assigned |
| Delivery owner | **Judy** (`coder`), or the assigned delivery specialist |
| Independent reviewer | **Amos** (`reviewer`), or the assigned reviewer; where no reviewer can be seated, A4's bot-plus-merge rule applies and the PR body says so |
| Merge | **Brandon**, by hand, into `develop`, `master` or `main` |

[decision 2026-10-23, Brandon, #173]. The staff model — the roster, routing, the Claude wrapper
contract, consultation patterns — is `~/.openclaw/workspace/docs/team-operating-model.md`; this
file does not restate it. Within an authorized B2 delivery, commits, pushes, PR creation and
updates, review responses and integration of reviewed lane work are routine and need no per-batch
approval; B2 stop-list actions and merges are not delegated with the lane. Routine reversible work
presents its A4 verdict, diff and gate evidence in the smallest sufficient packet.

- **Delegation:** canonical role IDs through the session's supported mechanism (`sessions_spawn`
  is one, not a requirement). RULE ZERO first; then role, deliverable, mode, file fence and tier.
- **Model selectors (A4 tiers):** the shared Claude wrapper pins its own model and rejects a
  caller selector, so a dispatch names its role tier, passes no selector, and records the model
  the wrapper pins. Which selector resolves each tier on a non-wrapper route is **unmeasured**;
  the 2026-10-24 per-role route census is in [`../history/openclaw.md`](../history/openclaw.md).
- **Restoration owners (B2 stop-list item 5)** [decision 2026-10-27, Brandon, #194]: **Ashford** for
OpenClaw control-plane capability (dispatch allow-lists, tool exposure, routes, configuration, the
instruction-source pointer and its reachability); **Bull** for host and runtime capability; the
**delivery owner** for repository and worktree capability, the protected root's post-release refresh
included. Camina routes the stop and keeps continuity; a stop that names its owner is complete and
needs no packet.

## Delivery topology

Autonomous specialists use B2's dedicated-worktree shape; attended lanes use B1's two shapes. For
this agreement repository, an amendment uses one isolated feature worktree off `develop`, never a
wave. A delivery worktree is created only through OpenClaw's managed worktree facility, from a
freshly fetched `develop` OID verified against `ls-remote`, bound explicitly to the Gateway
service's state directory, config and profile, and placed outside both `_agent/` and the
protected root; it is removed losslessly once its PR has merged, and the protected root is
fast-forwarded to `origin/master` after each release. Commands, checks and the audit fields:
[`../procedures/openclaw/managed-worktrees.md`](../procedures/openclaw/managed-worktrees.md),
read at pickup. OpenClaw's own background cleanup is a separate hazard: commit or back up work
you need before relying on a managed worktree's persistence.

**Pickup audit.** Record the checkout and HEAD, author identity, `core.hooksPath` and hook
presence, the dry-run probe (or N/A), the full gate result, branch ownership, target protection,
and the worktree bindings the procedure lists. Attribution injection and reset behaviour remain
unmeasured: require a delivery audit rather than assuming.

## Evidence store

Use the selected store's `evidence/` and `analysis/` per A2 and A6; date-name artifacts and label
claims. A scratch clone goes in the client's own scratch space, never under `_agent/`; where that
space is on this host, and whether specialists share it, is **unmeasured** — measure and record.

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
migration dispositions: [`../history/openclaw.md`](../history/openclaw.md). Nothing there is
startup reading.
