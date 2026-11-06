#!/usr/bin/python3
"""PreToolUse guard for the Bash tool: the git rules no agent may break.

Denies force-pushes, pushes to a release branch and PR merges into develop,
main or master (or whose base it cannot read), per the Sans Faux profile's Git
ritual and merge boundary, and commits or pushes whose author is not Brandon's
email, or whose message carries an attribution trailer (RULE ZERO). Merges between
feature, wave, lane and hotfix branches pass.
It parses the command rather than grepping it, so a commit message that
mentions `git push --force` passes. It stops honest mistakes, not a determined
bypass: git aliases, refspecs in shell variables and commands inside a quoted
"$(...)" are not resolved.
"""
import json
import os
import re
import shlex
import subprocess
import sys

RELEASE_BRANCHES = {"master", "main"}
PROTECTED_BASES = {"develop", "main", "master"}
AUTHOR_EMAIL = "brandon@brandonperfetti.com"
# The profile's no-attribution rule, as `procedures/rule-zero-check.md` greps for it.
TRAILER = re.compile(r"^(co-authored-by|[a-z-]*-session)\s*:|generated with", re.IGNORECASE | re.MULTILINE)
# `$name`, `${…}`, `$(…)`, the special parameters (`$*`, `$@`, `$#`, `$?`, `$$`, `$!`, `$-`, `$0`…) and backticks.
EXPANSION = re.compile(r"(?<!\\)\$(?:[\w{(]|[*@#?$!\-0-9])|`")


def expands(text):
    """True when the shell would expand something in `text`: a `$…` or backtick not escaped by an
    odd number of backslashes (`\\$M` is a literal backslash followed by an expansion)."""
    return bool(EXPANSION.search(re.sub(r"\\\\", "", text or "")))
# What the exact `-m "$(cat <<'TAG' … TAG\n)"` form looks like once its body has been blanked and the
# shell quotes removed: heredoc_commit_messages has already read that body.
EXACT_FORM = re.compile(r"^\$\(cat <<['\"]?[^'\"\s]*['\"]?[ \t]*\n+\)$")  # `"TAG"` loses its quotes to the lexer
COMMIT_VALUE_OPTS = {
    "-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c", "--reedit-message",
    "--fixup", "--squash", "--author", "--date", "--cleanup", "--trailer", "-t", "--template",
}
ASSIGNMENT = re.compile(r"[A-Za-z_]\w*=")
WRAPPERS = {"command", "env", "exec", "nohup", "sudo", "time", "xargs"}
SHELLS = {"ash", "bash", "dash", "ksh", "mksh", "sh", "zsh"}
SEPARATORS = ";&|()\n"
GIT_VALUE_OPTS = {"-C", "-c", "--git-dir", "--namespace", "--work-tree"}
PUSH_VALUE_OPTS = {"-o", "--exec", "--push-option", "--receive-pack", "--repo"}
GH_VALUE_OPTS = {"-R", "--repo"}
# Options that take a value, for `gh pr merge` and `gh api` alike; none is a flag in the other.
GH_ARG_VALUE_OPTS = GH_VALUE_OPTS | {
    "-A", "--author-email", "-b", "--body", "-F", "--body-file", "--field",
    "--match-head-commit", "-t", "--subject", "--template", "-f", "--raw-field",
    "-H", "--header", "--hostname", "--input", "-p", "--preview", "-q", "--jq",
    "--cache", "-X", "--method",
}
GH_MERGE_MUTATIONS = re.compile(
    r"mergePullRequest|enablePullRequestAutoMerge|mergeBranch|enqueuePullRequest"
)
FORCE_FLAGS = {"--force", "--force-if-includes", "--force-with-lease", "--mirror"}


def heredoc_word(text):
    """Read one shell word (the heredoc delimiter) with quote removal: (tag, quoted, length)."""
    tag, quoted, index = "", False, 0
    while index < len(text):
        char = text[index]
        if char in " \t\n;|&<>()":
            break
        if char == "\\" and index + 1 < len(text):
            tag += text[index + 1]; quoted = True; index += 2; continue
        if char in "'\"":
            end = text.find(char, index + 1)
            if end == -1:
                break
            tag += text[index + 1 : end]; quoted = True; index = end + 1; continue
        tag += char; index += 1
    return tag, quoted, index


