# Git hooks

Hooks git itself runs, on every repository on the Mac they are installed on and whatever client
made the commit. They check where git holds the fact, so no client-side parsing of shell text is
needed. Each stops honest mistakes, not a determined bypass.

| Hook | When git runs it | What it does |
| --- | --- | --- |
| `commit-msg` | After the message is final, before the commit object is written | Denies a commit whose message carries a `Co-Authored-By`, `*-Session` or "generated with" line, or whose author email is not `brandon@brandonperfetti.com` (RULE ZERO), printing the fix |

## Install or update

The Claude Code installer carries this folder too:

```bash
/usr/bin/python3 ~/dev/sansfaux/agent-working-agreements/hooks/claude-code/install.py
```

It copies `commit-msg` into `~/.config/git/hooks/` and, when `core.hooksPath` is unset, points
the global setting there. A `core.hooksPath` already set elsewhere is reported and left alone:
move that hook set under `~/.config/git/hooks/` or chain this one from it by hand. `--check` and
`--dry-run` behave as for the Claude Code hooks.

## Reach and limits

A repository that sets its own `core.hooksPath` (a husky repository, for one) does not run the
global hooks; git takes the repository's setting first. `git commit --no-verify` skips every
commit-msg hook. Both are covered by the Claude Code guard, which denies `--no-verify` and reads
the author and message of every commit a push would send, and by the RULE ZERO check before a
delivery is presented (`procedures/rule-zero-check.md`).
