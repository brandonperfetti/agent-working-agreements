#!/usr/bin/python3
"""PreToolUse guard for the Bash tool: the git rules no agent may break.

Denies force-pushes, pushes to a release branch and PR merges into develop,
main or master (or whose base it cannot read), per the Sans Faux profile's Git
ritual and merge boundary, save one exact command form into develop, the
delegated route (check_route_form; a form check, not eligibility); commits and merges that skip the commit-msg hook or
carry a configuration override, a git alias being read through its expansion (read from the command's words as the lexer
splits them, so a shape that hides a flag from them skips the hook: the push-time
scan and the read before presentation are the controls for that shape); and, best effort, pushes whose commits new to
the destination remote's tracking refs carry another author, a banned attribution
line, or an agent declaration that is malformed or not the commit's only one
(RULE ZERO; stale tracking refs are the documented limit, and the read before a
delivery is presented is the complete check). The author and message
of a commit being made are the commit-msg hook's to read (hooks/git), where git
holds them final; this guard reads only what git has already written. A push
is read in the state it will run in: only commands that cannot change where it
goes may come before it in the same call (note_prelude); the rest is refused,
not interpreted. Merges
between feature, wave, lane and hotfix branches pass. It parses the command rather than grepping it,
so a commit message that mentions `git push --force` passes. It stops honest
mistakes, not a determined bypass: a script or another tool that pushes is not
read (the README's limits).
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
# The attribution check; hooks/git/commit-msg carries the same patterns and function,
# and test_commit_msg.py holds the two copies to one table. A comment, quote or list prefix is still
# a line's start.
BANNED = re.compile(
    r"^[#>*+\- \t]*(co-authored-by|[a-z-]*-session)[ \t]*:"  # a contributor or session trailer
    r"|generated with"  # a promotional footer, anywhere
    r"|^[#>*+\- \t]*posted by an agent\b"  # the agent label the declaration replaced
    r"|claude\.ai/(chat|share|code/session)|chatgpt\.com/(c|share)/|chat\.openai\.com/(c|share)/",  # a session or chat link
    re.IGNORECASE | re.MULTILINE,
)
DECLARATION = re.compile(r"^[#>*+\- \t]*[*_]*agent[*_]*(?:[ \t]*\([^)\n]*\))?[*_]*[ \t]*:", re.IGNORECASE)  # **Agent**: and Agent (x): too
CLIENT = r"[^\s\u00b7](?:[^\u00b7\n]*[^\s\u00b7])?"  # the client, as it names itself
MODEL = r" \u00b7 [A-Za-z0-9][\w.:/@+\[\]-]*(?: \(requested\))?"  # the model id, marked when unattested
EFFORT = r" \u00b7 [a-z][a-z0-9-]*(?: \(requested\))?"  # the effort, marked the same way
AGENT_LINE = re.compile(
    r"Agent: (?:" + CLIENT + r" \(OpenClaw\)" + MODEL + "(?:" + EFFORT + ")?"  # OpenClaw: client and model
    r"|" + CLIENT + MODEL + EFFORT + ")"  # every other client: client, model and effort
)
ASSIGNMENT = re.compile(r"[A-Za-z_]\w*=")
WRAPPERS = {"command", "env", "exec", "nohup", "sudo", "time", "xargs"}
SHELLS = {"bash", "sh", "zsh"}
SEPARATORS = ";&|()\n"
GIT_VALUE_OPTS = {"-C", "-c", "--attr-source", "--config-env", "--git-dir", "--namespace", "--shallow-file", "--work-tree"}
# Git's other global options. `--version` and `--help` (and `-v`, `-h`) end the options: git runs
# version or help, whatever follows. The rest are flags, or take their value attached with `=`.
# An option the guard does not know may take the next word as its value and hide the subcommand,
# so the command is refused.
GIT_ENDING_FLAGS = {"-v", "--version", "-h", "--help"}
GIT_FLAGS = {"-p", "--paginate", "-P", "--no-pager", "--no-replace-objects", "--no-lazy-fetch",
             "--no-optional-locks", "--no-advice", "--bare", "--literal-pathspecs", "--no-literal-pathspecs",
             "--glob-pathspecs", "--noglob-pathspecs", "--icase-pathspecs", "--exec-path", "--html-path",
             "--man-path", "--info-path"}
GIT_ATTACHED_OPTS = GIT_VALUE_OPTS | {"--exec-path", "--list-cmds"}
# What may come before a push in the same call. The guard reads the repository before the call
# runs, so a command that can change where a push goes, or which checkout it runs in, makes that
# read stale. These cannot. Anything else is refused, not interpreted: the push runs in its own call.
PRELUDE_GIT = {"add", "commit", "status"}
CONTINUED_HASH = re.compile(r"#[^\n]*\\\n")
GIT_WORD = re.compile(r"(?:^|[^A-Za-z0-9_])(?:git|gh)(?:[^A-Za-z0-9_]|$)")
BARE_SOURCES = 20  # refspecs without a destination that one push may name
# Git ignores an alias named like one of its own commands, so these are never looked up; any other
# subcommand may be an alias for a push, a commit or a merge and is read through its expansion.
GIT_COMMANDS = frozenset(
    "add am apply bisect blame branch cat-file check-ignore checkout cherry cherry-pick clean clone commit "
    "config describe diff diff-tree fetch for-each-ref format-patch gc grep hash-object help init log ls-files "
    "ls-remote ls-tree merge merge-base mv name-rev notes pull push range-diff rebase reflog remote reset "
    "restore rev-list rev-parse revert rm shortlog show show-ref stash status submodule switch symbolic-ref "
    "tag update-index update-ref var version worktree".split()
)
PLUMBING_PUSHES = {"send-pack", "http-push"}  # what `git push` runs underneath; neither takes its rules
ALIAS_DEPTH = 10  # aliases of aliases the guard follows before it calls the chain a loop
# Variables that move git's configuration files, as GIT_CONFIG_* does.
CONFIG_HOME_VARS = {"HOME", "XDG_CONFIG_HOME"}
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


def attribution_problem(message):
    """What in one commit message breaks RULE ZERO's attribution clause, or None. The declaration
    is optional here; when present it is one line, in the standard shape."""
    if BANNED.search(message):
        return "no Co-Authored-By, session or chat link, or generated-with line on a commit"
    declarations = [line for line in message.split("\n") if DECLARATION.match(line)]
    if len(declarations) > 1:
        return "one Agent: line per commit, not {}".format(len(declarations))
    if declarations and not AGENT_LINE.fullmatch(declarations[0].rstrip()):
        return "an Agent: line reads exactly `Agent: <client> \u00b7 <model> \u00b7 <effort>`, not {!r}".format(declarations[0].strip())
    return None


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
            if "(" in token or ")" in token:
                # A subshell or substitution: a `cd` or assignment inside it does not carry out.
                # Its scope is not worked out; the marker is a command the guard does not read,
                # so a push later in the call is refused (note_prelude).
                result.append(["("])
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


def wrapped_with_options(prefix, tokens):
    """True when a wrapper's options precede a git or gh word: `env -u GH_REPO gh`, `sudo -u root
    git` and `env -S 'gh …'` (or `'-Sgh …'`, the operand attached) change what runs, or where, in
    ways strip_prefix does not model. The options themselves are read too, for an attached command."""
    names = [os.path.basename(t) for t in prefix]
    flagged = any(
        name in WRAPPERS and index + 1 < len(prefix) and prefix[index + 1].startswith("-")
        for index, name in enumerate(names)
    )
    named = re.compile(r"(?:^|[\s/=]|^-[A-Za-z]*S)(git|gh)(?=\s|$)")
    return flagged and any(named.search(token) for token in prefix + tokens if not ASSIGNMENT.match(token))


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
            encoding="utf-8",  # the push scan asks git for UTF-8 (--encoding); the locale may say otherwise
            errors="replace",  # a message with bytes outside the encoding is still read, not a traceback
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
    # Redirects were stripped before this walk by a lexer that cannot see quotes, so a quoted message
    # such as `-m "> note"` is gone and its option is left dangling in front of the next token. A
    # pending value that is missing or begins with `-` is therefore refused rather than read as the
    # value: `git commit -m --no-verify` is never what an agent means.
    flags, skip = [], None
    for arg in args:
        if skip:
            if arg.startswith("-") and arg != "-":  # `-F -` reads stdin, which the commit-msg hook then checks
                return "a commit whose option values cannot be read: a value is missing or looks like an option"
            skip = None
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
    if skip:
        return "a commit whose option values cannot be read: a value is missing or looks like an option"
    if "--dry-run" in flags and not any(flag.startswith("--no-d") for flag in flags):
        return None  # a flag, not `-m --dry-run`; any `--no-dry-run` makes it a real commit
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
    text = git_lines(directory, list(selectors) + ["log", "--encoding=UTF-8", "--format=%x1e%ae%x1f%B", "--not", "--remotes=" + remote, "--not"] + tag_option + ["--end-of-options"] + sources + ["--"], raw=True, env=environment(env))
    if text is None:  # the scan failed or timed out: nothing was checked
        return "a push whose commits could not be read for the author and trailer checks"
    records = [r for r in text.split("\x1e") if r.strip()]
    others = sorted({r.split("\x1f", 1)[0].strip() for r in records} - {AUTHOR_EMAIL})
    if others:
        return "a push of commits authored as {}".format(", ".join(others))
    for record in records:  # one message at a time: one declaration each, not one per push
        problem = attribution_problem(record.split("\x1f", 1)[1] if "\x1f" in record else "")
        if problem:
            return "a push of commits breaking the attribution rule ({})".format(problem)
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
    """The branch a refspec updates on the remote, `HEAD`/`@` resolved to the current branch and a
    source that is a symbolic ref to the branch it names, which is where git sends it."""
    source, colon, target = refspec.lstrip("+").partition(":")
    branch = target or source
    if branch in ("HEAD", "@"):
        return current_branch(directory, selectors, env)
    if not colon and not branch.startswith("-"):
        full = git_lines(directory, list(selectors) + ["rev-parse", "--symbolic-full-name", branch], environment(env))
        if full and full[0].startswith("refs/heads/"):
            return full[0][len("refs/heads/"):]
    return re.sub(r"^(refs/)?heads/", "", branch)


def check_push(args, directory, selectors=(), env=None, state=None):
    """The rule a `git push` breaks, or None: force, release branch, redirecting configuration, then the scan.
    `state` is what the same call ran before this push (note_prelude)."""
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

    # A dry run writes nothing, and the pickup guard's hook probe is one. Git takes the last of
    # `--dry-run` and `--no-dry-run`; the guard does not work out which is last: any negation
    # (a prefix from `--no-d`) ends the exemption and the push is read as a real one.
    if ("--dry-run" in options or "-n" in options) and not any(opt.startswith("--no-d") for opt in options):
        return None
    # In a short cluster, `-o` takes the rest as its value (`-ofleet`), so only letters before it count.
    short_force = any(re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", opt.split("o", 1)[0] if opt.startswith("-") and not opt.startswith("--") else opt) for opt in options)
    refspecs = positional[1:]
    if short_force or FORCE_FLAGS & set(options) or any(r.startswith("+") for r in refspecs):
        return "a force-push"
    if "--all" in options or "--branches" in options or ":" in refspecs:  # `:` pushes every matching branch
        return "a push of every branch, release branches included"
    if state and state["unread"]:
        return "a push after another command in the same call, which can change what the push sends"
    tags_only = ("--tags" in options or "--follow-tags" in options) and not refspecs and "--tags" in options
    environment_ = environment(env)
    # The destination remote, by name: a URL or `--repo` has no tracking refs to scan against.
    remote = positional[0] if positional else None
    if "--repo" in options or (remote and re.search(r"[:/@]", remote)):
        return "a push to a remote named by URL or --repo; name the remote"
    if remote is None:
        # As git chooses it: branch.<name>.pushRemote, remote.pushDefault, branch.<name>.remote, else origin.
        branch = current_branch(directory, selectors, env)
        keys = ["remote.pushDefault"] if not branch else ["branch.{}.pushRemote".format(branch), "remote.pushDefault", "branch.{}.remote".format(branch)]
        for key in keys:
            value = git_lines(directory, list(selectors) + ["config", "--get", key], environment_)
            if value and value[0].strip():
                remote = value[0].strip()
                break
        remote = remote or "origin"
        if re.search(r"[:/@]", remote):
            return "a push to a remote named by URL or --repo; name the remote"
    mirror = git_lines(directory, list(selectors) + ["config", "--bool", "--get", "remote.{}.mirror".format(remote)], environment_)
    if mirror and mirror[0].strip() == "true":
        return "a push to a mirror remote, which rewrites and deletes every ref"
    # `remote.<name>.push` maps a bare source (`feature`) or a bare push to other branches, and
    # `push.default=matching` sends every matching branch: the scan below would read the wrong
    # commits, so those are denied unless each refspec names its destination.
    default = git_lines(directory, list(selectors) + ["config", "--get", "push.default"], environment_)
    default = default[0].strip() if default else "simple"
    if not tags_only and (not refspecs or any(":" not in r for r in refspecs)):
        mapped = git_lines(directory, list(selectors) + ["config", "--get-regexp", r"^remote\..*\.push$"], environment_)
        if mapped or (not refspecs and default == "matching"):
            return "a push whose targets are chosen by remote.<name>.push or push.default, not the command"
    # Each source without a destination costs one read of the repository; the hook has ten seconds.
    if sum(":" not in r for r in refspecs) > BARE_SOURCES:
        return "a push naming more than {} branches".format(BARE_SOURCES)
    targets = [destination(r, directory, selectors, env) for r in refspecs]
    if not refspecs and not tags_only:
        # A bare push sends the current branch to its own name under simple and current (or git
        # refuses it), and to branch.<name>.merge under upstream. `@{push}` is not used: it names
        # the local tracking ref, which a fetch refspec may call something else than the branch
        # the push updates. Any other mode is refused as unresolved.
        branch = current_branch(directory, selectors, env)
        if default in ("simple", "current"):
            targets = [branch]
        elif default in ("upstream", "tracking") and branch:
            merge = git_lines(directory, list(selectors) + ["config", "--get", "branch.{}.merge".format(branch)], environment_)
            targets = [re.sub(r"^refs/heads/", "", merge[0].strip()) if merge else ""]
        else:
            targets = [""]
    if "" in targets:
        return "a push whose target branch could not be resolved"
    for target in targets:
        if target in RELEASE_BRANCHES or "*" in target:
            return "a push to a release branch ({})".format(target)
    if "--delete" in options or "-d" in options:
        return None
    return check_push_authors(refspecs, directory, "--tags" in options, selectors, env, remote)


def git_aliases(directory, selectors, settings, env, state):
    """Every alias git would find for this command, by lowercased name, read with the command's
    own settings and environment. One read per call: a long batch of git commands costs one."""
    cache = state.setdefault("aliases", {}) if state is not None else {}
    key = (directory, tuple(selectors), tuple(settings), tuple(sorted(env.items())))
    if key not in cache:
        text = git_lines(directory, list(selectors) + list(settings) + ["config", "--null", "--get-regexp", r"^alias\."], environment(env), raw=True)
        entries = [entry.partition("\n") for entry in (text or "").split("\0") if entry]
        cache[key] = {name[len("alias."):].lower(): body for name, _, body in entries}
    return cache[key]


def check_git(tokens, directory, env, state=None, depth=0):
    """Route a `git` command: global options first, an alias through its expansion, then push,
    commit and merge. `state` is what the same call ran before it (note_prelude)."""
    index, configured, selectors, keys, settings, start = 1, False, [], [], [], directory
    while index < len(tokens) and tokens[index].startswith("-"):
        if tokens[index] in GIT_ENDING_FLAGS:
            return None
        if not (tokens[index] in GIT_FLAGS | GIT_VALUE_OPTS or ("=" in tokens[index] and tokens[index].partition("=")[0] in GIT_ATTACHED_OPTS)):
            return "a git command with a global option the guard does not know ({})".format(tokens[index])
        if tokens[index] == "-C" and index + 1 < len(tokens):
            directory = os.path.join(directory, os.path.expanduser(tokens[index + 1]))
        elif tokens[index] == "-c" or tokens[index].partition("=")[0] == "--config-env":
            configured = True  # a setting for this command alone: push.default, remote.*.push, …
            setting = tokens[index + 1] if tokens[index] in ("-c", "--config-env") and index + 1 < len(tokens) else tokens[index].partition("=")[2]
            keys.append(setting.partition("=")[0].lower())
            settings += tokens[index : index + (2 if tokens[index] in GIT_VALUE_OPTS else 1)]
        elif tokens[index].partition("=")[0] in ("--git-dir", "--work-tree"):
            name, has_value, value = tokens[index].partition("=")
            selectors += [name, value] if has_value else tokens[index : index + 2]
        index += 2 if tokens[index] in GIT_VALUE_OPTS else 1
    if index < len(tokens) and tokens[index] in PLUMBING_PUSHES:
        return "a push through git's plumbing ({}), which the guard does not read".format(tokens[index])
    if index < len(tokens) and tokens[index] not in GIT_COMMANDS and state and state["unread"]:
        # The call may have changed its aliases since the guard read them: only a command this
        # git has of its own is read after another command.
        if "own" not in state:  # one read per call; configuration does not change this list
            state["own"] = set(git_lines(directory, ["--list-cmds=main,others"], environment(env)) or ())
        if tokens[index] not in state["own"]:
            return "a git alias or unknown git command ({}) following another command in the same call, which can change what it runs".format(tokens[index])
    if index < len(tokens) and tokens[index] not in GIT_COMMANDS:
        body = git_aliases(directory, selectors, settings, env, state).get(tokens[index].lower())
        # An alias named like a command this git has is never used; that list is read only then.
        if body is not None and tokens[index] not in (git_lines(directory, ["--list-cmds=main,others"], environment(env)) or ()):
            if body.startswith("!"):
                # A shell alias is a command line of its own, run with settings git hands on to it.
                # Reading it would mean interpreting it, so it is refused.
                return "a git shell alias ({}), which the guard does not read".format(tokens[index])
            try:
                words = shlex.split(body)
            except ValueError:
                words = None
            if words is None or depth >= ALIAS_DEPTH:
                return "a git alias the guard cannot follow ({})".format(tokens[index])
            return check_git(tokens[:index] + words + tokens[index + 1 :], start, env, state, depth + 1)
    # The shell opens a redirect's file before git starts: `git push > .git/config` empties the
    # configuration the guard has just read. Given after any more specific reason.
    redirected = "a {} with its output redirected to a file, which the shell writes before git reads its configuration".format(tokens[index]) if index < len(tokens) and state and state.get("redirected") else None
    moved = sorted(CONFIG_HOME_VARS & set(env))
    if index < len(tokens) and tokens[index] == "push":
        if configured or any(k.startswith("GIT_CONFIG") for k in env):
            return "a push with a configuration setting on the command, which can redirect it"
        if moved:
            return "a push with {} set on the command, which moves git's configuration".format(moved[0])
        if redirected:
            return redirected
        return check_push(tokens[index + 1 :], directory, selectors, {k: v for k, v in env.items() if k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR")}, state)
    if index < len(tokens) and tokens[index] in ("commit", "merge"):
        if moved:  # the commit-msg hook is found through the configuration under HOME
            return "a commit with {} set on the command, which moves git's configuration".format(moved[0])
        # A setting that can switch the hook off or rewrite the message denies; identity and other
        # benign keys pass (`-c user.name=…`). GIT_CONFIG_* in the environment is not read: denied.
        if any(k.startswith(HOOK_KEYS) or k in HOOK_KEYS for k in keys) or any(k.startswith("GIT_CONFIG") for k in env):
            return "a commit with a configuration setting on the command, which can switch off the commit-msg hook"
        # Option values are read from the tokens before redirects were stripped: a quoted message
        # that begins with `<` or `>` looks like a redirect and would otherwise vanish, leaving a
        # following `--no-verify` to be read as the message.
        args = tokens[index + 1 :]
        if tokens[index] == "merge":
            return check_commit(args, MERGE_VALUE_OPTS, MERGE_SHORTS) or redirected
        return check_commit(args) or redirected
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


# The one command form review-findings.md "Base merges" names for a delegated merge into develop.
INTEGRATION_BASE = "develop"
ROUTE_FLAGS = {"-m": "--merge", "--merge": "--merge", "-A": "--author-email",
               "--author-email": "--author-email", "--match-head-commit": "--match-head-commit",
               "-R": "--repo", "--repo": "--repo"}
FULL_SHA = re.compile(r"[0-9a-f]{40}")
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
PR_NUMBER = re.compile(r"[1-9][0-9]*")
# The whole tool call, for the route: plain words only, so the argv gh gets is the one checked here.
PLAIN_CALL = re.compile(r"gh( [A-Za-z0-9_./@=:+-]+)+")
# A call that mentions gh and a merge is read only when it is one simple gh command, word for word:
# assignments, a gh path, plain or quoted words holding no expansion, at most a trailing `2>&1`.
MERGE_WORDS = re.compile(r"merge", re.IGNORECASE)
BLANKS = " \t\n"  # the shell's blanks around a call; str.strip() would also drop Unicode spaces bash keeps
GH_WORD = re.compile(r"(?:^|[^A-Za-z0-9_-])gh(?:[^A-Za-z0-9_-]|$)")
_WORD = r"""(?:[A-Za-z0-9_./@=:+,%-]|'[^'\n]*'|"[^"$`\\\n]*")+"""
MERGE_CALL = re.compile(
    r"(?:[A-Za-z_]\w*=(?:{w})?[ \t]+)*(?:[A-Za-z0-9_./-]*/)?gh(?:[ \t]+{w})*(?:[ \t]+2>&1)?".format(w=_WORD)
)
# One simple git command, word for word, without `-c`: text such as a `--grep` or `-m` value that
# names gh and a merge is only text there, so the call is read as git.
GIT_CALL = re.compile(r"git(?:[ \t]+{w})*(?:[ \t]+2>&1)?".format(w=_WORD))