def herestring_word(text):
    """The whole shell word after `<<<` as git would read it: (text, expandable, length).

    Quoted parts join into one word (`''"$M"`); anything outside single quotes may expand."""
    word, expandable, index = "", False, 0
    while index < len(text):
        char = text[index]
        if char in " \t\n;|&<>()":
            break
        if char == "\\" and index + 1 < len(text):
            word += text[index + 1]; index += 2; continue
        if char == "'":
            end = text.find("'", index + 1)
            if end == -1:  # the quoted word runs past this line: not readable here
                expandable = True; break
            word += text[index + 1 : end]; index = end + 1; continue
        if char == '"':
            part, raw_start, index = "", index + 1, index + 1
            while index < len(text) and text[index] != '"':
                if text[index] == "\\" and index + 1 < len(text):
                    part += text[index + 1]; index += 2; continue
                part += text[index]; index += 1
            if index >= len(text):  # unterminated on this line: not readable here
                expandable = True; break
            expandable = expandable or expands(text[raw_start:index])  # parity on the raw text
            word += part; index += 1; continue
        if text.startswith("$'", index):  # ANSI-C quoting decodes escapes the hook does not model
            expandable = True
            end = text.find("'", index + 2)
            index = len(text) if end == -1 else end + 1
            continue
        word += char
        expandable = expandable or expands(text[max(index - 2, 0) : index + 2])
        index += 1
    return word, expandable, index


def redirections(line, quote=None):
    """Heredoc and here-string operators in one line, outside quotes and comments, in order.

    Returns (ops, state). Entries are ("heredoc", dash, tag, quoted, pos, fd) or
    ("herestring", text, expandable, pos, fd); `pos` is the operator's offset, `fd` the descriptor
    (0 unless a digit precedes the operator). `quote` is the quote still open from the previous
    line, so quoted text spanning lines is text. `state` carries the quote left open at the end and
    whether the line holds command separators outside quotes ("complex")."""
    ops, index, outer, separators = [], 0, [], []  # `outer`: quotes suspended by `$(`
    while index < len(line):
        char = line[index]
        if quote == "'":
            if char == "'":
                quote = None
            index += 1; continue
        arithmetic = line.startswith("$((", index) or (
            quote is None and line.startswith("((", index) and (index == 0 or line[index - 1] in " \t;|&")
        )
        if arithmetic:  # `$((1<<3))` and `(( x <<= 1 ))` shift bits; no operator lives inside them
            depth, index = 2, index + (3 if line[index] == "$" else 2)
            while index < len(line) and depth:
                depth += {"(": 1, ")": -1}.get(line[index], 0)
                index += 1
            continue
        if line.startswith("$(", index):  # a command substitution resets quoting inside it
            outer.append(quote); quote = None; index += 2; continue
        if char == ")" and outer and quote is None:
            quote = outer.pop(); index += 1; continue
        if quote == '"':
            if char == "\\":
                index += 2; continue
            if char == '"':
                quote = None
            index += 1; continue
        if char == "\\":
            index += 2; continue
        if char in "'\"":
            quote = char; index += 1; continue
        if char == "#" and (index == 0 or line[index - 1] in " \t;|&("):
            break  # a comment: nothing after it is an operator
        if char in ";|&" and not outer:
            separators.append(index)
        fd = int(line[index - 1]) if index and line[index - 1] in "0123456789" and (index < 2 or line[index - 2] in " \t") else 0
        if line.startswith("<<<", index):
            start = index + 3
            while start < len(line) and line[start] in " \t":
                start += 1
            text, expandable, used = herestring_word(line[start:])
            ops.append(("herestring", text, expandable, index, fd)); index = start + max(used, 1); continue
        if line.startswith("<<", index):
            dash = line[index + 2 : index + 3] == "-"
            start = index + 2 + dash
            while start < len(line) and line[start] in " \t":
                start += 1
            tag, quoted, used = heredoc_word(line[start:])
            if tag or quoted:  # `<<''` is a legal empty delimiter; a bare `<<` is not a heredoc
                ops.append(("heredoc", dash, tag, quoted, index, fd))
            index = start + max(used, 1); continue
        index += 1
    first = min((op[4] if op[0] == "heredoc" else op[3] for op in ops), default=len(line))
    # Separators before the first operator only prefix the command (`./check.sh && git commit …`);
    # a separator after it means another command shares the line with the redirection.
    complex_line = any(pos > first for pos in separators)
    return ops, {"quote": quote if not outer else outer[0] or quote, "complex": complex_line}


