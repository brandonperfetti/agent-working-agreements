#!/usr/bin/python3
"""PreToolUse guard for the Bash tool: the git rules no agent may break.

Denies force-pushes, pushes to a release branch and PR merges into develop,
main or master (or whose base it cannot read), per the Sans Faux profile's Git
ritual and merge boundary; commits and merges that skip the commit-msg hook or
carry a configuration override; and, best effort, pushes whose commits new to
the destination remote's tracking refs carry another author or an attribution
line (RULE ZERO; stale tracking refs are the documented limit, and the read
before a delivery is presented is the complete check). The author and message
of a commit being made are the commit-msg hook's to read (hooks/git), where git
holds them final; this guard reads only what git has already written. Merges
between feature, wave, lane and hotfix branches pass. It parses the command rather than grepping it,
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
TRAILER = re.compile(r"^[#> \t]*(co-authored-by|[a-z-]*-session)[ \t]*:|generated with|posted by an agent", re.IGNORECASE | re.MULTILINE)
ASSIGNMENT = re.compile(r"[A-Za-z_]\w*=")
WRAPPERS = {"command", "env", "exec", "nohup", "sudo", "time", "xargs"}
SHELLS = {"bash", "sh", "zsh"}
SEPARATORS = ";&|()\n"
GIT_VALUE_OPTS = {"-C", "-c", "--config-env", "--git-dir", "--namespace", "--work-tree"}
COMMIT_VALUE_OPTS = {"-m", "--message", "-F", "--file", "-C", "--reuse-message", "-c", "--reedit-message",
                     "--fixup", "--squash", "--author", "--date", "--cleanup", "--trailer", "-t", "--template",
                     "--pathspec-from-file"}
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
    """Drop redirection operators and their targets from one simple command's tokens."""
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
    return any(os.path.basename(t) in {"git", "gh"} | SHELLS for t in after)  # `xargs sh -c 'git {}'` too


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


REPOSITORY_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES")


def environment(env=None):
    """The guard's own environment for a git read: whatever selected a repository for the guard's
    process is dropped, and only the command's selection (`env`) applies."""
    base = {k: v for k, v in os.environ.items() if k not in REPOSITORY_VARS}
    base.update(env or {})
    return base


