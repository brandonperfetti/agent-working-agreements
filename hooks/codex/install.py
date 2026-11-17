#!/usr/bin/python3
"""Install the Codex guard hook: guard.py and guard_git.py, and one entry in hooks.json.

Copies guard.py and ../claude-code/guard_git.py into ~/.codex/hooks/awa-guard/ and adds one
PreToolUse hook, matcher Bash, to ~/.codex/hooks.json when no entry with exactly that command
is there. It never removes or rewrites an entry, its own older ones included: --check reports
an entry that differs, and it is edited by hand. It reads hooks.json again just before it replaces
it, and stops when the file has changed since the first read. It never edits config.toml and
cannot trust the hook: Codex skips a hook until its user trusts it in the CLI's /hooks screen, and
the proof it is live is the canary.

    /usr/bin/python3 install.py            # install or update
    /usr/bin/python3 install.py --dry-run  # say what would change, write nothing
    /usr/bin/python3 install.py --check    # exit 1 if the installed copy differs
"""
import argparse
import copy
import filecmp
import json
import os
import shlex
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = {
    "guard.py": os.path.join(HERE, "guard.py"),
    "guard_git.py": os.path.join(os.path.dirname(HERE), "claude-code", "guard_git.py"),
}
FOLDER = os.path.join("hooks", "awa-guard")
EVENT, MATCHER, SCRIPT = "PreToolUse", "Bash", "guard.py"
HOOK_TIMEOUT = 30  # seconds; guard.py gives the guard 10 and must answer before Codex stops it


def hook_entry(codex_dir=None):
    """The hooks.json entry; codex_dir is given only for a Codex home other than ~/.codex."""
    if codex_dir is None:
        command = '/usr/bin/python3 -I "$HOME/.codex/{}/{}"'.format(FOLDER, SCRIPT)
    else:
        command = "/usr/bin/python3 -I {}".format(shlex.quote(os.path.join(os.path.abspath(codex_dir), FOLDER, SCRIPT)))
    return {"type": "command", "command": command, "timeout": HOOK_TIMEOUT}


def well_formed(config):
    """True when hooks.json has the shape merge_hook walks: events of groups of hooks."""
    if not isinstance(config, dict) or not isinstance(config.get("hooks", {}), dict):
        return False
    for groups in config.get("hooks", {}).values():
        if not isinstance(groups, list):
            return False
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks", []), list):
                return False
    return True


def registered(config, entry):
    """The guard's entries already under PreToolUse, matcher Bash: those whose command is exactly
    the string this installer writes. Nothing is parsed, so no other command is ever taken for it."""
    return [hook
            for group in config.get("hooks", {}).get(EVENT, []) if group.get("matcher") == MATCHER
            for hook in group.get("hooks", [])
            if isinstance(hook, dict) and hook.get("command") == entry["command"]]


def merge_hook(config, codex_dir=None):
    """Return hooks.json's content with the guard's entry added, or `config` itself when an entry
    with exactly that command is already there. Add-only: no entry is ever removed or rewritten."""
    entry = hook_entry(codex_dir)
    if registered(config, entry):
        return config
    merged = copy.deepcopy(config)
    groups = merged.setdefault("hooks", {}).setdefault(EVENT, [])
    group = next((g for g in groups if g.get("matcher") == MATCHER), None)
    if group is None:
        groups.append({"matcher": MATCHER, "hooks": [entry]})
    else:
        group.setdefault("hooks", []).append(entry)
    return merged


def read_bytes(path):
    """The file's bytes, or None when there is no file."""
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except FileNotFoundError:
        return None


def write_atomic(path, data, mode=0o644, unchanged=None):
    """Write `data` to `path` through a temporary file, so a reader never sees half a file. Given
    `unchanged`, it is called as the last step before the rename, and a false answer raises
    RuntimeError with nothing written."""
    fd, temp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".install-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
        os.chmod(temp, mode)
        if unchanged is not None and not unchanged():
            raise RuntimeError(path)
        os.replace(temp, path)
    except BaseException:
        os.unlink(temp)
        raise


def main(argv=None):
    """Plan the copies and the hooks.json change; report them; write them unless --dry-run or --check."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="say what would change")
    parser.add_argument("--check", action="store_true", help="exit 1 on any drift")
    parser.add_argument("--codex-dir", default=os.path.expanduser("~/.codex"))
    args = parser.parse_args(argv)

    target_dir = os.path.join(args.codex_dir, FOLDER)
    hooks_path = os.path.join(args.codex_dir, "hooks.json")
    copies = []
    for name, source in sorted(SOURCES.items()):
        if not os.path.isfile(source):
            sys.exit("source {} is missing; nothing written.".format(source))
        target = os.path.join(target_dir, name)
        if not os.path.exists(target) or not filecmp.cmp(source, target, shallow=False):
            copies.append((source, target))

    config = {}
    # Where hooks.json leads (itself, or a link's target) and its bytes: both are read again just
    # before the write, so a file or link another writer changed in between is left to them.
    real_path = os.path.realpath(hooks_path)
    read = read_bytes(real_path)
    if read is not None:
        try:
            config = json.loads(read.decode("utf-8"))
        except ValueError as error:
            sys.exit("{} is not valid JSON ({}); nothing written.".format(hooks_path, error))
    if not well_formed(config):
        sys.exit("{} has no hooks block of the expected shape; nothing written.".format(hooks_path))
    default = os.path.realpath(os.path.expanduser("~/.codex")) == os.path.realpath(args.codex_dir)
    home = None if default else args.codex_dir
    merged = merge_hook(config, home)
    # An entry with our command but other settings (a timeout from another version, a second
    # copy) is reported and left for its owner: this installer adds, and changes nothing.
    found = registered(config, hook_entry(home))
    altered = bool(found) and found != [hook_entry(home)]

    for source, target in copies:
        print("{} {} -> {}".format("differs:" if args.check else "copy", source, target))
    if merged != config:
        print("{} hooks block of {}".format("differs:" if args.check else "update", hooks_path))
    if altered:
        print("differs: the guard's entry in {} is not the one this version writes; edit it by hand to {}".format(
            hooks_path, json.dumps(hook_entry(home))))
    changed = bool(copies) or merged != config
    if args.check:
        return 1 if changed or altered else 0
    if args.dry_run or not changed:
        if not changed and not altered:
            print("Already installed.")
        return 0

    os.makedirs(target_dir, exist_ok=True)
    for source, target in copies:
        with open(source, encoding="utf-8") as handle:
            write_atomic(target, handle.read())
    if merged != config:
        mode = 0o644
        if read is not None and os.path.exists(hooks_path):
            mode = os.stat(hooks_path).st_mode & 0o777
            backup = "{}.bak-{}".format(hooks_path, time.strftime("%Y%m%d-%H%M%S"))
            shutil.copy2(hooks_path, backup)
            print("backup {}".format(backup))
        try:
            write_atomic(real_path, json.dumps(merged, indent=2, ensure_ascii=False) + "\n", mode,
                         lambda: os.path.realpath(hooks_path) == real_path and read_bytes(real_path) == read)
        except RuntimeError:
            sys.exit("{} changed while installing; nothing written to it. Run the installer again.".format(hooks_path))
    print("Installed. Codex skips the hook until you trust it: run /hooks in the Codex CLI, then")
    print("check that `gh pr merge --help` is refused with `awa-guard-codex:` in a new session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