def check_route_form(positional, options, sole):
    """None when a PR merge into develop is exactly the route's form; otherwise why it is not.
    The form is checked, not eligibility: acceptance, checks and effects stay the route's to prove,
    and the base was read before the command runs, so a retarget in that window is not caught."""
    if not sole:
        return "a PR merge into develop that is not a plain command on its own"
    extra = sorted(name for name in options if name not in ROUTE_FLAGS)
    if extra:
        return "a PR merge into develop with {}, which the route does not use".format(", ".join(extra))
    given = {}
    for name, values in options.items():
        given.setdefault(ROUTE_FLAGS[name], []).extend(values)
    if any(len(values) != 1 for values in given.values()) or len(given) != len(set(ROUTE_FLAGS.values())):
        return "a PR merge into develop without each of --merge, --match-head-commit, --author-email and --repo exactly once"
    if given["--merge"] != [""]:
        return "a PR merge into develop whose --merge carries a value"
    if not FULL_SHA.fullmatch(given["--match-head-commit"][0]):
        return "a PR merge into develop whose --match-head-commit is not a full lowercase SHA"
    if given["--author-email"][0] != AUTHOR_EMAIL:
        return "a PR merge into develop with another author email"
    if not REPOSITORY.fullmatch(given["--repo"][0]):
        return "a PR merge into develop whose --repo is not owner/name"
    if len(positional) != 3 or not PR_NUMBER.fullmatch(positional[2]):
        return "a PR merge into develop that does not name one PR by number"
    return None


