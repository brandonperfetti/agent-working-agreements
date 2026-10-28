# Managed delivery worktrees and the protected root

This procedure carries mechanics for `clients/openclaw.md` and the rule it implements in
[`../../AGENT-WORKING-AGREEMENTS.md`](../../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts
A–B, and a rule here that contradicts one there is the rule that is wrong. The text below was moved
out of the appendix verbatim on 2026-10-27; evidence paragraphs that carried hashes went to
`history/openclaw.md`.

**Trigger:** Pickup of a delivery in OpenClaw: creating a delivery worktree, refreshing the
protected instruction-source root after a release, or removing a worktree after its PR merged.

**Owner:** The delivery owner for repository and worktree capability; Ashford for the Gateway
service context; Bull for host and runtime facts.

**Implements:** A6 (one store, no clones under `_agent/`), B2's git contract, and
`clients/openclaw.md` *Delivery topology*.

**Stop:** Any failed fetch, OID mismatch, dirty tree, path overlap or unreadable inventory: stop,
retain and report; never force. The stop names its restoration owner (B2 item 5).

---

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

[measured 2026-09-23, issue #24] Three delivery worktrees were created by commands that explicitly
selected the protected instruction-source root working tree with `git -C`; their presence violated
its then one-worktree contract even though the commands ran from the workspace root. Issue #180
supersedes only that topology assumption: the containment remains that no delivery operation alters
the protected instruction-source root working tree. It does not change runtime project bindings or
delete or migrate existing clones.

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

[source, B0 and Startup and mode] Future OpenClaw work still re-evaluates B0 for its exact
checkout and path as capability evidence, not as the B1/B2 mode selector.
