# Claude Code hooks

User-level hooks that enforce part of the Sans Faux profile in Claude Code. They run on every
session on the Mac they are installed on, whatever the repository. Each stops honest mistakes,
not a determined bypass; the profile's rules still hold where a hook does not reach (MCP tools,
other clients).

| Hook | Event | What it does |
| --- | --- | --- |
| `guard_git.py` | `PreToolUse`, matcher `Bash`, fails closed (Claude Code 2.1.295 or later) | Denies force-pushes, pushes to `master` or `main` (the matching refspec `:` and `--all` included), PR merges into `main` or `master` (or whose base it cannot read), PR merges into `develop` in any form but the delegated route's one (below), git or gh arguments fed through `xargs`, a commit that skips the commit-msg hook (`--no-verify`; a courtesy read of the command's words, so a shape that hides the flag from them skips the hook; the push-time scan and the read before presentation are the controls for that shape), a push with a `-c` setting or whose targets `remote.<name>.push` would choose, a push it cannot read in the state it will run in (*Push rules and limits*, below), and, best effort, a push whose commits new to the destination remote's tracking refs carry another author, a banned attribution line, or an `Agent:` declaration that is malformed or not that commit's only one (RULE ZERO). The author and message of a commit being made are [`../git/commit-msg`](../git/README.md)'s to read; the complete read is the one before a delivery is presented |
| `agreements_after_compact.py` | `SessionStart`, matcher `compact` | Restates RULE ZERO, the mode, who merges and the agreement paths after each compaction |
| `look_again.py` | `Stop` | Sends the agent back once when a file it read or wrote since your last prompt has changed since, naming the file, so it reads it again before it reports |
| `store_check.py` | `SessionStart` (no matcher: startup, resume, clear, compact) and `Stop` | Records the `_agent/` store's `node_modules` roots when a session starts, and sends the agent back at a stop when a new one has appeared, naming it and the fix (move it to the client scratch directory, keep receipts, logs and hashes). A stop names ten roots; the stops after it name the rest. Roots there before the session never block. A stop with no baseline (the walk at session start failed, which gets 20 s, or the session has no record from its start) says so once and lists the roots it sees, ten by name, which are the baseline from then on. A stop's own walk that fails lets the stop through, once a missing baseline has been said. A `node_modules` under a folder whose name ends in `.app`, or a symlink, is exempt. The folder name is the whole test: an app's contents copied without their `.app` folder are not exempt. Run as `store_check.py check`, it is the CLI any client or pulse can run: exit 1 on any `node_modules` root, any top-level tree (a store folder or an initiative) over 5 GB, or any path it cannot read, each on its own line (#283, #287) |

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