def current_branch(directory, selectors=(), env=None):
    """The checked-out branch of the repository the command selects (`--git-dir`, GIT_DIR, cwd)."""
    try:
        result = subprocess.run(
            ["git", "-C", directory] + list(selectors) + ["symbolic-ref", "--short", "-q", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
            env=environment(env),
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
            errors="replace",  # a message with bytes outside the locale is still read, not a traceback
            timeout=5,
            env=env,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    return result.stdout if raw else result.stdout.splitlines()


HOOK_KEYS = ("core.hookspath", "core.editor", "sequence.editor", "commit.template", "commit.cleanup", "core.commentchar", "core.commentstring", "trailer.", "include", "alias.")
MERGE_VALUE_OPTS = {"-m", "--message", "-F", "--file", "-s", "--strategy", "-X", "--strategy-option", "--cleanup", "--into-name"}
# Per command: the short letters that take a value (next argument when last in the cluster, else
# attached), those whose optional value must be attached, and whether a short `-n` means --no-verify.
COMMIT_SHORTS = ("mFCct", "Su", True)
MERGE_SHORTS = ("mFsX", "S", False)  # `git merge -n` is --no-stat


def check_commit(args, value_opts=None, shorts=COMMIT_SHORTS):
    """Keep the commit-msg hook in play: it, not this guard, reads the message and the author.
    `git merge` makes a commit too and takes the same `--no-verify`."""
    value_opts = COMMIT_VALUE_OPTS if value_opts is None else value_opts
    value_letters, attached_letters, short_n = shorts
    flags, skip = [], None
    for arg in args:
        if skip:
            skip = None  # the value of -m, -F, --author…: `git commit -m --no-verify` is a message, `-m --` too
        elif arg == "--":
            break
        elif arg.startswith("-"):
            name, has_value, _value = arg.partition("=")
            flags.append(name if has_value else arg)
            if has_value:
                pass  # `--author=X`: the value is attached
            elif arg in value_opts:
                skip = arg  # the next argument is this option's value
            elif not arg.startswith("--"):
                # In a cluster the first value-taking letter ends it; the value is the next argument
                # only when nothing follows that letter (`-am msg`), else attached (`-mtrim`). `-u`
                # and `-S` take an optional value that must be attached, so they never consume one.
                letter = re.search("[{}{}]".format(value_letters, attached_letters), arg[1:])
                skip = arg if bool(letter) and letter.group() in value_letters and letter.end() == len(arg) - 1 else None
    if "--dry-run" in flags:
        return None  # a flag, not `-m --dry-run`
    # `--no-verify` (any unique prefix from `--no-v`), `-n` and a cluster holding `n` before its
    # first value-taking letter skip the hook (`-anm msg` does; `-mn` is the message "n").
    def skips(flag):
        """True when this flag turns the commit-msg hook off."""
        if flag.startswith("--"):
            return "--no-verify".startswith(flag) and len(flag) >= 6
        if not short_n:
            return False
        cluster = re.match(r"-([a-zA-Z]*)", flag).group(1)
        cluster = re.split("[{}{}]".format(value_letters, attached_letters), cluster, maxsplit=1)[0]  # `-uno`, `-Skey`: attached values
        return "n" in cluster

    if any(skips(a) for a in flags):
        return "a commit that skips the commit-msg hook (--no-verify)"
    return None


def check_push_authors(refspecs, directory, tags=False, selectors=(), env=None, remote="origin"):
    """Read, best effort, the authors and messages of the commits this push sends: those reachable
    from the sources that `remote`'s local tracking refs do not already hold. Stale tracking refs
    can hide a commit the remote lacks; the read before a delivery is presented is the complete check.

    `selectors` are the command's `--git-dir`/`--work-tree` options and `env` its GIT_DIR and
    GIT_WORK_TREE, so the scan reads the repository the push would use. Only the destination
    remote's tracking refs are excluded: what another remote holds is still new to this one."""
    # `git push origin tag v1` names refs/tags/v1: the standalone word `tag` is a marker and the
    # name after it the revision to scan; `tag:topic`, or `tag` alone at the end, is a branch.
    named, index = [], 0
    while index < len(refspecs):
        if refspecs[index] == "tag" and index + 1 < len(refspecs):
            named.append("refs/tags/" + refspecs[index + 1])  # marker and name together: one tag
            index += 2
            continue
        named.append(refspecs[index])
        index += 1
    sources = [refspec.lstrip("+").partition(":")[0] for refspec in named]
    if not sources and not tags:
        sources = ["HEAD"]  # a bare push sends the current branch; `--tags` alone sends only tags
    sources = [source for source in sources if source]
    if any(source.startswith("-") for source in sources):
        return "a push naming an option-like revision"
    if not sources and not tags:
        return None
    # `--tags` is an option for log, so it goes before `--end-of-options`; the sources after it
    # are only ever revisions. One read of author and message per commit, record-separated:
    # `splitlines` would eat `\x1e`.
    tag_option = ["--tags"] if tags else []
    text = git_lines(directory, list(selectors) + ["log", "--format=%x1e%ae%x1f%B", "--not", "--remotes=" + remote, "--not"] + tag_option + ["--end-of-options"] + sources + ["--"], raw=True, env=environment(env))
    if text is None:  # the scan failed or timed out: nothing was checked
        return "a push whose commits could not be read for the author and trailer checks"
    records = [r for r in text.split("\x1e") if r.strip()]
    others = sorted({r.split("\x1f", 1)[0].strip() for r in records} - {AUTHOR_EMAIL})
    if others:
        return "a push of commits authored as {}".format(", ".join(others))
    if TRAILER.search("\n".join(r.split("\x1f", 1)[1] if "\x1f" in r else "" for r in records)):
        return "a push of commits carrying an attribution trailer"
    return None


PUSH_LONG_OPTS = (
    "--all", "--atomic", "--branches", "--delete", "--dry-run", "--exec", "--follow-tags", "--force",
    "--force-if-includes", "--force-with-lease", "--ipv4", "--ipv6", "--mirror", "--no-verify", "--porcelain",
    "--progress", "--prune", "--push-option", "--quiet", "--receive-pack", "--recurse-submodules", "--repo",
    "--set-upstream", "--signed", "--tags", "--thin", "--verbose", "--verify",
)


def canonical_push(name):
    """Git accepts a unique prefix of a long option (`--force-w`, `--mirr`, `--del`); resolve it."""
    if not name.startswith("--") or name in PUSH_LONG_OPTS:
        return name
    matches = [opt for opt in PUSH_LONG_OPTS if opt.startswith(name)]
    return matches[0] if len(matches) == 1 else name


def destination(refspec, directory, selectors=(), env=None):
    """The branch a refspec updates on the remote, `HEAD`/`@` resolved to the current branch."""
    source, _, target = refspec.lstrip("+").partition(":")
    branch = target or source
    if branch in ("HEAD", "@"):
        return current_branch(directory, selectors, env)
    return re.sub(r"^(refs/)?heads/", "", branch)


def check_push(args, directory, selectors=(), env=None):
    """The rule a `git push` breaks, or None: force, release branch, redirecting configuration, then the scan."""
    positional, options, skip = [], [], False
    for index, arg in enumerate(args):
        if skip:
            skip = False
        elif arg == "--":
            positional.extend(args[index + 1 :])
            break
        elif arg.startswith("-"):
            name, has_value, _ = arg.partition("=")
            name = canonical_push(name)
            options.append(name)
            # `-o fleet`, and a short cluster whose first `o` is its last letter (`-vo fleet`), take
            # the next operand; `-ofoo` and `-vofoo` carry the value attached.
            letters = arg[1:] if not arg.startswith("--") else ""
            skip = (name in PUSH_VALUE_OPTS and not has_value) or (letters.isalpha() and "o" in letters and letters.index("o") == len(letters) - 1)
        else:
            positional.append(arg)

    # A dry run writes nothing, and the pickup guard's hook probe is one.
    if "--dry-run" in options or "-n" in options:
        return None
    # In a short cluster, `-o` takes the rest as its value (`-ofleet`), so only letters before it count.
    short_force = any(re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", opt.split("o", 1)[0] if opt.startswith("-") and not opt.startswith("--") else opt) for opt in options)
    refspecs = positional[1:]
    if short_force or FORCE_FLAGS & set(options) or any(r.startswith("+") for r in refspecs):
        return "a force-push"
    if "--all" in options or "--branches" in options or ":" in refspecs:  # `:` pushes every matching branch
        return "a push of every branch, release branches included"
    tags_only = ("--tags" in options or "--follow-tags" in options) and not refspecs and "--tags" in options
    environment_ = environment(env)
    # The destination remote, by name: a URL or `--repo` has no tracking refs to scan against.
    remote = positional[0] if positional else None
    if "--repo" in options or (remote and re.search(r"[:/@]", remote)):
        return "a push to a remote named by URL or --repo; name the remote"
    if remote is None:
        # branch.<name>.pushRemote, then remote.pushDefault, then the remote `@{push}` names, else origin.
        branch = current_branch(directory, selectors, env)
        for key in (["config", "--get", "branch.{}.pushRemote".format(branch)] if branch else [None], ["config", "--get", "remote.pushDefault"]):
            value = git_lines(directory, list(selectors) + key, environment_) if key[0] else None
            if value and value[0].strip():
                remote = value[0].strip()
                break
        if remote is None:
            pushed = git_lines(directory, list(selectors) + ["rev-parse", "--abbrev-ref", "@{push}"], environment_)
            remote = pushed[0].strip().partition("/")[0] if pushed and "/" in pushed[0] else "origin"
        if re.search(r"[:/@]", remote):
            return "a push to a remote named by URL or --repo; name the remote"
    mirror = git_lines(directory, list(selectors) + ["config", "--bool", "--get", "remote.{}.mirror".format(remote)], environment_)
    if mirror and mirror[0].strip() == "true":
        return "a push to a mirror remote, which rewrites and deletes every ref"
    # `remote.<name>.push` maps a bare source (`feature`) or a bare push to other branches, and
    # `push.default=matching` sends every matching branch: the scan below would read the wrong
    # commits, so those are denied unless each refspec names its destination.
    if not tags_only and (not refspecs or any(":" not in r for r in refspecs)):
        mapped = git_lines(directory, list(selectors) + ["config", "--get-regexp", r"^remote\..*\.push$"], environment_)
        default = git_lines(directory, list(selectors) + ["config", "--get", "push.default"], environment_)
        if mapped or (not refspecs and default and default[0].strip() == "matching"):
            return "a push whose targets are chosen by remote.<name>.push or push.default, not the command"
    targets = [destination(r, directory, selectors, env) for r in refspecs]
    if not refspecs and not tags_only:
        # A bare push lands where `@{push}` says (push.default simple/current/upstream, pushRemote);
        # without an upstream git sends the current branch or refuses.
        pushed = git_lines(directory, list(selectors) + ["rev-parse", "--abbrev-ref", "@{push}"], environment_)
        targets = [pushed[0].strip().partition("/")[2]] if pushed and "/" in pushed[0] else [current_branch(directory, selectors, env)]
    if "" in targets:
        return "a push whose target branch could not be resolved"
    for target in targets:
        if target in RELEASE_BRANCHES or "*" in target:
            return "a push to a release branch ({})".format(target)
    if "--delete" in options or "-d" in options:
        return None
    return check_push_authors(refspecs, directory, "--tags" in options, selectors, env, remote)


def check_git(tokens, directory, env, unstripped=None):
    """Route a `git` command: global options first, then push, commit and merge."""
    index, configured, selectors, keys = 1, False, [], []
    while index < len(tokens) and tokens[index].startswith("-"):
        if tokens[index] == "-C" and index + 1 < len(tokens):
            directory = os.path.join(directory, os.path.expanduser(tokens[index + 1]))
        elif tokens[index] == "-c" or tokens[index].partition("=")[0] == "--config-env":
            configured = True  # a setting for this command alone: push.default, remote.*.push, …
            setting = tokens[index + 1] if tokens[index] in ("-c", "--config-env") and index + 1 < len(tokens) else tokens[index].partition("=")[2]
            keys.append(setting.partition("=")[0].lower())
        elif tokens[index].partition("=")[0] in ("--git-dir", "--work-tree"):
            name, has_value, value = tokens[index].partition("=")
            selectors += [name, value] if has_value else tokens[index : index + 2]
        index += 2 if tokens[index] in GIT_VALUE_OPTS else 1
    if index < len(tokens) and tokens[index] == "push":
        if configured or any(k.startswith("GIT_CONFIG") for k in env):
            return "a push with a configuration setting on the command, which can redirect it"
        return check_push(tokens[index + 1 :], directory, selectors, {k: v for k, v in env.items() if k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")})
    if index < len(tokens) and tokens[index] in ("commit", "merge"):
        # A setting that can switch the hook off or rewrite the message denies; identity and other
        # benign keys pass (`-c user.name=…`). GIT_CONFIG_* in the environment is not read: denied.
        if any(k.startswith(HOOK_KEYS) or k in HOOK_KEYS for k in keys) or any(k.startswith("GIT_CONFIG") for k in env):
            return "a commit with a configuration setting on the command, which can switch off the commit-msg hook"
        # Option values are read from the tokens before redirects were stripped: a quoted message
        # that begins with `<` or `>` looks like a redirect and would otherwise vanish, leaving a
        # following `--no-verify` to be read as the message.
        source = unstripped if unstripped and tokens[index] in unstripped else tokens
        args = source[source.index(tokens[index]) + 1 :]
        if tokens[index] == "merge":
            return check_commit(args, MERGE_VALUE_OPTS, MERGE_SHORTS)
        return check_commit(args)
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
    """The rule a `gh` command breaks, or None: PR merges into a protected base, by any gh route."""
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
        unstripped = strip_prefix(list(tokens))  # redirects kept: a quoted `> note` message is not a redirect
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
            reason = check_git(tokens, directory, env, unstripped)
        elif head == "gh":
            reason = check_gh(tokens, directory, env)
        if reason:
            return reason
    return None


def main():
    """Read Claude Code's PreToolUse payload from stdin and print a deny decision when a rule breaks."""
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
            advice = "RULE ZERO is checked by the commit-msg hook; commit or merge without --no-verify and without -c."
        elif "option-like revision" in reason:
            advice = "Name the branch to push plainly; a revision that starts with a dash is not read."
        elif "chosen by" in reason or "configuration setting on the command" in reason or "mirror remote" in reason or "named by URL" in reason:
            advice = "The guard must see what is pushed. Name the remote and the branch, with its destination, on the command line, without -c."
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
