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
delivery worktree is created only through OpenClaw's managed worktree facility, from a freshly
fetched and captured base. First fetch both base heads by name, not through the configured
refspec:
`git -C <repo-root> fetch origin +refs/heads/develop:refs/remotes/origin/develop +refs/heads/master:refs/remotes/origin/master`;
if the fetch fails, stop and report, and do not create the worktree. Then, for each of `develop`
and `master`, verify that `git -C <repo-root> rev-parse --verify 'origin/<name>^{commit}'` equals
the OID `git -C <repo-root> ls-remote origin refs/heads/<name>` reports; if either command fails
or they differ, stop and report, and do not create the worktree. The verified `origin/develop` OID
is the captured base OID.
Pass that captured `<base-oid>`, not the moving `origin/develop` name, and the Gateway context
explicitly as a bound invocation, with no `--profile` or `--dev` (see `<profile-binding>` below):

```sh
env <profile-binding> \
  OPENCLAW_STATE_DIR=<state-dir> \
  OPENCLAW_CONFIG_PATH=<config-path> \
  openclaw worktrees create <repo-root> --name <name> --base-ref <base-oid>
```

OpenClaw's documentation says that creation without a base ref fetches origin's remote default
branch, and that an explicit base must resolve to a commit and is never replaced by another base
[source] (`managed-worktrees.md` line 204); that text does not establish that a fetch or refresh
happens when an explicit base is given [source] (`managed-worktrees.md` line 204). [inference] The
required preceding named fetch and `ls-remote` comparison are what make the captured `<base-oid>`
current; what would verify that causation: in a disposable clone of a remote whose `develop` does
not move during the test, with the clone's `origin/develop` deliberately left stale behind it, the
`rev-parse` capture above run without a fetch returns the stale OID, and after the named fetch
above exits 0 the same capture returns the OID `git ls-remote origin refs/heads/develop` reports.
Before any delivery edit, verify that
`git -C <path> rev-parse HEAD`, where `<path>` is the created worktree's registered inventory path,
equals `<base-oid>`; on a mismatch, stop, and retain and report the worktree, its `HEAD`, and
`<base-oid>`. The worktree then lives under the managed worktree root and appears in OpenClaw's
registered-path inventory; a plain `git worktree add` outside that inventory is not a route for new
delivery. Each delivery branch starts at that verified `<base-oid>`. Worktree administration may run
from the protected instruction-source root working tree and update shared Git metadata, but
delivery edits, commits, branch switches, and cleanup never target it; of the operations this
appendix runs, only the release refresh below is meant to change its branch, index, or checked-out
files. [corrected 2026-10-26] An earlier revision said "the release refresh below is the only
operation that changes its branch, index, or checked-out files", which must not be relied upon:
[source] without a base ref, base preparation can fast-forward the protected root's checked-out
default branch, as described below, and no measurement covered every operation that can touch that
working tree. [inference] The qualified sentence covers only this appendix's operations and states
intent, not a measured guarantee; the before-and-after status comparison below is what would verify
it for one create run. Creation resolves its base through `resolveWorktreeCreationBase` [source]
(`service-BAfHLKXG.mjs` line 3879). With an explicit `--base-ref`, that base resolution never calls
base preparation [source] (`base-ref-B9lkLpLz.mjs` lines 24–40): it either uses a checkout commit
already captured [source] (`base-ref-B9lkLpLz.mjs` lines 25–34) or runs
`git -c core.warnAmbiguousRefs=true rev-parse --verify --end-of-options <base-oid>^{commit}` in
`<repo-root>` [source] (`base-ref-B9lkLpLz.mjs` lines 41–63). So base resolution neither fetches
nor fast-forwards anything; that statement covers base resolution only, not the rest of the create
operation. Without a base ref, base preparation fetches origin's default branch [source]
(`base-ref-B9lkLpLz.mjs` lines 76–83, 115 and 171–235) and then attempts
`git merge --ff-only` of the local default branch [source] (`base-ref-B9lkLpLz.mjs` lines 152 and
281–344). That merge runs only in `<repo-root>` itself, and only when `<repo-root>`'s `HEAD` is the
default branch, `<repo-root>` is that branch's only checkout and is unlocked, sparse checkout is
off, no other worktree Git operation is in progress,
`git status --porcelain --untracked-files=all` there prints nothing, and the local branch is behind
the fetched commit and an ancestor of it; otherwise it is skipped [source]
(`base-ref-B9lkLpLz.mjs` lines 281–344). That fast-forward would move the protected root's branch
and checked-out files, which is why the explicit `--base-ref <base-oid>` above is required.
[inference] The rest of the create operation, which this reading of the source does not cover,
also leaves the protected root's branch, index, and checked-out files unchanged, so the whole
create command with `--base-ref <base-oid>` does. What would verify it, for one run: with no other
process using `<repo-root>` meanwhile, run
`git -C <repo-root> status --porcelain=v2 --branch --untracked-files=all` just before and just
after the create command above and compare the two outputs for equality.