`install.py` copies the four hooks into `~/.claude/hooks/` and registers them in the `hooks`
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
expansion, and at most a trailing `2>&1`; a simple `git` command without `-c` whose values name them
is read as git. Beside a chain, substitution, wrapper, shell `-c`, continuation or other redirect, a
merge is refused whatever the base, since the base read could be stale or of another PR by the time
it runs. Harmless text and read-only chains that mention both are refused the same way, so run them
as their own call. A merge naming its repository twice is refused too, and so is a git or gh command
behind wrapper options (`env -u`, `env -S`, `sudo -u`). Into `develop` exactly one form passes, the
delegated route of [`review-findings.md`](../../procedures/review-findings.md#base-merges), as the
whole tool call in plain words (no prefix, wrapper, path, quote, redirect, chain, background, `eval`
or `sh -c`): `gh pr merge <N> --repo <owner/name> --merge --match-head-commit <40-hex>
--author-email brandon@brandonperfetti.com`, each flag once and no other (no squash, rebase,
`--admin`, `--auto`, branch deletion or message). Every `gh api` merge into `develop` stays refused.
This checks form, not whether the route is active or the PR eligible; those are the procedure's. Its
limits: the base is read before the command runs, so another session's retarget in that window is
not caught (only the head is pinned on the server); names the shell builds (`$'g\x68'`, `$(printf
gh)`, variables), shell functions, `PATH`, `--exec-path`, and `gh`
aliases and extensions are not resolved, so this guards literal commands, not an adversarial shell;
and on a base with a merge queue `gh` may enqueue rather than merge.

## Sealed cases

The tests above live in the tree a guard change edits, so the change can also edit what judges
it. A small set of **sealed cases** lives outside every checkout, in `~/.config/awa-sealed-cases/`,
where Claude Code's file tools are denied (#310). Each is one `<id>.json`: a setup, one Bash call
and the ruling the guard must give it, `refused` or `allowed`. Brandon, or a person he names,
adds, edits or removes a case, usually from a release-review finding; an agent may propose one
in a comment and never writes one. The first twelve are the nine shapes of #298 and #306, a
force-push, a push to `master`, and the delegated merge into `develop` while a `route-suspended`
issue is open, which the guard allows: it checks the route's form, and the suspension read is
the delivery owner's.

`sealed_cases.py` replays them against a `guard_git.py` (`--guard`, this folder's by default) on
the bare-repository fixture `test_push_differential.py` builds, with a `gh` that answers nothing.
It asks the guard as Claude Code does and runs no case's call. It prints `PASS <id>` or
`FAIL <id> expected=<x> got=<y>` per case and exits 1 on any failure; when the folder, a case or
the guard cannot be read it prints `SEALED CASES NOT RUN: <reason>` and exits 2. Its own logic is
tested by `test_sealed_cases.py`, on made-up cases. Install the trigger once per Mac:

```bash
/usr/bin/python3 ~/dev/sansfaux/agent-working-agreements/hooks/claude-code/sealed_cases.py --install-trigger
```

It copies [`../git/sealed-cases-trigger`](../git/README.md) into this repository's own hooks
folder as `post-commit` and `post-merge`, which the global `chain-repo-hook` runs, so a commit or
merge in any worktree that changes a file under `hooks/` prints the runner's lines (`--check`,
`--dry-run` as for `install.py`). Git ignores those hooks' exit status, so the lines are the
report. Limits: the seal is a permission deny in `~/.claude/settings.json` on Read, Edit and
Write of the folder; Claude Code 2.1.328 also refused a Bash command naming it, a read of the
command's words, not a wall against a shell; it seals no Codex or OpenClaw session, a known limit
until a lane there changes the guard (Brandon, 2026-11-24, #310). The runner and
trigger are in the tree they judge; a cherry-pick, a revert or a default rebase runs `post-commit`
for each commit it writes, but `git rebase --apply` runs neither hook; CI cannot see the folder
and does not run it.

## Push rules and limits

The guard reads the repository before the call runs, then decides where a push would go. Where it
would have to interpret the shell to know, it refuses and names the next step; it admits nothing
by interpreting (#236).

**The guard is the released guard plus refusals.** `guard_git.py` keeps the text released at
`v2026.11.17.2` unchanged, down to a marker line, but for one line its pin moved with: the footer
pattern, matched as words (#280). Everything below the marker can only refuse:
a call passes when the released check admits it as written, admits it again as git will read it
(an alias expanded, an option the released reader did not know dropped), and no rule below
refuses. So the guard never admits a call the released guard refuses, whatever the added code
does. `test_guard_git.py` pins this three ways: the released text's sha256; that nothing below the
marker rebinds a name the released code uses, but `check_command` and `main`; and that every
command the released guard refuses is refused. A later change to the released logic moves the pin
on purpose, in its own reviewed change.

- **Before a push, a call may hold only** `NAME=value`, a plain `git add`, `git commit` or
  `git status`, and a literal `cd <dir>`: an existing directory, with no option, `..`, `~`, `$`,
  glob, symbolic link or `CDPATH`. Anything else is refused with "run the push as its own call".
  A dry run is not limited. Whatever follows the push is not limited either, but for a `&`
  (below).
- **So these need the push in its own call:** tests or any script, then push; `git fetch`,
  `git pull`, `git merge` or `git tag`, then push; `git checkout -b <new>` or `git switch -c
  <new>`, then push; a comment line, or a comment after the push on its line; `cd` by a path with
  `..` or through a symlink; a `git` command behind a global option (`git --no-pager status`);
  an earlier command with a redirect (`git status > out.txt`; `2>&1` is fine); a git alias after
  any command the guard does not read (`npm test && git st`); anything in `( )` or `$( )`, or a
  pipe (`|`), earlier in the call. A pipe after the push is fine.
- **A push, commit or merge in a call that holds a single `&` is refused,** before or after
  it: the command before a `&` runs in the background, so a `cd` there never moves the shell
  (`cd <dir> & git push`). Join the commands with `&&`, or run the push as its own call. A dry
  run passes, and so does a quoted `&` (`git add -- '&'`, a message) (#298). A `&` after a `#`
  on its line is read the same way, comment or not; drop the comment (#306). A `&` inside a
  later shell's quoted body (`git commit …; bash -c '… & …'`) is read when that body is
  reached, so it refuses only what comes from there on (#306).
- **A call the guard cannot split is refused:** a git or gh call with unbalanced quotes. A
  backtick substitution earlier in a call refuses the push after it, as `$( )` does.
- **A `#` on a line that continues onto the next (`\` at its end) is refused** in a git or gh
  call: the shell ends a comment at the newline, and the guard does not work out which `#` is one.
- **A push or commit with its output redirected to a file is refused,** and so is a `git merge`:
  the shell writes the file before git starts, and it may be one git reads. `2>&1`, a pipe
  (`| tee out.txt`) and input (`<`, a heredoc) are fine. A git or gh call with `&>` is refused
  outright: write `2>&1`.
- **Configuration moved by the environment is refused:** `GIT_CONFIG_*`, `HOME` and
  `XDG_CONFIG_HOME` on a push, commit or merge. A `GIT_…=value` on a line of its own refuses the
  push, commit or merge after it: whether it is exported is not known. Put it on the command.
- **A git alias is read through its expansion,** found with the command's own `-c` settings. A
  shell alias (`!…`) is refused whatever it runs, and so is an alias holding a backslash: write
  the command out. A `git-<command>`
  program is read as `git <command>`; `git send-pack` and `git http-push` are refused.
- **Global options are read or the command is refused.** An option the guard does not know is
  refused. A call with `--version` or `--help` gets no added rule; the released verdict stands.
- **A bare push is resolved from the configuration git pushes by:** the current branch under
  `push.default` `simple` or `current`, `branch.<name>.merge` under `upstream`, else refused. A
  tracking ref's name is not used. With no remote named and no `origin`, it is refused. A
  source that is a symbolic ref goes where
  the ref points. A push naming more than 20 branches without a destination is refused.
- **A push with both a dry-run flag and `--no-dry-run` is refused,** whatever it names: an option
  given as the value of `-o` (`-o -n`) is not a flag, and the guard does not work out which of
  the two git obeys. Run the dry run or the push. On a commit, `--no-dry-run` ends the dry-run
  exemption (#298).
- **Under `push.default=upstream`, a branch pushed without its destination is refused**
  (`git push origin feature`, `-u` included): git may send it to `branch.<name>.merge`, which
  may name another branch. `HEAD` and `<src>:<dst>` pass: `git push <remote> <src>:<dst>` (#298).
- **A push that names no remote is refused when it goes to a `branch.<name>.remote` the author
  scan does not read:** the scan reads the remote `@{push}` names, else `origin`. This refuses
  the first bare push of a branch to such a remote; name the remote and the branch (#298), or
  for `--tags` the remote: `git push <remote> --tags` (#306).

`test_push_differential.py` holds these against git itself. It runs each call for real on bare
repositories on disk and fails if a call the guard allows moves `master` or `main`, deletes or
rewinds a ref, or commits past a refusing commit-msg hook. It also holds, row by row, that a
call the released guard refuses is refused.

**Limits.** The guard stops honest mistakes, not a determined bypass. It does not read:

- a script, Makefile, shell function or another tool that pushes (`./release.sh`, a `gh api` write
  to `git/refs`);
- programs that git itself runs during an allowed command: hooks, filters and `core.fsmonitor`.
  A repository whose own hooks move `HEAD` or change push configuration can send
  `git commit … && git push` somewhere the guard did not see;
- state another process changes between the guard's read and the push;
- `pushurl` and `insteadOf`, which send a correctly named branch to another repository;
- pushes that `--recurse-submodules=on-demand` makes inside submodules;
- a release branch not named `master` or `main`, and commits hidden by stale tracking refs in the
  author scan (the read before presentation is the complete check);
- a background `&` beside commands other than a push, commit or merge, and the values of push
  options, which reach the remote's own hooks;
- a `push.default` it fails to read, which it takes for unset.

**A refusal that is not a broken setup.** "A segment begins with an option" is the released
guard's own rule, on any command, `find` and read-only git included: a quoted or escaped word
made only of `;`, `&`, `|`, `(` or `)` reads as a separator, and the call is refused when an
option comes straight after it (`find . \( -name a -o -name b \) -print`,
`find … -exec … \; -print`, `git grep -n -e '(' -- src`, `git log -S '(' --oneline`). Pick a
form that passes, after reading what it changes:

- put that word last: `git log --oneline -S '('`. In `find`, `-print -exec … \;` prints each
  match whether or not the command succeeds, where `-exec … \; -print` prints only on success;
- give a regular expression another character: `git grep -n '[(]' -- src`. `git log -S` takes a
  literal string, so there the word goes last instead;
- end a `find -exec` with `{} +` only where one run over many matches will do. That test is
  always true, so a `-print` after it also prints the matches whose command failed, and `find`
  exits non-zero when the command fails;
- write a `find` test without the `\( … \)` group, with the action on each side:
  `find . -name a -print -o -name b -print`.

**A command-line parser will not be complete.** Each review of these rules has found a further
call shape that passes, and more exist. A new one is added below the marker as a refusal with a
differential row; it is never closed by teaching the guard to interpret more shell or more git.
