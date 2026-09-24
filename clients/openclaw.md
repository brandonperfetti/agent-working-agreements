# OpenClaw (Camina)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first, then
the target repository's instructions.** This appendix adds client mechanics only; it never overrides
Parts A–B, and a rule here that contradicts one there is the rule that is wrong. **Name this file
when you acknowledge your reading** — "read the agreements and
`clients/openclaw.md`" — so a skipped read is visible.

## Startup and mode

[measured 2026-09-22, issue #44] The workspace-root `AGENTS.md` routes Parts A–B and this appendix
to the canonical instruction-source clone, and the former workspace-root agreement path is a
non-authoritative stale-reader stub. That clone is the read-only instruction source, kept current
with released `master` per
[Instruction-source isolation and freshness](#instruction-source-isolation-and-freshness) below.
The stub stays in place, and the complete machine-local agreement it replaced stays preserved
intact for rollback, until the OpenClaw session on that host removes the stub once every
configured route has demonstrated the new pointer — a host-side step recorded in that host's
`_agent/` store, not a change this repository makes. The cutover steps this appendix carried until
this amendment remain readable at `29b6360:clients/openclaw.md`, lines 104–130. If the pointer,
Parts A–B, or this appendix is unreachable in the active session, downgrade to attended. After
changing the pointer, require a fresh-session observation before declaring it effective; do not
assume arbitrary external-file injection or automatic refresh.

**Default mode: attended.** The capability guard (B0) still decides, for the exact checkout and
delivery path. The accepted target is `OpenClaw → autonomous`, in a separate amendment supported
by fresh main- and specialist-session evidence. Any retained workspace-local layer adds client
mechanics only; it never copies or overrides Parts A–B. B2 still reserves merging to Brandon alone.

## Runtime and workspace

Resolve the active workspace and target checkout from live inventory; do not assume every specialist
shares main's CWD. When delegation is needed, use canonical role IDs and an explicit
`sessions_spawn` brief. Put A4's RULE ZERO first. Then include only the role, deliverable, mode,
file fence, role-based model tier, and OpenClaw selector that resolves that tier.

OpenClaw does not relax either mode's topology: attended sessions use B1's isolated-clone and mbox
shape; autonomous specialists use B2's dedicated-worktree shape. For this agreement repository,
the amendment exemption in its README means an autonomous amendment uses one isolated feature
worktree branched from `develop`, rather than a wave branch; do not invent a wave merely to obtain
isolation.

## Instruction-source isolation and freshness

**Cut every delivery worktree from the delivery checkout host, never from the instruction-source
clone.** [measured 2026-09-23, issue #24] Three delivery worktrees were created by commands that
explicitly selected the instruction-source clone with `git -C`; their presence violated that
clone's one-worktree contract even though the commands ran from the workspace root.

**After every `develop → master` merge, fetch and fast-forward the instruction-source clone before
any further work.** Run `git switch master`, then `git fetch origin`, then
`git merge --ff-only origin/master`; verify the tree is clean and `HEAD == origin/master`. The
next report names the exact SHA the clone serves.
[measured 2026-09-23] PR #41 merged at `b733b59982736285d078ee9f67209bcce2fea957` on
2026-09-22T20:18:10Z, but the clone remained six commits behind until the next day.

## Pickup guard and delivery audit

Record the checkout and HEAD, Git author identity, `core.hooksPath` and hook presence, an explicit
dry-run probe (or N/A when the repository installs no `pre-push` hook), the full gate result,
branch ownership, and target-protection audit. Parts A/B remain the authority for RULE ZERO,
no-force-push, and no-agent-merge; do not restate those rules here.

Attribution injection, arbitrary external injection, and exact reset/reload behavior remain
unmeasured. Require a delivery audit or controlled observation rather than assuming them. Record a
skill source/version when it materially affects delivery; skill precedence is not agreement
authority.

[measured 2026-09-20, current Gateway host] `claude-skills` could not pass guard item 2 because its
gate step 6 requires Ruby to validate `agents/openai.yaml`, and step 7 requires `zip` to rebuild and
compare the `.plugin` distribution. That measured session was therefore attended. OpenClaw may
deliver there, and [claude-skills #111](https://github.com/brandonperfetti/claude-skills/issues/111)
tracks a durable install and complete remeasurement; a future session's mode is still decided only
by rerunning B0 for its exact checkout and path. This does not block agreement adoption or the
pointer cutover.

## Evidence store

[measured 2026-09-22, current OpenClaw instance] This instance's per-machine `_agent` store resolves
to `/data/.openclaw/workspace/_agent/`; use its `evidence/` and `analysis/` subdirectories per A2
and A6. Date-name artifacts and label claims `[measured]`, `[source]`, or `[inference]`. Do not
assume that path is reachable from every OpenClaw workspace: use the active workspace's durable
`_agent/` store and record its concrete location with the capture.

## Migration dispositions

The complete machine-local agreement that preceded the canonical route carried rules that Parts
A–B now supersede. They are deliberately **not carried forward**, for these reasons:

- **A — autonomy:** the local autonomous default is superseded by B0's per-checkout mode decision
  and B2's Brandon-only merge boundary.
- **B — specialist commits:** shared-checkout delivery is not carried forward. Attended sessions
  use B1's isolated-clone and mbox shape; autonomous sessions use B2's dedicated-worktree shape.
- **C — builds and tests:** the local unconditional rule is superseded by the selected mode: B1 in
  attended sessions and B2 in autonomous sessions.
- **D — evidence:** the local requirement to retain raw capture for every measured claim is
  superseded by A2's classification. Only the OpenClaw evidence-store mapping above remains.
- **E — remote commit APIs:** the local permission is removed; A7's checkout-Git-only rule remains
  unchanged.
- **F — asking Brandon:** the local generic ask rule is superseded by A8 and B2's stop-list.

Staff consultation, Bubblewrap recovery, process restart behavior, and Claude wrapper behavior stay
in the fleet documents or wrappers that already own them. Do not copy them into this appendix or a
replacement local agreement.
