# Claude Code hooks

User-level hooks that enforce part of the Sans Faux profile in Claude Code. They run on every
session on the Mac they are installed on, whatever the repository. Each stops honest mistakes,
not a determined bypass; the profile's rules still hold where a hook does not reach (MCP tools,
other clients, git aliases).

| Hook | Event | What it does |
| --- | --- | --- |
| `guard_git.py` | `PreToolUse`, matcher `Bash`, fails closed (Claude Code 2.1.295 or later) | Denies force-pushes, pushes to `master` or `main`, PR merges into `develop`, `main` or `master` (or whose base it cannot read), and commits or pushes whose author is not `brandon@brandonperfetti.com` or whose message carries an attribution trailer (RULE ZERO); a message fed on stdin (`-F -`, a here-string, a pipe) or filled in by the shell (`-m "$MSG"`) is denied as uncheckable, and a substituted message is read only as `-m "$(cat <<'TAG' … TAG\n)"`, and a `-F` file named by an earlier command in the line counts as unreadable |
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
block of `~/.claude/settings.json`. Every other setting and every other hook stays as it was;
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
tmp=$(mktemp -d) && git -C ~/dev/sansfaux/agent-working-agreements archive origin/develop hooks/claude-code | tar -x -C "$tmp" && /usr/bin/python3 "$tmp/hooks/claude-code/install.py"; rm -r "$tmp"
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
