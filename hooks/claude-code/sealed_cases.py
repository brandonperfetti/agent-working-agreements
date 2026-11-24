#!/usr/bin/python3
"""Replay the sealed guard cases (#310) against a guard_git.py, one bare line per case.

The cases live outside every checkout (DEFAULT_CASES), where the agent changing the guard cannot
read or edit them through its file tools; a person curates them, and no agent writes one. Each is
one JSON file, `<id>.json`:

    {"id": "push-to-master", "source": "anchor", "setup": "<shell, run in the clone first>",
     "command": "<the Bash call the guard is asked about>", "expected": "refused" | "allowed"}

`{root}` in `setup` or `command` is the fixture's own directory. The fixture is the one
test_push_differential.py builds: two bare remotes, `work` on feature/x and `work2` on master. A
`gh` on the fixture's PATH answers nothing, so no case reaches GitHub; a case's setup may write its
own `{root}/bin/gh`. The guard is run as Claude Code runs it, a PreToolUse payload on stdin, and its
answer is the ruling: a deny decision (or exit 2) is `refused`, no output is `allowed`, anything
else (a crash, a timeout, output that is not a decision) is `error`, which no case expects. No
case's command is run.

    /usr/bin/python3 sealed_cases.py [--cases DIR] [--guard FILE]   # PASS <id> / FAIL <id> ...
    /usr/bin/python3 sealed_cases.py --install-trigger [--check | --dry-run]

Exit 0 when every case passes, 1 when one fails, 2 with `SEALED CASES NOT RUN: <reason>` when the
cases or the guard cannot be reached: never a silent pass. `--install-trigger` copies
../git/sealed-cases-trigger into this repository's hooks folder as post-commit and post-merge,
where ../git/chain-repo-hook hands them git's call.
"""
import argparse
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

DEFAULT_CASES = os.path.join("~", ".config", "awa-sealed-cases")
DEFAULT_GUARD = os.path.join(HERE, "guard_git.py")
RULINGS = ("refused", "allowed")
CASE_ID = re.compile(r"[a-z0-9][a-z0-9-]*")
NO_GH = "#!/bin/sh\necho 'gh: not reachable from a sealed case' >&2\nexit 1\n"
GUARD_TIMEOUT = 30
TRIGGER = os.path.join(os.path.dirname(HERE), "git", "sealed-cases-trigger")
TRIGGER_HOOKS = ("post-commit", "post-merge")
OWNED = "installed-by: agent-working-agreements/hooks/claude-code/sealed_cases.py"
AUTHOR_EMAIL = "brandon@brandonperfetti.com"  # the fixture's commit identity, as guard_git.py names it


class NotRun(Exception):
    """The cases, the guard or the fixture cannot be reached: nothing was judged."""


def problem_with(case, name):
    """Why a parsed case file is not a case, or None."""
    if not isinstance(case, dict):
        return "not a JSON object"
    for key in ("id", "command", "expected"):
        if not isinstance(case.get(key), str) or not case[key]:
            return "no {}".format(key)
    if not isinstance(case.get("setup", ""), str):
        return "setup is not a string"
    if case["expected"] not in RULINGS:
        return "expected is {!r}, not refused or allowed".format(case["expected"])
    if not CASE_ID.fullmatch(case["id"]):
        return "id {!r} is not lowercase words joined by -".format(case["id"])
    if name != case["id"] + ".json":
        return "the file name is not its id"
    return None


def load_cases(folder):
    """Every case in the folder, in name order; NotRun when the folder or a case cannot be read."""
    try:
        names = sorted(os.listdir(folder))
    except FileNotFoundError:
        raise NotRun("{} does not exist".format(folder))
    except NotADirectoryError:
        raise NotRun("{} is not a folder".format(folder))
    except PermissionError:
        raise NotRun("{} cannot be read".format(folder))
    except OSError as error:
        raise NotRun("{} cannot be read: {}".format(folder, error.strerror or error))
    files = [name for name in names if name.endswith(".json")]
    if not files:
        raise NotRun("{} holds no case files".format(folder))
    cases = []
    for name in files:
        try:
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                case = json.load(handle)
        except (OSError, ValueError) as error:
            raise NotRun("{} cannot be read: {}".format(name, error))
        problem = problem_with(case, name)
        if problem:
            raise NotRun("{}: {}".format(name, problem))
        cases.append(case)
    return cases


