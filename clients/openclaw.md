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
The stub stays in place until the OpenClaw session on that host removes it in a reviewed cleanup,
once every configured route has demonstrated the new pointer — a host-side step recorded in that
host's `_agent/` store, not a change this repository makes. The complete machine-local agreement
the stub replaced stays preserved intact for rollback. The cutover steps this appendix carried until
the 2026-09-24 amendment for issue #54 remain readable at `29b6360:clients/openclaw.md`, lines
104–130. If the pointer, Parts A–B, or this appendix is unreachable in the active session,
downgrade to attended. After
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

## Bubblewrap circuit breaker

[source, issue #58] Camina's measured specification, transcribed; a Mac session cannot observe
OpenClaw's sandbox. The signature is a **prelaunch** failure: Bubblewrap cannot create a namespace
inside the Docker/AppArmor boundary, so the target program never starts. [source, issue #58, from
the OpenClaw system expert] OpenClaw has no supported sticky per-session failover —
`tools.exec.host: auto` does not reclassify a failed Bubblewrap launch, loop detection does not
reroute execution, and a fixed `host: gateway` must be configured in advance — so the breaker is a
rule the session keeps:

1. One confirmed namespace/Bubblewrap/AppArmor prelaunch failure marks the native sandbox
   unavailable for the remainder of that session.
2. Do not retry the same boundary through another native shell, elevation mode, absolute path, or
   native patch call.
3. Route the bounded operation deterministically, by the table below.
4. Preserve AppArmor/seccomp, the task's authority, and its original read/write constraints.
5. If no bounded fallback exists, stop and report the missing capability instead of improvising
   an overwrite.

**The signature, and what rule 1's "confirmed" means.** [source, issue #67, comment of 2026-09-27
relaying Camina's follow-ups of 2026-09-26; measured there, on the OpenClaw Gateway host] The exact
prelaunch error string:

```text
bwrap: No permissions to create a new namespace, likely because the kernel does not allow non-privileged user namespaces. On e.g. debian this can be enabled with 'sysctl kernel.unprivileged_userns_clone=1'.
```

[source, Camina's, same comment] The `sysctl` remedy the message names is **not** a route:
enabling unprivileged user namespaces would weaken the sandbox, which #58's "Not" list, carried in
this section's closing paragraph, rules out. A failure is **confirmed** when the native boundary
returns the Bubblewrap/namespace/AppArmor prelaunch signature **before** the requested target
produces any output or side effect: the target never started. A failure after the target starts,
shown by output, exit behaviour or side effects that belong to the target, is a target failure and
does not trip the breaker.

| Operation | Route |
| --- | --- |
| read-only shell and Git inspection | Gateway execution of a command that writes nothing outside what the task may write; the bound is the command's (below) |
| GitHub work | GitHub tools or `gh` through Gateway |
| repository edits | an exact unified patch, `git apply --check`, `git apply`, then diff/readback verification through Gateway |
| non-repository workspace or memory writes | the appropriate OpenClaw-owned write tool |
| reviewer filesystem failure | supply the exact diff and receipts to the same reviewer and label the verdict evidence-bounded |

A7 still governs the GitHub row: the GitHub MCP's write tools never author commits, so a commit
comes from a checkout on every route.

**Row 1's bound is the command's, not Gateway's.** Inspection qualifies only when the command
writes nothing outside what the task may write. Gateway's `workdir` supplies no bound — Camina's
inference, on the measured host, in the paragraph below that begins "**Test runs deliberately have
no route.**", where its measurement is cited. [source, Camina's, issue #88, 2026-10-01] A linked
worktree's index resolves to `.git/worktrees/<id>/index` in the main repository, outside the
worktree directory, and nothing in the breaker's contract (rule 4) implicitly expands a
worktree-only write grant to that administrative directory. [inference, Camina's, same comment]
An index refresh there is therefore outside a worktree-only grant unless the session's original
grant expressly includes that exact path. [measured 2026-09-30, issue #88, git 2.46.0, scratch
repos] In a linked worktree with a stat-stale tracked file, `git status` and `git diff` rewrote
that index; `git --no-optional-locks status` and `git log` did not, and `--no-optional-locks` did
not stop `git diff`'s write. Camina's eligible set for row 1: [measured, Camina's label, issue #88;
its controls ran `git --no-optional-locks status` and `git log --oneline`]
`git --no-optional-locks status --porcelain …` and `git log` without patch or textconv output;
[source, Camina's, issue #88] ref and object reads such as `git rev-parse`, `git for-each-ref`,
`git cat-file` and `git ls-tree`;
`git -c diff.autoRefreshIndex=false diff --no-ext-diff --no-textconv …`; and plumbing comparisons
such as `git diff-files`, `git diff-index --cached` and `git diff-tree`, with external diff and
textconv disabled where applicable. [inference/recommendation, Camina's, issue #88] Row 1 permits
only commands whose complete execution, configured helpers, fsmonitor and lazy fetching included,
has been established not to write outside authorized paths, and default-denies ordinary
worktree-facing `git diff`, default `git status`, `git describe --dirty` and explicit index
refreshes; an inspection for which that cannot be established has no Gateway route.
Her answer is bounded to the current OpenClaw contract and measured host; a session whose original
grant expressly includes the exact linked-worktree administrative path needs a fresh determination.

**Test runs deliberately have no route.** Once rule 1 has marked the native sandbox unavailable,
no row above routes a test run of any repository's suite, and none is to be improvised from them:
a test run executes project code and can write caches, snapshots or build output, so it is not
read-only inspection. [source, issue #67, measured there 2026-09-30] Camina's measurement: the live
Gateway execution surface takes a host command and a `workdir` and exposes no filesystem-root or
path allowlist, mount namespace, UID remap or read-only-filesystem control; in a positive-control
canary from a probe worktree, `printf 'escape\n' > ../outside/escape.txt` succeeded. [inference,
Camina's, issue #67, from that measurement] `workdir` selects the starting directory and does not
confine writes on the measured host, so no command and `workdir` pair, however narrowly scoped,
keeps a test run inside the session's worktree as rule 4 requires, and rule 5 applies.
**Attended:** Brandon runs the suite (B1); give him the exact command. **Autonomous:** stop and
report that the required command has no bounded route, naming it exactly; do not run it through
Gateway. This repository's `./scripts/check-index.sh && ./scripts/check-index.test.sh` is an
example of such a command, not the rule.

**A confirmed strike does not change the session's mode:** it marks the native sandbox unavailable
(rule 1) and leaves the mode as B0 selected it, so the session carries on by bounded routes and
stops at the first required operation that has none — attended, giving Brandon the exact command;
autonomous, stopping and reporting it — and only Brandon's explicit override changes the mode after
pickup, while a strike during the pickup guard that stops the gate being demonstrated is an
ordinary B0 attended start (Brandon's decision of 2026-10-01, on Camina's recommendation; see
issue #94).

The breaker is **not** a global switch to Gateway execution, a weakening of sandbox controls, or a
generic rule for failures that occur after the target program starts. [source, issue #58,
measured there 2026-09-23] The agent-working-agreements delivery cycle retried native shell and
patch paths after the same prelaunch error; the bounded Gateway equivalents reached the target.

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

**Remove a delivery worktree and its local branch once its feature PR has merged into `develop`.**
Run it from the delivery checkout host, never the instruction-source clone: `git fetch origin`
— if the fetch fails, stop, and retain and report the worktree and branch — then
`git merge-base --is-ancestor <branch> origin/develop`. Exit 0 is the only permission, and
not by itself enough: a protected base worktree (the delivery checkout host itself, and any other
the host reserves, such as its release-review worktree), a dirty worktree, and a branch that is
not an ancestor of `origin/develop` are all retained and reported. On exit 0 and outside those
exclusions, `git worktree remove <path>` without `--force`; then, only if that removal succeeded,
`git branch -d <branch>`.
Any refusal from either command is left as it is and reported, never overridden.
[measured 2026-09-23, issue #57] The delivery host went from 13 to 16 registered worktrees in one
delivery cycle; the dry-run and live cleanup the ticket records then removed 14 merged worktrees
and their branches without forcing a dirty removal, leaving the protected delivery host plus a
release-review worktree.

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
deliver there, and claude-skills #111
tracks a durable install and complete remeasurement; a future session's mode is still decided only
by rerunning B0 for its exact checkout and path. It did not block agreement adoption or the
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

Staff consultation, process restart behavior, Claude wrapper behavior, and Bubblewrap recovery's
fuller five-step pattern (`docs/team-operating-model.md` on the OpenClaw host) stay in the fleet
documents or wrappers that already own them; only the one-strike circuit breaker above, the part
that applies in-session, lives here. Do not copy them into this appendix or a replacement local
agreement.
