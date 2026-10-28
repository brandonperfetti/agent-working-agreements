# Native sandbox breaker (dormant)

This procedure carries mechanics for `clients/openclaw.md` and the rule it implements in
[`../../AGENT-WORKING-AGREEMENTS.md`](../../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts
A–B, and a rule here that contradicts one there is the rule that is wrong. The text below was moved
out of the appendix verbatim on 2026-10-27; evidence paragraphs that carried hashes went to
`history/openclaw.md`.

**Trigger:** A native shell or patch call returns the exact Bubblewrap/namespace/AppArmor prelaunch
signature quoted in `clients/openclaw.md` before the target produces any output. The Mac mini has no
Bubblewrap [measured 2026-10-27, #186]; this fires only on a host that does.

**Owner:** The session that saw the strike; Ashford for the cross-session record; Bull for host
facts.

**Implements:** B0's OpenClaw exception and `clients/openclaw.md` *Dormant: the native sandbox
breaker*.

**Stop:** No bounded route for the operation: stop and report the missing capability and its owner;
never weaken the sandbox.

---

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
