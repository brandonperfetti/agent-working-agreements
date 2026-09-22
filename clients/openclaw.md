# OpenClaw (Camina)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first, then
the target repository's instructions.** This appendix adds client mechanics only; it never overrides
Parts A–B, and a rule here that contradicts one there is the rule that is wrong. **Name this file
when you acknowledge your reading** — "read the agreements and
`clients/openclaw.md`" — so a skipped read is visible.

## Startup and mode

[source 2026-09-20] The workspace-root `AGENTS.md` currently points to the full machine-local
agreement at `/data/.openclaw/workspace/AGENT-WORKING-AGREEMENTS.md`; it does not yet point to this
checkout or appendix. The migration target is one startup pointer naming the canonical agreement and
this appendix. If that pointer, Parts A/B, or this appendix is unreachable in the active session,
downgrade to attended. After installing or changing the pointer, require a fresh-session observation
before declaring it effective; do not assume arbitrary external-file injection or automatic refresh.

**Mode:** B0 maps OpenClaw to attended and decides the mode for the exact checkout and delivery
path. [measured 2026-09-20, current OpenClaw session] The workspace boots the full machine-local
agreement at `/data/.openclaw/workspace/AGENT-WORKING-AGREEMENTS.md`. That agreement remains
authoritative for any session still booted from it. Once a fresh or reset session loads the
canonical pointer and acknowledges Parts A–B plus this appendix, those canonical sources are
authoritative in that session. Any retained workspace-local layer adds client mechanics only; it
never copies or overrides Parts A–B. B2 still reserves merging to Brandon alone.

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

[source 2026-09-20] Workspace-root `AGENTS.md` still points to a complete machine-local agreement.
At cutover, preserve the referenced complete machine-local agreement intact for rollback; do not
edit it into a second canonical layer.
The following rules are deliberately **not carried forward** from it:

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

## Quiet cutover contract

Merging this amendment does **not** change OpenClaw startup. Brandon schedules the cutover window;
no agent starts it merely because the PR merged.

1. **Quiesce and inventory.** Stop new dispatches. Confirm there is no in-flight delivery,
   uncommitted work, or branch operation. Record active main and specialist sessions, their
   checkouts, branches, and instruction source.
2. **Preserve rollback.** Hash the complete machine-local agreement, move it intact to a dated
   `_agent/quarantine/` path, and record the inverse move. Delete nothing.
3. **Install the pointer.** Replace the old agreement path with an explicitly **not authoritative**
   “Moved — the agent working agreements are a repo now” stub, used only to expose stale readers.
   Update workspace-root `AGENTS.md` to point to the canonical Parts A–B and this appendix.
4. **Verify every route.** Start fresh or reset main and every configured specialist. Each must name
   Parts A–B and `clients/openclaw.md`, then run B0's guard for its exact checkout and delivery path.
   Drain every session still holding the old instructions.
5. **Observe before cleanup.** Keep the stub until every configured route has demonstrated the new
   pointer. A later reviewed cleanup removes the stub and this Quiet cutover contract together, and
   condenses Migration dispositions to the enduring explanation of why the superseded local rules
   are absent. If verification fails, stop or drain every affected session, restore the preserved
   agreement and previous pointer using the recorded inverse operation, start fresh sessions, and
   verify that every route loads the restored agreement before dispatches resume.

The worktree topology above is adopted before this window and verified independently, so the window
changes only instruction pickup. The post-cutover B0 default amendment is a separate PR supported by
fresh main- and specialist-session evidence. Its accepted target is `OpenClaw → autonomous`, with
the same per-session, checkout-specific guard still deciding the effective mode.
