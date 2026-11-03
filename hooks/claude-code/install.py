#!/usr/bin/python3
"""Install the user-level Claude Code hooks from this folder.

Copies each hook into ~/.claude/hooks/ and registers it in the `hooks` block of
~/.claude/settings.json, leaving every other setting and every other hook as it
was. It copies rather than links, so switching the branch of this checkout never
changes the hooks a running session uses; `--check` reports drift instead.
Re-running it is safe: a hook already registered is updated in place, not added
twice.

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
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# event, matcher, script, extra fields. The command runs the copy in ~/.claude/hooks.
HOOKS = [
    ("PreToolUse", "Bash", "guard_git.py", {"timeout": 10, "onFailure": "block"}),
    ("SessionStart", "compact", "agreements_after_compact.py", {"timeout": 10}),
]


def hook_entry(script, extra):
    entry = {
        "type": "command",
        "command": '/usr/bin/python3 -I "$HOME/.claude/hooks/{}"'.format(script),
    }
    entry.update(extra)
    return entry


def runs_script(command, script):
    """True when the command runs this script by name, not one whose name ends in it."""
    return re.search(r"(^|[/\s\"'])" + re.escape(script) + r"($|[\s\"'])", command) is not None


def well_formed(settings):
    """True when the hooks block has the shape merge_hooks walks: events of groups of hooks."""
    if not isinstance(settings, dict):
        return False
    events = settings.get("hooks", {})
    if not isinstance(events, dict):
        return False
    for groups in events.values():
        if not isinstance(groups, list):
            return False
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks", []), list):
                return False
            for hook in group.get("hooks", []):
                if not isinstance(hook, dict) or not isinstance(hook.get("command", ""), str):
                    return False
    return True


def merge_hooks(settings):
    """Return a copy of settings with every hook in HOOKS registered once."""
    merged = copy.deepcopy(settings)
    events = merged.setdefault("hooks", {})
    for event, matcher, script, extra in HOOKS:
        wanted = hook_entry(script, extra)
        groups = events.setdefault(event, [])
        found = False
        for group in groups:
            for index, hook in enumerate(group.get("hooks", [])):
                if runs_script(hook.get("command", ""), script):
                    if group.get("matcher") == matcher:
                        group["hooks"][index] = wanted
                        found = True
        if found:
            continue
        group = next((g for g in groups if g.get("matcher") == matcher), None)
        if group is None:
            groups.append({"matcher": matcher, "hooks": [wanted]})
        else:
            group.setdefault("hooks", []).append(wanted)
    return merged


def write_atomic(path, data, mode=0o644):
    directory = os.path.dirname(path)
    fd, temp = tempfile.mkstemp(dir=directory, prefix=".install-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
        os.chmod(temp, mode)
        os.replace(temp, path)
    except BaseException:
        os.unlink(temp)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="say what would change")
    parser.add_argument("--check", action="store_true", help="exit 1 on any drift")
    parser.add_argument("--claude-dir", default=os.path.expanduser("~/.claude"))
    args = parser.parse_args(argv)

    hooks_dir = os.path.join(args.claude_dir, "hooks")
    settings_path = os.path.join(args.claude_dir, "settings.json")
    changes = []

    for script in sorted({hook[2] for hook in HOOKS}):
        source, target = os.path.join(HERE, script), os.path.join(hooks_dir, script)
        if not os.path.exists(target) or not filecmp.cmp(source, target, shallow=False):
            changes.append(("copy", source, target))

    settings = {}
    if os.path.exists(settings_path):
        try:
            with open(settings_path, encoding="utf-8") as handle:
                settings = json.load(handle)
        except ValueError as error:
            sys.exit("{} is not valid JSON ({}); nothing written.".format(settings_path, error))
    if not well_formed(settings):
        sys.exit("{} has no hooks block of the expected shape; nothing written.".format(settings_path))
    merged = merge_hooks(settings)
    if merged != settings:
        changes.append(("settings", settings_path, None))

    for kind, path, target in changes:
        if kind == "copy":
            print("{} {} -> {}".format("differs:" if args.check else "copy", path, target))
        else:
            print("{} hooks block of {}".format("differs:" if args.check else "update", path))
    if args.check:
        return 1 if changes else 0
    if args.dry_run or not changes:
        if not changes:
            print("Already installed.")
        return 0

    os.makedirs(hooks_dir, exist_ok=True)
    for kind, path, target in changes:
        if kind == "copy":
            with open(path, encoding="utf-8") as handle:
                write_atomic(target, handle.read())
    if merged != settings:
        mode = 0o644
        if os.path.exists(settings_path):
            mode = os.stat(settings_path).st_mode & 0o777
            backup = "{}.bak-{}".format(settings_path, time.strftime("%Y%m%d-%H%M%S"))
            shutil.copy2(settings_path, backup)
            print("backup {}".format(backup))
        # Through a symlink, as into a dotfiles repo; the hook copies above replace theirs.
        write_atomic(os.path.realpath(settings_path), json.dumps(merged, indent=2, ensure_ascii=False) + "\n", mode)
    print("Installed. Start a new Claude Code session for the settings change to load.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