OpenClaw documentation sources, all from the installed 2026.10.6 docs at
`<runtime>/lib/node_modules/openclaw/docs/`, where `<runtime>` is
`~/.openclaw/runtime/2026.10.6-release-41c5d94f722c-2026-10-22T19-49-54.000Z`, read
2026-10-25: `gateway/config-runtime.md` (SHA-256
`ee38d26c0cb37439c7c4b0ac71f826b8564a2559b6c451109cee7485568b60c8`),
`concepts/managed-worktrees.md` (SHA-256
`ecdbbfd79164e46e8883297680c975d13ff9d7cda149511c52be52dd6560d18d`),
`help/environment.md` (SHA-256
`adb51f50950f3d94814c19fd03164d0c100bf72ac749aaaa17cbd072da6411b8`),
`install/nix.md` (SHA-256
`db205205042c5351c47f94bb37385308706ae50f7389edd0dc175c5bc5ceeca8`),
`install/uninstall.md` (SHA-256
`74a52dab06de3ad3a96461b88eb51a04873f220f8a604d4abc9e2b50876be434`), and
`cli/gateway/query.md` (SHA-256
`2d179b4159fff0a1cef8c958ccbb96d386e5b5d1ed013c763a6211461dc33c65`).
Installed runtime source, all in `<runtime>/lib/node_modules/openclaw/dist/`:
`profile-utils-BsmgdpgZ.mjs` (SHA-256
`99679c5ce486640d779cb56e8a64b099a49a479c76d6e691242f52f0abd6c3bd`),
`state-dir-CYkBUd_G.mjs` (SHA-256
`f18c1153a532214e9efb50e1f4b99a5a6af2c41229292c4895c328747093c3e1`),
`profile-D1GpjMFM.mjs` (SHA-256
`fcf1469bb3923ec0e0bda20aa7317710827f9dc536282ab407e5aa97deb83224`),
`argv-invocation-BHqD0obO.mjs` (SHA-256
`3d2d71e1932e07791f918c94d1e6a997d32bfa9c794148dd5f503b81bc57aec9`),
`help-CRbQOEKD.mjs` (SHA-256
`1c0d1eaf0682cc773797b483888fda3b6c180f231243f62c0f08e3e67e4d7cd2`),
`run-command-CrXOzzsc.mjs` (SHA-256
`b252fb2a80021189666fd3ff8a3808e6d35a5efc94c77473a5ea846a7b91a71a`),
`entry.js` (SHA-256
`84d9ae4527bb46be0eece8f95cafefa40559cba8bd921e1358998b331cea0d08`),
`paths-BP0DYpE8.mjs` (SHA-256
`25900721157f35508fdd0f49b65ba6be8ad50f9fe259209929543e0cf50accff`), and, read 2026-10-26,
`base-ref-B9lkLpLz.mjs` (SHA-256
`b4723d93a05b4c97c3b82c20ada3e46a34c3ead7215d1d195e8ff37080b35c0d`) and
`service-BAfHLKXG.mjs` (SHA-256
`ebd36bea37c2c403e6f0376e432e5d68268bde54c047c3bada395143c6dc46ae`),
whose generated filenames and line references identify this exact installed build.

