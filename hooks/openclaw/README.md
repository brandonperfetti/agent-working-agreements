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
MCP `execute`, because no API call is an equivalent route.

A plugin that is not loaded blocks nothing. So before every delegated merge, the delivery owner
runs the canary `gh pr merge --help` as its own tool call. Only a refusal whose reason carries
`awa-guard-git:` counts; any other outcome sends the merge to Brandon.

On the Codex-native shell the relay applies, but Codex's own sandbox refuses `gh`, and its
approval reviewer refused the escalation in qualification. That path is guarded, not a merge route.
The merge goes through OpenClaw `exec`: Code Mode, or a claude-cli turn's `mcp__openclaw__exec`.

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
Apply it, or reload an edited plugin, at a quiet moment, then run the canary. At the first apply,
the plugin was briefly reported not found, and no guard ran for about three seconds. A reload under
load once replaced the plugin but timed out restarting another plugin's service.
Decisions on blocked and merge-bearing calls are logged to
`~/.openclaw/logs/awa-guard-git.jsonl`.

## Limits

- It inherits the guard's limits: it stops honest mistakes, not a determined bypass.
- Another plugin that rewrites a tool's parameters after this hook has read them is not seen.
  Codex-native calls cannot be rewritten at all.
- Code Mode's default Node executor is not a security boundary, so guest code that reaches
  the host directly instead of through a tool is not seen.
- A command that a file tool writes into a script, and the shell then runs by name, is
  checked by name only.

## Tests

```bash
node --test hooks/openclaw/relay.test.mjs
```