def gh_options(tokens):
    """Split gh arguments as gh reads them: `-sb x` clusters, `--opt=x`, and `--`. `-X` is filed
    under `--method`, one flag in gh, so the last method in argv order is the list's last."""
    positional, options, index = [], {}, 0

    def add(name, value):
        options.setdefault("--method" if name == "-X" else name, []).append(value)

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
            elif name not in GH_ARG_VALUE_OPTS and equals:
                value = "=" + value  # `--merge=` and `--merge=false` are not a bare `--merge`
            add(name, value)
        elif token.startswith("-") and len(token) > 1:
            for position in range(1, len(token)):
                name = "-" + token[position]
                rest = token[position + 1 :]
                if len(rest) > 1 and rest[0] == "=":
                    # pflag, at any letter of a cluster: `-iX=PUT` sets -X, `-d=f` sets the Boolean -d.
                    value = rest[1:] if name in GH_ARG_VALUE_OPTS else rest
                    add(name, value)
                    break
                if name in GH_ARG_VALUE_OPTS:
                    if not rest:
                        index += 1
                        rest = tokens[index] if index < len(tokens) else ""
                    add(name, rest)  # a lone `-b=` is the body `=`
                    break
                add(name, "")
        else:
            positional.append(token)
        index += 1
    return positional, options


