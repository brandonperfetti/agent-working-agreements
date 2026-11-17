#!/usr/bin/python3
"""PreToolUse hook for Codex: hand each shell command to guard_git.py, and deny unless it passes.

guard_git.py owns the rules. This file only carries the command to it and reads the verdict,
because Codex runs the command when a hook crashes, times out or prints something it cannot read.
So every outcome but a clean pass (exit 0, nothing on stdout) is turned into a denial here.
Codex still runs the command when this file cannot start, is killed at Codex's own timeout, or
the hook is untrusted or disabled: the canary before each merge is the check for that.
"""
import json
import os
import subprocess
import sys

MARK = "awa-guard-codex"
HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(HERE, "guard_git.py")  # installed beside this file
PYTHON = "/usr/bin/python3"
TIMEOUT = 10  # seconds, as Claude Code allows the guard; the Codex hook entry allows more
HAND_BACK = "hand it back rather than routing around this"


def decide(raw, guard=GUARD, python=PYTHON, timeout=TIMEOUT, no_repo_dir=HERE):
    """Why this tool call is denied, or None when the guard passed it."""
    try:
        payload = json.loads(raw)
    except ValueError:
        return "the hook input could not be read; " + HAND_BACK
    tool_input = payload.get("tool_input") if isinstance(payload, dict) else None
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return "a shell call with no command the hook can read; " + HAND_BACK
    # Only an absolute directory names the checkout. Without one the guard runs outside any
    # repository, so a check that needs the checkout denies.
    cwd = payload.get("cwd")
    env = dict(os.environ)
    if not (isinstance(cwd, str) and os.path.isabs(cwd) and os.path.isdir(cwd)):
        cwd = no_repo_dir
        env["GIT_CEILING_DIRECTORIES"] = os.path.dirname(no_repo_dir)
    try:
        result = subprocess.run(
            [python, "-I", guard],
            input=json.dumps({"tool_input": {"command": command}, "cwd": cwd}),
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return "the guard timed out after {} s; {}".format(timeout, HAND_BACK)
    except (OSError, subprocess.SubprocessError) as error:
        return "the guard could not run ({}); {}".format(error, HAND_BACK)
    if result.returncode != 0:
        return "the guard exited {}; {}".format(result.returncode, HAND_BACK)
    output = result.stdout.strip()
    if not output:
        return None
    try:
        decision = json.loads(output)["hookSpecificOutput"]
        reason = decision["permissionDecisionReason"]
        if decision["permissionDecision"] == "deny" and isinstance(reason, str) and reason.strip():
            return reason.replace("~/.claude/hooks/guard_git.py", guard)
    except (ValueError, KeyError, TypeError):
        pass
    return "the guard's verdict could not be read; " + HAND_BACK


def main():
    """Print Codex's deny decision unless the guard passed the command."""
    reason = decide(sys.stdin.read())
    if reason is not None:  # only None is a pass; an empty reason is still a denial
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "{}: {}".format(MARK, reason or "denied; " + HAND_BACK),
        }}))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:  # Codex blocks on exit 2 with a reason on stderr, and on little else
        sys.stderr.write("{}: the hook failed ({}); {}\n".format(MARK, type(error).__name__, HAND_BACK))
        sys.exit(2)
