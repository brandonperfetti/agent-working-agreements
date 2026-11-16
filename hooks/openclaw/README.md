# OpenClaw relay for `guard_git.py`

`awa-guard-git` is an OpenClaw plugin. It sends every shell command an OpenClaw agent runs
to [`../claude-code/guard_git.py`](../claude-code/guard_git.py), unchanged, through
OpenClaw's `before_tool_call` hook. That covers OpenClaw's own `exec` tool and the Codex-native
shell relayed to the hook. A Code Mode cell is not read as a command: each tool it calls
re-enters the hook as its own call. The guard owns the rules: force-pushes, release-branch pushes, RULE
ZERO, and PR merges into a protected base other than the delegated route's one form. The relay
only carries the command and reads the verdict.

The relay blocks the call unless the guard exits 0 with nothing on stdout. A denial, a nonzero
exit, unreadable output, a missing guard, a timeout and a shell call whose command it cannot read
all block. It also blocks any non-text tool whose parameters name GitHub and a merge, such as an
MCP `execute` or a merge-named tool, because no API call is an equivalent route; any `process`
input to a running shell session that names `git` or `gh`, keys and hex bytes included; and an
`exec` whose own `env` sets a variable that changes git or gh (`GIT_*`, `GH_*`, `GITHUB_*`,
`PATH`, `HOME` and the like), which the guard would not see: put those in the command.

The guard reads the checkout from the call's absolute `workdir` (or `cwd`). The hook is not told
the session's default directory, so a call without one is checked outside any repository: a
command that needs the checkout, such as a push, is then refused. Give `exec` an absolute
`workdir`, or `cd` to an absolute path in the command.

A plugin that is not loaded blocks nothing. So before every delegated merge, the delivery owner
runs the canary `gh pr merge --help` alone, through the tool the merge will use. Only a refusal
whose reason carries `awa-guard-git:` counts; any other outcome sends the merge to Brandon.

The merge route is an OpenClaw-runtime turn's Code Mode `exec`, or a claude-cli turn's
`mcp__openclaw__exec`, qualified on OpenClaw 2026.11.1. In a Codex-harness turn the relay applies,
but Codex's sandbox refuses `gh`, its approval reviewer refused the escalation, and its
`gateway_exec` was not measured: every tool there is guarded, not a merge route.

## Install

From a checkout of the commit to install:

```bash
node hooks/openclaw/install.mjs                 # copies the plugin, relay.mjs and guard_git.py
node hooks/openclaw/install.mjs --print-patch   # the config patch that loads it
node hooks/openclaw/install.mjs --check         # bytes match, and OpenClaw lists it enabled
```

The files go to `~/.openclaw/hooks/awa-guard/`. The installer never edits OpenClaw's config.
The OpenClaw control-plane owner applies the patch (`plugins.allow`, `plugins.load.paths`,
`plugins.entries`) with `openclaw config patch`. Plugin config reloads without a Gateway restart.
Apply it, reload an edited plugin, or re-enable a disabled one at a quiet moment. The change counts
only once the canary is refused with `awa-guard-git:`. If it is not, restart the Gateway: a patch
can persist without reaching the running Gateway, and a second patch then finds nothing to apply.
At the first apply, no guard ran for about three seconds.
Decisions on blocked and merge-bearing calls are logged to
`~/.openclaw/logs/awa-guard-git.jsonl`, with each assignment's and `env` entry's value removed.
An unset or empty `plugins.allow` is unrestricted, and the printed patch leaves it so.

## Limits

- It inherits the guard's limits: it stops honest mistakes, not a determined bypass.
- Another plugin that rewrites a tool's parameters after this hook has read them is not seen.
  Codex-native calls cannot be rewritten at all.
- Code Mode's default Node executor is not a security boundary, so guest code that reaches
  the host directly instead of through a tool is not seen.
- A command that a file tool writes into a script, and the shell then runs by name, is
  checked by name only.
- Session input split across several `process` calls, so that no one call names `git` or `gh`,
  is not seen.
- An ACP child (`sessions_spawn` with `runtime: "acp"`) is an outside harness whose tool calls
  never reach this hook; only its brief is checked, and a later `sessions_send` to it is not. Its
  merges are its own client's, never this route's.

## Tests

```bash
node --test hooks/openclaw/relay.test.mjs
```
