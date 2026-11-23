# Managed delivery worktrees and the protected root

**Trigger:** Pickup of a delivery in OpenClaw: creating a delivery worktree, refreshing the
protected instruction-source root after a release, or removing a worktree after its PR merged.

**Owner:** The delivery owner for repository and worktree capability; Ashford for the Gateway
service context; Bull for host and runtime facts.

**Implements:** A6 (one store, no clones under `_agent/`), B2's git contract, and
`clients/openclaw.md` *Delivery topology*.

**Stop:** Any failed fetch, OID mismatch, dirty tree, path overlap or unreadable inventory: stop,
retain and report; never force. The stop names its restoration owner (B2 item 5).

This procedure implements the canonical agreement; it never overrides Parts A–B, and
a rule here that contradicts one there is the rule that is wrong. Two harms shape it: a delivery
that moves the protected root moves the instructions every agent reads, and a forced removal loses
work. Each step's checks are commands in
[`scripts/openclaw/runbook.sh`](../../scripts/openclaw/runbook.sh), whose stop and retention
branches CI tests (#191). Each prints its audit lines and stops or retains on any failed check.
Cleanup runs only through `runbook.sh cleanup`, whose exact matching of one record to one branch is
what keeps it from removing the wrong worktree; the other steps may be run by hand.

## Instruction-source isolation and freshness

The protected root stays clean, on `master`, and equal to `origin/master` once each release is
refreshed. Its Git administration may host delivery worktrees; delivery edits, commits, branch
switches and cleanup never target its working tree.

**Create** a delivery worktree only through OpenClaw's managed facility, from a base you captured:

1. `runbook.sh capture-base <repo-root>` fetches `develop` and `master` by name, checks each against
   `ls-remote`, and prints the base OID.
2. `runbook.sh check-overlap --agent-store <store> --protected-root <root> <managed-root>` before
   the create: the managed root (below) may not lie inside or contain either, and one it cannot
   resolve stops too.
3. Create with that OID, never the moving name. Without `--base-ref`, OpenClaw can fast-forward the
   protected root's checked-out branch.

   ```sh
   env <profile-binding> OPENCLAW_STATE_DIR=<state-dir> OPENCLAW_CONFIG_PATH=<config-path> \
     openclaw worktrees create <repo-root> --name <name> --base-ref <base-oid>
   ```

4. `runbook.sh verify-head <path> <base-oid>` before any edit, and
   `runbook.sh check-overlap --agent-store <store> --protected-root <root> <managed-root> <path>`:
   neither path may lie inside or contain the `_agent/` store or the protected root.

**Bind every `openclaw worktrees` command to the Gateway service's context**, not the probing
shell's. Take the service's state directory, config path and profile from its own environment and
command arguments (`openclaw gateway status` shows the config paths it uses). The managed root is
`worktreeRoot` in that config, else `<state-dir>/worktrees`. Pass both paths explicitly, with
`<profile-binding>` set to `OPENCLAW_PROFILE=<service-profile>` or `-u OPENCLAW_PROFILE`. Never pass
`--profile` or `--dev`: either can swap the state directory you passed for a profile's own. If the
service's context cannot be determined, stop and report what you resolved.

**After every `develop → master` merge**, run `runbook.sh refresh-root <protected-root>` before
further work: clean status, `git switch master`, a named fetch of `master`, `git merge --ff-only`,
clean status again, `HEAD` equal to `origin/master`. Report the SHA the root now serves.

## Cleanup after merge

Remove a delivery worktree and its branch once its PR has merged into `develop`, losing nothing:

- **Quiescence first.** The delivery owner guarantees nothing writes to the worktree until removal
  and records that guarantee (#279).
- **Eligible only** if the branch is an ancestor of a freshly fetched `origin/develop`, its status
  is empty with ignored files counted, and `git ls-files -v` shows no `assume-unchanged` or
  `skip-worktree` entry. A non-forced `git worktree remove` deletes ignored files, and neither
  status nor removal sees edits behind those two flags.
- **Never eligible:** the protected root, the clone's main working tree, any worktree on `master`
  or `develop`, detached, or locked. Lock a protected base worktree on another branch when you
  create it (`git worktree lock --reason 'protected base worktree' <worktree>`).
- **Route:** a registered worktree goes through bound `openclaw worktrees remove <id> --if-lossless
  --json`, where only `removed: true` is a removal; never plain `remove`, `--force`, or a fallback
  to `git worktree remove`. A plain Git worktree outside the managed root takes
  `git worktree remove <path>` without `--force`. Then `git branch -d <branch>`. A refusal or
  retention is reported, never overridden.

`runbook.sh cleanup` runs all of this; it takes every path, the bound context and
`--quiesced-by <owner>` explicitly, with no defaults. Run it while a Gateway owns the local state:
an offline `openclaw worktrees list` can retire missing checkouts.

**OpenClaw's own background cleanup does not apply these checks.** Cap eviction
(`worktreeMaxCount`) and idle cleanup can remove a managed checkout even when it is dirty, and a
lock does not exempt it from cap eviction; a snapshot, when one is made, stays restorable for 30
days. Push or commit what you need before leaving a worktree idle, and keep
the live count below the cap.

## Pickup audit

Record the checkout and `HEAD`, author identity, `core.hooksPath` and hook presence, the dry-run
probe (or N/A), the gate result, branch ownership, target protection, and for a delivery worktree
the resolved state directory, config, profile and managed root with where each came from, plus the
`runbook.sh` audit lines. Any overlap stops the delivery.