- The managed worktree root is the global `worktreeRoot` key in `openclaw.json`; unset, it defaults
  to `<openclaw-state-dir>/worktrees`, and checkouts are created at
  `<worktreeRoot>/<repo-fingerprint>/<name>` [source: `config-runtime.md` lines 16 and 24;
  `managed-worktrees.md` lines 67 and 199]. The state directory is `OPENCLAW_STATE_DIR` when set,
  and the config file is `OPENCLAW_CONFIG_PATH` when set, otherwise
  `$OPENCLAW_STATE_DIR/openclaw.json`; `OPENCLAW_HOME`, when set, replaces the home directory for
  these defaults [source: `environment.md` lines 50, 346 and 347; `nix.md` line 89]. State
  resolution itself returns `OPENCLAW_STATE_DIR` when set and otherwise `<home>/.openclaw`; it does
  not read `OPENCLAW_PROFILE` [source: `state-dir-CYkBUd_G.mjs` lines 16–28;
  `paths-BP0DYpE8.mjs` lines 115 and 121–142]. A profile-specific root `~/.openclaw-<profile>`
  arises only when the command line carries `--profile <name>` or a root/profile-selecting `--dev`,
  which selects profile `dev`: `entry.js` then calls
  `applyCliProfileEnv`, which computes the root with `resolveProfileStateDir` and exports
  `OPENCLAW_PROFILE`, `OPENCLAW_STATE_DIR`, and `OPENCLAW_CONFIG_PATH` before paths are resolved
  [source: `entry.js` lines 189–190 and 242–251; `profile-D1GpjMFM.mjs` lines 10–65 and 66–102;
  `profile-utils-BsmgdpgZ.mjs` lines 17–21; `paths-BP0DYpE8.mjs` lines 143–158]. A `--dev` is
  root/profile-selecting only when no `gateway` command precedes it: `parseCliProfileArgs` passes a
  `--dev` through unchanged, selecting no profile, when `resolveCliArgvInvocation` finds `gateway`
  as the primary command among the arguments before it, so `openclaw gateway --dev` uses the
  Gateway command's own `--dev` ("Create a dev config + workspace if missing") and selects no
  profile, while `openclaw --dev gateway` selects `dev` [source: `profile-D1GpjMFM.mjs`
  lines 14–25; `argv-invocation-BHqD0obO.mjs` lines 4–11; `help-CRbQOEKD.mjs` line 48 (root
  `--dev`, "Dev profile"); `run-command-CrXOzzsc.mjs` line 36 (Gateway `--dev`)]. A service
  environment's `OPENCLAW_PROFILE` alone does not select `~/.openclaw-<profile>`, although
  `uninstall.md` line 88 describes profile defaults for both `--profile` and `OPENCLAW_PROFILE`.
- `openclaw gateway status` human output includes the CLI's and service's config paths and their
  validity, to diagnose profile or state-dir drift [source: `query.md` line 281]. When a Gateway
  is running, its worktree CLI mutations use the authenticated Gateway that owns the selected local
  state directory [source: `managed-worktrees.md` lines 583–589].
- Changing `worktreeRoot` affects new allocations only; registered worktrees keep their recorded
  paths for reuse, cleanup, and restore [source: `config-runtime.md` line 26].
- `openclaw worktrees list --json` reports OpenClaw's registered worktrees, including those recorded
  paths [source: `managed-worktrees.md` lines 79, 408 and 621]. It does not list plain Git
  worktrees [inference: OpenClaw records managed worktrees in the shared state database
  (`managed-worktrees.md` line 11); what would verify it: one plain `git worktree add` in a
  scratch repository, absent from the list, and one OpenClaw-managed worktree of that repository,
  present in it].
  Run it while a Gateway owns the local state: offline listing can retire missing checkouts
  [source: `managed-worktrees.md` lines 591–595].
- Ordinary `openclaw worktrees remove <id>` is archival and uses Git's forced checkout removal
  after a snapshot; `--if-lossless` is the non-force route, retains dirty or unpublished work, never
  retries a Git refusal with force, and cannot be combined with `--force`. With `--json` it
  returns `removed` and the recorded `cleanup` outcome; `removed: false` is a retention, not a
  deletion [source: `managed-worktrees.md` lines 370, 623 and 635].

**Resolve the managed worktree root from the Gateway service's context before creating or using a
delivery worktree.** The probing shell's environment is not the service's; resolve in this order
and record each result with its source:

1. The service's effective state directory. Its home is the service's `OPENCLAW_HOME` when set,
   or else the service user's home directory [source: `environment.md` lines 50 and 346]. When the
   service's recorded command arguments carry no `--profile` and no root/profile-selecting `--dev`
   (a `--dev` after the `gateway` command, as in `openclaw gateway --dev`, does not count), the
   state directory is
   `OPENCLAW_STATE_DIR` from the Gateway service's environment when set, otherwise that home
   followed by `/.openclaw`, whatever the service's `OPENCLAW_PROFILE` value
   [source: `state-dir-CYkBUd_G.mjs` lines 16–28]. When they carry `--profile <name>` or a
   root/profile-selecting `--dev` (profile `dev`; a `--dev` after the `gateway` command is the
   Gateway command's own option and selects no profile [source: `profile-D1GpjMFM.mjs`
   lines 14–17; `run-command-CrXOzzsc.mjs` line 36]), the service
   process applies `applyCliProfileEnv` to its environment: with no `OPENCLAW_STATE_DIR` there, the
   state directory is that home followed by `/.openclaw-<name>` (`/.openclaw` for `default`), and
   an `OPENCLAW_STATE_DIR` equal to the inherited profile's default root is replaced by it
   [source: `entry.js` lines 189–190 and 242–251; `profile-D1GpjMFM.mjs` lines 14–25, 71–76, 83–86
   and 94–95; `profile-utils-BsmgdpgZ.mjs` lines 17–21].
2. The service's config: `OPENCLAW_CONFIG_PATH` from that environment when set, otherwise
   `openclaw.json` in that state directory; with a service `--profile` or root/profile-selecting
   `--dev`, take it from
   what `applyCliProfileEnv` exports for that environment [source: `profile-D1GpjMFM.mjs`
   lines 87–92 and 96].
3. The effective worktree root: `worktreeRoot` from that config when set, otherwise
   `<state-dir>/worktrees` for the state directory from step 1.

The service's effective profile is the `--profile` value in its command arguments when present,
or `dev` when they carry a root/profile-selecting `--dev`, otherwise `OPENCLAW_PROFILE` from its
environment, otherwise unset; a Gateway `--dev` (`openclaw gateway --dev`) does not make it `dev`
[source: `profile-D1GpjMFM.mjs` lines 14–25 and 93; `run-command-CrXOzzsc.mjs` line 36].