def merge_bearing(command):
    """True when a call names gh and a merge anywhere, read past quotes and line continuations."""
    text = re.sub(r"['\"\\\n]", "", command)
    if not (MERGE_WORDS.search(text) and GH_WORD.search(text)):
        return False
    if GIT_CALL.fullmatch(command.strip(BLANKS)):
        words = shlex.split(command.strip(BLANKS))
        return any(w.startswith(("-c", "--config-env")) for w in words[1:])
    return True


def check_gh(tokens, directory, env, sole=False):
    """The rule a `gh` command breaks, or None: PR merges into a protected base, by any gh route,
    except the delegated route's one form into develop. `sole` is True only when the whole tool call
    is that one plain `gh` command."""
    positional, options = gh_options(tokens[1:])
    repos = options.get("-R", []) + options.get("--repo", [])
    repo = ["--repo", repos[-1]] if repos else []
    if positional[:2] == ["pr", "merge"] and len(repos) > 1:
        # gh takes the last in argv order; the guard does not track that order across spellings.
        return "a PR merge that names its repository more than once"
    if positional[:2] == ["pr", "merge"]:
        # The guard's documented live probe: answered here, with no lookup.
        if "--help" in options or "-h" in options:
            return "a PR merge"
        # An auto-merge lands later, after a stacked PR may have been retargeted to develop.
        if "--auto" in options:
            return "an auto-merge, whose base can change before it lands"
        selector = positional[2:3]
        if selector and selector[0].startswith("-"):
            # Read back without its `--`, a selector such as `--comments=false` would be a view option.
            return "a PR merge whose selector begins with a dash"
        base = gh_read(
            ["pr", "view"] + selector + repo + ["--json", "baseRefName", "--jq", ".baseRefName"],
            directory,
            env,
        )
        if base == INTEGRATION_BASE:
            return check_route_form(positional, options, sole)
        return check_merge_base(base)
    if positional[:1] == ["api"]:
        call = " ".join(tokens[1:])
        if GH_MERGE_MUTATIONS.search(call):
            return "a PR merge"
        if re.search(r"repos/[^/\s]+/[^/\s]+/merges\b", call):
            return "a branch merge through the API"
        methods = options.get("--method", [])
        if not methods or methods[-1].upper() != "PUT":
            return None  # gh sends the last method given, by either spelling
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


