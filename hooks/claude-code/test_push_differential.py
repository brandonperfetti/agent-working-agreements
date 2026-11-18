#!/usr/bin/python3
"""Differential test for guard_git.py's push rules (#236): the guard's verdict beside what git does.

Each row is one shell call. The test asks the guard for its verdict, then runs the call for real
against bare repositories on disk and reads what happened. Two things are held for every row: the
verdict is the one the row names, and no call the guard allows moves a release branch, deletes a
ref, rewinds one, or makes a commit the commit-msg hook would have refused. So the guard's model
is checked against git itself, not against a second copy of the model. Nothing here reaches a
network or the host's git configuration.

Run: /usr/bin/python3 hooks/claude-code/test_push_differential.py
With AWA_GUARD_BASE=<an earlier guard_git.py> it also holds that nothing that guard refused is
admitted now unless running it does no harm.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guard_git  # noqa: E402

ALLOW, DENY = "allow", "deny"
UP_MASTER = "git branch -q --set-upstream-to=origin/master"
DIVERGE = "git push -q origin feature/x && git commit -q --amend --allow-empty -m 'feat: f1, rewritten'"
ON_MASTER = "git checkout -q master"

# (name, setup run in the clone first, the call, the verdict). `{root}` is the fixture's own
# directory, for a call that names an absolute path.
ROWS = [
    # Ordinary feature-branch pushes, and the forms the fleet uses every day: these pass.
    ("a bare push under simple", "", "git push", ALLOW),
    ("origin HEAD", "", "git push origin HEAD", ALLOW),
    ("-u origin <branch>", "", "git push -u origin feature/x", ALLOW),
    ("src:dst to the same name", "", "git push origin feature/x:feature/x", ALLOW),
    ("a bare push under current", "git config push.default current", "git push", ALLOW),
    ("--tags", "", "git push --tags", ALLOW),
    ("origin tag <t>", "", "git push origin tag v1", ALLOW),
    ("a release tag by full refspec", "", "git push --no-follow-tags origin refs/tags/v1:refs/tags/v1", ALLOW),
    ("the release fast-forward of develop", "", "git push origin HEAD:develop", ALLOW),
    ("commit, then push origin HEAD", "", "git commit -q --allow-empty -m 'feat: f2' && git push origin HEAD", ALLOW),
    ("add, commit, then a bare push", "", "git add -A && git commit -q --allow-empty -m 'feat: f2' && git push", ALLOW),
    ("status, then push", "", "git status --short && git push", ALLOW),
    ("an assignment, then push", "", "NOTE=1; export OTHER=2; git push", ALLOW),
    ("a push after cd into a worktree", "git worktree add -q ../wt -b feature/y", "cd {root}/wt && git push -u origin feature/y", ALLOW),
    ("a push, then other commands", "", "git push origin feature/x && git checkout -q master", ALLOW),
    ("push.followTags", "git config push.followTags true", "git push", ALLOW),
    ("remote.pushDefault under current", "git config push.default current; git config remote.pushDefault other", "git push", ALLOW),
    ("simple with a release upstream: git refuses it", UP_MASTER, "git push", ALLOW),
    ("remote.<name>.push with --tags sends tags only", "git config remote.origin.push HEAD:master", "git push --tags", ALLOW),
    ("pushurl: another repository, the same branch", "git config remote.origin.pushurl ../other.git", "git push origin feature/x", ALLOW),
    ("insteadOf: another repository, the same branch", "git config url.../other.git.insteadOf ../remote.git", "git push", ALLOW),
    ("a dry run to a release branch", "", "git push --dry-run origin HEAD:master", ALLOW),
    ("a dry run after other commands", "", "git checkout -q master && git push --dry-run", ALLOW),
    ("a commit the hook itself refuses", "", "git commit -q --allow-empty -m bypass", ALLOW),
    # Safe, but the guard would have to interpret the call to know: each needs the push in its own call.
    ("fetch, then push", "", "git fetch -q && git push", DENY),
    ("a new branch, then a push that names it", "", "git checkout -q -b feature/new && git push -u origin feature/new", DENY),
    ("a comment line, then push", "", "# push the reviewed branch\ngit push -u origin feature/x", DENY),
    ("a trailing comment on the push", "", "git push origin feature/x # done", DENY),
    ("status behind a global flag, then push", "", "git --no-optional-locks status --short && git push", DENY),
    ("any other command, then push", "", "echo pushing && git push", DENY),
    ("cd by a relative path with .., then push", "git worktree add -q ../wt -b feature/y", "cd ../wt && git push -u origin feature/y", DENY),
    # push.default
    ("upstream in the repository, tracking master", "git config push.default upstream; " + UP_MASTER, "git push", DENY),
    ("upstream, the remote named", "git config push.default upstream; " + UP_MASTER, "git push origin", DENY),
    ("upstream in the global config", "git config --global push.default upstream; " + UP_MASTER, "git push", DENY),
    ("upstream through include.path", "git config include.path ../../upstream.inc; " + UP_MASTER, "git push", DENY),
    ("matching in the repository", "git config push.default matching", "git push", DENY),
    ("matching, the remote named", "git config push.default matching", "git push origin", DENY),
    ("matching in the global config", "git config --global push.default matching", "git push", DENY),
    ("-c push.default=upstream", UP_MASTER, "git -c push.default=upstream push", DENY),
    ("-c push.default=matching", "", "git -c push.default=matching push", DENY),
    # remote.<name>.push
    ("remote.origin.push, a bare push", "git config remote.origin.push HEAD:master", "git push", DENY),
    ("remote.origin.push, the remote named", "git config remote.origin.push HEAD:master", "git push origin", DENY),
    ("remote.origin.push maps a bare source", "git config remote.origin.push refs/heads/feature/x:refs/heads/master", "git push origin feature/x", DENY),
    ("remote.origin.push in the global config", "git config --global remote.origin.push HEAD:master", "git push", DENY),
    ("-c remote.origin.push", "", "git -c remote.origin.push=HEAD:master push", DENY),
    ("remote.origin.push with --follow-tags", "git config remote.origin.push HEAD:master", "git push --follow-tags", DENY),
    # The branch's upstream, pushRemote and mirrors
    ("pushRemote with an upstream on master", "git config push.default upstream; git config branch.feature/x.pushRemote other; git config branch.feature/x.remote other; git config branch.feature/x.merge refs/heads/master", "git push", DENY),
    ("a mirror remote, a bare push", "git config remote.origin.mirror true", "git push", DENY),
    ("a mirror remote, named", "git config remote.origin.mirror true", "git push origin", DENY),
    ("pushRemote names a mirror", "git config remote.other.mirror true; git config branch.feature/x.pushRemote other", "git push", DENY),
    # Every branch
    ("--all", "", "git push --all", DENY),
    ("--al, abbreviated", "", "git push --al origin", DENY),
    ("--branches", "", "git push --branches origin", DENY),
    ("--mirror", "", "git push --mirror", DENY),
    ("--mir, abbreviated", "", "git push --mir origin", DENY),
    ("--prune with a wildcard", "", "git push --prune origin 'refs/heads/*:refs/heads/*'", DENY),
    ("the matching refspec", "", "git push origin :", DENY),
    # HEAD forms and sources that mislead
    ("HEAD:master", "", "git push origin HEAD:master", DENY),
    ("@:master", "", "git push origin @:master", DENY),
    ("HEAD:refs/heads/master", "", "git push origin HEAD:refs/heads/master", DENY),
    ("HEAD:heads/master", "", "git push origin HEAD:heads/master", DENY),
    ("<branch>:main", "", "git push origin feature/x:main", DENY),
    ("on master, origin HEAD", ON_MASTER, "git push origin HEAD", DENY),
    ("on master, a bare push", ON_MASTER, "git push", DENY),
    ("a refspec in a shell variable", "", "B=HEAD:master; git push origin $B", DENY),
    ("a refspec from a substitution", "", "git push origin $(echo HEAD:master)", DENY),
    # State changed earlier in the same call
    ("checkout master, then origin HEAD", "", "git checkout -q master && git push origin HEAD", DENY),
    ("checkout master, then a bare push", "", "git checkout -q master && git push", DENY),
    ("config push.default, then push", "", "git config push.default matching && git push", DENY),
    ("config remote.origin.push, then push", "", "git config remote.origin.push HEAD:master && git push", DENY),
    ("set the upstream and the mode, then push", "", "git branch -q -u origin/master && git config push.default upstream && git push", DENY),
    ("fetch --set-upstream, then push", "git config push.default upstream", "git fetch -q --set-upstream origin master && git push", DENY),
    ("a new branch from master, pushed by name", "", "git checkout -q -B feature/x master && git push origin feature/x", DENY),
    # A directory the guard does not follow
    ("-C to a checkout on master", "", "git -C ../work2 push origin HEAD", DENY),
    ("cd to a checkout on master", "", "cd {root}/work2 && git push origin HEAD", DENY),
    ("cd .. to a checkout on master", "", "cd ../work2 && git push origin HEAD", DENY),
    ("pushd to a checkout on master", "", "pushd ../work2 >/dev/null && git push origin HEAD", DENY),
    ("cd -- to a checkout on master", "", "cd -- ../work2 && git push origin HEAD", DENY),
    ("cd -P to a checkout on master", "", "cd -P {root}/work2 && git push", DENY),
    ("cd through a symlink and back", "mkdir sub && ln -s ../work/sub ../work2/link", "cd {root}/work2/link/.. && git push origin HEAD", DENY),
    ("cd through a symlink to a checkout on master", "ln -s work2 ../link2", "cd {root}/link2 && git push origin HEAD", DENY),
    ("a cd that fails, then a push from where the shell stayed", "", "cd {root}/work2 && cd {root}/work/missing/..; git push origin HEAD", DENY),
    ("a cd that fails, then || push", "", "cd {root}/work2 && cd {root}/work/missing/.. || git push origin HEAD", DENY),
    ("a cd inside a comment", "", "cd {root}/work2\n# note; cd {root}/work\ngit push origin HEAD", DENY),
    ("GIT_DIR of a checkout on master", "", "GIT_DIR=../work2/.git git push origin HEAD", DENY),
    # A `#` inside ${...} is data, not a comment: the command after it is still there
    ("${x:- #} before a release push", ON_MASTER, "x=${x:- #}; git push origin HEAD", DENY),
    ("${x# #} before a push to main", "", "x=${x# #}; git push origin HEAD:main", DENY),
    ("${x% #} before a force-push", DIVERGE, "x=${x% #}; git push --force origin feature/x", DENY),
    ("${x:- #} before a branch deletion", "", "x=${x:- #}; git push origin :main", DENY),
    ("${x:- #} before a commit that skips the hook", "", "x=${x:- #}; git commit -q --allow-empty -m bypass --no-verify", DENY),
    ("${x:- #} inside eval", "", "eval 'x=${x:- #}; git push origin HEAD:master'", DENY),
    ("${x:- #} inside bash -c", "", "bash -c 'x=${x:- #}; git push origin HEAD:master'", DENY),
    # Configuration on the command or in its environment
    ("GIT_CONFIG_COUNT", "", "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=push.default GIT_CONFIG_VALUE_0=matching git push", DENY),
    ("GIT_CONFIG_GLOBAL", "", "GIT_CONFIG_GLOBAL=../matching.cfg git push", DENY),
    ("an exported GIT_CONFIG_GLOBAL", "", "export GIT_CONFIG_GLOBAL=../matching.cfg; git push", DENY),
    ("--config-env", "", "P=matching git --config-env=push.default=P push", DENY),
    ("--no-pager before a release push", "", "git --no-pager push origin HEAD:master", DENY),
    # Remotes by URL
    ("--repo", "git config push.default matching", "git push --repo=other", DENY),
    ("a path as the remote", "", "git push ../remote.git HEAD:master", DENY),
    # The commit-msg hook
    ("--no-verify", "", "git commit -q --allow-empty -m bypass --no-verify", DENY),
    ("-c core.hooksPath", "", "git -c core.hooksPath=/nonexistent-hooks commit -q --allow-empty -m bypass", DENY),
    # HOME and XDG_CONFIG_HOME move git's configuration
    ("HOME moved", "", "HOME=../althome git push", DENY),
    ("HOME moved through env", "", "env HOME=../althome git push", DENY),
    ("HOME exported", "", "export HOME=../althome; git push", DENY),
    ("HOME assigned on its own line", "", "HOME=../althome\ngit push", DENY),
    ("XDG_CONFIG_HOME moved", "mkdir -p ../xdg/git && cp ../matching.cfg ../xdg/git/config", "XDG_CONFIG_HOME=../xdg git push", DENY),
    ("HOME moved on a commit, away from the hook", "", "HOME=../althome git commit -q --allow-empty -m bypass", DENY),
    ("HOME moved on a commit inside a shell", "", "bash -c 'HOME=../althome; git commit -q --allow-empty -m bypass'", DENY),
    # A negated dry run is a real push
    ("--dry-run, then --no-dry-run", "", "git push --dry-run --no-dry-run origin HEAD:master", DENY),
    ("-n, then --no-dry-run", "", "git push -n --no-dry-run origin HEAD:master", DENY),
    ("--no-dry, abbreviated", "", "git push -n --no-dry origin HEAD:master", DENY),
    ("--no-dry-run before a force-push", DIVERGE, "git push --dry-run --no-dry-run --force origin feature/x", DENY),
    ("a dry run named last is still read as a push", "", "git push --no-dry-run --dry-run origin HEAD:master", DENY),
    # Global options: read, or refused
    ("--attr-source with its value apart", "", "git --attr-source HEAD push origin HEAD:master", DENY),
    ("--attr-source before a force-push", DIVERGE, "git --attr-source HEAD push --force origin feature/x", DENY),
    ("--attr-source before a commit that skips the hook", "", "git --attr-source HEAD commit -q --allow-empty -m bypass --no-verify", DENY),
    ("a global option git does not have", "", "git --no-such-option push origin HEAD:master", DENY),
    ("--attr-source before an ordinary push", "", "git --attr-source HEAD push origin feature/x", ALLOW),
    # Resolution: as git resolves it, or refused
    ("upstream with no tracking ref for master", "git config push.default upstream; git config remote.origin.fetch '+refs/heads/develop:refs/remotes/origin/develop'; git config branch.feature/x.merge refs/heads/master", "git push", DENY),
    ("branch.<name>.remote names a mirror", "git config remote.other.mirror true; git config branch.feature/x.remote other; git config branch.feature/x.merge refs/heads/nope", "git push", DENY),
    ("a branch that is a symbolic ref to master", "git symbolic-ref refs/heads/sneaky refs/heads/master", "git push origin sneaky", DENY),
    ("a tag that is a symbolic ref to master", "git symbolic-ref refs/tags/tsneak refs/heads/master", "git push origin tag tsneak", DENY),
    ("a branch that is a symbolic ref to a feature branch", "git symbolic-ref refs/heads/same refs/heads/feature/x", "git push origin same", ALLOW),
    # Aliases: a word alias is read through its expansion, a shell alias is refused
    ("an alias for a whole push", "git config alias.p 'push origin HEAD:master'", "git p", DENY),
    ("an alias for push, the refspec on the command", "git config alias.p push", "git p origin HEAD:master", DENY),
    ("an alias in the global config", "git config --global alias.p 'push origin HEAD:master'", "git p", DENY),
    ("an alias of an alias", "git config alias.a b; git config alias.b 'push origin HEAD:master'", "git a", DENY),
    ("an alias that forces", "git config alias.p 'push --force'; " + DIVERGE, "git p origin feature/x", DENY),
    ("an alias set with -c", "", "git -c alias.p=push p origin HEAD:master", DENY),
    ("an alias set in the environment", "", "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=alias.p GIT_CONFIG_VALUE_0='push origin HEAD:master' git p", DENY),
    ("an alias under a moved HOME", "", "HOME=../althome git p", DENY),
    ("an alias for commit, skipping the hook", "git config alias.ci 'commit -q'", "git ci --allow-empty -m bypass --no-verify", DENY),
    ("a shell alias", "git config alias.pf '!git push origin HEAD:master'", "git pf", DENY),
    ("a shell alias with a setting on the command", "git config alias.p '!git push'", "git -c remote.origin.push=HEAD:master p", DENY),
    ("a shell alias made a mirror by -c", "git config alias.p '!git push'; " + DIVERGE, "git -c remote.origin.mirror=true p", DENY),
    ("a shell alias for commit, the hooks path moved by -c", "git config alias.ci '!git commit'", "git -c core.hooksPath=/nonexistent-hooks ci -q --allow-empty -m bypass", DENY),
    ("an alias for an ordinary push", "git config alias.pu 'push -u origin'", "git pu feature/x", ALLOW),
    ("an alias for commit, the hook in play", "git config alias.ci 'commit -q'", "git ci --allow-empty -m bypass", ALLOW),
    # (rows for the next rule go above this line)
]


def run(script, cwd, env, check=True):
    result = subprocess.run(["bash", "-c", script], cwd=cwd, env=env, capture_output=True, text=True, timeout=60)
    if check and result.returncode:
        raise RuntimeError("fixture step failed: {}\n{}{}".format(script, result.stdout, result.stderr))
    return result


def environment_for(root):
    """The host's environment without its git settings, and a home of the fixture's own."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in ("XDG_CONFIG_HOME", "CDPATH")}
    env.update(HOME=os.path.join(root, "home"), GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
    return env


def build(root):
    """Two bare remotes; `work` on feature/x with local master and main ahead; `work2` on master.
    A commit-msg hook refuses any message holding the word `bypass`. Every path in the fixture's
    configuration is relative, so a copy of the tree works as the original does."""
    os.makedirs(os.path.join(root, "home"))
    os.makedirs(os.path.join(root, "hooks"))
    hook = os.path.join(root, "hooks", "commit-msg")
    with open(hook, "w") as handle:
        handle.write("#!/bin/sh\nif grep -q bypass \"$1\"; then echo hook-fired >&2; exit 1; fi\n")
    os.chmod(hook, 0o755)
    run(
        """
        git config --global user.name Test && git config --global user.email {email}
        git config --global init.defaultBranch master && git config --global commit.gpgsign false
        git config --global core.hooksPath ../hooks
        git init -q --bare remote.git && git init -q --bare other.git
        git init -q seed && cd seed && git commit -q --allow-empty -m 'chore: c0'
        git branch main && git branch develop && git branch feature/x
        git push -q ../remote.git master main develop feature/x && git push -q ../other.git master main develop
        cd .. && git clone -q remote.git work && cd work && git remote set-url origin ../remote.git
        git remote add other ../other.git && git fetch -q other && git branch -q main origin/main
        git commit -q --allow-empty -m 'chore: m1 on master'
        git checkout -q main && git commit -q --allow-empty -m 'chore: n1 on main'
        git checkout -q -b feature/x origin/feature/x && git commit -q --allow-empty -m 'feat: f1' && git tag v1
        cd .. && git clone -q remote.git work2 && cd work2 && git remote set-url origin ../remote.git
        git commit -q --allow-empty -m 'chore: w2 on master'
        mkdir ../althome && git config --file ../althome/.gitconfig user.name Test
        git config --file ../althome/.gitconfig user.email {email}
        git config --file ../althome/.gitconfig push.default matching
        git config --file ../althome/.gitconfig alias.p 'push origin HEAD:master'
        git config --file ../matching.cfg push.default matching
        git config --file ../upstream.inc push.default upstream
        """.format(email=guard_git.AUTHOR_EMAIL),
        root,
        environment_for(root),
    )


def refs(root, env):
    """Every ref of both bare remotes, by name."""
    found = {}
    for remote in ("remote.git", "other.git"):
        listing = run("git -C {} for-each-ref --format='%(refname) %(objectname)'".format(remote), root, env).stdout
        for line in listing.splitlines():
            name, oid = line.split()
            found[remote + ":" + name] = oid
    return found


def harm(root, env, before, after):
    """What the call did that no allowed call may do: move a release branch, delete or rewind a
    ref, or make a commit the commit-msg hook refuses."""
    done = []
    for name, old in sorted(before.items()):
        new = after.get(name)
        remote, ref = name.split(":", 1)
        if new is None:
            done.append("deleted " + name)
        elif new != old and ref in ("refs/heads/master", "refs/heads/main"):
            done.append("moved " + name)
        elif new != old and run("git -C {} merge-base --is-ancestor {} {}".format(remote, old, new), root, env, check=False).returncode:
            done.append("rewound " + name)
    done += ["created " + name for name in sorted(set(after) - set(before)) if name.split(":", 1)[1] in ("refs/heads/master", "refs/heads/main")]
    for clone in ("work", "work2"):
        if "bypass" in run("git -C {} log --all --format=%s".format(clone), root, env).stdout:
            done.append("committed past the hook in " + clone)
    return done


class PushDifferentialTest(unittest.TestCase):
    rows = ROWS

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = os.path.realpath(cls.tmp.name)  # a call may name the fixture by absolute path
        cls.template = os.path.join(cls.base, "template")
        os.makedirs(cls.template)
        build(cls.template)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def outcome(self, index, setup, command, earlier=None):
        """The guard's reason for the call (None when it passes) and the harm running it did; with
        `earlier`, another version of the guard, its reason for the same call comes first."""
        root = os.path.join(self.base, "row-{}".format(index))
        shutil.copytree(self.template, root, symlinks=True)
        try:
            env = environment_for(root)
            work = os.path.join(root, "work")
            command = command.replace("{root}", root)
            if setup:
                run(setup.replace("{root}", root), work, env)
            before = refs(root, env)
            with mock.patch.dict(os.environ, env, clear=True):
                reason = guard_git.check_command(command, work)
                was = earlier.check_command(command, work) if earlier else None
            run(command, work, env, check=False)
            done = harm(root, env, before, refs(root, env))
            return (was, reason, done) if earlier else (reason, done)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_the_verdict_matches_what_git_does(self):
        for index, (name, setup, command, verdict) in enumerate(self.rows):
            with self.subTest(name=name, command=command):
                reason, done = self.outcome(index, setup, command)
                if verdict == ALLOW:
                    self.assertIsNone(reason, "an ordinary call was refused")
                else:
                    self.assertIsNotNone(reason, "passed the guard; running it: {}".format(", ".join(done) or "no harm on this fixture"))
                if reason is None:
                    self.assertEqual(done, [], "the guard allowed a call that did harm")

    def test_nothing_an_earlier_guard_refused_is_admitted_with_harm(self):
        """With AWA_GUARD_BASE naming an earlier guard_git.py (`git show <commit>:hooks/claude-code/
        guard_git.py`, saved to a file), a row that guard refused and this one admits must do no
        harm when run: the guard is loosened only where a row proves the shape harmless."""
        path = os.environ.get("AWA_GUARD_BASE")
        if not path:
            self.skipTest("set AWA_GUARD_BASE to an earlier guard_git.py to compare against it")
        spec = importlib.util.spec_from_file_location("guard_git_base", path)
        earlier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(earlier)
        loosened = []
        for index, (name, setup, command, _verdict) in enumerate(self.rows):
            was, reason, done = self.outcome("base-{}".format(index), setup, command, earlier)
            if was is not None and reason is None:
                loosened.append(name)
                with self.subTest(name=name, command=command):
                    self.assertEqual(done, [], "refused before, admitted now, and it did harm")
        print("\nrefused by the earlier guard and admitted now (each harmless when run): {}".format("; ".join(loosened) or "none"), file=sys.stderr)

    def test_the_fixture_can_show_harm(self):
        """The instrument's positive control: each kind of harm registers when it happens."""
        for index, (setup, command, expected) in enumerate((
            ("", "git push origin HEAD:master", "moved remote.git:refs/heads/master"),
            (DIVERGE, "git push --force origin feature/x", "rewound remote.git:refs/heads/feature/x"),
            ("", "git push origin :develop", "deleted remote.git:refs/heads/develop"),
            ("", "git commit -q --allow-empty -m bypass --no-verify", "committed past the hook in work"),
        )):
            with self.subTest(command=command):
                _reason, done = self.outcome("control-{}".format(index), setup, command)
                self.assertIn(expected, done)


if __name__ == "__main__":
    unittest.main()