def heredocs(command):
    """Each heredoc in the command as (head, body, dash, quoted, span); the body ends at the exact
    delimiter line (`<<-` also strips leading tabs, as the shell does). Unterminated: to the end.
    `span` is the (start, end) of the raw body and delimiter line, for blanking."""
    found, pos, quote = [], 0, None
    while pos < len(command):
        line_end = command.find("\n", pos)
        if line_end == -1:
            return found
        line_no = command.count("\n", 0, pos)  # the head's real line index
        head = command[pos:line_end]
        cursor = line_end + 1
        ops, state = redirections(head, quote)
        quote = state["quote"]  # a quote left open makes the next line text, not operators
        for op in ops:
            if op[0] != "heredoc":
                continue
            _, dash, tag, quoted, _offset, _fd = op
            lines, body, end = [], None, len(command)
            for line in command[cursor:].split("\n"):
                check = line.lstrip("\t") if dash else line
                if check == tag:
                    body = "\n".join(lines) + ("\n" if lines else "")
                    end = cursor + len(body) + len(line)
                    break
                lines.append(line)
            if body is None:
                body = "\n".join(lines)
            if dash:
                body = re.sub(r"^\t+", "", body, flags=re.MULTILINE)
            found.append((head, body, dash, quoted, (cursor, end), line_no))
            cursor = end + 1 if end < len(command) else end  # body text is data, never another heredoc
        pos = cursor
    return found


def drop_heredocs(command):
    """Blank each heredoc body, unless a shell is reading it as commands."""
    for head, body, dash, quoted, (start, end), _line in reversed(heredocs(command)):
        # A shell as a command word (`bash`, `/bin/zsh -s`, `dash`), not a script name such as
        # `check.sh`; `source` and `.` only where a command starts, so `git add .` is an argument.
        if re.search(r"(^|[\s;&|(/\"'])(ba|z|da|k|mk|a)?sh(?=[\s<\"';&|)]|$)", head) or re.search(
            r"(^|[;&|(])\s*(source|\.)(?=\s)", head
        ):
            continue
        command = command[:start] + command[end:]  # body and delimiter line go; the head stays
    return command


def segments(command):
    """Split a command line into one token list per simple command."""
    command = drop_heredocs(command)
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=SEPARATORS)
        lexer.whitespace = " \t\r"
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        # Unbalanced quotes: read it as plain words so a real push still shows.
        parts = re.split(r"&&|\|\||[;|\n()]", command)
        return [part.replace('"', " ").replace("'", " ").split() for part in parts]
    result, current = [], []
    for token in tokens:
        if token and set(token) <= set(SEPARATORS):
            result.append(current)
            current = []
        else:
            current.append(token)
    result.append(current)
    return result


def strip_redirects(tokens):
    kept, skip = [], False
    for token in tokens:
        if skip:
            skip = False
        elif re.fullmatch(r"\d*[<>]+", token):
            skip = True
        elif not re.match(r"\d*[<>]", token):
            kept.append(token)
    return kept


def strip_prefix(tokens):
    """Drop env assignments and wrappers such as `env` or `sudo`."""
    while tokens:
        if ASSIGNMENT.match(tokens[0]):
            tokens = tokens[1:]
        elif os.path.basename(tokens[0]) in WRAPPERS:
            tokens = tokens[1:]
            while tokens and tokens[0].startswith("-"):
                tokens = tokens[1:]
        else:
            break
    return tokens