Run every `openclaw worktrees` command — `create`, `list`, and `remove` — as a bound invocation:
both effective Gateway values explicitly on that invocation, `OPENCLAW_PROFILE` set to the
service's effective profile or unset when the service has none, and never `--profile` or `--dev`:
`env <profile-binding> OPENCLAW_STATE_DIR=<state-dir> OPENCLAW_CONFIG_PATH=<config-path> openclaw
worktrees …`, where `<profile-binding>` is `OPENCLAW_PROFILE=<service-profile>` or
`-u OPENCLAW_PROFILE`. A CLI profile is prohibited because `entry.js` applies it with
`applyCliProfileEnv`, which replaces a passed `OPENCLAW_STATE_DIR` or `OPENCLAW_CONFIG_PATH` that
equals the inherited profile's default root or config with the selected profile's, and also clears
inherited Gateway service selectors and, for `dev`, sets `OPENCLAW_GATEWAY_PORT` to `19001`
[source: `entry.js` lines 189–190 and 242–251; `profile-D1GpjMFM.mjs` lines 77–101]. The ambient
profile is bound because `OPENCLAW_PROFILE` still decides whether an invocation holds the default
install identity that owns host service management [source: `paths-BP0DYpE8.mjs` lines 26–29
and 52–78]. [inference: `state-dir-CYkBUd_G.mjs` lines 16–28 and `paths-BP0DYpE8.mjs` lines
121–142 read the passed values, and no CLI profile reaches `applyCliProfileEnv`; what would verify
it: with a different profile that has its own config and a deliberately distinct worktree
inventory, export `OPENCLAW_PROFILE` naming that profile in the probing shell, then run
`OPENCLAW_STATE_DIR=<state-dir> OPENCLAW_CONFIG_PATH=<config-path> openclaw gateway status` and
`OPENCLAW_STATE_DIR=<state-dir> OPENCLAW_CONFIG_PATH=<config-path> openclaw worktrees list --json`
with no `--profile` or `--dev`, and confirm that status reports the passed config path as the CLI's
config path and the list returns the passed state directory's inventory, not the ambient profile's
config path or inventory; repeat the list in the full bound form and confirm the same inventory;
this verifies only those commands in those forms] Passing both effective values and the bound
profile prevents state, config, and profile selection from falling back to the probing shell's
ambient values. When
a Gateway is running, mutations use the authenticated owner of that selected local state directory.
Canonicalize the resolved root and the delivery worktree path, and verify that neither lies inside
or contains the selected `_agent/` artifact store
or the protected instruction-source root working tree. If the service's state directory, config, or
root cannot be determined, or any of those paths overlap, stop and report the resolved paths; do
not create or use the worktree. The delivery audit records the service state directory and which
source supplied it (the service's `OPENCLAW_STATE_DIR`; with no explicit state directory, the
service's `OPENCLAW_HOME` or service user's home plus `/.openclaw`; or, only when the service's
command arguments carry `--profile <name>` or a root/profile-selecting `--dev`, not a Gateway
`--dev`, the `applyCliProfileEnv` result such as
`/.openclaw-<name>`), the service's command-line profile if any and its environment
`OPENCLAW_PROFILE` value, the config path and its source, the resolved root and whether it came
from `worktreeRoot` or the default, and the worktree path with its registered inventory record.
For each creation, it also records the named two-ref fetch's exit status; for each of
`origin/develop` and `origin/master`, the local `rev-parse` OID, the `ls-remote` OID, and their
equality result; the captured `<base-oid>` and the `origin/develop` ref it was read from; and the
created worktree's `HEAD` readback with its equality to `<base-oid>`.
For each `openclaw worktrees` invocation, record its subcommand, the explicit state directory and
config path passed, the `OPENCLAW_PROFILE` value set or that it was unset, the absence of
`--profile` and `--dev`, and its result.
[measured 2026-10-26T03:55:06Z, this host, OpenClaw 2026.10.6 (41c5d94); the earlier
2026-10-25 reading has no capture located, so this replaces it; raw captures `gateway-status.json`,
`openclaw.json.copy`, `worktrees-list.json`, `gateway-status.err` and `worktrees-list.err`
preserved at
`/Users/brandonperfetti/dev/sansfaux/_agent/evidence/2026-10-25-agent-working-agreements-pr-181-gateway-worktree-inventory/`]
`openclaw gateway status --json` (empty stderr; output SHA-256
`2dbd291d1021280837b9192200db23fe75992968b642d93f4788b6629d34c81f`) reported a loaded launchd
service from `~/Library/LaunchAgents/ai.openclaw.gateway.plist` with
`"OPENCLAW_PROFILE": "default"`, `"OPENCLAW_STATE_DIR":
"/Users/brandonperfetti/.openclaw"` and `"OPENCLAW_CONFIG_PATH":
"/Users/brandonperfetti/.openclaw/openclaw.json"` under `service.command.environment`, and
`service.command.programArguments` contained only the recorded Bun and `dist/index.js` paths,
`--no-install`, `gateway`, `--port` and `18789`, with neither `--profile` nor a
root/profile-selecting `--dev`; thus its effective profile is that environment's `default`.
It also reported `config.daemon.path` set to
`/Users/brandonperfetti/.openclaw/openclaw.json`. That file, read in the same pass (SHA-256
`87027a892fc01a1464c5dc492389f196ef1494b2a01a03a79ac0dcd81fc668a3`), contains no `worktreeRoot`
string.
[superseded 2026-10-25] An earlier revision continued: "`openclaw worktrees list --json` (empty
stderr; output SHA-256 `3a25f8eae2dcf7c05707413dd65845a14330f7fad1365a23c3214b9fc5c040d0`)
recorded this delivery's worktree as …". That reading came from the capture whose bindings were
not recorded, `worktrees-list.json` with `worktrees-list.err` in the gateway-inventory directory
above, which stays preserved unchanged. It is superseded by the bound capture below and must not
be relied upon for the inventory claim. [measured 2026-10-25] That directory holds no argv,
invocation manifest or record of the state directory, config path or profile the invocation was
bound to; its `worktrees-list.json` SHA-256 equals that of the bound capture's `stdout.json`.
[inference] Equal bytes do not show which state directory, config or profile the earlier invocation
selected, so the earlier capture cannot support the inventory claim on its own; only the bound
capture does. No later reading can verify the earlier invocation's bindings, because they were never
recorded.
[measured 2026-10-26T04:37:53Z, this host, OpenClaw 2026.10.6 (41c5d94); raw captures
`argv.txt`, `argv-flag-check.txt`, `invocation-manifest.txt`, `run.sh`, `stdout.json`,
`stderr.txt`, `exit-status.txt`, `captured-at-utc.txt`, `openclaw-version.txt` and `SHA256SUMS`
preserved at
`/Users/brandonperfetti/dev/sansfaux/_agent/evidence/2026-10-25-agent-working-agreements-pr-181-bound-worktrees-list/`]
One `openclaw worktrees list --json` invocation ran with the call-local bindings
`OPENCLAW_STATE_DIR=/Users/brandonperfetti/.openclaw`,
`OPENCLAW_CONFIG_PATH=/Users/brandonperfetti/.openclaw/openclaw.json` and
`OPENCLAW_PROFILE=default`; its actual argv was
`/Users/brandonperfetti/.openclaw/bin/openclaw worktrees list --json`, with neither `--profile`
nor `--dev`. Its `invocation-manifest.txt` records those three call-local bindings exactly,
including `OPENCLAW_PROFILE=default` and the config path; `SHA256SUMS` records that manifest as
`f0d0408d0f68f42f38eb6dee5b312d88fa0d223b9658237a488d58293cdd0283`.
It exited 0 with zero-byte stderr (stdout SHA-256
`3a25f8eae2dcf7c05707413dd65845a14330f7fad1365a23c3214b9fc5c040d0`) and listed 26 entries, 17
active and 9 carrying `removedAt`. It recorded this delivery's
worktree as `"repoFingerprint": "3be5ac1eed078a0d"`, `"path":
"/Users/brandonperfetti/.openclaw/worktrees/3be5ac1eed078a0d/awa-180-protected-root-worktrees"`,
with `id`, `branch` and `repoRoot` set. That is one record; it does not cover every managed
worktree. [inference] The effective root here is the default
`/Users/brandonperfetti/.openclaw/worktrees`, outside `$AGENT_ROOT/_agent/`; what would verify it:
the service state directory still resolves to `/Users/brandonperfetti/.openclaw`, the service config
at `config.daemon.path` has no `worktreeRoot` key, and the recorded inventory path for a newly
created managed worktree lies under that root. Resolve it again for each delivery rather than
reusing this value.

