# OpenClaw (Camina)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first, then
the target repository's instructions.** This appendix adds client mechanics only; it never overrides
Parts A–B, and a rule here that contradicts one there is the rule that is wrong. **Name this file
when you acknowledge your reading** — "read the agreements and
`clients/openclaw.md`" — so a skipped read is visible.

## Startup and mode

**Configured native agent root.** On Brandon's native macOS OpenClaw installation, the configured
agent root is `~/dev/sansfaux`, currently resolving for the live account to
`/Users/brandonperfetti/dev/sansfaux`. Its authoritative protected instruction-source root working
tree is `$AGENT_ROOT/agent-working-agreements/`; its artifact store is `$AGENT_ROOT/_agent/`. That
working tree is protected from delivery mutations and kept current with released `master` by the
release refresh in
[Instruction-source isolation and freshness](#instruction-source-isolation-and-freshness) below.

After a workspace's reviewed `AGENTS.md` pointer is replaced, the first approved acceptance session
for that role selects `$AGENT_ROOT/_agent/` at startup on a provisional basis so it can execute the
ordinary create/readback canary. This startup selection is independent of the later acceptance
verdict and remains fixed for that session under A6. Declare the mapping operationally accepted for
the role only after the session reports the exact instruction path and hashes, names that selected
store, and passes the canary through its supported tool route. A partial pointer application affects
only fresh sessions started from the changed subset. Existing sessions remain bound to the concrete
artifact store they selected at startup; they do not switch or dual-write mid-session.

The former workspace instruction-source checkout and the prior workspace artifact store remain
preserved as independent rollback roots. Do not merge, mirror, symlink, move, delete, or rewrite
either history as part of this mapping. The complete machine-local agreement replaced by the older
workspace pointer also remains preserved intact. The cutover steps this appendix carried until the
2026-09-24 amendment for issue #54 remain readable at `29b6360:clients/openclaw.md`, lines 104–130.
If the pointer, Parts A–B, or this appendix is unreachable in the active session, stop the affected
work with the missing instruction-source capability recorded; do not automatically downgrade it to
B1. After changing a pointer, require the fresh-session observation above before declaring it
effective; do not assume arbitrary external-file injection or automatic refresh.

**Default mode: autonomous.** The capability guard (B0) is still evaluated for the unit B0 names;
that Camina coordinates several deliveries in one conversation does not widen it. In OpenClaw, an
unavailable capability is evidence about its affected operation: it does not switch the delivery or
team to B1, and the team stops at that operation with the exact missing safe route. This is a
canonical policy decision, not a claim that every capability has been measured. Any retained
workspace-local layer adds client mechanics only; it never copies or overrides Parts A–B. B2 still
reserves merging to Brandon alone. [learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]

## Runtime and workspace

Resolve the active workspace and target checkout from live inventory; do not assume every specialist
shares main's CWD. When delegation is needed, use canonical role IDs and the supported native or
OpenClaw delegation mechanism available to that session; `sessions_spawn` is one available
OpenClaw mechanism, not a universal requirement. Put A4's RULE ZERO first. Then include only the
role, deliverable, mode, file fence and role-based model tier, and the selector that resolves that
tier where the mechanism accepts a caller's selection.

**Model selectors (A4's tiers).** Which selector resolves each A4 role tier for an OpenClaw
specialist is not recorded here — **unmeasured**; measure and record. The shared Claude Code
wrapper takes no caller selector and pins its own exact model [source:
`~/.openclaw/workspace/docs/team-operating-model.md` lines 198–199, read 2026-10-24, SHA-256
`1bf9bcef0f5f2b17273c9d14f3062f19ae51a5ffa5e0c017621055fa6b84f163`, quoted below], so a dispatch
through it names its role tier, passes no selector, and records the model the wrapper pins (A4).
Those two lines read exactly, line break kept:

```text
Invoke the wrapper without `--model` or `--fallback-model`; the wrapper pins the exact
model and rejects caller-supplied model selection. Transmitting relevant in-scope local
```

**Claude routes and intentional exceptions.** The same source applies its wrapper rule only where
a role has a supported Claude route; without one, the affected substantive operation stops and
reports the missing route, which is not a failed Claude invocation [source: same file, lines
204–206, same read and SHA-256]. The 2026-10-23 role-local normalization covered Camina and ten
specialist role sources, not the four roles below [source, issue #177].

Search boundary [measured, 2026-10-24]: a case-insensitive `claude|wrapper` search of only six
top-level files in each `~/.openclaw/workspace-<role>/`: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`,
`USER.md`, `HEARTBEAT.md` and `MEMORY.md`. All other files and subdirectories were excluded, among
them `DREAMS.md`, `memory/`, `media/`, `avatars/`, `avatar-candidates*/`, `drafts/` and `_agent/`.
"Only" and "no" about wrapper text below mean within that boundary, not across the workspace. Of
the 14 `workspace-*/SOUL.md` files, those of `finance`, `marketing` and `openclaw-admin` do not
name `claude-with-max.sh`, and `assistant`'s names it only conditionally [measured]. Configuration
facts come from `~/.openclaw/openclaw.json` [source: read 2026-10-24, SHA-256
`bf567245857808ffeef414e2904ee5b5873948eacde98ff639df54bba2b62ec6`]. Pilot and Slack-class facts
come from `~/.openclaw/workspace/memory/2026-10-24.md` lines 121 and 131 [source: read 2026-10-24;
lines 1–137 SHA-256 `267584c20d41942f872ecff7aed128158e2d16e8aa5baf4906afad40b3eb4459`]. Each
entry covers only the role it names:

- **`assistant` (Cortana):** the only wrapper text is `SOUL.md` lines 113–115 [measured; file
  SHA-256 `1d96e6b2ebdb047194e14a3ad73c90d9a9830d967edc7a549ba3ed8e95b625a8`], which say the role
  does not currently use Claude Code and that any future capability goes only through
  `scripts/agent/claude-with-max.sh`, never bare `claude` [source]. Its config entry, lines
  211–242, sets primary `openai/gpt-5.6-luna`, lists only `openai/gpt-5.6-luna` (runtime `codex`)
  and `openai/gpt-5.6-terra` (runtime `openclaw`), and has `tools.alsoAllow` of `memory_write`
  only [source]. That text grants no route; the role's runtime route is **unmeasured**.
- **`finance` (Graham):** no wrapper text; the only `claude` match is `AGENTS.md` line 20's pointer
  to a repository's `CLAUDE.md` [measured]. Its config entry, lines 628–695, sets primary
  `openai/gpt-5.6-sol`, its `modelPolicy.allow` is only `openai/gpt-6-astra` and
  `openai/gpt-5.6-sol`, and it has `tools.alsoAllow` of `memory_write` only [source]. The role
  is an intentional GPT-only pilot [source: memory lines 121 and 131].
- **`marketing` (Sloane):** no wrapper text; the only `claude` match is the same `AGENTS.md`
  line 20 pointer [measured]. Its config entry, lines 696–763, sets primary `openai/gpt-5.6-sol`,
  its `modelPolicy.allow` is only `openai/gpt-5.6-sol` and `openai/gpt-6-astra`, and it has
  `tools.alsoAllow` of `memory_write` only [source].
- **`finance` and `marketing` Slack class:** their `toolsBySender` rules, lines 676–693 and
  744–761, cover the same two Slack senders, and each sender rule both denies `group:runtime` and
  allows `gateway_exec` through its own `alsoAllow` [source]. For `finance`, that `gateway_exec`
  allow is stale, and its authenticated Slack canary exposed no executable tools and made zero
  Claude calls [source: memory line 121]. That class has no supported Claude route [source: memory
  line 131]. Substantive filesystem-grounded work arriving through it therefore stops at the
  missing route [inference, from the stop rule at lines 204–206 above applied to that source; not
  inferred from the configured grants; what would verify it: an authenticated canary from one of
  those two senders, to each role, that requests substantive filesystem-grounded work and
  observes the missing-route stop, with no Claude call]. `marketing`'s route outside that class is
  **unmeasured**.
- **`openclaw-admin` (Ashford):** no match for either term in the six searched files [measured].
  Its unsearched `_agent/` does contain `claude` or `wrapper` matches [measured], so that no-match
  statement holds only within the stated boundary. Its config entry, lines 588–627, sets primary
  `openai/gpt-5.6-sol`, lists only `openai/gpt-5.6-*` models, and has `tools.alsoAllow` of
  `memory_write` only [source]. Its route status remains **unmeasured**; measure and record. Do
  not infer it from the other entries.

No runtime route, present or absent, is inferred here from missing wrapper text or configuration
alone. This list is not a census: whether other roles outside the role-local wrapper contract
exist, and the route status of any that do, is **unmeasured**; the entries above cover only the
four roles they name.

OpenClaw does not relax either mode's topology. Attended lanes use one of B1's two shapes: an
mbox lane runs git only in its isolated clone, and a lane delivering uncommitted edits may edit its
named files in the shared checkout but runs no git there. The delivery owner, a specialist
dispatched as a sub-agent included, alone controls the shared checkout's git state: it stages a
batch and commits after Brandon's batch approval, and applies an mbox series with `git am` only
after that approval, since `git am` is the commit (A4, B1). Autonomous specialists use B2's
dedicated-worktree shape. For this agreement repository,
the amendment exemption in its README means an autonomous amendment uses one isolated feature
worktree branched from `develop`, rather than a wave branch; do not invent a wave merely to obtain
isolation.

## Staff operating model

This is an OpenClaw-only operating model. It does not change B0's guard, B1/B2's delivery rules,
the Part B ritual, or another client's appendix.

OpenClaw fills A4's three seats, and Brandon's, with distinct roles [decision 2026-10-23, Brandon,
issue #173]:

- **Camina — orchestrator.** Holds A4's orchestrator duties, preserves continuity across the
  conversation, and synthesizes the decision-ready hand-back. While a delivery specialist is
  assigned, Camina does not execute that delivery's repository mechanics; the orchestrating session
  fills the delivery-owner seat only when no specialist is assigned.
- **Judy (coder), or the assigned delivery specialist — delivery owner.** Holds A4's
  delivery-owner duties, and implementation and diagnostics of the delivery's authorized routine,
  reversible repository work.
- **Amos (reviewer), or the assigned reviewer — independent reviewer.** Holds A4's
  independent-reviewer duties; neither a lane's nor the delivery owner's own report is that review.
- **Brandon — merge.** Brandon alone merges into `develop`, `master`, or `main`.

A4 is the authority for each seat's complete duties, but for A6's one-off close record, which A6
assigns to the agent closing a delivery with no initiative; this list binds OpenClaw roles to them.

Work outside the authorized routine, reversible boundary escalates rather than staying with the
specialist, and administration outside it retains its existing authorization and stop conditions.

The OpenClaw agent team owns installs, builds, test suites, and verification for authorized,
routine, reversible repository work through a ready B2 pull request; an authorized B2-qualified
specialist lane is the default delivery path. Progress and status updates are informational and
non-blocking: sending one neither requests owner approval nor creates an approval checkpoint.
If a required safe route is unavailable, the team records that capability evidence and stops at the
affected operation with the precise missing route. It does not fall back to B1 or make Brandon the
command runner. [learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]

Keep five decisions separate:

1. **Staff authority** — the owner has authorized the lane to decide and proceed within its scope.
2. **Lane capability** — B0 is evaluated for the selected lane's exact checkout and delivery path;
   a parent session unable to use that path does not downgrade the lane.
3. **Risk and reversibility** — only routine, reversible repository work may proceed on that
   authority.
4. **Delivery topology** — OpenClaw's autonomous default uses B2's dedicated-worktree shape;
   B1's lane shapes apply only when Brandon explicitly selects attended delivery.
5. **Human approval** — Brandon alone merges into `develop`, `master`, or `main`.

An authorized autonomous specialist owns authorized routine, reversible repository work through
the ready B2 pull request. Brandon alone accepts and merges into `develop`, `master`, or
`main`; he is not the command runner for that delivery. Every existing stop remains in force,
including destructive, irreversible, production, credentialed, financial, and externally published
actions; those stops are not delegated with the lane.

Within an authorized B2 delivery, commits, pushes, pull-request creation or updates, review
responses, and integration of reviewed lane work are routine delivery work and require no
per-batch owner approval. This is not authority for a B2 stop-list action or for a merge into
`develop`, `master`, or `main`; Brandon's ready-PR acceptance and manual merge remain the human
acceptance boundary.

Within an assigned B2 feature branch, an authorized lane may create a lane branch from that
feature branch. The delivery owner may integrate the lane's reviewed work back into that feature
branch only after a completed A4 two-axis review. B1 deliveries retain B1's lane shapes (mbox or
uncommitted edits). Neither lane-branch composition nor feature-branch ownership permits an agent
merge into `develop`, `master`, or `main`.

Every delivery retains a completed A4 two-axis verdict, the relevant diff and gate evidence, and
Brandon's decision context. Routine reversible work may present those required items in the
smallest sufficient packet; higher-risk or more substantive work adds scrutiny and evidence. This
scales ceremony around A4; it does not waive or replace A4's review requirement.

The B2 readiness boundary is unchanged: Brandon receives a ready feature PR with its A4 verdict,
relevant diff and gate evidence, and material decisions. This section adds no second acceptance
ceremony.

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

**Cross-session native-boundary capability record.** [source, issue #112, Brandon's 2026-10-07
decision]
The contract also defines an Ashford/OpenClaw-owned durable capability record for the existing
host and its native-exec boundary. It is metadata, not repository state, session memory,
`_agent/` artifact state, a replica, or a new instance, container, image, volume, database, or
probe environment. An Ashford-managed resolver/writer uses the supported OpenClaw-owned state
location Ashford designates, validates the schema and fingerprint, and makes locked atomic
transitions; this policy names no machine path. Until Ashford designates both an Ashford-managed,
supported resolver/writer and supported state location as active, the cross-session protocol is
documented but inactive: no record is valid, and the existing one-strike-per-session rules apply.

When active, a fresh session consults that record through the resolver before its first native
shell or native patch attempt. Ashford is its sole logical writer and lifecycle owner; sessions
consult it mechanically and never write, clear, invent, or edit it. Bull supplies read-only
host/runtime/security change facts and evidence, but does not write or clear the record, run the
restoration canary, or declare availability. Camina coordinates. The non-secret fingerprint is a
composite of stable host/instance identity; the OpenClaw and native-executor build and effective
configuration; OCI image, runtime, and effective security configuration (including user/UID
mapping, user namespace, capabilities, `no_new_privs`, mounts, and security options); and kernel
plus relevant user-namespace, AppArmor, and seccomp facts. It excludes chat, session, process and
PID identity; cwd, repository and worktree; model/provider; and command text.

A valid `unavailable` record may be written by Ashford only after a session reports a strike
matching the exact confirmed Bubblewrap/namespace/AppArmor prelaunch signature below, before
target output or side effect. It suppresses the default native probe and uses the existing routing
table; an operation with no bounded route still stops. A valid `available` record may be written
by Ashford only after both (a) separately authorized repair or a relevant boundary change and (b)
separately authorized execution of one fixed native-exec, no-write canary through that same
recomputed boundary; repair or change does not itself authorize the canary. Its durable evidence
records native-exec route attestation, correlation and timestamp, exit 0 with the expected marker,
absence of the prelaunch signature, old/new fingerprint comparison, the authorization reference,
and an evidence locator with integrity information. It proves only that the native prelaunch
boundary reached the no-write target; it does not establish B0 eligibility or general health,
weaken security, reclassify a target failure, or change B0's selected mode.

Missing, malformed, schema-invalid, evidence-invalid, or fingerprint-mismatched state is no valid
record and retains the one-strike behavior; a fingerprint mismatch invalidates to unknown, never
to available, and triggers no repair. Invalidate to unknown on host replacement, reimage, or
migration; a kernel, LSM, or relevant user-namespace setting change; AppArmor or seccomp revision,
mode, or label change; OCI image, runtime, container, effective user/UID mapping, user namespace,
capabilities, `no_new_privs`, mounts, or security-option change; an OpenClaw/native-exec launcher,
backend, build, or effective-configuration change; explicit sandbox-repair maintenance; or
inability to re-attest a keyed fact. A new chat, session, process, PID, or time alone does not
invalidate. A restart preserves validity only when the resolver re-attests every keyed fact and
the same deployment/container boundary; otherwise the record becomes unknown.

This policy authorizes no maintenance, repair, container lifecycle work, runtime weakening, or
canary execution; each requires separately approved maintenance scope.

The record changes only whether a fresh session spends the default probe. It does not grant the
audited-check route below. That route separately narrows #67's categorical test no-route while
preserving its measured Gateway boundary; #58's signature-confirmation, #88's command-bounded
inspection, and #94's no-mode-change remain unchanged.

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
| source-audited executable check | Gateway execution only after the eligibility procedure below passes; otherwise no route |

A7 still governs the GitHub row: the GitHub MCP's write tools never author commits, so a commit
comes from a checkout on every route.

**Row 1's bound is the command's, not Gateway's.** Inspection qualifies only when the command
writes nothing outside what the task may write. Gateway's `workdir` supplies no bound — Camina's
inference, on the measured host, in the paragraph below that begins "**Executable checks are
classified by behavior, not by name.**", where its measurement is cited.
[source, Camina's, issue #88, 2026-10-01] A linked
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

**Row 3's readback form.** [inference/recommendation, Camina's, issue #96] Confirmed for the
current OpenClaw host and breaker contract: row 3's diff/readback is inspection; when that
inspection uses Git diff, it uses the row 1 eligible form:

```sh
git -c diff.autoRefreshIndex=false diff --no-ext-diff --no-textconv -- <patched paths>
```

[measured 2026-10-01 by the Spec reviewer of #88's change, git 2.46.0, scratch repos on the
maintainer's machine, not the OpenClaw host; recorded on issue #96, whose record names the diff
form without its `-- <patched paths>` pathspec, and which Camina cites and did not re-run]
`git apply --check` and `git apply` left the linked worktree index unchanged. Plain `git diff`
rewrote the index when another tracked file was stat-stale; the command above did not.
[source, Camina's, issue #96] The current breaker requires every fallback to preserve the task's
original read/write constraints. Row 1's confirmed eligible set already includes this diff form;
`--no-ext-diff` and `--no-textconv` exclude those configured helper paths.
[inference/recommendation, Camina's, issue #96] Pointing row 3 at row 1's eligible set keeps one
inspection boundary and prevents "diff/readback" from being read as permission for plain
worktree-facing `git diff`. Restricting the pathspec to the patched paths also keeps the readback
bounded to the edit.

**Row 3's readback of a file the patch adds.** [inference/recommendation, Camina's, issue #103]
An added file's readback has a route. After a confirmed strike, row 3 may read each added path
directly through Gateway, provided that exact path is inside the session's original read scope
and the complete command writes nothing outside the authorized paths. For a regular file, the
`cat` form qualifies. [source, Camina's, issue #104] Gateway execution accepts one `command` value
described as a shell command; it does not expose an argv-array command interface. It separately
exposes `env` overrides described as literal, with no expansion. Gateway therefore does not
automatically make a patch-derived path safe if the session splices that path into the command
string, but it does provide a separate literal-value channel that avoids doing so.
[inference/recommendation, Camina's, issue #104] Row 3 passes the exact, scope-validated added
path as a literal `ADDED_PATH` environment override supplied separately from the fixed shell
command, then uses a quoted expansion:

```text
env:     {"ADDED_PATH": "<exact added path, supplied as a literal value>"}
command: cat -- "$ADDED_PATH"
```

[inference/recommendation, Camina's, issue #104] The quoted expansion reaches `cat` as one
argument. The session must not splice the path into `command`, re-evaluate it with `eval`, or
leave the expansion unquoted.
[inference/recommendation, Camina's, issue #103] A generic/native read tool is not automatically
a route after the strike; it qualifies only if it is separately established not to cross the
failed native boundary. The deterministic breaker route is the exact-path read through Gateway.
[measured 2026-10-02 by the orchestrator that filed issue #103, git 2.46.0, a scratch repository
on the maintainer's machine, not the OpenClaw host; recorded on that issue, which Camina cites and
did not re-run] `git apply` left the added file untracked, and row 3's index-based diff printed no
hunk for it. [source, Camina's, issue #103] The current breaker requires the fallback to preserve
the task's original read/write constraints, and row 1 admits inspection only when the command's
complete execution writes nothing outside what the task may write. A direct read of an authorized
regular-file path invokes no Git index, external diff, or textconv helper.
[source, Camina's, issue #103] Git documents `git diff --no-index` as comparing two paths on the
filesystem and says that form implies `--exit-code`. It also documents `--no-ext-diff` and
`--no-textconv` as disabling those helper paths. Accordingly, the `--no-index` form is also an
eligible patch-shaped read for an added regular text file.
[inference/recommendation, Camina's, issue #104] The same passing rule applies to the
patch-shaped regular-text form:

```text
env:     {"ADDED_PATH": "<exact added path, supplied as a literal value>"}
command: git --no-pager diff --no-index --no-ext-diff --no-textconv -- /dev/null "$ADDED_PATH"
```

[source, Camina's, issue #103] Exit 1 is the expected "different" result; the emitted added-file
patch is the readback. [inference/recommendation, Camina's, issue #104] The literal environment
override plus the quoted expansion—not `--`—is what closes shell splitting, globbing, expansion,
and command-substitution vectors for the path value.
[inference/recommendation, Camina's, issue #103] The direct exact-path Gateway read is the general
rule, and the `--no-index` form the convenient regular-text form. Do not use `cat` to dereference
an added symlink: inspect its link payload without dereference instead.
[inference/recommendation, Camina's, issue #104] With the same literal environment override, use
`readlink -- "$ADDED_PATH"` (or an equivalent argv-based, non-dereferencing link-payload read if
Gateway later provides one), then apply A2's complete-output checks.
[inference/recommendation, Camina's, issue #103] For binary content, or whenever tool output can
truncate, use a bounded byte-for-byte read or checksum/size comparison and verify complete output
under A2; a partial display is not confirmation.

**Executable checks are classified by behavior, not by name.** Gateway is not a generic test
runner. [source, issue #67] The live Gateway execution surface takes a host command and a
`workdir` and exposes no filesystem-root or path allowlist, mount namespace, UID remap or
read-only-filesystem control. [measured, issue #67, 2026-09-30] In a positive-control canary from a
probe worktree, `printf 'escape\n' > ../outside/escape.txt` succeeded. [inference, Camina's,
issue #67, from that measurement] `workdir` selects the starting directory and does not confine writes
on the measured host.

When the native sandbox is unavailable — either rule 1 marked it unavailable in this session or a
valid durable `unavailable` record suppressed the default probe — an executable check may use
Gateway only when every condition below is established before the run:

1. The delivery changes neither the command nor any repository-controlled executable it invokes.
2. The agent reads those executables in full, records their SHA-256 values, and enumerates every
   subprocess. Every host utility, shell runtime, and shell builtin is named; executable paths and
   versions or hashes are recorded where exposed, and the relevant read, write, network, and
   process behavior is established from trusted documentation or measurement. The transitive
   execution path contains no package manager, build tool, test framework, hook, plugin, or
   dynamically discovered or loaded code.
3. Inputs, execution order, and the expected exit and output are deterministic and declared. The
   command reads no clock, randomness, ambient mutable state, or input outside the recorded set.
4. Every write is confined to one exact task-authorized scratch root, passed as a literal
   environment value and consumed through quoted expansion. The command writes no repository,
   Git-index, system, or shared state.
5. The command uses no network, credential, external service, production resource, or
   externally published surface.
6. The evidence record names the exact command; executable and utility identities; subprocesses;
   recorded inputs; expected exit and output; complete write set; scratch root; a SHA-256 of the
   pre-run candidate diff; and the checks supporting conditions 1–5.

Run the eligible command with the literal scratch-root environment value. Completion requires the
observed exit and output to match the recorded expectation, removal of the scratch root, and the
bounded Git readback's SHA-256 to equal the pre-run candidate-diff SHA-256. CI remains the arbiter
and must pass before hand-back.

If any condition cannot be established, the command is an unbounded test and has no Gateway route.
For OpenClaw's autonomous default, stop and name the exact missing route; do not convert the
operation into B1 or make Brandon the command runner. This repository's unchanged
`./scripts/check-index.sh && ./scripts/check-index.test.sh` is the motivating example, not a
permanent exception; establish the conditions for each delivery, and a delivery that changes either
script fails condition 1.

**A confirmed strike does not change the selected mode** [decision 2026-10-01, Brandon, on
Camina's recommendation; see issue #94]: it marks the native sandbox unavailable (rule 1) and
leaves unchanged the mode B0 selected, including an explicit owner-selected attended override. For
OpenClaw's autonomous default, Brandon's 2026-10-17 direction is that the team carries on by
bounded routes and stops at the first required operation that has none, reporting the precise
unavailable route; it does not turn that operation into B1 or ask Brandon to run it. An explicitly
owner-selected B1 delivery remains attended. Only a later explicit owner override changes the mode
after pickup; a strike during the pickup guard records that the specific operation lacks a safe
route.

The breaker is **not** a global switch to Gateway execution, a weakening of sandbox controls, or a
generic rule for failures that occur after the target program starts. [source, issue #58,
measured there 2026-09-23] The agent-working-agreements delivery cycle retried native shell and
patch paths after the same prelaunch error; the bounded Gateway equivalents reached the target.

## Instruction-source isolation and freshness

**The protected instruction-source root working tree stays protected.** It remains clean, checked
out on `master`, and equal to `origin/master` after the verified fast-forward following each
`develop → master` release. Its Git administration may host isolated delivery worktrees. A new AWA
delivery worktree is created only through OpenClaw's managed worktree facility, for example
`openclaw worktrees create <repo-root> --name <name> --base-ref origin/develop`, so that it lives
under the managed worktree root and appears in OpenClaw's registered-path inventory; a plain
`git worktree add` outside that inventory is not a route for new delivery. Each delivery branch
starts at `origin/develop`. Worktree administration may run from the protected instruction-source
root working tree and update shared Git metadata, but delivery edits, commits, branch switches, and
cleanup never target it; the release refresh below is the only operation that changes its branch,
index, or checked-out files.

OpenClaw sources, all from the installed 2026.10.6 docs at `<runtime>/lib/node_modules/openclaw/docs/`,
where `<runtime>` is `~/.openclaw/runtime/2026.10.6-release-41c5d94f722c-2026-10-22T19-49-54.000Z`,
read 2026-10-25: `gateway/config-runtime.md` (SHA-256
`ee38d26c0cb37439c7c4b0ac71f826b8564a2559b6c451109cee7485568b60c8`),
`concepts/managed-worktrees.md` (SHA-256
`ecdbbfd79164e46e8883297680c975d13ff9d7cda149511c52be52dd6560d18d`) and
`plugins/memory-wiki.md` (SHA-256
`57db87ba73a5ea0ddc23caa25b56e95746adf1541c4f2e3791439f35938de19c`).

- The managed worktree root is the global `worktreeRoot` key in `openclaw.json`; unset, it defaults
  to `<openclaw-state-dir>/worktrees`, and checkouts are created at
  `<worktreeRoot>/<repo-fingerprint>/<name>` [source: `config-runtime.md` lines 16 and 24;
  `managed-worktrees.md` lines 67 and 199]. The state directory is `~/.openclaw` unless
  `OPENCLAW_STATE_DIR` is set [source: `memory-wiki.md` line 427].
- Changing `worktreeRoot` affects new allocations only; registered worktrees keep their recorded
  paths for reuse, cleanup, and restore [source: `config-runtime.md` line 26].
- `openclaw worktrees list --json` reports OpenClaw's registered worktrees, including those recorded
  paths [source: `managed-worktrees.md` lines 79, 408 and 621]. It does not list plain Git
  worktrees [inference: OpenClaw records managed worktrees in its state database (line 11); what
  would verify it: one plain `git worktree add` in a scratch repository, absent from the list].
  Run it while a Gateway owns the local state: offline listing can retire missing checkouts
  [source: `managed-worktrees.md` lines 591–596].

**Resolve the managed worktree root before creating or using a delivery worktree.** Take
`worktreeRoot` from the Gateway's `openclaw.json` when set; otherwise apply the documented default.
Canonicalize the resolved root and the delivery worktree path, and verify that neither lies inside
or contains the selected `_agent/` artifact store or the protected instruction-source root working
tree. If the root cannot be resolved or any of those paths overlap, stop and report the resolved
paths; do not create or use the worktree. The delivery audit records the resolved root, whether it
came from `worktreeRoot` or the default, and the worktree path with its registered inventory record.
[measured 2026-10-25, this host] `~/.openclaw/openclaw.json` has no `worktreeRoot` key, the probing
shell had `OPENCLAW_STATE_DIR` unset, and `git worktree list` showed this repository's managed
delivery worktrees under `/Users/brandonperfetti/.openclaw/worktrees/<repo-fingerprint>/<name>`.
[inference] The effective root here is the default `~/.openclaw/worktrees`, outside
`$AGENT_ROOT/_agent/`; the Gateway service's environment was not probed, so resolve the root again
for each delivery rather than reusing this value.

[measured 2026-09-23, issue #24] Three delivery worktrees were created by commands that explicitly
selected the protected instruction-source root working tree with `git -C`; their presence violated
its then one-worktree contract even though the commands ran from the workspace root. Issue #180
supersedes only that topology assumption: the containment remains that no delivery operation alters
the protected instruction-source root working tree. It does not change runtime project bindings or
delete or migrate existing clones.

**After every `develop → master` merge, fetch and fast-forward the protected instruction-source
root working tree before any further work.** Run `git switch master`, then `git fetch origin`; if
the fetch fails, stop and report before any merge. Then run `git merge --ff-only origin/master`;
verify the tree is clean and `HEAD == origin/master`. The next report names the exact SHA the
protected instruction-source root working tree serves.
[measured 2026-09-23] PR #41 merged at `b733b59982736285d078ee9f67209bcce2fea957` on
2026-09-22T20:18:10Z, but the protected instruction-source root working tree remained six commits
behind until the next day.

**Remove a delivery worktree and its local branch once its feature PR has merged into `develop`.**
These safeguards apply to every delivery worktree, managed or an existing plain Git worktree.
Run it from any of the repository's worktrees; the protected instruction-source root working tree
may serve, but only for Git administration and never against its working tree:
`git fetch origin` — if the fetch fails, stop, and retain and report the worktree and branch — then
`git merge-base --is-ancestor <branch> origin/develop`. Exit 0 is the only permission, and
not by itself enough: the protected instruction-source root working tree, another protected base
worktree such as a release-review worktree, a dirty delivery worktree, and a branch that is not an
ancestor of `origin/develop` are all retained and reported. The protected instruction-source root
working tree is never eligible for cleanup. `<path>` is the value of the `worktree` line of the
unique record in `git worktree list --porcelain` whose `branch` line is `refs/heads/<branch>`; on
zero or multiple matches, stop, and retain and report the branch and every candidate worktree. On
exit 0, with one match, and outside those exclusions, `git worktree remove <path>` without
`--force`; then, only if that removal succeeded, `git branch -d <branch>`.
Any refusal from either command is left as it is and reported, never overridden.
[measured 2026-09-23, issue #57] The delivery host went from 13 to 16 registered worktrees in one
delivery cycle; the dry-run and live cleanup the ticket records then removed 14 merged worktrees
and their branches without forcing a dirty removal, leaving the protected delivery host plus a
release-review worktree.

## Pickup guard and delivery audit

Record the checkout and HEAD, Git author identity, `core.hooksPath` and hook presence, an explicit
dry-run probe (or N/A when the repository installs no `pre-push` hook), the full gate result,
branch ownership, and target-protection audit. For a delivery worktree, also record the resolved
managed worktree root, its source (`worktreeRoot` or the default), the worktree path, its
registered inventory record, and the `_agent/` and protected-root overlap check; any overlap stops
the delivery (see
[Instruction-source isolation and freshness](#instruction-source-isolation-and-freshness)).
Parts A/B remain the authority for RULE ZERO, no-force-push, and no-agent-merge; do not restate
those rules here.

Attribution injection, arbitrary external injection, and exact reset/reload behavior remain
unmeasured. Require a delivery audit or controlled observation rather than assuming them. Record a
skill source/version when it materially affects delivery; skill precedence is not agreement
authority.

[measured 2026-09-20, current Gateway host] `claude-skills` could not pass guard item 2 because its
gate step 6 requires Ruby to validate `agents/openai.yaml`, and step 7 requires `zip` to rebuild and
compare the `.plugin` distribution. That measured session was therefore attended. OpenClaw may
deliver there, and claude-skills #111
tracks a durable install and complete remeasurement. It did not block agreement adoption or the
pointer cutover.

[source, B0 and Startup and mode] Future OpenClaw work still re-evaluates B0 for its exact
checkout and path as capability evidence, not as the B1/B2 mode selector.

## Evidence store

**Configured native store.** For a fresh role started from a replaced pointer under the approved
acceptance procedure in [Startup and mode](#startup-and-mode), the native artifact store resolves
provisionally at session startup to `/Users/brandonperfetti/dev/sansfaux/_agent/`; that same store is
retained whether the later role verdict passes or fails. For a role whose pointer is still unchanged,
and on any other host, use the concrete durable `_agent/` store selected by the active workspace
policy and record its location with the capture; do not infer this Mac path across hosts. An active
session remains bound to the store it selected at startup even if a workspace pointer changes later.
Never switch stores or write the same artifact to both stores mid-session.

Use the selected store's `evidence/` and `analysis/` subdirectories per A2 and A6. Date-name
artifacts and label claims `[measured]`, `[source]`, or `[inference]`.

**Scratch clones (A6, "Clones").** The task-authorized scratch root in the Gateway
executable-check conditions above is not a place for a scratch clone: it exists for one eligible
check and is removed when that check completes [source: this appendix]. Where a scratch clone goes
on this host, and whether specialists share a scratch space, is **unmeasured** — measure and
record. Never under `_agent/`.

## Migration dispositions

The complete machine-local agreement that preceded the canonical route carried rules that Parts
A–B now supersede. They are deliberately **not carried forward**, for these reasons:

- **A — autonomy:** the local autonomous default is superseded by the canonical OpenClaw
  autonomous default, B0's per-checkout capability evidence, and B2's Brandon-only merge boundary;
  an unavailable operation stops at its missing safe route rather than downgrading the team to B1.
- **B — specialist commits:** a dispatched lane specialist committing, staging or running any
  other git in the shared checkout is not carried forward. Attended sessions use B1's two lane
  shapes — an mbox series committed in the lane's isolated clone, or uncommitted edits to named
  files in the shared checkout with no git run there — and the delivery owner (A4) alone keeps the
  shared checkout's git state, staging, committing and applying with `git am` per B1; autonomous
  sessions use B2's dedicated-worktree shape. A delivery owner dispatched as a sub-agent is not a
  lane and keeps those A4 shared-checkout git-state duties.
- **C — builds and tests:** OpenClaw's autonomous team owns installs, builds, tests, and
  verification through the ready B2 PR; an unavailable safe route stops that operation with its
  evidence, while B1 applies only when Brandon explicitly selects attended delivery.
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
