#!/usr/bin/python3
"""Keep package installs and oversized trees out of the `_agent/` store (#283).

The rule is "Clones" in procedures/agent-workspace-layout.md: no clone, worktree, package install,
`node_modules` or build output under `_agent/`. This file checks it two ways.

As a CLI, for a person or a scheduled pulse on any client:

    /usr/bin/python3 store_check.py check [--store PATH] [--cap-gb 5] [--budget 120]

It exits 1 and lists every `node_modules` root under the store and every top-level tree over the
cap. A top-level tree is a folder directly under `_agent/`, or under `_agent/initiatives/` (one
initiative). Sizes are disk usage, as `du` counts them. A walk that outruns its budget or cannot
read a tree fails as unmeasured. With no --store it uses the agent root found by walking upward
from the working directory.

As a Claude Code hook pair (no arguments, the hook's JSON on stdin): at SessionStart it records the
store's `node_modules` roots once per session; at Stop it blocks once when a root has appeared
since, naming it and the fix. Roots that were already there never block, so a store still being
cleaned does not hold every session. Sizes are the CLI's alone: measuring them is too slow for
every turn.

A `node_modules` inside a `*.app` bundle is exempt: a shipped app copied in as evidence, not an
install. The walk does not enter a bundle, and never follows a symlink; a symlink named
`node_modules` is not an install here. A hard-linked file counts once, as `du` counts it.
"""
import argparse
import json
import os
import sys
import tempfile
import time

CAP_GB = 5
BUDGET = 120.0  # seconds the CLI spends measuring sizes before it fails
MAX_LISTED = 10
HOOK_WALK = 20.0  # seconds the hook spends walking the store; a hook entry's timeout is 30
STATE_DIR = os.path.join(tempfile.gettempdir(), "claude-store-check")
RULE = "procedures/agent-workspace-layout.md, \"Clones\", in agent-working-agreements"


class OutOfTime(Exception):
    pass


def raise_walk_error(error):
    """Propagate an unreadable directory instead of treating its contents as absent."""
    raise error


def find_store(start):
    """The `_agent/` directory of the agent root above start, or None off-fleet."""
    path = os.path.abspath(start)
    while True:
        candidate = os.path.join(path, "_agent")
        if os.path.isdir(candidate) and not os.path.islink(candidate):
            return os.path.realpath(candidate)
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent


def install_roots(store, deadline=None):
    """Every `node_modules` directory under store, outermost only, outside `*.app` bundles;
    OutOfTime past the deadline."""
    roots = []
    for top, dirs, _ in os.walk(store, onerror=raise_walk_error):
        if deadline is not None and time.monotonic() > deadline:
            raise OutOfTime(store)
        keep = []
        for name in dirs:
            if os.path.islink(os.path.join(top, name)):
                continue
            if name == "node_modules":
                roots.append(os.path.join(top, name))
            elif not name.endswith(".app"):
                keep.append(name)
        dirs[:] = keep  # os.walk does not follow symlinks; this prunes installs and bundles
    return sorted(roots)


def top_trees(store):
    """The folders a size cap applies to: each child of the store, each initiative in place of
    `initiatives/` itself."""
    trees = []
    for name in sorted(os.listdir(store)):
        path = os.path.join(store, name)
        if not os.path.isdir(path) or os.path.islink(path):
            continue
        if name == "initiatives":
            trees.extend(
                os.path.join(path, child) for child in sorted(os.listdir(path))
                if os.path.isdir(os.path.join(path, child)) and not os.path.islink(os.path.join(path, child))
            )
        else:
            trees.append(path)
    return trees


def disk_usage(path, deadline):
    """Bytes on disk under path, as du counts them; OutOfTime past the deadline."""
    total, seen = 0, set()
    for top, dirs, files in os.walk(path, onerror=raise_walk_error):
        if time.monotonic() > deadline:
            raise OutOfTime(path)
        for name in dirs + files:
            info = os.lstat(os.path.join(top, name))
            if info.st_nlink > 1:
                if (info.st_dev, info.st_ino) in seen:
                    continue
                seen.add((info.st_dev, info.st_ino))
            total += info.st_blocks * 512
    return total