def ruling(guard, command, directory, env):
    """The guard's answer to the call, as Claude Code would act on it."""
    payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                          "tool_input": {"command": command}, "cwd": directory})
    try:
        result = subprocess.run([sys.executable, "-I", guard], input=payload.encode("utf-8"),
                                capture_output=True, cwd=directory, env=env, timeout=GUARD_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return "error"
    if result.returncode == 2:
        # Claude Code blocks a call whose hook exits 2, whatever its stderr holds; Python also exits
        # 2 when it cannot open the script, and that is no ruling.
        return "error" if b"can't open file" in result.stderr else "refused"
    try:
        # Output that is not UTF-8, anywhere in either stream, is no ruling: got=error, never a PASS.
        stdout, _ = result.stdout.decode("utf-8"), result.stderr.decode("utf-8")
    except UnicodeDecodeError:
        return "error"
    if result.returncode or stdout.strip() == "":
        return "error" if result.returncode else "allowed"
    try:
        output = json.loads(stdout)["hookSpecificOutput"]
        # The hooks reference requires hookEventName set to the event's name, and does not say what
        # Claude Code does without it, so a decision for no named PreToolUse event is no ruling.
        if not isinstance(output, dict) or output.get("hookEventName") != "PreToolUse":
            return "error"
        decision = output["permissionDecision"]
    except (ValueError, KeyError, TypeError):
        return "error"
    return {"deny": "refused", "allow": "allowed"}.get(decision, "error") if isinstance(decision, str) else "error"


def load_fixtures():
    """test_push_differential, whose bare-repository fixture the cases run on. It imports this
    folder's guard_git.py only for the author email, so it imports a stand-in that carries the
    email: the guard under judgement runs only in the timed process each case asks, never in the
    runner, and one that does not import, or exits as it does, answers each case for itself."""
    if "test_push_differential" in sys.modules:
        return sys.modules["test_push_differential"]
    held = sys.modules.get("guard_git")
    stand_in = types.ModuleType("guard_git")
    stand_in.AUTHOR_EMAIL = AUTHOR_EMAIL
    sys.modules["guard_git"] = stand_in
    try:
        import test_push_differential as fixtures
        return fixtures
    except (Exception, SystemExit) as error:
        sys.modules.pop("test_push_differential", None)
        raise NotRun("the fixture could not be loaded: {}: {}".format(type(error).__name__, error))
    finally:
        if held is None:
            sys.modules.pop("guard_git", None)
        else:
            sys.modules["guard_git"] = held


def build_template(base, fixtures):
    """The differential test's fixture, with a gh that answers nothing."""
    template = os.path.join(base, "template")
    os.makedirs(template)
    try:
        fixtures.build(template)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        raise NotRun("the fixture could not be built: {}".format(str(error).splitlines()[0]))
    os.makedirs(os.path.join(template, "bin"))
    gh = os.path.join(template, "bin", "gh")
    with open(gh, "w") as handle:
        handle.write(NO_GH)
    os.chmod(gh, 0o755)
    return template


def judge(case, guard, template, base, index, fixtures):
    """The ruling the guard gives the case, on a fresh copy of the fixture."""
    root = os.path.join(base, "case-{}".format(index))
    shutil.copytree(template, root, symlinks=True)
    try:
        env = fixtures.environment_for(root)
        env["PATH"] = os.path.join(root, "bin") + os.pathsep + env.get("PATH", os.defpath)
        work = os.path.join(root, "work")
        setup = case.get("setup", "")
        if setup:
            try:
                fixtures.run(setup.replace("{root}", root), work, env)
            except (RuntimeError, UnicodeError, subprocess.SubprocessError):  # UnicodeError: output not UTF-8
                return "setup-error"
        return ruling(guard, case["command"].replace("{root}", root), work, env)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def run_cases(folder, guard, out=sys.stdout):
    """Print one line per case; the exit status."""
    try:
        folder = os.path.expanduser(folder)
        cases = load_cases(folder)
        if not os.path.isfile(guard):
            raise NotRun("no guard at {}".format(guard))
        try:
            with open(guard, "rb"):
                pass
        except OSError as error:
            raise NotRun("the guard at {} cannot be read: {}".format(guard, error.strerror or error))
        with tempfile.TemporaryDirectory() as tmp:
            base = os.path.realpath(tmp)
            fixtures = load_fixtures()
            template = build_template(base, fixtures)
            failed = False
            for index, case in enumerate(cases):
                got = judge(case, guard, template, base, index, fixtures)
                if got == case["expected"]:
                    print("PASS {}".format(case["id"]), file=out, flush=True)
                else:
                    failed = True
                    print("FAIL {} expected={} got={}".format(case["id"], case["expected"], got), file=out, flush=True)
            return 1 if failed else 0
    except NotRun as reason:
        print("SEALED CASES NOT RUN: {}".format(reason), file=out, flush=True)
        return 2


def hooks_dir(start=HERE):
    """This repository's own hooks folder, the one chain-repo-hook hands git's calls to."""
    # GIT_DIR, GIT_COMMON_DIR and the rest would name another repository whatever the cwd.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                            cwd=start, capture_output=True, text=True, env=env)
    if common.returncode:
        raise NotRun("not inside a git repository: {}".format(start))
    return os.path.join(common.stdout.strip(), "hooks")


def install_trigger(target, mode="install", out=sys.stdout):
    """Copy the trigger to post-commit and post-merge in `target`; the exit status. A file there
    that this installer did not write is left alone and reported."""
    status = 0
    for name in TRIGGER_HOOKS:
        dest = os.path.join(target, name)
        if os.path.lexists(dest):
            try:
                with open(dest, encoding="utf-8", errors="replace") as handle:
                    ours = OWNED in handle.read()
            except OSError:
                ours = False
            if not ours:
                print("{}: not written by this installer; left as it is".format(dest), file=out)
                status = 1
                continue
            same = os.path.isfile(dest) and not os.path.islink(dest) and filecmp.cmp(TRIGGER, dest, shallow=False)
            if same and os.access(dest, os.X_OK):
                print("{}: up to date".format(dest), file=out)
                continue
        else:
            same = False
        if mode == "check":
            state = "not executable" if same else "differs from the source" if os.path.lexists(dest) else "not installed"
            print("{}: {}".format(dest, state), file=out)
            status = 1
        elif mode == "dry-run":
            print("{}: would install".format(dest), file=out)
        else:
            os.makedirs(target, exist_ok=True)
            if os.path.islink(dest):
                os.unlink(dest)
            shutil.copyfile(TRIGGER, dest)
            os.chmod(dest, 0o755)
            print("{}: installed".format(dest), file=out)
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cases", default=DEFAULT_CASES, help="the sealed case folder")
    parser.add_argument("--guard", default=DEFAULT_GUARD, help="the guard_git.py to judge")
    parser.add_argument("--install-trigger", action="store_true", help="install the post-commit and post-merge trigger")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="with --install-trigger: exit 1 if the installed copy differs")
    group.add_argument("--dry-run", action="store_true", help="with --install-trigger: say what would change")
    args = parser.parse_args(argv)
    if args.install_trigger:
        try:
            target = hooks_dir()
        except NotRun as reason:
            print(reason)
            return 1
        return install_trigger(target, "check" if args.check else "dry-run" if args.dry_run else "install")
    if args.check or args.dry_run:
        parser.error("--check and --dry-run go with --install-trigger")
    return run_cases(args.cases, os.path.abspath(args.guard))


if __name__ == "__main__":
    sys.exit(main())