def current_branch(directory):
    try:
        result = subprocess.run(
            ["git", "-C", directory, "symbolic-ref", "--short", "-q", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip()


TIMEOUT = "timeout"  # git_lines' marker for a read that ran out of time (not a failure, not empty)


def git_lines(directory, args, env=None, raw=False):
    """Run a read-only git command; None when it fails (git reports its own error), TIMEOUT when
    it ran out of time, else its output lines (`raw`: the text itself, so a record separator such
    as `\x1e`, which `splitlines` would read as a line break, survives)."""
    try:
        result = subprocess.run(
            ["git", "-C", directory] + args,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=5,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return TIMEOUT
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    return result.stdout if raw else result.stdout.splitlines()


def email_of(ident):
    match = re.search(r"<([^>]*)>", ident)
    return match.group(1) if match else ident.strip()


def check_commit(args, directory, configs, env, stdin_bodies=None, written=()):
    """Resolve the author the commit will carry, as git would, then read its message."""
    message, stdin_used, dry_run = commit_message(args, directory, written=written)
    if dry_run:  # option-aware: `-m --dry-run` is a message, not a dry run; `-n` is --no-verify
        return None
    editors = {"GIT_EDITOR", "VISUAL", "EDITOR"} & set(env)
    settings = {c.partition("=")[0].lower() for c in configs} & {"core.editor", "commit.template", "sequence.editor"}
    if editors or settings:  # an editor or template set for this command may add text after this check
        return "a commit whose message cannot be checked for attribution trailers"
    author = None
    for index, arg in enumerate(args):
        if arg == "--":
            break
        if arg.startswith("--author="):
            author = arg.split("=", 1)[1]
        elif arg == "--author" and index + 1 < len(args):
            author = args[index + 1]
    if author is None:
        options = [part for config in configs for part in ("-c", config)]
        lines = git_lines(directory, options + ["var", "GIT_AUTHOR_IDENT"], dict(os.environ, **env))
        author = lines[0] if lines and lines is not TIMEOUT else None  # fail-open: git reports it
    if author is not None:
        email = email_of(author)
        if email != AUTHOR_EMAIL:
            return "a commit authored as {}".format(email or "an empty email")
    if TRAILER.search(message):
        return "a commit carrying an attribution trailer"
    if stdin_used:
        # Each stdin-reading commit consumes the body written for it: none left means a pipe, and a
        # body of None means the shell would expand it (an unquoted `$VAR`), which cannot be read here.
        body = stdin_bodies.pop(0) if stdin_bodies else None
        if body is None:
            return "a commit whose message cannot be checked for attribution trailers"
    return None


def message_of(directory, revision):
    """The full message of one commit; a value that looks like an option is not a revision."""
    if not revision or revision.startswith("-"):
        return []
    lines = git_lines(directory, ["log", "-1", "--format=%B", "--end-of-options", revision])
    return None if lines is TIMEOUT else (lines or [])


COMMIT_LONG_OPTS = (
    "--amend", "--author", "--cleanup", "--date", "--dry-run", "--file", "--fixup", "--message",
    "--edit", "--no-edit", "--no-verify", "--reedit-message", "--reset-author", "--reuse-message", "--squash",
    "--template", "--trailer", "--untracked-files", "--gpg-sign",
)


def canonical(name):
    """Git accepts a unique prefix of a long option (`--am`, `--trail`); resolve it, else keep it."""
    if not name.startswith("--") or name in COMMIT_LONG_OPTS:
        return name
    matches = [opt for opt in COMMIT_LONG_OPTS if opt.startswith(name)]
    return matches[0] if len(matches) == 1 else name


def commit_message(args, directory, read=True, written=()):
    """The message text the command supplies: -m parts, -F files and --trailer lines.

    `written` holds the words of the commands that run first: a `-F` file one of them names may be
    rewritten before the commit reads it, so its text on disk now proves nothing.

    `-F -` is read by heredoc_commit_messages from the raw command; a piped stdin is not readable
    here, and the push check reads the committed message instead.
    """
    parts, supplied, stdin_used, dry_run, template = [], False, False, False, False
    unreadable = False  # a message source the hook cannot read: a special file, a timed-out revision
    index = 0
    while index < len(args) and args[index] != "--":
        arg = args[index]
        name, has_value, value = arg.partition("=")
        name = canonical(name)
        if arg.startswith("--") and not has_value:
            arg = name  # an abbreviated long option behaves as its full name below
        # A short-option cluster ends at its first value-taking letter: `-am msg`, `-aF file`,
        # `-mmsg`, `-F-`; `-tform` is -t with the value "form", and takes no message.
        # `-u[mode]` and `-S[keyid]` take an attached optional value, so they end a cluster.
        cluster = re.match(r"-([a-tv-zA-RT-Z]*?)([mFtCc])(.*)", arg) if not arg.startswith("--") else None
        if cluster:
            letter, value = cluster.group(2), cluster.group(3)
            name = "-" + letter
            has_value = bool(value)
            if "e" in cluster.group(1) and read:
                unreadable = True  # `-em msg`, `-aem msg`: the editor opens after the message is set
        elif read and re.fullmatch(r"-[a-zA-Z]*e[a-zA-Z]*", arg):
            unreadable = True  # `-ae`: a cluster of flags with the editor among them
        if not has_value and (arg in COMMIT_VALUE_OPTS or cluster) and index + 1 < len(args):
            value = args[index + 1]
            index += 1
        if arg == "--dry-run":
            dry_run = True
        if read and name in ("-m", "--message", "--trailer") and value and (value.startswith("$") or expands(value)) and not EXACT_FORM.match(value):
            # `-m "$(cat msg.txt)"`, `-m "$MSG"`, `-m $'…'` (ANSI-C quoting, whose escapes the lexer
            # leaves undecoded): the shell fills these in, not the text here.
            unreadable = True
        if name in ("-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c",
                    "--reedit-message", "--fixup", "--squash"):
            supplied = True
        if name in ("-m", "--message"):
            parts.append(value)
        elif name in ("-e", "--edit") and read:
            unreadable = True  # an editor adds text after this check; the push scan is the backstop
        elif name in ("-t", "--template"):
            template = True  # read only when the editor opens, which an explicit message prevents
        elif name == "--trailer":
            # Git accepts `Key=Value` as well as `Key: Value`; normalise to the colon form.
            parts.append(re.sub(r"^\s*([^:=]+?)\s*[:=]\s*", r"\1: ", value))
        elif name in ("-F", "--file") and value == "-":
            stdin_used = True
        elif name in ("-F", "--file") and value and read:
            path = os.path.join(directory, os.path.expanduser(value))
            # Only a regular file is read: /dev/stdin, a FIFO or a device could block the hook or
            # hand it the hook's own stdin, so those count as unreadable.
            base = os.path.basename(value)  # `> ./msg.txt`, `>msg.txt` and `msg.txt` name one file
            named = any(os.path.basename(re.sub(r"^\d*[<>&|]+", "", word)) == base for word in written)
            # A redirect target the shell fills in (`> $F`) may be this file too.
            targets = [w.lstrip("0123456789>") if ">" in w else w for i, w in enumerate(written) if ">" in w or (i and written[i - 1].endswith(">"))]
            named = named or any(expands(t) for t in targets)
            if named or not os.path.isfile(path) or os.path.realpath(path).startswith("/dev/"):
                unreadable = True
            else:
                try:
                    with open(path, errors="replace") as handle:
                        parts.append(handle.read())
                except OSError:
                    unreadable = True
        elif name in ("-C", "--reuse-message", "-c", "--reedit-message") and value and read:
            reused = message_of(directory, value)
            if reused is None:
                unreadable = True
            else:
                parts.extend(reused)
        elif name in ("--fixup", "--squash") and value:
            # `--fixup=amend:<c>` / `reword:<c>` take the target's message; a plain fixup/squash
            # generates "fixup! <subject>" from it, which carries no trailer.
            kind, sep, target = value.partition(":")
            if sep and kind in ("amend", "reword") and read:
                reused = message_of(directory, target)
                if reused is None:
                    unreadable = True
                else:
                    parts.extend(reused)
        index += 1
    if read and template and not supplied:
        unreadable = True
    amended = any(canonical(a.partition("=")[0]) == "--amend" for a in args[: args.index("--") if "--" in args else len(args)])
    if read and amended and not supplied:
        # `--amend` without a new message keeps HEAD's; an explicit -m/-F/-C/--fixup replaces it.
        kept = message_of(directory, "HEAD")
        if kept is None:
            unreadable = True
        else:
            parts.extend(kept)
    return "\n".join(parts), stdin_used or unreadable, dry_run


def check_push_authors(refspecs, directory, tags=False):
    """Read the authors of the commits this push sends that no remote has yet."""
    sources = [refspec.lstrip("+").partition(":")[0] for refspec in refspecs] or ["HEAD"]
    # `git push origin tag v1` names refs/tags/v1; the word `tag` is not a revision.
    sources = [source for source in sources if source and source != "tag"]
    if not sources and not tags:
        return None
    if any(source.startswith("-") for source in sources):
        return "a push naming an option-like revision"
    # `--tags` sends every local tag too, and the commits only a tag reaches: an option for log,
    # so it goes before `--end-of-options`; the sources after it are only ever revisions.
    tag_option = ["--tags"] if tags else []
    # One read for authors and messages, so the hook stays well inside its timeout. A failed read is
    # None: git reports its own error, and a repo with nothing to log is not a blocked push.
    # `--not --remotes --not` excludes what any remote has; `--end-of-options` keeps a source a revision.
    text = git_lines(directory, ["log", "--format=%x1e%ae%x1f%B", "--not", "--remotes", "--not"] + tag_option + ["--end-of-options"] + sources + ["--"], raw=True)
    if text is TIMEOUT:
        return "a push whose history could not be read in time for the author and trailer checks"
    if not text:
        return None
    records = [r for r in text.split("\x1e") if r.strip()]
    authors = {r.split("\x1f", 1)[0].strip() for r in records}
    others = sorted(authors - {AUTHOR_EMAIL})
    if others:
        return "a push of commits authored as {}".format(", ".join(others))
    if TRAILER.search("\n".join(r.split("\x1f", 1)[1] if "\x1f" in r else "" for r in records)):
        return "a push of commits carrying an attribution trailer"
    return None


def destination(refspec, directory):
    source, _, target = refspec.lstrip("+").partition(":")
    branch = target or source
    if branch in ("HEAD", "@"):
        return current_branch(directory)
    return re.sub(r"^(refs/)?heads/", "", branch)


def check_push(args, directory):
    positional, options, skip = [], [], False
    for index, arg in enumerate(args):
        if skip:
            skip = False
        elif arg == "--":
            positional.extend(args[index + 1 :])
            break
        elif arg.startswith("-"):
            options.append(arg.split("=")[0])
            skip = arg in PUSH_VALUE_OPTS
        else:
            positional.append(arg)

    # A dry run writes nothing, and the pickup guard's hook probe is one.
    if "--dry-run" in options or "-n" in options:
        return None
    short_force = any(re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", opt) for opt in options)
    refspecs = positional[1:]
    if short_force or FORCE_FLAGS & set(options) or any(r.startswith("+") for r in refspecs):
        return "a force-push"
    if "--all" in options or "--branches" in options:
        return "a push of every branch, release branches included"
    targets = [destination(r, directory) for r in refspecs]
    if not refspecs:
        targets = [current_branch(directory)]
    for target in targets:
        if target in RELEASE_BRANCHES or "*" in target:
            return "a push to a release branch ({})".format(target)
    if "--delete" in options or "-d" in options:
        return None
    return check_push_authors(refspecs, directory, "--tags" in options)


def check_git(tokens, directory, env, stdin_bodies=None, written=()):
    index, configs = 1, []
    while index < len(tokens) and tokens[index].startswith("-"):
        if tokens[index] == "-C" and index + 1 < len(tokens):
            directory = os.path.join(directory, os.path.expanduser(tokens[index + 1]))
        elif tokens[index] == "-c" and index + 1 < len(tokens):
            configs.append(tokens[index + 1])
        index += 2 if tokens[index] in GIT_VALUE_OPTS else 1
    if index < len(tokens) and tokens[index] == "push":
        return check_push(tokens[index + 1 :], directory)
    if index < len(tokens) and tokens[index] == "commit":
        return check_commit(tokens[index + 1 :], directory, configs, env, stdin_bodies, written)
    return None


def gh_read(args, directory, env):
    """Run a read-only gh command; its output, or None when it fails or says nothing."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=6,
            cwd=directory,
            env=dict(os.environ, **env),
        )
    except (OSError, subprocess.SubprocessError):
        return None
    output = result.stdout.strip()
    return output if result.returncode == 0 and output else None


def check_merge_base(base):
    """A merge into a protected base, or one whose base is unknown, stays with Brandon."""
    if base is None:
        return "a PR merge whose base branch could not be read"
    if base in PROTECTED_BASES:
        return "a PR merge into {}".format(base)
    return None


def gh_options(tokens):
    """Split gh arguments as gh reads them: `-sb x` clusters, `--opt=x`, and `--`."""
    positional, options, index = [], {}, 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            positional.extend(tokens[index + 1 :])
            break
        if token.startswith("--"):
            name, equals, value = token.partition("=")
            if name in GH_ARG_VALUE_OPTS and not equals:
                index += 1
                value = tokens[index] if index < len(tokens) else ""
            options.setdefault(name, []).append(value)
        elif token.startswith("-") and len(token) > 1:
            for position in range(1, len(token)):
                name = "-" + token[position]
                value = ""
                if name in GH_ARG_VALUE_OPTS:
                    value = token[position + 1 :]
                    if not value:
                        index += 1
                        value = tokens[index] if index < len(tokens) else ""
                options.setdefault(name, []).append(value)
                if name in GH_ARG_VALUE_OPTS:
                    break
        else:
            positional.append(token)
        index += 1
    return positional, options


def check_gh(tokens, directory, env):
    positional, options = gh_options(tokens[1:])
    repos = options.get("-R", []) + options.get("--repo", [])
    repo = ["--repo", repos[-1]] if repos else []
    if positional[:2] == ["pr", "merge"]:
        # The guard's documented live probe: answered here, with no lookup.
        if "--help" in options or "-h" in options:
            return "a PR merge"
        # An auto-merge lands later, after a stacked PR may have been retargeted to develop.
        if "--auto" in options:
            return "an auto-merge, whose base can change before it lands"
        selector = positional[2:3]
        base = gh_read(
            ["pr", "view"] + selector + repo + ["--json", "baseRefName", "--jq", ".baseRefName"],
            directory,
            env,
        )
        return check_merge_base(base)
    if positional[:1] == ["api"]:
        call = " ".join(tokens[1:])
        if GH_MERGE_MUTATIONS.search(call):
            return "a PR merge"
        if re.search(r"repos/[^/\s]+/[^/\s]+/merges\b", call):
            return "a branch merge through the API"
        methods = [m.upper() for m in options.get("-X", []) + options.get("--method", [])]
        if "PUT" not in methods:
            return None
        endpoint = positional[1] if len(positional) > 1 else ""
        merge_url = re.fullmatch(r"(.*\brepos/[^/]+/[^/]+/pulls/[^/]+)/merge/?", endpoint)
        if merge_url:
            hosts = options.get("--hostname", [])
            host = ["--hostname", hosts[-1]] if hosts else []
            base = gh_read(
                ["api", merge_url.group(1)] + host + ["--jq", ".base.ref"], directory, env
            )
            return check_merge_base(base)
        if re.search(r"/pulls/[^/\s]+/merge\b", call):
            return "a PR merge whose base branch could not be read"
    return None


def commit_reader(reader):
    """The `git commit` tokens of the simple command that ends `reader`, or None.

    Separators inside quotes (an author named "A | B") do not split the command; a dry run
    commits nothing and so reads nothing worth checking.
    """
    simple = None
    for candidate in (reader, reader + '"', reader + "'"):  # a reader cut inside `-m "$(` is unfinished
        try:
            parsed = list(segments(candidate + " <<EOF\nEOF"))  # terminate a dangling redirection
        except Exception:  # pragma: no cover - the lexer raises inside segments
            parsed = []
        git_segments = [t for t in parsed if t and os.path.basename(strip_prefix(strip_redirects(t))[0] if strip_prefix(strip_redirects(t)) else "") == "git"]
        if git_segments:
            simple = git_segments[-1]
            break
    if not simple:
        return None
    tokens = strip_prefix(strip_redirects(simple))
    if not tokens or os.path.basename(tokens[0]) != "git" or "commit" not in tokens:
        return None
    if commit_message(tokens[tokens.index("commit") + 1 :], "", read=False)[2]:  # a real --dry-run option
        return None
    return tokens


def reads_commit_stdin(reader):
    """True when the command before a `<<`/`<<<` is `git commit` reading its message from stdin."""
    tokens = commit_reader(reader)
    if not tokens:
        return False
    return commit_message(tokens[tokens.index("commit") + 1 :], "", read=False)[1]  # stdin_used


SUBSTITUTION = re.compile(r'^(?P<pre>.*?)(?P<opt>-m|--message)(?:=| +)"\$\(cat <<(?P<q>[\'"])(?P<tag>[^\'"]*)(?P=q)[ \t]*$')
SUBSTITUTION_CLOSE = re.compile(r'^\)"(?P<rest>.*)$')


def heredoc_commit_messages(command):
    """Message text reaching `git commit` through the shell, in the one readable shape.

    Returns (stdin_bodies, substituted). Every stdin-fed message (`-F -` with a heredoc, a
    here-string, a pipe, any redirection) is recorded as None: the guard does not model the shell's
    stdin, so check_commit denies it as uncheckable and asks for -m or -F <file>. A substituted
    message is read only in the exact literal form

        git commit … -m "$(cat <<'TAG'
        …body…
        TAG
        )" [more options]

    with a quoted delimiter and an operand-free `cat`; any other `$(` message is None too."""
    bodies, substituted = [], []
    found = heredocs(command)
    by_line, body_lines = {}, set()
    for entry in found:
        by_line.setdefault(entry[5], []).append(entry)
        start, end = entry[4]
        first = command.count("\n", 0, start)
        body_lines.update(range(first, first + command.count("\n", start, end) + 1))
    lines = command.split("\n")
    quote = None
    for line_no, line in enumerate(lines):
        if line_no in body_lines:
            continue  # heredoc body and delimiter lines are data
        ops, state = redirections(line, quote)
        quote = state["quote"]
        if not ops:
            continue
        first = ops[0]
        reader = line[: first[4] if first[0] == "heredoc" else first[3]]
        if reads_commit_stdin(reader):
            bodies.append(None)  # stdin is never read here, whatever feeds it
            continue
        if "$(" not in line or not commit_reader(line.rsplit("$(", 1)[0]):
            continue  # no substituted commit on this line
        match = SUBSTITUTION.match(line)
        entries = by_line.get(line_no, [])
        if match and len(ops) == 1 and ops[0][0] == "heredoc" and ops[0][3] and entries and not state["complex"]:
            body = entries[0][1]
            after = line_no + command.count("\n", entries[0][4][0], entries[0][4][1]) + 2  # past body and delimiter
            close = SUBSTITUTION_CLOSE.match(lines[after]) if after < len(lines) else None
            if close:
                argv_line = match.group("pre") + match.group("opt") + ' "X"' + close.group("rest")
                # The commit is the first `git commit` on that line (`./check.sh &&` may precede it);
                # `&& git push` after it is the main loop's to check, and must not hide the body here.
                first = next(
                    (t for t in (strip_prefix(strip_redirects(seg)) for seg in segments(argv_line) if seg)
                     if t and os.path.basename(t[0]) == "git" and "commit" in t),
                    None,
                )
                if first:
                    if commit_message(first[first.index("commit") + 1 :], "", read=False)[2]:
                        continue  # a dry run commits nothing
                    substituted.append(body)
                    continue
        substituted.append(None)  # some other substituted message: not readable here
    return bodies, substituted


CONTINUATION = re.compile(r"(\\+)\n")


def join_continuations(command):
    """Join `\`-newline as bash does before it reads anything else: only an unescaped backslash
    continues the line, so `a\\` followed by a newline ends a command, as it does in the shell."""
    return CONTINUATION.sub(lambda m: m.group(1)[:-1] if len(m.group(1)) % 2 else m.group(0), command)


def check_command(command, directory, inherited=None, written=()):
    """The first rule the command breaks, or None. `inherited` is a calling shell's environment.

    Bash joins `\`-newline before reading a command, except inside single quotes and a heredoc
    whose delimiter is quoted, where the pair stays text: `Signed\` + newline + `Co-Authored-By:`
    is a trailer at a line start there. The joined text is read first; when the command holds a
    continuation at all, the raw text is read too, and either reading can deny."""
    reason = check_text(join_continuations(command), directory, inherited, written)
    if reason is None and CONTINUATION.search(command):
        reason = check_text(command, directory, inherited, written)
    return reason


def check_text(command, directory, inherited=None, written=()):
    stdin_bodies, substituted = heredoc_commit_messages(command)
    if TRAILER.search("\n".join(b for b in stdin_bodies + substituted if b)):
        return "a commit carrying an attribution trailer"
    if any(b is None for b in substituted):
        return "a commit whose message cannot be checked for attribution trailers"
    exported = dict(inherited or {})
    earlier = list(written)  # the words of the simple commands already run: a file they name may be rewritten
    for raw_tokens in segments(command):
        written = tuple(earlier)
        earlier.extend(raw_tokens)
        tokens = strip_redirects(raw_tokens)
        command_tokens = strip_prefix(tokens)
        prefix = tokens[: len(tokens) - len(command_tokens)]
        env = dict(exported)
        env.update(token.split("=", 1) for token in prefix if ASSIGNMENT.match(token))
        tokens = command_tokens
        if not tokens:
            continue
        head = os.path.basename(tokens[0])
        reason = None
        if head == "export":
            exported.update(token.split("=", 1) for token in tokens[1:] if ASSIGNMENT.match(token))
        elif head == "cd" and len(tokens) == 2:
            directory = os.path.join(directory, os.path.expanduser(tokens[1]))
        elif head == "eval":
            reason = check_command(" ".join(tokens[1:]), directory, env, written)
        elif head in SHELLS:
            for index, token in enumerate(tokens[:-1]):
                if re.fullmatch(r"-[a-z]*c", token):
                    reason = check_command(tokens[index + 1], directory, env, written)
                    break
        elif head == "git":
            reason = check_git(tokens, directory, env, stdin_bodies, written)
        elif head == "gh":
            reason = check_gh(tokens, directory, env)
        if reason:
            return reason
    return None


def main():
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    reason = check_command(command, payload.get("cwd") or os.getcwd())
    if reason:
        if "cannot be checked" in reason:
            advice = (
                "RULE ZERO: the message must be readable here. Pass literal text with -m or "
                "-F <file>, or -m \"$(cat <<'EOF' … EOF\n)\" exactly; no pipe, -F -, $var or other "
                "substitution, so the guard can check it for attribution lines. An editor or "
                "template route (-e, -t, GIT_EDITOR/VISUAL/EDITOR, core.editor) set in the same "
                "command is denied too: drop it from the command."
            )
        elif "could not be read in time" in reason:
            advice = "RULE ZERO: the history read timed out. Retry once; if it keeps timing out, hand the push back to Brandon."
        elif "attribution trailer" in reason:
            advice = (
                "RULE ZERO: no Co-Authored-By, session or generated-with line on a commit. "
                "Remove the trailer (git commit --amend for a commit already made) and retry."
            )
        elif reason.startswith(("a commit", "a push of commits")):
            advice = (
                "RULE ZERO: every agent commit carries the author email {}. Fix the "
                "identity (git config user.email, or git commit --amend --reset-author "
                "for a commit already made) and retry; an outside contributor's commits "
                "go back to Brandon."
            ).format(AUTHOR_EMAIL)
        else:
            advice = (
                "The working agreements keep that with Brandon; "
                "hand it back rather than routing around this."
            )
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": (
                            "Blocked by ~/.claude/hooks/guard_git.py: this is {}. {}"
                        ).format(reason, advice),
                    }
                }
            )
        )


if __name__ == "__main__":
    main()
