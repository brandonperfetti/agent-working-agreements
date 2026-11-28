# Store retention

`store_retention.py` keeps the `_agent/` store to about a month of heavy files (#328). Brandon
decided on 2026-11-28 that markdown and JSON receipts, together with the current code, are enough to
support a past claim. Screenshots, captures, builds and logs only need to last about a month
([decision](https://github.com/brandonperfetti/agent-working-agreements/issues/325#issuecomment-7239951719)).
The script's docstring is the full contract. This page covers what it does and how to install it.

```bash
/usr/bin/python3 -I scripts/store-retention/store_retention.py --store ~/dev/sansfaux/_agent          # dry run
/usr/bin/python3 -I scripts/store-retention/store_retention.py --store ~/dev/sansfaux/_agent --apply
```

## What a run does

| Step | Which files | Where a record goes |
| --- | --- | --- |
| Trash | heavy files and trees whose newest mtime is over 30 days old, to `_trash/<run>/` with their paths kept | `evidence/store-retention/<run>/manifest.tsv`: path, kind, bytes, SHA-256, mtime, reason |
| Compress | `.log` files 7 to 30 days old, gzipped in place, keeping their mtime | `compressed.tsv`: the log's bytes and SHA-256, recorded before the log is removed |
| Purge | trash batches this script made, 30 days after the move, if they hold only what their manifest lists | `purged.tsv`, written before the delete. The batch's manifest stays. |

Each `--apply` run also writes `report.md` in the same folder. A dry run prints the plan and writes
nothing. Heavy means one of these kinds:

- media;
- served-response captures: `.body`, `.rsc`, `.har`, `.mhtml` and `.webarchive`, plus `.html` or
  `.htm` of 256 KiB or more;
- archives;
- database copies;
- logs;
- build-output, install and app-bundle trees.

A tree is moved whole only when it holds no `.git`. Two kinds of tree are moved whole even with
package metadata inside: an exact name like `node_modules` or `.next`, and a real macOS app bundle.
Any other matched tree must hold no receipt anywhere, or it is walked like any folder. That covers
an `.app` that isn't a bundle, and `dist`, `build` and `out`. Any other file stays. A receipt is
never heavy, compressed or not: markdown, JSON (with `.jsonl`), text, TSV, CSV, YAML and hash
files.

These are never touched:

- anything changed in the last 72 hours;
- anything open, or under a running process's working directory;
- anything a receipt naming an open PR cites, by path or by file name, and everything inside a
  folder it cites;
- `.worktrees/`, folders that hold `.git`, symlinks, and anything outside the store.

Anything in `_trash/` that this script didn't put there is left for
`organize.sh --empty-trash`. `--apply` moves nothing, and says why in its report (on its output,
for a symlink), when:

- `lsof` or `gh` can't run;
- a PR search reaches its 1000-result limit;
- `_trash` or the report folder is a symlink.

To restore a file within its 30 days, move it from `_trash/<run>/<path>` back to `<path>`. The
manifest lists every path.

## `organize.sh`

`organize.sh` isn't tracked, so Brandon adds the mode by hand. Put this line after `SELF=...`:

```bash
[ "${1:-}" = "--prune-store" ] && { shift; exec /usr/bin/python3 -I "$ROOT/agent-working-agreements/scripts/store-retention/store_retention.py" --store "$ROOT/_agent" "$@"; }
```

Then add a header line, so that `--help` lists the mode:

```bash
#   ./organize.sh --prune-store [--apply]   # RETENTION: heavy files >30 days to _agent/_trash/<run>/, deleted 30 days later (#328)
```

## LaunchAgent

`ai.sansfaux.agent-store-retention.plist` runs `--apply` at 04:45 on the 1st of each month. It is a
template: launchd expands no variables, so the install step writes your home directory into it.
The plist runs the script from the agreement checkout at `~/dev/sansfaux/agent-working-agreements`.
Install it once that checkout holds the script.

```bash
cd ~/dev/sansfaux/agent-working-agreements
test -f scripts/store-retention/store_retention.py
sed "s|@HOME@|$HOME|g" scripts/store-retention/ai.sansfaux.agent-store-retention.plist \
  > ~/Library/LaunchAgents/ai.sansfaux.agent-store-retention.plist
plutil -lint ~/Library/LaunchAgents/ai.sansfaux.agent-store-retention.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.sansfaux.agent-store-retention.plist
launchctl kickstart gui/$(id -u)/ai.sansfaux.agent-store-retention   # the first run, now
```

The job's output goes to `~/Library/Logs/sansfaux-agent-store-retention.log`, and its report goes to
`_agent/evidence/store-retention/`. To remove it, run
`launchctl bootout gui/$(id -u)/ai.sansfaux.agent-store-retention` and delete the plist.