def check(store, cap_bytes, budget):
    """The problems found, one line each; empty when the store is clean."""
    problems = ["node_modules: {}".format(root) for root in install_roots(store)]
    deadline = time.monotonic() + budget
    for tree in top_trees(store):
        try:
            size = disk_usage(tree, deadline)
        except OutOfTime:
            problems.append("unmeasured: {} (the size walk ran out of its {:g} s budget)".format(tree, budget))
            break
        if size > cap_bytes:
            problems.append("over cap: {} ({:.1f} GB > {:g} GB)".format(tree, size / 1e9, cap_bytes / 1e9))
    return problems


def cli(argv):
    parser = argparse.ArgumentParser(prog="store_check.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("check", help="list installs and oversized trees under the store")
    run.add_argument("--store", help="the _agent/ directory (default: found above the working directory)")
    run.add_argument("--cap-gb", type=float, default=CAP_GB, help="size cap per top-level tree, in GB")
    run.add_argument("--budget", type=float, default=BUDGET, help="seconds allowed for the size walk")
    args = parser.parse_args(argv)
    store = args.store or find_store(os.getcwd())
    if not store or not os.path.isdir(store):
        print("store_check: no _agent/ store found", file=sys.stderr)
        return 2
    try:
        problems = check(os.path.abspath(store), args.cap_gb * 1e9, args.budget)
    except OSError as error:
        problems = ["unmeasured: {}".format(error)]
    for line in problems:
        print(line)
    if problems:
        print("store_check: {} problem(s) under {}; the rule: {}".format(len(problems), store, RULE), file=sys.stderr)
        return 1
    return 0


def load_state(path):
    """The session's state ({store: {"seen": [...], "reported": [...]}}), or {} when unreadable."""
    try:
        with open(path, encoding="utf-8") as handle:
            state = json.load(handle)
        return state if isinstance(state, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(path, state):
    """Write state atomically, leaving no temp file behind on failure."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".state-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle)
        os.replace(temp, path)
    except BaseException:
        try:
            os.unlink(temp)
        except OSError:
            pass
        raise


def decide(payload):
    """The hook's JSON reply, or None."""
    store = find_store(payload.get("cwd") or os.getcwd())
    if not store:
        return None
    session = os.path.basename(str(payload.get("session_id") or "unknown"))
    state_path = os.path.join(STATE_DIR, session + ".json")
    state = load_state(state_path)
    snapshot = state.get(store)
    if snapshot is not None and payload.get("hook_event_name") == "SessionStart":
        return None  # the first snapshot holds: a resume or compaction keeps it
    try:
        current = install_roots(store, time.monotonic() + HOOK_WALK)
    except (OutOfTime, OSError):
        return None  # an incomplete walk cannot replace the baseline; the CLI reports the gap
    if snapshot is None:
        state[store] = {"seen": current, "reported": []}
        save_state(state_path, state)
        return None
    reported = set(snapshot.get("reported", []))
    seen = set(snapshot.get("seen", []))
    fresh = [root for root in current if root not in seen and root not in reported]
    if not fresh:
        return None
    snapshot["reported"] = sorted(reported | set(fresh))
    save_state(state_path, state)
    lines = ["- {}".format(root) for root in fresh[:MAX_LISTED]]
    if len(fresh) > MAX_LISTED:
        lines.append("- and {} more".format(len(fresh) - MAX_LISTED))
    return {
        "decision": "block",
        "reason": "A package install appeared under the _agent/ store since this session started:\n"
        + "\n".join(lines)
        + "\nIf this session made it, move each tree, with the app or consumer that holds it, to your client"
        " scratch directory (the scratchpad your session names), and keep only its receipts, logs and hashes"
        " in the store. A brief that says \"move, don't delete\" still means out of _agent/. If another"
        " session made it, leave it and say so in one line. The rule: " + RULE + ".",
    }


def main(argv):
    if argv:
        return cli(argv)
    try:
        reply = decide(json.load(sys.stdin))
    except Exception as error:  # a broken check must never trap the agent
        print("store_check: {}".format(error), file=sys.stderr)
        return 1
    if reply:
        print(json.dumps(reply))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
