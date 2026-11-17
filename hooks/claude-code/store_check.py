#!/usr/bin/python3
"""Keep package installs and oversized trees out of the `_agent/` store (#283).

The rule is "Clones" in procedures/agent-workspace-layout.md: no clone, worktree, package install,
`node_modules` or build output under `_agent/`. This file checks it two ways.

As a CLI, for a person or a scheduled pulse on any client:

    /usr/bin/python3 store_check.py check [--store PATH] [--cap-gb 5] [--budget 120]

It exits 1 and lists every `node_modules` root under the store and every top-level tree over the
cap. A top-level tree is a folder directly under `_agent/`, or under `_agent/initiatives/` (one
initiative). Sizes are disk usage, as `du` counts them. A walk that outruns its budget fails as
unmeasured. A path it cannot read is listed as unmeasured too, beside everything else it found.
With no --store it uses the agent root found by walking upward from the working directory.

As a Claude Code hook pair (no arguments, the hook's JSON on stdin): at SessionStart it records the
store's `node_modules` roots once per session; at Stop it blocks when a root has appeared since,
naming it and the fix. It names ten roots at a stop and the rest at the stops after. Roots that
were already there never block, so a store still being cleaned does not hold every session. A
Stop with no baseline (the walk at SessionStart failed, or there is no record from the start) says
so once and lists the roots it sees, which are the baseline from then on. Sizes are the CLI's
alone: measuring them is too slow for every turn.

A `node_modules` under a folder whose name ends in `.app` is exempt: a shipped app copied in as
evidence, not an install. The folder name is the whole test, so an app's contents copied without
their `.app` folder are not exempt. The walk does not enter such a folder, and never follows a
symlink; a symlink named `node_modules` is not an install here. A hard-linked file counts once, as
`du` counts it.
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

NO_BASELINE = "This check has no record of the _agent/ store from this session's start, so it has no baseline."
FIX = ("Move each tree this session made, with the app or consumer that holds it, to your client scratch"
       " directory (the scratchpad your session names), and keep only its receipts, logs and hashes in the"
       " store. A brief that says \"move, don't delete\" still means out of _agent/. Leave a tree another"
       " session made, and say so in one line. The rule: " + RULE + ".")


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


def install_roots(store, deadline=None, unreadable=None):
    """Every `node_modules` directory under store, outermost only, outside `*.app` bundles;
    OutOfTime past the deadline. A directory that cannot be read raises, or with an `unreadable`
    list its error is added there and the walk goes on."""
    roots = []
    on_error = raise_walk_error if unreadable is None else unreadable.append
    for top, dirs, _ in os.walk(store, onerror=on_error):
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


def top_trees(store, unreadable):
    """The folders a size cap applies to: each child of the store, each initiative in place of
    `initiatives/` itself. A listing that fails adds its error to `unreadable` and the rest go on."""
    def folders(parent):
        try:
            names = sorted(os.listdir(parent))
        except OSError as error:
            unreadable.append(error)
            return []
        paths = [os.path.join(parent, name) for name in names]
        return [path for path in paths if os.path.isdir(path) and not os.path.islink(path)]

    trees = []
    for path in folders(store):
        trees.extend(folders(path) if os.path.basename(path) == "initiatives" else [path])
    return trees


def disk_usage(path, deadline):
    """Bytes on disk under path, as du counts them; OutOfTime past the deadline."""
    total, seen = 0, set()
    for top, dirs, files in os.walk(path, onerror=raise_walk_error):
        if time.monotonic() > deadline:
            raise OutOfTime(path)
        for name in dirs + files:
            if time.monotonic() > deadline:
                raise OutOfTime(path)
            info = os.lstat(os.path.join(top, name))
            if info.st_nlink > 1:
                if (info.st_dev, info.st_ino) in seen:
                    continue
                seen.add((info.st_dev, info.st_ino))
            total += info.st_blocks * 512
    if time.monotonic() > deadline:
        raise OutOfTime(path)
    return total


def check(store, cap_bytes, budget):
    """The problems found, one line each; empty when the store is clean."""
    unreadable = []
    problems = ["node_modules: {}".format(root) for root in install_roots(store, unreadable=unreadable)]
    trees = top_trees(store, unreadable)
    problems.extend(dict.fromkeys("unmeasured: {}".format(error) for error in unreadable))  # each path once
    deadline = time.monotonic() + budget
    for tree in trees:
        try:
            size = disk_usage(tree, deadline)
        except OutOfTime:
            problems.append("unmeasured: {} (the size walk ran out of its {:g} s budget)".format(tree, budget))
            break
        except OSError as error:  # one tree's read error keeps the findings before and after it
            problems.append("unmeasured: {} ({})".format(tree, error))
            continue
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
    problems = check(os.path.abspath(store), args.cap_gb * 1e9, args.budget)
    for line in problems:
        print(line)
    if problems:
        print("store_check: {} problem(s) under {}; the rule: {}".format(len(problems), store, RULE), file=sys.stderr)
        return 1
    return 0


def load_state(path):
    """The session's state ({store: {"seen": [...], "reported": [...]}}, with "baseline": false
    while a store has none), or {} when unreadable."""
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
    session = os.path.basename(str(payload.get("session_id") or "unknown"))
    state_path = os.path.join(STATE_DIR, session + ".json")
    state = load_state(state_path)
    store = find_store(payload.get("cwd") or os.getcwd())
    stores = [store] if store else []
    if payload.get("hook_event_name") == "Stop":
        stores = list(dict.fromkeys(list(state) + stores))
    deadline = time.monotonic() + HOOK_WALK
    for store in stores:
        reply = check_session_store(payload, store, state, state_path, deadline)
        if reply:
            return reply
    return None


def check_session_store(payload, store, state, state_path, deadline):
    """Check one recorded store, even after cwd leaves it, within the shared hook budget."""
    snapshot = state.get(store)
    stop = payload.get("hook_event_name") == "Stop"
    if not stop and snapshot is not None:
        return None  # the first snapshot holds: a resume or compaction keeps it
    # A stop with no record has no baseline either: the start walk failed under a version that
    # recorded nothing, the hook was installed mid-session, or the session came to this store later.
    if snapshot is None:
        snapshot = {"seen": [], "reported": [], "baseline": False}
    no_baseline = snapshot.get("baseline") is False
    try:
        current = install_roots(store, deadline)
    except (OutOfTime, OSError):
        # An incomplete walk cannot be the baseline, or replace one; the CLI reports the gap.
        if not stop or (no_baseline and not snapshot.get("told")):
            snapshot["told"] = stop
            state[store] = snapshot
            save_state(state_path, state)
            if stop:
                return block(NO_BASELINE + " The walk did not finish at this stop either, so run"
                             " `store_check.py check` for the node_modules roots under it. " + FIX)
        return None
    if no_baseline:
        state[store] = {"seen": current, "reported": []}  # what this walk saw is the baseline from here on
        save_state(state_path, state)
        if not stop:
            return None
        if current:
            return block(NO_BASELINE + " These node_modules roots are under it now, and this check cannot tell"
                         " which of them this session made:\n" + listing(current, " (`store_check.py check` lists them all)")
                         + "\n" + FIX)
        return None if snapshot.get("told") else block(
            NO_BASELINE + " It sees no node_modules under the store now, so there is nothing to move.")
    reported = set(snapshot.get("reported", []))
    seen = set(snapshot.get("seen", []))
    fresh = [root for root in current if root not in seen and root not in reported]
    if not fresh:
        return None
    # Only the roots this reply names are marked, so the next stop names the next ten (#287).
    snapshot["reported"] = sorted(reported | set(fresh[:MAX_LISTED]))
    save_state(state_path, state)
    return block("A package install appeared under the _agent/ store since this session started:\n"
                 + listing(fresh, ", named at the next stop") + "\n" + FIX)


def listing(roots, rest):
    """The first MAX_LISTED roots, one per line, then how many more and where they are named."""
    lines = ["- {}".format(root) for root in roots[:MAX_LISTED]]
    if len(roots) > MAX_LISTED:
        lines.append("- and {} more{}".format(len(roots) - MAX_LISTED, rest))
    return "\n".join(lines)


def block(reason):
    return {"decision": "block", "reason": reason}


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
