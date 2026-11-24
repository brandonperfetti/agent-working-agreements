#!/usr/bin/python3
"""Tests of sealed_cases.py's own logic (#310), against temporary case folders and stub guards.

None of these is a sealed case: the sealed set lives outside the checkout and is read only by the
runner. Here the cases are made up for each test, and the guard is mostly a stub, so what is held is
the runner: one bare line per case, a non-zero exit on any failure, SEALED CASES NOT RUN when the
folder cannot be read, and the trigger that runs it on a change under hooks/.

Run: /usr/bin/python3 -m unittest hooks/claude-code/test_sealed_cases.py
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sealed_cases  # noqa: E402

STUBS = {
    "allow": "import sys\nsys.stdin.read()\n",
    "deny": ("import json, sys\nsys.stdin.read()\nprint(json.dumps({'hookSpecificOutput': {'hookEventName': "
             "'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': 'no'}}))\n"),
    "exit2": "import sys\nsys.stdin.read()\nsys.exit(2)\n",
    "crash": "import sys\nsys.stdin.read()\nraise SystemExit(1)\n",
    "garbage": "import sys\nsys.stdin.read()\nprint('not a decision')\n",
    # Refuses exactly the calls whose command holds the word `deny-me`; reads the cwd it was given.
    "words": ("import json, os, sys\np = json.load(sys.stdin)\nassert os.path.isdir(os.path.join(p['cwd'], '.git'))\n"
              "if 'deny-me' in p['tool_input']['command']:\n    print(json.dumps({'hookSpecificOutput': "
              "{'permissionDecision': 'deny'}}))\n"),
}


class Folder:
    """A temporary case folder and stub guards."""

    def __init__(self, test):
        tmp = tempfile.TemporaryDirectory()
        test.addCleanup(tmp.cleanup)
        self.root = os.path.realpath(tmp.name)
        self.cases = os.path.join(self.root, "cases")
        os.makedirs(self.cases)

    def case(self, cid, command, expected, setup="", name=None, **extra):
        with open(os.path.join(self.cases, name or cid + ".json"), "w") as handle:
            json.dump(dict(id=cid, command=command, expected=expected, setup=setup, **extra), handle)

    def stub(self, kind):
        path = os.path.join(self.root, kind + "_guard.py")
        with open(path, "w") as handle:
            handle.write(STUBS[kind])
        return path


def run(folder, guard):
    out = io.StringIO()
    status = sealed_cases.run_cases(folder, guard, out)
    return status, out.getvalue().splitlines()


class RunnerTest(unittest.TestCase):
    def test_every_case_passes_one_bare_line_each(self):
        f = Folder(self)
        f.case("b-refused", "git push deny-me", "refused")
        f.case("a-allowed", "git status", "allowed")
        self.assertEqual(run(f.cases, f.stub("words")), (0, ["PASS a-allowed", "PASS b-refused"]))

    def test_a_guard_that_allows_everything_fails(self):
        f = Folder(self)
        f.case("refused-one", "git push origin HEAD:master", "refused")
        f.case("allowed-one", "git status", "allowed")
        self.assertEqual(run(f.cases, f.stub("allow")),
                         (1, ["PASS allowed-one", "FAIL refused-one expected=refused got=allowed"]))

    def test_a_guard_that_refuses_everything_fails(self):
        f = Folder(self)
        f.case("allowed-one", "git status", "allowed")
        self.assertEqual(run(f.cases, f.stub("deny")), (1, ["FAIL allowed-one expected=allowed got=refused"]))

    def test_exit_two_is_a_refusal(self):
        f = Folder(self)
        f.case("refused-one", "git push", "refused")
        self.assertEqual(run(f.cases, f.stub("exit2")), (0, ["PASS refused-one"]))

    def test_a_crash_or_stray_output_is_an_error_no_case_expects(self):
        f = Folder(self)
        f.case("refused-one", "git push", "refused")
        for kind in ("crash", "garbage"):
            with self.subTest(kind=kind):
                self.assertEqual(run(f.cases, f.stub(kind)), (1, ["FAIL refused-one expected=refused got=error"]))

    def test_a_setup_that_fails_fails_its_case(self):
        f = Folder(self)
        f.case("bad-setup", "git status", "allowed", setup="false")
        self.assertEqual(run(f.cases, f.stub("allow")), (1, ["FAIL bad-setup expected=allowed got=setup-error"]))

    def test_root_is_the_fixture_and_gh_answers_nothing(self):
        f = Folder(self)
        f.case("root-and-gh", "git status", "allowed",
               setup="test -d {root}/work2 && test -d {root}/remote.git && ! gh auth status")
        self.assertEqual(run(f.cases, f.stub("allow")), (0, ["PASS root-and-gh"]))

    def test_the_real_guard(self):
        f = Folder(self)
        f.case("plain-status", "git status --short", "allowed")
        f.case("release-push", "git push origin HEAD:main", "refused")
        self.assertEqual(run(f.cases, sealed_cases.DEFAULT_GUARD), (0, ["PASS plain-status", "PASS release-push"]))


class NotRunTest(unittest.TestCase):
    def assertNotRun(self, folder, guard, reason):
        status, lines = run(folder, guard)
        self.assertEqual(status, 2)
        self.assertEqual(len(lines), 1, lines)
        self.assertTrue(lines[0].startswith("SEALED CASES NOT RUN: "), lines)
        self.assertIn(reason, lines[0])

    def test_a_missing_folder(self):
        f = Folder(self)
        self.assertNotRun(os.path.join(f.root, "absent"), f.stub("allow"), "does not exist")

    def test_a_file_in_place_of_the_folder(self):
        f = Folder(self)
        self.assertNotRun(f.stub("allow"), f.stub("allow"), "is not a folder")

    @unittest.skipIf(os.geteuid() == 0, "root reads any folder")
    def test_a_folder_that_cannot_be_read(self):
        f = Folder(self)
        f.case("one", "git status", "allowed")
        os.chmod(f.cases, 0)
        self.addCleanup(os.chmod, f.cases, 0o700)
        self.assertNotRun(f.cases, f.stub("allow"), "cannot be read")

    def test_an_empty_folder(self):
        f = Folder(self)
        self.assertNotRun(f.cases, f.stub("allow"), "holds no case files")

    def test_a_case_that_is_not_json(self):
        f = Folder(self)
        with open(os.path.join(f.cases, "broken.json"), "w") as handle:
            handle.write("{")
        self.assertNotRun(f.cases, f.stub("allow"), "broken.json cannot be read")

    def test_a_case_with_another_ruling(self):
        f = Folder(self)
        f.case("one", "git status", "maybe")
        self.assertNotRun(f.cases, f.stub("allow"), "not refused or allowed")

    def test_a_case_named_unlike_its_id(self):
        f = Folder(self)
        f.case("one", "git status", "allowed", name="two.json")
        self.assertNotRun(f.cases, f.stub("allow"), "the file name is not its id")

    def test_no_guard(self):
        f = Folder(self)
        f.case("one", "git status", "allowed")
        self.assertNotRun(f.cases, os.path.join(f.root, "absent.py"), "no guard at")


def git(cwd, *args, env=None):
    return subprocess.run(("git",) + args, cwd=cwd, env=env, capture_output=True, text=True, check=True)


class TriggerTest(unittest.TestCase):
    """The trigger in a scratch repository whose runner is a stand-in that says it ran."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = os.path.realpath(tmp.name)
        self.repo = os.path.join(root, "repo")
        os.makedirs(os.path.join(root, "home"))
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(HOME=os.path.join(root, "home"), GIT_CONFIG_NOSYSTEM="1")
        git(root, "init", "-q", "-b", "develop", "repo", env=self.env)
        for key, value in (("user.email", "a@example.com"), ("user.name", "A"), ("commit.gpgsign", "false")):
            git(self.repo, "config", key, value, env=self.env)
        self.runner = os.path.join(self.repo, "hooks", "claude-code", "sealed_cases.py")
        os.makedirs(os.path.dirname(self.runner))
        with open(self.runner, "w") as handle:
            handle.write("import sys\nprint('RUNNER RAN', ' '.join(sys.argv[1:]))\n")
        self.commit("README", "first")
        out = io.StringIO()
        self.assertEqual(sealed_cases.install_trigger(os.path.join(self.repo, ".git", "hooks"), out=out), 0)

    def commit(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "a") as handle:
            handle.write(text + "\n")
        git(self.repo, "add", "-A", env=self.env)
        result = git(self.repo, "commit", "-q", "-m", "chore: " + text, env=self.env)
        return result.stdout + result.stderr

    def test_a_commit_under_hooks_runs_the_runner(self):
        output = self.commit("hooks/claude-code/guard_git.py", "x")
        self.assertIn("post-commit: the change touches hooks/", output)
        self.assertIn("RUNNER RAN --guard " + os.path.join(self.repo, "hooks", "claude-code", "guard_git.py"), output)

    def test_a_commit_elsewhere_runs_nothing(self):
        self.assertEqual(self.commit("docs/note.md", "x"), "")

    def test_no_runner_says_so(self):
        os.remove(self.runner)
        self.assertIn("SEALED CASES NOT RUN: no runner at", self.commit("hooks/git/x", "x"))

    def test_a_merge_under_hooks_runs_the_runner(self):
        git(self.repo, "checkout", "-q", "-b", "feature", env=self.env)
        self.commit("hooks/git/x", "x")
        git(self.repo, "checkout", "-q", "develop", env=self.env)
        before = git(self.repo, "rev-parse", "HEAD", env=self.env).stdout.strip()
        for name, flags in (("a merge commit", ["--no-ff", "--no-edit"]), ("a fast-forward", ["--ff-only"])):
            with self.subTest(name):
                merged = git(self.repo, "merge", "-q", *flags, "feature", env=self.env)
                self.assertIn("post-merge: the change touches hooks/", merged.stdout + merged.stderr)
                self.assertIn("RUNNER RAN", merged.stdout + merged.stderr)
                git(self.repo, "reset", "-q", "--hard", before, env=self.env)

    def test_a_merge_elsewhere_runs_nothing(self):
        git(self.repo, "checkout", "-q", "-b", "feature", env=self.env)
        self.commit("docs/x.md", "x")
        git(self.repo, "checkout", "-q", "develop", env=self.env)
        merged = git(self.repo, "merge", "-q", "feature", env=self.env)
        self.assertNotIn("RUNNER RAN", merged.stdout + merged.stderr)


class InstallTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.hooks = tmp.name

    def install(self, mode="install"):
        out = io.StringIO()
        return sealed_cases.install_trigger(self.hooks, mode, out), out.getvalue()

    def test_install_check_and_update(self):
        self.assertEqual(self.install("check")[0], 1)
        self.assertEqual(self.install("dry-run"), (0, "".join(
            "{}: would install\n".format(os.path.join(self.hooks, n)) for n in sealed_cases.TRIGGER_HOOKS)))
        self.assertFalse(os.listdir(self.hooks))
        self.assertEqual(self.install()[0], 0)
        for name in sealed_cases.TRIGGER_HOOKS:
            path = os.path.join(self.hooks, name)
            self.assertTrue(os.access(path, os.X_OK))
            with open(path) as a, open(sealed_cases.TRIGGER) as b:
                self.assertEqual(a.read(), b.read())
        self.assertEqual(self.install("check")[0], 0)
        with open(os.path.join(self.hooks, "post-merge"), "a") as handle:
            handle.write("# drift\n")
        self.assertEqual(self.install("check")[0], 1)
        self.assertEqual(self.install()[0], 0)
        self.assertEqual(self.install("check")[0], 0)

    def test_a_hook_it_did_not_write_is_left_alone(self):
        theirs = os.path.join(self.hooks, "post-commit")
        with open(theirs, "w") as handle:
            handle.write("#!/bin/sh\necho theirs\n")
        status, output = self.install()
        self.assertEqual(status, 1)
        self.assertIn("not written by this installer", output)
        with open(theirs) as handle:
            self.assertEqual(handle.read(), "#!/bin/sh\necho theirs\n")
        self.assertTrue(os.path.isfile(os.path.join(self.hooks, "post-merge")))

    def test_the_trigger_source_is_marked_as_ours(self):
        with open(sealed_cases.TRIGGER) as handle:
            self.assertIn(sealed_cases.OWNED, handle.read())
        self.assertTrue(os.access(sealed_cases.TRIGGER, os.X_OK))


if __name__ == "__main__":
    unittest.main()