[measured 2026-09-23, issue #24] Three delivery worktrees were created by commands that explicitly
selected the protected instruction-source root working tree with `git -C`; their presence violated
its then one-worktree contract even though the commands ran from the workspace root. Issue #180
supersedes only that topology assumption: the containment remains that no delivery operation alters
the protected instruction-source root working tree. It does not change runtime project bindings or
delete or migrate existing clones.

**After every `develop → master` merge, fetch and fast-forward the protected instruction-source
root working tree before any further work.** If any step below fails, exits nonzero, or finds a
mismatch, stop and report its command, exit status, and output; run no later step. Run
`git switch master`, then
`git fetch origin +refs/heads/master:refs/remotes/origin/master`. Then
`git status --porcelain --untracked-files=all` must exit 0 with empty output before any merge.
Then run `git merge --ff-only origin/master`. Finally, that status command must again exit 0 with
empty output, and `git rev-parse HEAD` must equal `git rev-parse --verify 'origin/master^{commit}'`.
The next report names the exact SHA the
protected instruction-source root working tree serves.
[measured 2026-09-23] PR #41 merged at `b733b59982736285d078ee9f67209bcce2fea957` on
2026-09-22T20:18:10Z, but the protected instruction-source root working tree remained six commits
behind until the next day.

**Remove a delivery worktree and its local branch once its feature PR has merged into `develop`.**
These safeguards govern only this manual post-merge cleanup route, for every delivery worktree it
removes, managed or an existing plain Git worktree; they do not bind OpenClaw's own background
cleanup (see the background-cleanup paragraph after this procedure).
Run it from any of the repository's worktrees; the protected instruction-source root working tree
may serve, but only for Git administration and never against its working tree. First read
`git worktree list --porcelain` once and keep that output; if it cannot be read, stop, and retain
and report the worktree and branch. That one read, taken before any other cleanup step, is the
protected-worktree inventory's source and the only source for `<path>` below. Then fetch
`develop` by name, not through the configured refspec:
`git fetch origin +refs/heads/develop:refs/remotes/origin/develop` — if the fetch fails, stop, and
retain and report the worktree and branch — then
`git merge-base --is-ancestor <branch> origin/develop`. Exit 0 is the only permission, and
not by itself enough: the protected instruction-source root working tree, another protected base
worktree such as a release-review worktree, a dirty delivery worktree, and a branch that is not an
ancestor of `origin/develop` are all retained and reported. The protected instruction-source root
working tree is never eligible for cleanup. `<path>` is the canonical form, with every symlink
resolved, of the value of the `worktree` line of the unique record in that output whose `branch`
line is `refs/heads/<branch>`; on zero or multiple matches, stop, and retain and report the branch
and every candidate worktree. If that value cannot be canonicalized, or a lookup of `<path>` itself
does not positively report that it exists, stop, and retain and report the worktree and branch.
The authoritative protected-worktree inventory is the protected instruction-source root working
tree named under [Startup and mode](#startup-and-mode) plus every record of that output that is a
protected base worktree: the first record, which is the main working tree of the clone being
cleaned; every record whose `branch` line is `refs/heads/master` or `refs/heads/develop`, or that
has a `detached` line, which covers a release-review worktree checked out on its base; and every
record with a `locked` line, whatever its reason. A protected base worktree on any other branch is
in the inventory only through its lock, so lock it with
`git worktree lock --reason 'protected base worktree' <worktree>` when it is created. The inventory
is indeterminate, and the cleanup stops, retaining and reporting the worktree, branch, and every
unclassified record, if any record lacks a `worktree` line or any record after the first has
neither a `branch` nor a `detached` line. Canonicalize the named root and the path of every
worktree in that inventory, with every symlink resolved, and compare each with `<path>`; if any of
them cannot be canonicalized or equals `<path>`, stop, and retain and report the worktree and
branch, with no inventory query, removal route, or branch deletion. Then run
`git --no-optional-locks -C <path> status --porcelain --untracked-files=all --ignored`; ignored
files count, since [inference] `git worktree remove` without `--force` deletes them. What would
verify it: in a disposable repository, add a worktree whose only local content is a file matched by
`.gitignore`, run `git worktree remove <worktree>` without `--force`, and check that it exits 0
and the file is gone. [corrected 2026-10-26] An earlier revision labelled that claim "[measured
2026-10-25, Git 2.56.0, a scratch repository; recorded in commit
`adef2b1e7d6f2d3a4572d68802a6ed24edd661b7`]", which must not be relied upon: no raw output of
that scratch-repository run was preserved, and that commit only introduced the wording, so it
locates the claim's history, not a measurement. If that status command exits nonzero, cannot be
run, or prints any output, stop, and retain and report the worktree and branch with its exit
status and output. Only exit 0 with empty output permits cleanup to continue. Then pick the
removal route from OpenClaw's registered inventory. Run:

```sh
env <profile-binding> \
  OPENCLAW_STATE_DIR=<state-dir> \
  OPENCLAW_CONFIG_PATH=<config-path> \
  openclaw worktrees list --json
```

if it cannot be read, stop, and retain and report the worktree and branch:

- **Managed worktree.** Canonicalize the `path` of every `worktrees` record, with every symlink
  resolved, before matching. Skip a record only when the lookup of its `path` positively reports
  no such file and its `branch` is not `<branch>`, since it cannot equal `<path>`, which is
  canonical and was positively confirmed to exist above. If such a record's `branch` is
  `<branch>`, or on any other failure to canonicalize or determine a record's `path`, including
  an existence lookup that cannot say, stop, and retain and report the worktree, branch, and
  record. `<id>` is the `id` of the unique `worktrees` record whose canonical `path` is `<path>`;
  on zero matches the worktree is not managed. On multiple matches, or a match whose `branch` is
  not `<branch>`, stop, and retain and report every candidate record. Run this explicitly bound
  command:

  ```sh
  env <profile-binding> \
    OPENCLAW_STATE_DIR=<state-dir> \
    OPENCLAW_CONFIG_PATH=<config-path> \
    openclaw worktrees remove <id> --if-lossless --json
  ```

  Only `removed: true` is a successful removal; `removed: false` is a retention, reported with its
  recorded `cleanup` outcome. Never run
  ordinary `openclaw worktrees remove <id>`, which removes with Git force, or `--force`, and never
  fall back to `git worktree remove` for a registered worktree.
- **Existing plain Git worktree.** Only a worktree with no inventory record and outside the resolved
  managed worktree root qualifies; one with no record inside that root is retained and reported.
  Immediately before removal, repeat the
  `git --no-optional-locks -C <path> status --porcelain --untracked-files=all --ignored` check,
  which must again exit 0 with empty output, and read `git worktree list --porcelain` again, which
  must contain exactly one record whose canonical `worktree` path is `<path>`, with `branch` line
  `refs/heads/<branch>`. On any failure, output, or mismatch, stop, and retain and report the
  worktree and branch. Then run `git worktree remove <path>` without `--force`.

On exit 0, with one match, and outside those exclusions, remove by that route; then, only if that
removal succeeded and `refs/heads/<branch>` still exists, `git branch -d <branch>`. Any refusal or
retention from either command is left as it is and reported, never overridden. The cleanup audit
records the inventory read and its output, each record's classification with the line that decided
it, and every canonicalization and comparison the cleanup makes with its outcome, including a
failure or a stop: the named root and each inventory worktree, each compared with `<path>`; every
candidate record for `<branch>`, and `<path>` with its existence lookup; the clean-status check of
`<path>` with its exit status and output; each `worktrees` record's canonical `path`, or its skip
with the existence lookup that allowed it, compared with `<path>`,
and its `branch` compared with `<branch>`; and, on the plain Git route, the check of `<path>`
against the resolved managed worktree root and the repeated status and inventory checks with their
outputs.
[measured 2026-09-23, issue #57] The delivery host went from 13 to 16 registered worktrees in one
delivery cycle; the dry-run and live cleanup the ticket records then removed 14 merged worktrees
and their branches without forcing a dirty removal, leaving the protected delivery host plus a
release-review worktree.

**OpenClaw's background cleanup can purge a managed delivery worktree outside that manual route.**
[source: `managed-worktrees.md` lines 95 and 379–380] [inference] It does not apply that route's
safeguards: none of them appears among the cleanup rules or the eviction policy; what would verify
it: re-read `managed-worktrees.md` lines 87–101 and 376–392 for any of those checks.
[source: `managed-worktrees.md` lines 77, 87, 95, 101, 379–382 and 693] Capacity
eviction enforces `worktreeMaxCount` (default 4096) across every owner sharing the state directory:
it removes checkouts on branches merged into the default branch first, then squash-landed ones, then
idle checkouts from oldest last use, and manual worktrees (managed worktrees created manually,
recorded with `ownerKind: manual`) and unsaved data are eligible. Idle
cleanup snapshots and removes unlocked session- and Workboard-owned worktrees idle for more than 7
days, even when dirty, and a session worktree whose owner is archived or absent without waiting.
OpenClaw snapshots dirty contents when it can, but snapshot failure does not block cap eviction;
a snapshot record stays restorable for 30 days. Live owner leases protect active runs, and creation
that would have to evict one is refused, naming the cap and live owners. Ordinary idle cleanup
preserves foreign or unrecognized Git worktree locks. [inference] A lock, including the
`protected base worktree` lock above, does not protect a managed checkout from cap eviction: the
cap's stated exemptions name only live owner leases, and remembered idle-cleanup protection never
exempts a checkout from it [source: `managed-worktrees.md` lines 95, 101 and 392]; what would
verify it: in a scratch state directory, a locked, idle managed checkout evicted after
`worktreeMaxCount` is lowered below the live count. Mitigation
[source: `managed-worktrees.md` lines 87, 95, 101 and 381]: commit or otherwise back up work you
need to retain before leaving a managed delivery worktree inactive, and keep the live managed
worktree count below `worktreeMaxCount`, raising it in `openclaw.json` when needed. A snapshot
record, when one was made, stays restorable for 30 days; that text does not say whether eviction
keeps or deletes the checkout's branch or commits, so it shows committed work neither lost nor
retained.

## Pickup guard and delivery audit

Record the checkout and HEAD, Git author identity, `core.hooksPath` and hook presence, an explicit
dry-run probe (or N/A when the repository installs no `pre-push` hook), the full gate result,
branch ownership, and target-protection audit. For a delivery worktree, also record the Gateway
service's state directory with the source that supplied it (service `OPENCLAW_STATE_DIR`; with
no explicit state directory, service `OPENCLAW_HOME` or service home plus `/.openclaw`; or, only
when the service's command arguments carry `--profile <name>` or a root/profile-selecting `--dev`,
not a Gateway `--dev`, the `applyCliProfileEnv` result such as `/.openclaw-<name>`), its
command-line profile if any and its environment
`OPENCLAW_PROFILE` value, its config path with its source, the resolved managed worktree root and
its source (`worktreeRoot` or the default), the worktree path, its registered inventory record,
each `openclaw worktrees` invocation with the explicit state directory and config path passed, the
`OPENCLAW_PROFILE` value set or that it was unset, the absence of `--profile` and `--dev`, and its
result, the cleanup audit with every canonicalization and comparison outcome, the cleanup route
with its `id` or plain Git path, and the `_agent/` and protected-root overlap check; any overlap
stops the delivery (see
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