def plain_cd(directory, words, env):
    """The directory a literal `cd <dir>` enters, or None when the guard would have to interpret
    the path to know: an option, `~`, an expansion or a glob, a `..`, a symbolic link in it, a
    CDPATH search, or a path that is not a directory (the shell then stays where it was)."""
    if len(words) != 1 or "CDPATH" in env or "CDPATH" in os.environ:
        return None
    word = words[0]
    if word.startswith(("-", "~")) or re.search(r"[$`*?\[\]{}\\]", word) or ".." in word.split("/"):
        return None
    target = os.path.join(directory, word)
    if not os.path.isdir(target) or os.path.realpath(target) != os.path.normpath(os.path.join(os.path.realpath(directory), word)):
        return None
    return target


def note_prelude(tokens, state):
    """Mark the call unread for a later push unless this command is one that cannot change where
    a push goes: `export NAME=value`, or a plain `git add`, `git commit` or `git status`. A `cd`
    is judged where the directory is tracked (check_command)."""
    head, words = os.path.basename(tokens[0]), tokens[1:]
    if head == "cd" or (head == "export" and all(ASSIGNMENT.match(word) for word in words)):
        return
    if head == "git" and words and words[0] in PRELUDE_GIT:
        return
    state["unread"] = True


def check_command(command, directory, inherited=None, nested=False, state=None):
    """The first rule the command breaks, or None. `inherited` is a calling shell's environment;
    `nested` marks a command read from inside `eval` or a shell's `-c`; `state` is what the call
    ran before this command, for a push that follows (note_prelude)."""
    exported = dict(inherited or {})
    state = state if state is not None else {"unread": False}
    # The shell ends a comment at its newline, backslash or not; joining continued lines below
    # would fold the next line into it. Whether a `#` here is a comment is not worked out.
    if "&>" in command and GIT_WORD.search(command):
        # The lexer splits `&>` at its `&`, so the redirect would be read as another command's.
        return "a git or gh call with &>, which the guard cannot read"
    if CONTINUED_HASH.search(command) and GIT_WORD.search(command.replace("\\\n", "")):  # the word itself may be continued
        return "a git or gh call with a # on a line that continues onto the next, which the guard cannot read"
    # A descriptor duplication (`2>&1`) would split at its `&` and hide the words after it from the
    # command they belong to, so it is dropped before splitting: `gh … 2>&1 -R x/y` stays one argv.
    # The shell also joins a backslash-newline before reading words.
    parts = segments(re.sub(r"\d*[<>]&(\d+|-)", " ", command.replace("\\\n", "")))
    # Only a call that is one plain `gh` command, with no prefix, wrapper, redirect, quote, chain or
    # expansion, can carry the route: its words are exactly the argv gh receives.
    sole = not nested and bool(PLAIN_CALL.fullmatch(command.strip(BLANKS)))
    if merge_bearing(command):
        # Beside anything else (a chain, substitution, wrapper, shell, redirect or continuation) a
        # merge's base read can be stale or of another PR before it runs, so only this shape is read.
        if nested or not MERGE_CALL.fullmatch(command.strip(BLANKS)):
            return "a gh merge in a call the guard cannot read word for word"
        # Only an unquoted trailing `2>&1` is a redirect; a quoted one is gh's argument.
        words = shlex.split(re.sub(r"[ \t]+2>&1$", "", command.strip(BLANKS)))
        env = dict(exported)
        while ASSIGNMENT.match(words[0]):
            env.update([words.pop(0).split("=", 1)])
        return check_gh(words, directory, env, sole=sole)
    for tokens in parts:
        # A redirect of output writes a file, the repository's configuration among them. Which
        # file is not worked out: the push, commit or merge it is on, and a push later in the
        # call, are refused. `2>&1` was dropped above; reading input (`<`, a heredoc) writes nothing.
        redirected = any(re.match(r"\d*>", token) for token in tokens)
        state["redirected"] = redirected
        tokens = strip_redirects(tokens)
        command_tokens = strip_prefix(tokens)
        prefix = tokens[: len(tokens) - len(command_tokens)]
        env = dict(exported)
        env.update(token.split("=", 1) for token in prefix if ASSIGNMENT.match(token))
        tokens = command_tokens
        if wrapped_with_options(prefix, command_tokens):
            return "a git or gh command behind wrapper options the guard does not parse"
        if not tokens:
            # `NAME=value` alone sets a shell variable, and changes the environment when the name
            # is already exported (HOME is): what follows is read with it.
            exported.update(env)
            state["unread"] = state["unread"] or redirected
            continue
        head = os.path.basename(tokens[0])
        reason = None
        if head.startswith("-"):
            # A segment that opens with an option is a piece of a command the lexer split off (a quoted
            # `&` or `;` used as a redirect target); whatever it carries cannot be read in place.
            return "a command the guard cannot read: a segment begins with an option"
        if fed_by_xargs(prefix, command_tokens):
            return "a git or gh command whose arguments arrive through xargs and are not visible here"
        if head == "export":
            exported.update(token.split("=", 1) for token in tokens[1:] if ASSIGNMENT.match(token))
        elif head == "cd":
            entered = plain_cd(directory, tokens[1:], env)  # `CDPATH=x cd dir` counts too
            if entered:
                directory = entered
            else:
                state["unread"] = True  # where a later push would run is not known
                if len(tokens) == 2:  # as before, for the reads of what follows
                    directory = os.path.join(directory, os.path.expanduser(tokens[1]))
        elif head == "eval":
            reason = check_command(" ".join(tokens[1:]), directory, env, nested=True, state=state)
        elif head in SHELLS:
            for index, token in enumerate(tokens[:-1]):
                if re.fullmatch(r"-[A-Za-z]*c[A-Za-z]*", token):
                    reason = check_command(tokens[index + 1], directory, env, nested=True, state=state)
                    break
        elif head == "git" or head.startswith("git-"):
            # `git-push`, as git's exec path holds it, is `git push` by another name.
            reason = check_git(tokens if head == "git" else ["git", head[len("git-"):]] + tokens[1:], directory, env, state)
        elif head == "gh":
            reason = check_gh(tokens, directory, env, sole=sole)
        if reason:
            return reason
        note_prelude(tokens, state)
        state["unread"] = state["unread"] or redirected
    return None


