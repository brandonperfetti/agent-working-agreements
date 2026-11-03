#!/usr/bin/python3
"""Stop hook: send the agent back when a file it read has changed since.

An answer is only as current as the last read of its sources. Before the agent
stops, this reads the session's transcript for every file the agent read or
wrote with its file tools, and compares each file's modification time with the
last time the agent touched it. A file changed since then (by another session,
a person or a job) blocks the stop once, naming the file, so the agent reads it
again before it reports.

A file the agent touched through Bash after reading it counts as seen, since
Bash edits are the agent's own: the command must name a path that resolves to
it from the session's directory, or, when the command may change directory,
its bare name or a path ending in it.

A file gone after a Bash command removed or moved it is the agent's own
deletion: it was named in a part of the command that starts with rm, unlink,
trash or git rm, or as a source of mv or git mv. A file gone after any other
command is reported.

Each change is reported once, and a chain of stops is sent back at most
MAX_BLOCKS times, so a file that never stops changing cannot hold the agent.

Checks that need more than file times (re-fetching an index, a test run) belong
in the project's own Stop hook in its .claude/settings.json.
"""
import datetime
import json
import os
import re
import sys
import tempfile

FILE_TOOLS = {"Read", "Write", "Edit", "MultiEdit", "NotebookEdit"}
SLACK = 2.0  # seconds: a formatter hook may touch a file just after the agent's write
MAX_BLOCKS = 3
MAX_LISTED = 10
STATE_DIR = os.path.join(tempfile.gettempdir(), "claude-look-again")
SKIP = os.path.join(os.path.expanduser("~"), ".claude", "projects") + os.sep
WORD = re.compile(r"""[^\s'"`;|&<>()=]+""")
MOVES = re.compile(r"(^|[\s;&|(])(cd|pushd|popd)(\s|$)|\b(git|make)\s+-C\s")
REMOVES = re.compile(r"\s*(sudo\s+)?(rm|unlink|mv|trash|git(\s+-C\s+\S+)?\s+(rm|mv))\s")
MOVERS = re.compile(r"\s*(sudo\s+)?(mv|git(\s+-C\s+\S+)?\s+mv)\s")
PARTS = re.compile(r"[;&|\n]+")
TRAILERS = re.compile(r"\s#.*$|\s*\d*[<>]+&?\s*\S*")  # comments and redirections, not operands
OWN_REMOVAL = "Bash rm"


def seconds(stamp):
    """Epoch seconds from a transcript timestamp such as 2026-11-03T00:55:06.449Z."""
    return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()


def named(command, by_base, cwd, loose):
    """The tracked paths a Bash command names, from by_base (file name -> paths).

    A word must resolve to the path from cwd. When loose (cwd unknown, or the
    command may change directory), a bare name or a path ending in the word
    also counts.
    """
    found = set()
    for word in WORD.findall(command):
        candidates = by_base.get(os.path.basename(word))
        if not candidates:
            continue
        word = os.path.normpath(os.path.expandvars(os.path.expanduser(word)))
        for path in candidates:
            if os.path.isabs(word):
                hit = word == path
            else:
                hit = bool(cwd) and os.path.normpath(os.path.join(cwd, word)) == path
                hit = hit or bool(loose and path.endswith(os.sep + word))
            if hit:
                found.add(path)
    return found


def last_seen(transcript_path):
    """Map each file the agent touched to (epoch seconds of the last touch, tool name)."""
    pending, seen = {}, {}
    with open(transcript_path, encoding="utf-8") as handle:
        for line in handle:
            if '"tool_use"' not in line and '"tool_result"' not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("isSidechain"):
                continue
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    pending[block.get("id")] = (block.get("name"), block.get("input") or {})
                elif block.get("type") == "tool_result" and "timestamp" in entry:
                    name, args = pending.pop(block.get("tool_use_id"), (None, {}))
                    if block.get("is_error") or name is None:
                        continue
                    when = seconds(entry["timestamp"])
                    if name in FILE_TOOLS:
                        path = args.get("file_path") or args.get("notebook_path")
                        if path:
                            seen[os.path.abspath(path)] = (when, name)
                    elif name == "Bash":
                        command = args.get("command", "")
                        cwd = entry.get("cwd")
                        loose = not cwd or bool(MOVES.search(command))
                        by_base = {}
                        for path in seen:
                            by_base.setdefault(os.path.basename(path), []).append(path)
                        for part in PARTS.split(command):
                            removes = REMOVES.match(part) and "--cached" not in part
                            kept = ""
                            if removes and MOVERS.match(part):  # mv's last operand stays
                                words = TRAILERS.sub("", part).split()
                                part, kept = " ".join(words[:-1]), words[-1]
                            for path in named(part, by_base, cwd, loose):
                                seen[path] = (when, OWN_REMOVAL if removes else name)
                            for path in named(kept, by_base, cwd, loose):
                                seen[path] = (when, name)
    return seen


def changed_files(seen):
    """(path, detail, key) for each file changed or gone since the agent last touched it."""
    found = []
    for path, (when, tool) in sorted(seen.items()):
        if path.startswith(SKIP):
            continue
        try:
            mtime = os.stat(path).st_mtime
        except FileNotFoundError:
            if tool != OWN_REMOVAL:
                found.append((path, "now gone", "gone"))
            continue
        except OSError:
            continue
        if mtime > when + SLACK:
            detail = "changed {}, your last look {}".format(clock(mtime), clock(when))
            found.append((path, detail, str(mtime)))
    return found


def clock(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime("%H:%M:%S")


def load_state(path):
    try:
        with open(path, encoding="utf-8") as handle:
            state = json.load(handle)
        if isinstance(state, dict):
            return state
    except (OSError, ValueError):
        pass
    return {}


def save_state(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(state, handle)


def decide(payload):
    """The hook's JSON reply, or None to let the agent stop."""
    transcript = payload.get("transcript_path")
    session = os.path.basename(str(payload.get("session_id") or "unknown"))
    if not transcript or not os.path.exists(transcript):
        return None
    state_path = os.path.join(STATE_DIR, session + ".json")
    state = load_state(state_path)
    reported = state.get("reported", {})
    blocks = state.get("blocks", 0) if payload.get("stop_hook_active") else 0

    fresh = [f for f in changed_files(last_seen(transcript)) if reported.get(f[0]) != f[2]]
    if not fresh:
        reply = None
    elif blocks >= MAX_BLOCKS:
        reply = {
            "systemMessage": "look_again: {} file(s) still changed after {} looks; stopping anyway.".format(
                len(fresh), MAX_BLOCKS
            )
        }
    else:
        for path, _, key in fresh[:MAX_LISTED]:
            reported[path] = key
        blocks += 1
        lines = ["- {} ({})".format(path, detail) for path, detail, _ in fresh[:MAX_LISTED]]
        if len(fresh) > MAX_LISTED:
            lines.append("- and {} more, listed when you stop again".format(len(fresh) - MAX_LISTED))
        reply = {
            "decision": "block",
            "reason": "Look again before you stop. These files changed after you last read or wrote them:\n"
            + "\n".join(lines)
            + "\nRead each one again. If a change alters your answer or your work, update it; if not, say so in one line.",
        }
    save_state(state_path, {"reported": reported, "blocks": blocks})
    return reply


def main():
    try:
        reply = decide(json.load(sys.stdin))
    except Exception as error:  # a broken check must never trap the agent
        print("look_again: {}".format(error), file=sys.stderr)
        return 1
    if reply:
        print(json.dumps(reply))
    return 0


if __name__ == "__main__":
    sys.exit(main())
