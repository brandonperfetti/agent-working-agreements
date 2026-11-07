# Git hooks

Hooks git itself runs, on every repository on the Mac they are installed on and whatever client
made the commit. They check where git holds the fact, so no client-side parsing of shell text is
needed. Each stops honest mistakes, not a determined bypass.

| Hook | When git runs it | What it does |
| --- | --- | --- |
| `commit-msg` | After the message is final, before the commit object is written | Denies a commit whose message file carries a `Co-Authored-By`, `*-Session` or "generated with" line (the staged diff `commit -v` appends included, since the hook cannot tell whether git will keep it), or whose author email is not `brandon@brandonperfetti.com` (RULE ZERO), printing the fix; then runs the repository's own `commit-msg` hook if it has one |
| `chain-repo-hook` | Installed under every other hook name git knows | Runs the repository's own hook of that name, so a global `core.hooksPath` hides no repository check |

## Install or update

The Claude Code installer carries this folder too:

```bash
/usr/bin/python3 ~/dev/sansfaux/agent-working-agreements/hooks/claude-code/install.py
```

It copies `commit-msg` into `~/.config/git/hooks/`, links `chain-repo-hook` there under every other
hook name, and, when `core.hooksPath` is unset, points the global setting there. A `core.hooksPath`
already set elsewhere is reported and left alone; to use these hooks there, have that folder's own
`commit-msg` and `applypatch-msg` run the installed `commit-msg` under their own names (a symlink,
or `exec -a applypatch-msg ~/.config/git/hooks/commit-msg "$@"`: the script reads the patch author
only when it runs as `applypatch-msg`), never when that folder is a repository's own `.git/hooks`
(the installed hook would then run it again, and the two would loop). The installer never repoints a
set path, and refuses a folder holding other files under the names it manages. `--check` and
`--dry-run` behave as for the Claude Code hooks.

## Reach and limits

A repository that sets its own `core.hooksPath` (a husky repository, for one) does not run the
global hooks; git takes the repository's setting first. `git commit --no-verify` skips every
commit-msg hook, and the Claude Code guard denies it on `git commit` and `git merge`. `git
cherry-pick` and `git rebase` write commits without running it and keep the author and message they
import; a merge commit runs it (a fast-forward makes no commit). The Claude Code guard's push-time
scan is a best-effort read: it checks the commits reachable from the pushed sources that the
destination remote's tracking refs do not already hold, so stale tracking refs or a remote git
chooses by configuration the guard does not read can leave a commit unscanned. The complete check is
the RULE ZERO read before a delivery is pushed, merged or presented
(`procedures/rule-zero-check.md`).
