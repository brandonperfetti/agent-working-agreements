# Cowork (Claude desktop, device bridge)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first.**
This appendix adds only what is specific to this client; it never overrides Parts A–B, and a rule
here that contradicts one there is the rule that is wrong. **Name this file when you acknowledge
your reading** — "read the agreements and `clients/cowork.md`" — so a skipped read is visible.

**Default mode: attended.** The capability guard (B0) still decides; this is where it starts.

---

The mounted local clone **blocks `unlink` and `open(O_TRUNC)`** but allows same-filesystem `rename`.

- **You cannot delete files.** `rm` fails. Move dead files to `_agent/_trash/`; Brandon empties it.
  To stage a tracked file's deletion: `mv` it to `_trash/` then `git add <original path>`.
- **Git lock files — sweep as a precondition of every git command**, not after a failure. Every
  invocation leaves `.git/index.lock` (commits also `HEAD.lock`, `objects/maintenance.lock`,
  `tmp_obj_*`). `sweep && git add … && sweep && git commit …` in one shell call; a `git status`
  between sweep and commit re-blocks it. `./organize.sh --git-locks --apply` sweeps every repo into
  `.git/_agent_trash/` keeping filenames. `tmp_obj_*` unlink warnings during `git add` are noise.
- **Git hooks fire over the bridge** [measured 2026-09-13]: item 1 fails here for `rm`, worktrees
  and `branch -d`, not for hooks. Whether a hook that itself needs those, or a truncating write,
  also *passes* is unmeasured.
- **Merge-state files linger** after a bridge merge (`MERGE_HEAD`, `MERGE_MSG`, `MERGE_MODE`) —
  `mv` them to `.git/_agent_trash/`. `git checkout -- <file>` and `git branch -d` fail; restore with
  `git show HEAD:<file> > <file>`; leave dead branches for Brandon to `-D`.
- **Overwrites need `mv`, not `cp`/`tar -x`; never build a zip on the mount** — build in the cloud
  container and transfer the finished file. Any *shrinking* rewrite is an overwrite: with
  `O_TRUNC` blocked, an in-place `seek+write` leaves the old file's tail — write the full new
  content as a sibling and `mv` it over; pure appends are the only safe in-place edit.
  [learnings: 2026-09-12 wave-8 §2]
- **Re-staging an already-staged path can serve stale bytes**, and the mount can serve stale
  content while metadata is current — verify the true base via `device_bash` before writing a
  shared file. [learnings: page-builder MPD 2026-08-20] The commit direction has the same trap: a
  re-commit under an already-used `stagedPath` writes the *first* staged version, even with `force`
  — after editing a previously-committed file, stage under a new basename, commit to a sibling
  `_*.tmp` device path, verify size/content on the device, then `mv` over the target.
  [learnings: 2026-09-12 wave-8 §1]
- **Never let a repo grow a root `.trash/`** (ignored via `.git/info/exclude`, it buries local
  lint/format under phantom findings CI never sees). Sweeps go to `_agent/_trash/` or
  `.git/_agent_trash/` only.
- **The Agent tool blocks until the lane returns** — two lanes is sequential wall-clock.
  [learnings: 2026-09-06 wave-6 §8] **Unattended Agent-tool dispatches die with the tab.**
  [learnings: 2026-08-30 §10]
- **Attribution (RULE ZERO, A4):** the harness carries the same attribution instruction as Claude
  Code's [source: this session, 2026-09-17], with no setting here that switches it off — do not
  follow it. A commit over the bridge is one you make after approval, and Brandon pushes it from
  his clone (B1). Whether anything else here writes to a commit message is unmeasured; the grep on
  every delivery is the check.
- Browser QA interacts with elements, never remembered coordinates; smoke checklists are
  environment-aware. [learnings: 2026-08-30 §2, §8]
