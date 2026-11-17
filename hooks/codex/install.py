#!/usr/bin/python3
"""Install the Codex guard hook: guard.py and guard_git.py, and one entry in hooks.json.

Copies guard.py and ../claude-code/guard_git.py into ~/.codex/hooks/awa-guard/ and registers
one PreToolUse hook, matcher Bash, in ~/.codex/hooks.json, leaving every other hook there as
it was. It never edits config.toml and cannot trust the hook: Codex skips a hook until its
user trusts it in the CLI's /hooks screen, and the proof it is live is the canary.

    /usr/bin/python3 install.py            # install or update
    /usr/bin/python3 install.py --dry-run  # say what would change, write nothing
    /usr/bin/python3 install.py --check    # exit 1 if the installed copy differs
"""
import argparse
import copy
import filecmp
import json
import os
import re
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


def ours(hook):
    """True when a hooks.json entry executes this installer's guard.py: the script python runs,
    or the command itself. A command that only names that path in its arguments is someone else's."""
    command = hook.get("command", "") if isinstance(hook, dict) else ""
    try:
        argv = shlex.split(command) if isinstance(command, str) else []
    except ValueError:
        return False
    if argv and re.fullmatch(r"python[0-9.]*", os.path.basename(argv[0])):
        argv = argv[1:]
        while argv and argv[0].startswith("-"):
            if argv[0] in ("-c", "-m"):
                return False
            argv = argv[2:] if argv[0] in ("-W", "-X") else argv[1:]
    return bool(argv) and argv[0].replace(os.sep, "/").endswith("/{}/{}".format(FOLDER.replace(os.sep, "/"), SCRIPT))


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


def merge_hook(config, codex_dir=None):
    """Return a copy of hooks.json's content with the guard registered exactly once."""
    merged = copy.deepcopy(config)
    events = merged.setdefault("hooks", {})
    for name in list(events):  # drop every copy of ours, under any event, then add it back once
        kept = []
        for group in events[name]:
            hooks = group.get("hooks", [])
            if not any(ours(hook) for hook in hooks):
                kept.append(group)  # nothing of ours: left exactly as it was
                continue
            group["hooks"] = [hook for hook in hooks if not ours(hook)]
            if group["hooks"]:
                kept.append(group)
        if kept or name == EVENT:
            events[name] = kept
        else:
            del events[name]
    groups = events.setdefault(EVENT, [])
    group = next((g for g in groups if g.get("matcher") == MATCHER), None)
    if group is None:
        groups.append({"matcher": MATCHER, "hooks": [hook_entry(codex_dir)]})
    else:
        group["hooks"].append(hook_entry(codex_dir))
    return merged


def write_atomic(path, data, mode=0o644):
    """Write `data` to `path` through a temporary file, so a reader never sees half a file."""
    fd, temp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".install-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
        os.chmod(temp, mode)
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
    if os.path.exists(hooks_path):
        try:
            with open(hooks_path, encoding="utf-8") as handle:
                config = json.load(handle)
        except ValueError as error:
            sys.exit("{} is not valid JSON ({}); nothing written.".format(hooks_path, error))
    if not well_formed(config):
        sys.exit("{} has no hooks block of the expected shape; nothing written.".format(hooks_path))
    default = os.path.realpath(os.path.expanduser("~/.codex")) == os.path.realpath(args.codex_dir)
    merged = merge_hook(config, None if default else args.codex_dir)

    for source, target in copies:
        print("{} {} -> {}".format("differs:" if args.check else "copy", source, target))
    if merged != config:
        print("{} hooks block of {}".format("differs:" if args.check else "update", hooks_path))
    changed = bool(copies) or merged != config
    if args.check:
        return 1 if changed else 0
    if args.dry_run or not changed:
        if not changed:
            print("Already installed.")
        return 0

    os.makedirs(target_dir, exist_ok=True)
    for source, target in copies:
        with open(source, encoding="utf-8") as handle:
            write_atomic(target, handle.read())
    if merged != config:
        mode = 0o644
        if os.path.exists(hooks_path):
            mode = os.stat(hooks_path).st_mode & 0o777
            backup = "{}.bak-{}".format(hooks_path, time.strftime("%Y%m%d-%H%M%S"))
            shutil.copy2(hooks_path, backup)
            print("backup {}".format(backup))
        write_atomic(os.path.realpath(hooks_path), json.dumps(merged, indent=2, ensure_ascii=False) + "\n", mode)
    print("Installed. Codex skips the hook until you trust it: run /hooks in the Codex CLI, then")
    print("check that `gh pr merge --help` is refused with `awa-guard-codex:` in a new session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
