#!/usr/bin/python3
"""Install the user-level Claude Code hooks from this folder, and the git hooks beside it.

Copies each Claude Code hook into ~/.claude/hooks/ and registers it in the `hooks`
block of ~/.claude/settings.json, leaving every other setting and every other hook
as it was. Copies each hook under ../git into ~/.config/git/hooks/ and, when
`core.hooksPath` is unset, points the global git setting there; a path already set
elsewhere is reported and never overridden. It copies rather than links, so switching the branch of this checkout never
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
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GIT_HOOKS_SOURCE = os.path.join(os.path.dirname(HERE), "git")
GIT_HOOKS = ["commit-msg"]  # hooks git runs itself, for every client on the Mac

# event, matcher, script, extra fields. The command runs the copy in ~/.claude/hooks.
# A matcher of None is an event without matchers; its group carries no matcher key.
HOOKS = [
    ("PreToolUse", "Bash", "guard_git.py", {"timeout": 10, "onFailure": "block"}),
    ("SessionStart", "compact", "agreements_after_compact.py", {"timeout": 10}),
    ("Stop", None, "look_again.py", {"timeout": 30}),
]


def hook_entry(script, extra, hooks_dir=None):
    """The settings entry; hooks_dir is given only for a Claude directory other than ~/.claude."""
    if hooks_dir is None:
        command = '/usr/bin/python3 -I "$HOME/.claude/hooks/{}"'.format(script)
    else:
        command = "/usr/bin/python3 -I {}".format(shlex.quote(os.path.join(os.path.abspath(hooks_dir), script)))
    entry = {"type": "command", "command": command}
    entry.update(extra)
    return entry


def runs_script(command, script):
    """True when the command executes this script, directly or as python's script operand."""
    try:
        argv = shlex.split(command)
    except ValueError:
        return False
    if argv and re.fullmatch(r"python[0-9.]*", os.path.basename(argv[0])):
        argv = argv[1:]
        while argv and argv[0].startswith("-"):
            if argv[0] in ("-c", "-m"):
                return False
            argv = argv[2:] if argv[0] in ("-W", "-X") else argv[1:]
    return bool(argv) and os.path.basename(argv[0]) == script


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


def merge_hooks(settings, hooks_dir=None):
    """Return a copy of settings with every hook in HOOKS registered once."""
    merged = copy.deepcopy(settings)
    events = merged.setdefault("hooks", {})
    for event, matcher, script, extra in HOOKS:
        wanted = hook_entry(script, extra, hooks_dir)
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
            groups.append({"hooks": [wanted]} if matcher is None else {"matcher": matcher, "hooks": [wanted]})
        else:
            group.setdefault("hooks", []).append(wanted)
    return merged


def global_hooks_path():
    """The global core.hooksPath, "" when unset, None when git could not be asked."""
    try:
        result = subprocess.run(["git", "config", "--global", "--get", "core.hooksPath"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode not in (0, 1):
        return None
    return result.stdout.strip()


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
    parser.add_argument("--git-hooks-dir", default=os.path.expanduser("~/.config/git/hooks"))
    args = parser.parse_args(argv)

    hooks_dir = os.path.join(args.claude_dir, "hooks")
    git_hooks_dir = os.path.abspath(os.path.expanduser(args.git_hooks_dir))
    settings_path = os.path.join(args.claude_dir, "settings.json")
    changes = []

    for script in sorted({hook[2] for hook in HOOKS}):
        source, target = os.path.join(HERE, script), os.path.join(hooks_dir, script)
        if not os.path.exists(target) or not filecmp.cmp(source, target, shallow=False):
            changes.append(("copy", source, target))

    for script in GIT_HOOKS:
        source, target = os.path.join(GIT_HOOKS_SOURCE, script), os.path.join(git_hooks_dir, script)
        if not os.path.exists(target) or not filecmp.cmp(source, target, shallow=False) or not os.access(target, os.X_OK):
            changes.append(("git-hook", source, target))
    current = global_hooks_path()
    if current is None:
        sys.exit("git could not be asked for core.hooksPath; nothing written.")
    if current == "":
        changes.append(("hooks-path", git_hooks_dir, None))
    elif os.path.realpath(os.path.expanduser(current)) != os.path.realpath(git_hooks_dir):
        print("note: core.hooksPath is {}; the git hooks under {} are not active until it points there or chains them.".format(current, git_hooks_dir))

    settings = {}
    if os.path.exists(settings_path):
        try:
            with open(settings_path, encoding="utf-8") as handle:
                settings = json.load(handle)
        except ValueError as error:
            sys.exit("{} is not valid JSON ({}); nothing written.".format(settings_path, error))
    if not well_formed(settings):
        sys.exit("{} has no hooks block of the expected shape; nothing written.".format(settings_path))
    default = os.path.realpath(os.path.expanduser("~/.claude")) == os.path.realpath(args.claude_dir)
    merged = merge_hooks(settings, None if default else hooks_dir)
    if merged != settings:
        changes.append(("settings", settings_path, None))

    for kind, path, target in changes:
        if kind in ("copy", "git-hook"):
            print("{} {} -> {}".format("differs:" if args.check else "copy", path, target))
        elif kind == "hooks-path":
            print("{} git config --global core.hooksPath {}".format("unset:" if args.check else "set", path))
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
        elif kind == "git-hook":
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(path, encoding="utf-8") as handle:
                write_atomic(target, handle.read(), 0o755)  # git runs only an executable hook
        elif kind == "hooks-path":
            subprocess.run(["git", "config", "--global", "core.hooksPath", path], check=True, timeout=5)
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
