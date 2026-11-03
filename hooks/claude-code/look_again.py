#!/usr/bin/python3
"""Stop hook: send the agent back when a file it read has changed since.

An answer is only as current as the last read of its sources. Before the agent
stops, this reads the session's transcript for every file the agent read or
wrote with its file tools, and compares each file's modification time with the
last time the agent touched it. A file changed since then (by another session,
a person or a job) blocks the stop once, naming the file, so the agent reads it
again before it reports.

Only files touched since the last prompt a person typed count. The stop checks
the answer to that prompt, and a file read for an earlier prompt was checked at
that prompt's own stops. Compaction is not the boundary, since a long session
can run for days without one. Hook feedback, messages from other sessions,
task notifications, system notices, CI events and compaction summaries are not
prompts. The cost: a file the agent leans on from an earlier prompt without
touching it again is not checked.

A file the agent touched through Bash after reading it counts as seen, since
Bash edits are the agent's own: the command must name a path that resolves to
it from the session's directory, or, when the command may change directory,
its bare name or a path ending in it.

A file gone after a Bash command removed or moved it is the agent's own
deletion: it was named in a part of the command that starts with rm, unlink,
trash or git rm, or as a source of mv or git mv. A file gone after any other
command is reported, unless its folder is gone too: a removed worktree or
temp tree is routine cleanup (a folder renamed by someone else reads the same).

Claude Code's own temp tree (/tmp/claude-<uid>: scratchpads, task output) and
~/.claude/projects are skipped.

Claude Code writes the transcript asynchronously, so at a stop it may not yet
hold the turn's last entries. Before reading it, the hook waits up to CATCH_UP
seconds for the turn's last message (last_assistant_message) to appear; entries
are appended in order, so the tool results before that message are there too.

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
import time

FILE_TOOLS = {"Read", "Write", "Edit", "MultiEdit", "NotebookEdit"}
SLACK = 2.0  # seconds: a formatter hook may touch a file just after the agent's write
MAX_BLOCKS = 3
MAX_LISTED = 10
CATCH_UP = 2.0  # seconds to wait for the transcript to hold the turn's last message
TAIL = 1 << 20  # bytes read from the transcript's end to find that message
STATE_DIR = os.path.join(tempfile.gettempdir(), "claude-look-again")
NOT_TYPED = ("<system-reminder>", "<ci-monitor-event>", "<task-notification>")  # injected, origin-less
SKIP = (
    os.path.join(os.path.expanduser("~"), ".claude", "projects") + os.sep,
    "/tmp/claude-{}/".format(os.getuid()),
    "/private/tmp/claude-{}/".format(os.getuid()),
)
WORD = re.compile(r"""[^\s'"`;|&<>()=]+""")
MOVES = re.compile(r"(^|[\s;&|(])(cd|pushd|popd)(\s|$)|\b(git|make)\s+-C\s")
REMOVES = re.compile(r"\s*(sudo\s+)?(rm|unlink|mv|trash|git(\s+-C\s+\S+)?\s+(rm|mv))\s")
MOVERS = re.compile(r"\s*(sudo\s+)?(mv|git(\s+-C\s+\S+)?\s+mv)\s")
PARTS = re.compile(r"[;&|\n]+")
TRAILERS = re.compile(r"\s#.*$|\s*\d*[<>]+&?\s*\S*|\s\\$")  # comments, redirections, a line continuation
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


def is_prompt(entry):
    """True for a prompt a person typed, not a tool result, hook feedback, message or summary.

    An entry with no origin that opens with an injected notice is machine-sent, whatever follows
    the notice: in local transcripts that text is a side-session event, a peer message or a task
    from another session, never typed text. A typed prompt carries an origin.
    """
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isCompactSummary"):
        return False
    origin = entry.get("origin")
    if isinstance(origin, dict) and origin.get("kind") != "human":
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        if any(isinstance(block, dict) and block.get("type") == "tool_result" for block in content):
            return False
        content = "".join(block.get("text", "") for block in content if isinstance(block, dict))
    if not isinstance(content, str):
        return False
    return origin is not None or not content.lstrip().startswith(NOT_TYPED)


def last_seen(transcript_path):
    """Map each file the agent touched since the last prompt to (last touch, tool name, last file-tool touch).

    Times are epoch seconds. A Bash command naming a file moves its last touch but
    not its last file-tool touch.
    """
    pending, seen = {}, {}
    with open(transcript_path, encoding="utf-8") as handle:
        for line in handle:
            if '"tool_use"' not in line and '"tool_result"' not in line and '"user"' not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("isSidechain"):
                continue
            if is_prompt(entry):
                seen.clear()
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
                            seen[os.path.abspath(path)] = (when, name, when)
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
                                seen[path] = (when, OWN_REMOVAL if removes else name, seen[path][2])
                            for path in named(kept, by_base, cwd, loose):
                                seen[path] = (when, name, seen[path][2])
    return seen


def caught_up(transcript_path, message):
    """True when the transcript's last entry with text is this turn's, and ends the turn's last message."""
    with open(transcript_path, "rb") as handle:
        handle.seek(0, os.SEEK_END)
        handle.seek(max(0, handle.tell() - TAIL))
        lines = handle.read().decode("utf-8", "replace").splitlines()
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except ValueError:  # the cut first line, or a line still being written
            continue
        if entry.get("isSidechain"):
            continue
        if entry.get("type") == "user":
            return False  # a prompt or tool result after the last text: that text is not this turn's end
        content = (entry.get("message") or {}).get("content") if entry.get("type") == "assistant" else None
        if isinstance(content, list):
            content = "".join(
                block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
            )
        if isinstance(content, str) and content.strip():
            return " ".join(message.split()).endswith(" ".join(content.split()))
    return False


def changed_files(seen):
    """(path, detail, key) for each file changed or gone since the agent last touched it."""
    found = []
    for path, (when, tool, opened) in sorted(seen.items()):
        if path.startswith(SKIP):
            continue
        try:
            mtime = os.stat(path).st_mtime
        except FileNotFoundError:
            if tool != OWN_REMOVAL and os.path.isdir(os.path.dirname(path)):
                found.append((path, "now gone", "gone after {}".format(opened)))
            continue
        except OSError:
            continue
        if mtime > when + SLACK:
            detail = "changed {}, your last look {}".format(clock(mtime), clock(when))
            found.append((path, detail, str(mtime)))
    return found


def clock(epoch):
    """The time today, or the date and time for an earlier day."""
    moment = datetime.datetime.fromtimestamp(epoch)
    if moment.date() == datetime.date.today():
        return moment.strftime("%H:%M:%S")
    return moment.strftime("%Y-%m-%d %H:%M:%S")


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
    message = payload.get("last_assistant_message")
    if isinstance(message, str) and message.strip():
        deadline = time.time() + CATCH_UP
        while not caught_up(transcript, message) and time.time() < deadline:
            time.sleep(0.05)  # still behind: past the deadline, check what it holds
    state_path = os.path.join(STATE_DIR, session + ".json")
    state = load_state(state_path)
    reported = state.get("reported", {})
    blocks = state.get("blocks", 0) if payload.get("stop_hook_active") else 0

    for path in [p for p, key in reported.items() if key.startswith("gone") and os.path.exists(p)]:
        del reported[path]  # back again, so a later deletion is news
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
        # the last block the chain allows names every file; earlier ones name MAX_LISTED
        listed = fresh if blocks + 1 >= MAX_BLOCKS else fresh[:MAX_LISTED]
        for path, _, key in listed:
            reported[path] = key
        blocks += 1
        lines = ["- {} ({})".format(path, detail) for path, detail, _ in listed]
        if len(fresh) > len(listed):
            lines.append("- and {} more, listed when you stop again".format(len(fresh) - len(listed)))
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
