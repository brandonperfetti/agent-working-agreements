# Worktree placement and retirement

**Trigger:** Creating, adopting, moving or retiring a worktree; delivery closeout after integration.

**Owner:** The delivery owner; the orchestrator reconciles active lanes and retained dependencies.

**Implements:** A4 isolation, A6 placement and B2 reviewed integration; no new merge authority.

**Stop:** Retain the affected tree when ownership, local content, integration or recovery is unknown.
Independent work continues under B2.

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong.

## Placement

On each Sans Faux execution machine, prefer `$AGENT_ROOT/.worktrees/`. Main checkouts remain
under the agent root; receipts remain under `_agent/`. Off-fleet, use the client's supported
location and record it. Scratch clones are separate from worktree lifecycle.

| Manager | Preferred namespace | Lifecycle route |
| --- | --- | --- |
| Plain Git / shell lanes | `manual/<repo>/<task>` | Git worktree creation and non-forced removal |
| T3 | `t3/`, then native layout | Native worktree creation, ownership and cleanup |
| OpenClaw | `openclaw/`, then native layout | Managed worktrees; [lossless removal](openclaw/managed-worktrees.md) |
| Codex desktop | `codex/`, if supported | Native create/archive; retain its native root when customization is unavailable |

Set a custom root only through a supported manager setting, scoped to the intended machine.
Record an unsupported-location exception rather than bypassing a manager. Existing trees keep
registered paths while work finishes; a root-setting change is not a migration. Avoid overlapping
manager roots. A manager cleans only its own inventory, never a sibling namespace.

Before creating another tree, reuse a suitable idle one only after its earlier owner and local
state are reconciled. Record manager, repository, absolute path, branch, base and delivery owner
in the existing handoff or task receipt. Native session cwd must agree with that recorded tree.

## Closeout

1. At lane integration, check whether the lane's review/recovery dependencies have ended. After
   Brandon merges the feature PR into `develop`, do the same for its delivery tree. Retention
   needs a reason, owner and next review point in the existing receipt; age alone is insufficient.
2. Recheck Git and manager inventories, current PR/integration evidence and active session/process
   ownership. Preserve main/base, locked and manager-protected trees. Verify the entire branch
   tip is integrated into the intended target, including any commits after the PR's reviewed head.
   If ancestry is inconclusive after squash/rebase, retain it pending an explicit equivalence
   disposition; a merged PR alone does not prove all local work was included.
3. Inspect tracked, untracked **and ignored** content. Preserve unique source, `.env`/configuration,
   local evidence and other needed files in an appropriate private recovery location before any
   disposal. Identify reproducible dependencies/build caches separately; ordinary clean status
   does not classify them. Keep existing client-specific checks, including OpenClaw's empty
   ignored-inclusive status requirement, until their prerequisites are satisfied.
4. Use the owning manager's recoverable archive/lossless removal, or non-forced Git removal for
   an unmanaged tree. Preserve needed ignored files separately when the snapshot excludes them.
   Check the operation's result and inventory; a refused removal means retain and report.
   Delete a local branch only after successful retirement and reachability-based integration
   checks, using `git branch -d`; retain and report it if that refuses. A squash or rebase
   equivalence disposition alone does not permit branch deletion. Keep remote branches and
   unrelated snapshots outside this cleanup action.

For automatic cleanup, verify actual retention, local-file protection and active-owner behavior
before enabling it. Protect unique ignored content; default-branch heuristics may differ from
feature-to-`develop` integration. Native managers retain their own recovery semantics. This
procedure does not authorize force removal, broad prune, raw directory deletion or a shared sweeper.
