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
TRAILER = re.compile(r"^(co-authored-by|[a-z-]*-session):|generated with", re.IGNORECASE | re.MULTILINE)
COMMIT_VALUE_OPTS = {
    "-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c", "--reedit-message",
    "--fixup", "--squash", "--author", "--date", "--cleanup", "--trailer", "-t", "--template",
}
ASSIGNMENT = re.compile(r"[A-Za-z_]\w*=")
WRAPPERS = {"command", "env", "exec", "nohup", "sudo", "time", "xargs"}
SHELLS = {"bash", "sh", "zsh"}
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
HEREDOC = re.compile(
    # The delimiter line is exact for `<<`; `<<-` strips leading tabs only, as the shell does.
    r"^(?P<head>[^\n]*<<(?P<dash>-?)[ \t]*['\"]?(?P<tag>\w+)['\"]?[^\n]*)\n.*?^(?(dash)\t*)(?P=tag)$",
    re.DOTALL | re.MULTILINE,
)


def drop_heredoc(match):
    """Blank a heredoc body, unless a shell is reading it as commands."""
    head = match.group("head")
    # A shell as a command word (`bash`, `/bin/zsh -s`), not a script name such as `check.sh`.
    if re.search(r"(^|[\s;&|(/\"'])(ba|z)?sh(?=[\s<\"']|$)", head):
        return match.group(0)
    return head


def segments(command):
    """Split a command line into one token list per simple command."""
    command = HEREDOC.sub(drop_heredoc, command)
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


def git_lines(directory, args, env=None):
    """Run a read-only git command; None when it fails, so git reports its own error."""
    try:
        result = subprocess.run(
            ["git", "-C", directory] + args,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=5,
            env=env,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    return result.stdout.splitlines()


def email_of(ident):
    match = re.search(r"<([^>]*)>", ident)
    return match.group(1) if match else ident.strip()


def check_commit(args, directory, configs, env):
    """Resolve the author the commit will carry, as git would."""
    if "--dry-run" in args:
        return None
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
        if not lines:
            return None
        author = lines[0]
    email = email_of(author)
    if email != AUTHOR_EMAIL:
        return "a commit authored as {}".format(email or "an empty email")
    if TRAILER.search(commit_message(args, directory)):
        return "a commit carrying an attribution trailer"
    return None


def commit_message(args, directory):
    """The message text the command supplies: -m parts, -F files and --trailer lines.

    `-F -` is read by heredoc_commit_messages from the raw command; a piped stdin is not readable
    here, and the push check reads the committed message instead.
    """
    parts, supplied = [], False
    index = 0
    while index < len(args) and args[index] != "--":
        arg = args[index]
        name, has_value, value = arg.partition("=")
        # A short-option cluster ends at its first value-taking letter: `-am msg`, `-aF file`,
        # `-mmsg`, `-F-`; `-tform` is -t with the value "form", and takes no message.
        cluster = re.match(r"-([a-zA-Z]*?)([mFtCc])(.*)", arg) if not arg.startswith("--") else None
        if cluster:
            letter, value = cluster.group(2), cluster.group(3)
            name = "-" + letter
            has_value = bool(value)
        if not has_value and (arg in COMMIT_VALUE_OPTS or cluster) and index + 1 < len(args):
            value = args[index + 1]
            index += 1
        if name in ("-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c", "--reedit-message"):
            supplied = True
        if name in ("-m", "--message", "--trailer"):
            parts.append(value)
        elif name in ("-F", "--file") and value and value != "-":
            try:
                path = os.path.join(directory, os.path.expanduser(value))
                with open(path, errors="replace") as handle:
                    parts.append(handle.read())
            except OSError:
                pass
        elif name in ("-C", "--reuse-message", "-c", "--reedit-message") and value:
            parts.extend(git_lines(directory, ["log", "-1", "--format=%B", value]) or [])
        index += 1
    if "--amend" in args[: args.index("--") if "--" in args else len(args)] and not supplied:
        # `--amend` without a new message keeps HEAD's; an explicit -m/-F/-C replaces it.
        parts.extend(git_lines(directory, ["log", "-1", "--format=%B", "HEAD"]) or [])
    return "\n".join(parts)


def check_push_authors(refspecs, directory, tags=False):
    """Read the authors of the commits this push sends that no remote has yet."""
    sources = [refspec.lstrip("+").partition(":")[0] for refspec in refspecs] or ["HEAD"]
    # `git push origin tag v1` names refs/tags/v1; the word `tag` is not a revision.
    sources = [source for source in sources if source and source != "tag"]
    # `--tags` sends every local tag too, and the commits only a tag reaches.
    sources += ["--tags"] if tags else []
    if not sources:
        return None
    lines = git_lines(directory, ["log", "--format=%ae"] + sources + ["--not", "--remotes", "--"])
    others = sorted(set(lines or []) - {AUTHOR_EMAIL})
    if others:
        return "a push of commits authored as {}".format(", ".join(others))
    # Like the author read above, a failed read is None: git reports its own error, and a repo
    # with nothing to log (no commits, no remote yet) is not a blocked push.
    bodies = git_lines(directory, ["log", "--format=%B"] + sources + ["--not", "--remotes", "--"])
    if bodies and TRAILER.search("\n".join(bodies)):
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


def check_git(tokens, directory, env):
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
        return check_commit(tokens[index + 1 :], directory, configs, env)
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


def heredoc_commit_messages(command):
    """Bodies of heredocs that feed `git commit -F -` (or `--file -`/`--file=-`) on stdin.

    A pipe into `-F -` cannot be read here; the push check reads the committed message later.
    """
    bodies = []
    for match in HEREDOC.finditer(command):
        head = match.group("head")
        reader = head.split("<<", 1)[0]  # the command that consumes the body, not a trailing comment
        if re.search(r"\bgit\b.*\bcommit\b", reader) and re.search(r"(-F|--file)[ =]?-(\s|$)", reader + " "):
            body = match.group(0)[len(head) :]
            if match.group("dash"):
                body = re.sub(r"^\t+", "", body, flags=re.MULTILINE)  # `<<-` strips leading tabs
            bodies.append(body)
    return "\n".join(bodies)


def check_command(command, directory, inherited=None):
    """The first rule the command breaks, or None. `inherited` is a calling shell's environment."""
    if TRAILER.search(heredoc_commit_messages(command)):
        return "a commit carrying an attribution trailer"
    exported = dict(inherited or {})
    for tokens in segments(command):
        tokens = strip_redirects(tokens)
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
            reason = check_command(" ".join(tokens[1:]), directory, env)
        elif head in SHELLS:
            for index, token in enumerate(tokens[:-1]):
                if re.fullmatch(r"-[a-z]*c", token):
                    reason = check_command(tokens[index + 1], directory, env)
                    break
        elif head == "git":
            reason = check_git(tokens, directory, env)
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
        if "attribution trailer" in reason:
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
