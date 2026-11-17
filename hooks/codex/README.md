# Codex hook for `guard_git.py`

`guard.py` is a Codex `PreToolUse` hook, matcher `Bash`. It sends every shell command a Codex
session runs to [`../claude-code/guard_git.py`](../claude-code/guard_git.py), unchanged, and
denies the command unless the guard passes it. It covers the Codex CLI and a T3-hosted Codex
session, which run the same binary against the same `~/.codex`. The guard owns the rules:
force-pushes, release-branch pushes, RULE ZERO, and PR merges into a protected base other than
the delegated route's one form. This file only carries the command and reads the verdict.

Codex runs a command when its hook exits nonzero, times out or prints something Codex cannot
read (measured on 0.169.0). So `guard.py` turns every outcome but a clean pass into a denial: a
guard that denies, exits nonzero, hangs past 10 s, is missing, or prints an unreadable verdict,
and hook input with no command it can read. A denial's reason begins `awa-guard-codex:`.

## The canary

A hook that Codex does not run blocks nothing, and Codex says nothing about it. So immediately
before every delegated merge, the delivery owner runs `gh pr merge --help` alone, in the session
that will merge. Only a refusal whose reason carries `awa-guard-codex:` counts. Printed help
text is a failure; that, or a missing or ambiguous refusal, stops the merge and sends it to
Brandon. A refusal is evidence for that one merge only.

## Install

From a checkout of the commit to install:

```bash
/usr/bin/python3 hooks/codex/install.py            # copies both files, registers the hook
/usr/bin/python3 hooks/codex/install.py --dry-run  # says what would change, writes nothing
/usr/bin/python3 hooks/codex/install.py --check    # exit 1 if the installed copy differs
```

The files go to `~/.codex/hooks/awa-guard/`, and one entry goes into `~/.codex/hooks.json`,
which is backed up beside itself first. Every other hook there stays as it was. The installer
never edits `config.toml`.

**Codex skips the hook until its user trusts it.** After the first install, Brandon opens the
Codex CLI, runs `/hooks` and trusts the entry. Trust is tied to the entry's text, so an update
that changes only the two scripts needs no new trust; one that changes the entry does. The
install counts only once the canary is refused in a new session. `--check` compares bytes and
the entry; it cannot read trust.

`gh` needs the network. A T3 Codex session runs with full access, so `gh` works there. A Codex
CLI session in its default sandbox refuses the network: run it with full access, or approve the
`gh` call when Codex asks.

## Limits

- It inherits the guard's limits: it stops honest mistakes, not a determined bypass.
- **Codex fails open where this file cannot answer.** The command runs when `guard.py` cannot
  start (no `/usr/bin/python3`, a login shell that fails), when Codex stops it at the entry's
  30 s timeout, or when the hook is untrusted, disabled, or switched off with `features.hooks`.
  The canary detects a hook that is not live. It does not detect a single failed run. A managed
  hook in `/etc/codex/requirements.toml` cannot be switched off by the user and needs no trust;
  it is the stronger option if this proves too weak.
- Only shell commands are checked. A merge through an MCP tool, such as GitHub's
  `merge_pull_request` or a Kody `execute`, is not seen here, and is no route: see below.
- Input typed into a command that is already running (`write_stdin`) is not checked again.
- The ChatGPT desktop app's Codex was not measured.

## Why the shell form is the only route

A merge through GitHub's MCP tool or the REST API was considered and rejected (Brandon,
2026-11-17). Its arguments can carry the expected head and the merge method. They cannot carry
the author email: neither `merge_pull_request` nor `PUT /pulls/{n}/merge` takes one, so GitHub
chooses the merge commit's author address, and RULE ZERO needs it to be
`brandon@brandonperfetti.com`, exactly. `gh pr merge --author-email` sets it. A Kody `execute`
is arbitrary code, which no hook can read word for word. An API route would also need a second
decision engine beside `guard_git.py`.

## Tests

```bash
/usr/bin/python3 -m unittest discover -s hooks/codex
```