def main():
    """Read Claude Code's PreToolUse payload from stdin and print a deny decision when a rule breaks."""
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    reason = check_command(command, payload.get("cwd") or os.getcwd())
    if reason:
        if "attribution rule" in reason:
            advice = (
                "RULE ZERO: at most one Agent: <client> \u00b7 <model> \u00b7 <effort> trailer, and no "
                "Co-Authored-By, session or chat link, or generated-with line, on a commit. Fix the "
                "message (git commit --amend for a commit already made) and retry."
            )
        elif "cannot be read" in reason and "segment" in reason:
            advice = "Quote redirect targets without shell separators, or split the command, so the guard can read each part."
        elif "option values cannot be read" in reason:
            advice = "Give each -m, -F, --author or --trailer a value that begins with a word, not with -, <, > or a digit followed by < or > (2>, 2<), so the guard can read the command."
        elif "commit-msg hook" in reason:
            advice = "RULE ZERO is checked by the commit-msg hook; commit or merge without --no-verify and without -c."
        # A shape the agent can fix says what to do next; only what is Brandon's says hand it back.
        elif "after another command" in reason:
            advice = "Run the push as its own call. Before it, a call may hold only NAME=value, cd to an existing directory (no .., ~, $ or symlink), git add, git commit and git status."
        elif "target branch could not be resolved" in reason:
            advice = "Name the remote and the branch on the command: git push <remote> <branch>."
        elif "moves git's configuration" in reason:
            advice = 'Run the command again without setting that variable.'
        elif 'global option the guard does not know' in reason:
            advice = 'Run the command again without that option, or with its value attached by =.'
        elif 'a push naming more than' in reason:
            advice = 'Push fewer branches in one call.'
        elif "with &>" in reason:
            advice = "Write 2>&1 in its place, with a pipe if the output is wanted (2>&1 | tee out.txt)."
        elif "output redirected to a file" in reason:
            advice = "Run it without the redirect; 2>&1 and a pipe (| tee out.txt) are fine."
        elif "continues onto the next" in reason:
            advice = "Put the command on one line, or drop the #."
        elif "alias or unknown git command" in reason:
            advice = "Write the git command out in full, or run it as its own call."
        elif "alias" in reason:
            advice = "Write the git command out in full, without the alias."
        elif "git's plumbing" in reason:
            advice = 'Use git push <remote> <branch> instead.'
        elif "option-like revision" in reason:
            advice = "Name the branch to push plainly; a revision that starts with a dash is not read."
        elif "chosen by" in reason or "configuration setting on the command" in reason or "mirror remote" in reason or "named by URL" in reason:
            advice = "The guard must see what is pushed. Name the remote and the branch, with its destination, on the command line, without -c."
        elif "could not be read for the author" in reason:
            advice = "RULE ZERO: the history read failed or timed out. Check the revision and retry once; if it keeps failing, hand the push back to Brandon."
        elif reason.startswith("a PR merge into develop "):
            advice = (
                "Only an accepted PR whose binding's route is active merges into develop, as one "
                "command on its own: gh pr merge <N> --repo <owner/name> --merge "
                "--match-head-commit <40-hex head> --author-email {}. A refusal here is not "
                "routed around; see procedures/review-findings.md, Base merges."
            ).format(AUTHOR_EMAIL)
        elif reason.startswith("a gh merge in a call"):
            advice = (
                "Run the gh merge as its own tool call: one gh command, with no chain, pipe, "
                "substitution, wrapper, shell -c, line continuation or redirect but a trailing 2>&1; "
                "pass a message with --body-file."
            )
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
