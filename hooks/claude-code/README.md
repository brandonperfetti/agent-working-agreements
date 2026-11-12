# Claude Code hooks

User-level hooks that enforce part of the Sans Faux profile in Claude Code. They run on every
session on the Mac they are installed on, whatever the repository. Each stops honest mistakes,
not a determined bypass; the profile's rules still hold where a hook does not reach (MCP tools,
other clients, git aliases).

| Hook | Event | What it does |
| --- | --- | --- |
| `guard_git.py` | `PreToolUse`, matcher `Bash`, fails closed (Claude Code 2.1.295 or later) | Denies force-pushes, pushes to `master` or `main` (the matching refspec `:` and `--all` included), PR merges into `main` or `master` (or whose base it cannot read), PR merges into `develop` in any form but the delegated route's one (below), git or gh arguments fed through `xargs`, a commit that skips the commit-msg hook (`--no-verify`; a courtesy read of the command's words, so a shape that hides the flag from them skips the hook; the push-time scan and the read before presentation are the controls for that shape), a push with a `-c` setting or whose targets `remote.<name>.push` would choose, and, best effort, a push whose commits new to the destination remote's tracking refs carry another author or an attribution line (RULE ZERO). The author and message of a commit being made are [`../git/commit-msg`](../git/README.md)'s to read; the complete read is the one before a delivery is presented |
| `agreements_after_compact.py` | `SessionStart`, matcher `compact` | Restates RULE ZERO, the mode and the agreement paths after each compaction |
| `look_again.py` | `Stop` | Sends the agent back once when a file it read or wrote since your last prompt has changed since, naming the file, so it reads it again before it reports |

`look_again.py` sees only the files the agent touched with its file tools since your last prompt;
a file it later named in a Bash command counts as seen. A file gone with its folder (a removed
worktree) and Claude Code's own temp tree are not reported. It reports each change once and sends
one chain of stops back at most three times. A check that needs more, such as re-fetching an index
or running the tests, belongs in that project's own `Stop` hook in its `.claude/settings.json`.

## Install or update

From this clone, on each Mac:

```bash
/usr/bin/python3 ~/dev/sansfaux/agent-working-agreements/hooks/claude-code/install.py
```

`install.py` copies the three hooks into `~/.claude/hooks/` and registers them in the `hooks`
block of `~/.claude/settings.json`; it also installs the git hooks under
[`../git`](../git/README.md). Every other setting and every other hook stays as it was;
`settings.json` is backed up beside itself before it changes. Re-running it updates a hook
already registered rather than adding it twice. Start a new session afterwards.

Fail-closed rests on the hook's `onFailure: "block"`, which Claude Code reads from 2.1.295 on;
an older version lets a Bash call through when the guard crashes or times out. Check
`claude --version` on a Mac before relying on it.

It copies rather than links: a branch switched in this clone never changes the hooks a running
session uses. To see whether a Mac has drifted from this folder, run it with `--check` (exit 1 on
any difference); `--dry-run` says what an install would change and writes nothing.

Until this folder reaches `master`, install from `develop` without switching the clone's branch:

```bash
git -C ~/dev/sansfaux/agent-working-agreements fetch origin
```

```bash
tmp=$(mktemp -d) && git -C ~/dev/sansfaux/agent-working-agreements archive origin/develop hooks | tar -x -C "$tmp" && /usr/bin/python3 "$tmp/hooks/claude-code/install.py"; rm -r "$tmp"
```

## Change a hook

Edit it here, never in `~/.claude/hooks/`, then run the tests and reinstall:

```bash
/usr/bin/python3 -m unittest discover -s hooks/claude-code
```

A live probe that the guard is loaded: `gh pr merge --help` in a Claude Code session is denied.
The guard reads a PR's base with `gh pr view` (or `gh api` for a REST merge), so a merge between
feature, wave, lane or hotfix branches passes; it refuses when that read fails. `gh pr merge
--auto` is refused whatever the base, since a stacked PR can be retargeted to `develop` before
it lands.

A call that names `gh` and a merge (read past quotes and line continuations) is read only as one
simple `gh` command: assignments, then `gh` or its path, then plain or quoted words with no
expansion, and at most a trailing `2>&1`; a simple `git` command without `-c` whose values name
them is read as git. Beside a chain, substitution, wrapper, shell `-c`, continuation or other
redirect, a merge is refused whatever the base, since the base read could be stale or of another
PR by the time it runs; a merge naming its repository twice is refused too, and so is a git or
gh command behind wrapper options (`env -u`, `env -S`, `sudo -u`). Into `develop` exactly one
form passes, the delegated route of
[`review-findings.md`](../../procedures/review-findings.md#base-merges), as the whole tool call
in plain words (no prefix, wrapper, path, quote, redirect, chain, background, `eval` or `sh -c`):
`gh pr merge <N> --repo <owner/name> --merge --match-head-commit <40-hex> --author-email
brandon@brandonperfetti.com`, each flag once and no other (no squash, rebase, `--admin`, `--auto`,
branch deletion or message). Every `gh api` merge into `develop` stays refused. This checks form,
not whether the route is active or the PR eligible; those are the procedure's. Its limits: the
base is read before the command runs, so another session's retarget in that window is not caught
(only the head is pinned on the server); shell functions, `PATH`, `gh` aliases and extensions are
not resolved; and on a base with a merge queue `gh` may enqueue rather than merge.
