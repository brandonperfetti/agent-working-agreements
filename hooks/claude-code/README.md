# Claude Code hooks

User-level hooks that enforce part of the Sans Faux profile in Claude Code. They run on every
session on the Mac they are installed on, whatever the repository. Each stops honest mistakes,
not a determined bypass; the profile's rules still hold where a hook does not reach (MCP tools,
other clients, git aliases).

| Hook | Event | What it does |
| --- | --- | --- |
| `guard_git.py` | `PreToolUse`, matcher `Bash`, fails closed | Denies force-pushes, pushes to `master` or `main`, PR merges, and commits or pushes whose author is not `brandon@brandonperfetti.com` (RULE ZERO) |
| `agreements_after_compact.py` | `SessionStart`, matcher `compact` | Restates RULE ZERO, the mode and the agreement paths after each compaction |

## Install or update

From this clone, on each Mac:

```bash
/usr/bin/python3 ~/dev/sansfaux/agent-working-agreements/hooks/claude-code/install.py
```

`install.py` copies the two hooks into `~/.claude/hooks/` and registers them in the `hooks`
block of `~/.claude/settings.json`. Every other setting and every other hook stays as it was;
`settings.json` is backed up beside itself before it changes. Re-running it updates a hook
already registered rather than adding it twice. Start a new session afterwards.

It copies rather than links: a branch switched in this clone never changes the hooks a running
session uses. To see whether a Mac has drifted from this folder, run it with `--check` (exit 1 on
any difference); `--dry-run` says what an install would change and writes nothing.

Until this folder reaches `master`, install from `develop` without switching the clone's branch:

```bash
git -C ~/dev/sansfaux/agent-working-agreements fetch origin
```

```bash
tmp=$(mktemp -d) && git -C ~/dev/sansfaux/agent-working-agreements archive origin/develop hooks/claude-code | tar -x -C "$tmp" && /usr/bin/python3 "$tmp/hooks/claude-code/install.py"
```

## Change a hook

Edit it here, never in `~/.claude/hooks/`, then run the tests and reinstall:

```bash
/usr/bin/python3 -m unittest discover -s hooks/claude-code
```

A live probe that the guard is loaded: `gh pr merge --help` in a Claude Code session is denied.
