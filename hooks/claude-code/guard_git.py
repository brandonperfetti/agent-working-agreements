#!/usr/bin/python3
"""PreToolUse guard for the Bash tool: the git rules no agent may break.

Denies force-pushes, pushes to a release branch and PR merges into develop,
main or master (or whose base it cannot read), per the Sans Faux profile's Git
ritual and merge boundary; commits whose author is not Brandon's email or that
skip the commit-msg hook; and pushes whose unpushed commits carry another
author or an attribution line (RULE ZERO). The message of a commit being made
is the commit-msg hook's to read (hooks/git), where git holds it final; this
guard reads only what git has already written. Merges between feature, wave,
lane and hotfix branches pass. It parses the command rather than grepping it,
so a commit message that mentions `git push --force` passes. It stops honest
mistakes, not a determined bypass: git aliases, refspecs in shell variables and
commands inside a quoted "$(...)" are not resolved.
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
TRAILER = re.compile(r"^[#>\s]*(co-authored-by|[a-z-]*-session)\s*:|generated with", re.IGNORECASE | re.MULTILINE)
ASSIGNMENT = re.compile(r"[A-Za-z_]\w*=")
WRAPPERS = {"command", "env", "exec", "nohup", "sudo", "time", "xargs"}
SHELLS = {"bash", "sh", "zsh"}
SEPARATORS = ";&|()\n"
GIT_VALUE_OPTS = {"-C", "-c", "--git-dir", "--namespace", "--work-tree"}
COMMIT_VALUE_OPTS = {"-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c", "--reedit-message",
                     "--fixup", "--squash", "--author", "--date", "--cleanup", "--trailer", "-t", "--template"}
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
    r"^(?P<head>[^\n]*<<-?[ \t]*['\"]?(?P<tag>\w+)['\"]?[^\n]*)\n.*?^\s*(?P=tag)\s*$",
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


def fed_by_xargs(prefix, tokens):
    """True when xargs, in command position, hands git or gh arguments the guard never sees. Its
    options are not modelled: any git or gh word after it counts (`xargs grep git` is denied too)."""
    names = [os.path.basename(t) for t in prefix]
    if "xargs" not in names:
        return False
    after = (prefix + tokens)[names.index("xargs") + 1 :]
    return any(os.path.basename(t) in ("git", "gh") for t in after)


def strip_prefix(tokens):
    """Drop env assignments and wrappers such as `env` or `sudo`."""
    while tokens:
        if ASSIGNMENT.match(tokens[0]) or tokens[0] in ("{", "}", "!", "if", "elif", "while", "until", "then", "do", "else"):
            tokens = tokens[1:]  # `{ git push -f; }`, `if git push -f; then`: list words are not the command
        elif os.path.basename(tokens[0]) in WRAPPERS:
            tokens = tokens[1:]
            while tokens and tokens[0].startswith("-"):
                tokens = tokens[1:]
        else:
            break
    return tokens


def current_branch(directory, selectors=(), env=None):
    """The checked-out branch of the repository the command selects (`--git-dir`, GIT_DIR, cwd)."""
    try:
        result = subprocess.run(
            ["git", "-C", directory] + list(selectors) + ["symbolic-ref", "--short", "-q", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
            env=dict(os.environ, **(env or {})),
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip()


def git_lines(directory, args, env=None, raw=False):
    """Run a read-only git command; None when it fails, so git reports its own error. `raw`
    returns the text itself: `splitlines` reads the record separator `\x1e` as a line break."""
    try:
        result = subprocess.run(
            ["git", "-C", directory] + args,
            capture_output=True,
            text=True,
            timeout=5,
            env=env,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    return result.stdout if raw else result.stdout.splitlines()


def email_of(ident):
    match = re.search(r"<([^>]*)>", ident)
    return match.group(1) if match else ident.strip()


def check_commit(args, directory, configs, env, selectors=()):
    """Resolve the author the commit will carry, as git would, and keep the commit-msg hook in play."""
    flags, values, skip = [], {}, None
    for arg in args[: args.index("--")] if "--" in args else args:
        if skip:
            values[skip] = arg  # the value of -m, -F, --author…: `git commit -m --no-verify` is a message
            skip = None
        elif arg.startswith("-"):
            name, has_value, value = arg.partition("=")
            flags.append(name if has_value else arg)
            if has_value:
                values[name] = value
            elif arg in COMMIT_VALUE_OPTS:
                skip = arg  # the next argument is this option's value
            elif not arg.startswith("--"):
                # In a cluster the first value-taking letter ends it; the value is the next argument
                # only when nothing follows that letter (`-am msg`), else attached (`-mtrim`). `-u`
                # and `-S` take an optional value that must be attached, so they never consume one.
                letter = re.search(r"[mFCctSu]", arg[1:])
                skip = arg if bool(letter) and letter.group() in "mFCct" and letter.end() == len(arg) - 1 else None
    if "--dry-run" in flags:
        return None  # a flag, not `-m --dry-run`
    # `--no-verify` (any unique prefix from `--no-v`), `-n` and a cluster holding `n` before its
    # first value-taking letter skip the hook (`-anm msg` does; `-mn` is the message "n").
    def skips(flag):
        if flag.startswith("--"):
            return "--no-verify".startswith(flag) and len(flag) >= 6
        cluster = re.match(r"-([a-zA-Z]*)", flag).group(1)
        cluster = re.split(r"[mFCctSu]", cluster, maxsplit=1)[0]  # `-uno`, `-Skey`: attached values
        return "n" in cluster

    if any(skips(a) for a in flags):
        return "a commit that skips the commit-msg hook (--no-verify)"
    author = values.get("--author")
    if author is None:
        options = [part for config in configs for part in ("-c", config)]
        lines = git_lines(directory, list(selectors) + options + ["var", "GIT_AUTHOR_IDENT"], dict(os.environ, **env))
        if not lines:
            return None
        author = lines[0]
    email = email_of(author)
    if email != AUTHOR_EMAIL:
        return "a commit authored as {}".format(email or "an empty email")
    return None


def check_push_authors(refspecs, directory, tags=False, selectors=(), env=None):
    """Read the authors and messages of the commits this push sends that no remote has yet.

    `selectors` are the command's `--git-dir`/`--work-tree` options and `env` its GIT_DIR and
    GIT_WORK_TREE, so the scan reads the repository the push would use."""
    sources = [refspec.lstrip("+").partition(":")[0] for refspec in refspecs] or ["HEAD"]
    # `git push origin tag v1` names refs/tags/v1; the word `tag` is not a revision.
    sources = [source for source in sources if source and source != "tag"]
    if any(source.startswith("-") for source in sources):
        return "a push naming an option-like revision"
    if not sources and not tags:
        return None
    # `--tags` is an option for log, so it goes before `--end-of-options`; the sources after it
    # are only ever revisions. One read of author and message per commit, record-separated:
    # `splitlines` would eat `\x1e`.
    tag_option = ["--tags"] if tags else []
    text = git_lines(directory, list(selectors) + ["log", "--format=%x1e%ae%x1f%B", "--not", "--remotes", "--not"] + tag_option + ["--end-of-options"] + sources + ["--"], raw=True, env=dict(os.environ, **(env or {})))
    if text is None:  # the scan failed or timed out: nothing was checked
        return "a push whose commits could not be read for the author and trailer checks"
    records = [r for r in text.split("\x1e") if r.strip()]
    others = sorted({r.split("\x1f", 1)[0].strip() for r in records} - {AUTHOR_EMAIL})
    if others:
        return "a push of commits authored as {}".format(", ".join(others))
    if TRAILER.search("\n".join(r.split("\x1f", 1)[1] if "\x1f" in r else "" for r in records)):
        return "a push of commits carrying an attribution trailer"
    return None


def destination(refspec, directory, selectors=(), env=None):
    source, _, target = refspec.lstrip("+").partition(":")
    branch = target or source
    if branch in ("HEAD", "@"):
        return current_branch(directory, selectors, env)
    return re.sub(r"^(refs/)?heads/", "", branch)


def check_push(args, directory, selectors=(), env=None):
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
    if "--all" in options or "--branches" in options or ":" in refspecs:  # `:` pushes every matching branch
        return "a push of every branch, release branches included"
    targets = [destination(r, directory, selectors, env) for r in refspecs]
    if not refspecs:
        targets = [current_branch(directory, selectors, env)]
    for target in targets:
        if target in RELEASE_BRANCHES or "*" in target:
            return "a push to a release branch ({})".format(target)
    if "--delete" in options or "-d" in options:
        return None
    return check_push_authors(refspecs, directory, "--tags" in options, selectors, env)


def check_git(tokens, directory, env):
    index, configs, selectors = 1, [], []
    while index < len(tokens) and tokens[index].startswith("-"):
        if tokens[index] == "-C" and index + 1 < len(tokens):
            directory = os.path.join(directory, os.path.expanduser(tokens[index + 1]))
        elif tokens[index] == "-c" and index + 1 < len(tokens):
            configs.append(tokens[index + 1])
        elif tokens[index].partition("=")[0] in ("--git-dir", "--work-tree"):
            name, has_value, value = tokens[index].partition("=")
            selectors += [name, value] if has_value else tokens[index : index + 2]
        index += 2 if tokens[index] in GIT_VALUE_OPTS else 1
    if index < len(tokens) and tokens[index] == "push":
        return check_push(tokens[index + 1 :], directory, selectors, {k: v for k, v in env.items() if k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")})
    if index < len(tokens) and tokens[index] == "commit":
        return check_commit(tokens[index + 1 :], directory, configs, env, selectors)
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


def check_command(command, directory, inherited=None):
    """The first rule the command breaks, or None. `inherited` is a calling shell's environment."""
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
        if fed_by_xargs(prefix, command_tokens):
            return "a git or gh command whose arguments arrive through xargs and are not visible here"
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
        elif "commit-msg hook" in reason:
            advice = "RULE ZERO is checked by the commit-msg hook; commit without --no-verify."
        elif "option-like revision" in reason:
            advice = "Name the branch to push plainly; a revision that starts with a dash is not read."
        elif "could not be read for the author" in reason:
            advice = "RULE ZERO: the history read failed or timed out. Check the revision and retry once; if it keeps failing, hand the push back to Brandon."
        elif "through xargs" in reason:
            advice = "Pass the git or gh command and its arguments directly, without xargs."
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
