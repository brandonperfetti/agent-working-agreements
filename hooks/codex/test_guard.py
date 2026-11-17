#!/usr/bin/python3
"""Tests for the Codex guard hook and its installer. Run: /usr/bin/python3 -m unittest discover -s hooks/codex"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

HERE = os.path.dirname(os.path.abspath(__file__))
CLAUDE = os.path.join(os.path.dirname(HERE), "claude-code")
sys.path.insert(0, HERE)
sys.path.insert(1, CLAUDE)
import guard  # noqa: E402
import install  # noqa: E402
from test_guard_git import BLOCKED_ANYWHERE  # noqa: E402  the guard's own table, not a second copy

REAL_GUARD = os.path.join(CLAUDE, "guard_git.py")
ROUTE = ("gh pr merge 7 --repo o/r --merge --match-head-commit " + "a" * 40
         + " --author-email brandon@brandonperfetti.com")
DENY = json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                          "permissionDecisionReason": "Blocked by ~/.claude/hooks/guard_git.py: this is x."}})


def payload(command, cwd=None):
    """Codex's PreToolUse input, as measured on 0.169.0."""
    return json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                       "tool_input": {"command": command}, "cwd": cwd or tempfile.gettempdir()})


class Stubs(unittest.TestCase):
    """The wrapper against stand-in guards: every outcome but a clean pass denies."""

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="awa-codex-guard-")
        self.addCleanup(shutil.rmtree, self.dir, True)

    def stub(self, body):
        path = os.path.join(self.dir, "stub.py")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(body)
        return path

    def test_clean_pass_allows(self):
        self.assertIsNone(guard.decide(payload("ls"), guard=self.stub("")))

    def test_the_guard_gets_the_whole_command_and_the_directory(self):
        seen = os.path.join(self.dir, "seen.json")
        stub = self.stub("import sys\nopen({!r}, 'w').write(sys.stdin.read())\n".format(seen))
        command = "cd x && git push origin 'a b' # tail"
        self.assertIsNone(guard.decide(payload(command, self.dir), guard=stub))
        with open(seen, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle), {"tool_input": {"command": command}, "cwd": self.dir})

    def test_a_denial_carries_the_guards_reason(self):
        stub = self.stub("print({!r})\n".format(DENY))
        self.assertEqual(guard.decide(payload("x"), guard=stub), "Blocked by {}: this is x.".format(stub))

    def test_every_other_outcome_denies(self):
        cases = {
            "exit 1": "import sys\nsys.exit(1)\n",
            "exit 2": "import sys\nsys.exit(2)\n",
            "a traceback": "raise RuntimeError('boom')\n",
            "not JSON": "print('{not json')\n",
            "an empty object": "print('{}')\n",
            "an allow": "print('{\"hookSpecificOutput\": {\"permissionDecision\": \"allow\"}}')\n",
            "a deny with no reason": "print('{\"hookSpecificOutput\": {\"permissionDecision\": \"deny\"}}')\n",
            "a deny with an empty reason": "print('{\"hookSpecificOutput\": {\"permissionDecision\": \"deny\", \"permissionDecisionReason\": \"\"}}')\n",
            "a deny with a blank reason": "print('{\"hookSpecificOutput\": {\"permissionDecision\": \"deny\", \"permissionDecisionReason\": \" \\\\n\"}}')\n",
            "plain text": "print('ok')\n",
        }
        for name, body in cases.items():
            with self.subTest(name):
                self.assertIn("hand it back", guard.decide(payload("x"), guard=self.stub(body)))

    def test_only_none_is_a_pass_when_the_decision_is_printed(self):
        for reason in ("", "x"):
            with self.subTest(reason), unittest.mock.patch.object(guard, "decide", return_value=reason), \
                    unittest.mock.patch.object(sys, "stdin", io.StringIO("{}")):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    guard.main()
                decision = json.loads(out.getvalue())["hookSpecificOutput"]
                self.assertEqual(decision["permissionDecision"], "deny")
                self.assertTrue(decision["permissionDecisionReason"].startswith("awa-guard-codex: " + (reason or "denied")))

    def test_a_missing_guard_and_a_missing_interpreter_deny(self):
        self.assertIn("the guard exited", guard.decide(payload("x"), guard=os.path.join(self.dir, "absent.py")))
        self.assertIn("could not run", guard.decide(payload("x"), guard=self.stub(""), python=os.path.join(self.dir, "no-python")))

    def test_a_slow_guard_denies_at_the_timeout(self):
        stub = self.stub("import time\ntime.sleep(5)\n")
        self.assertIn("timed out", guard.decide(payload("x"), guard=stub, timeout=0.2))

    def test_input_the_hook_cannot_read_denies(self):
        stub = self.stub("")
        for raw in ("", "not json", "[]", "{}", json.dumps({"tool_input": {}}),
                    json.dumps({"tool_input": {"command": ["gh", "pr", "merge"]}}),
                    json.dumps({"tool_input": "gh pr merge"})):
            with self.subTest(raw):
                self.assertIn("hand it back", guard.decide(raw, guard=stub))

    def test_without_a_directory_the_guard_runs_outside_any_repository(self):
        stub = self.stub("import os, sys\nsys.exit(0 if os.environ.get('GIT_CEILING_DIRECTORIES') and os.getcwd() == os.path.realpath({!r}) else 1)\n".format(self.dir))
        for cwd in (None, "relative/path", os.path.join(self.dir, "absent")):
            with self.subTest(cwd):
                raw = json.dumps({"tool_input": {"command": "git status"}, "cwd": cwd})
                self.assertIsNone(guard.decide(raw, guard=stub, no_repo_dir=self.dir))


class Installed(unittest.TestCase):
    """The installed layout, run as Codex runs it: the real guard beside the wrapper."""

    @classmethod
    def setUpClass(cls):
        cls.home = tempfile.mkdtemp(prefix="awa-codex-home-")
        cls.addClassCleanup(shutil.rmtree, cls.home, True)
        with contextlib.redirect_stdout(io.StringIO()):
            assert install.main(["--codex-dir", cls.home]) == 0
        cls.script = os.path.join(cls.home, install.FOLDER, "guard.py")
        cls.outside = tempfile.mkdtemp(prefix="awa-codex-norepo-")
        cls.addClassCleanup(shutil.rmtree, cls.outside, True)

    def run_hook(self, raw, script=None):
        return subprocess.run(["/usr/bin/python3", "-I", script or self.script], input=raw,
                              capture_output=True, text=True, timeout=60)

    def denied(self, command):
        result = self.run_hook(payload(command, self.outside))
        self.assertEqual(result.returncode, 0, result.stderr)
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual((decision["hookEventName"], decision["permissionDecision"]), ("PreToolUse", "deny"))
        self.assertTrue(decision["permissionDecisionReason"].startswith("awa-guard-codex: "))
        return decision["permissionDecisionReason"]

    def test_a_read_passes_in_silence(self):
        result = self.run_hook(payload("git status", self.outside))
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_the_canary_is_refused_with_the_mark_and_the_installed_path(self):
        reason = self.denied("gh pr merge --help")
        self.assertIn("this is a PR merge", reason)
        self.assertIn(os.path.join(self.home, install.FOLDER, "guard_git.py"), reason)

    def test_the_guards_own_table_is_refused(self):
        for command in BLOCKED_ANYWHERE:
            with self.subTest(command):
                self.denied(command)

    def test_merges_the_guard_refuses_without_a_lookup(self):
        for command, expected in [
            (ROUTE + " --auto", "an auto-merge"),
            ("cd /tmp && " + ROUTE, "cannot read word for word"),
            (ROUTE + " | cat", "cannot read word for word"),
            ('gh api graphql -f query="mutation { mergePullRequest(input: {}) { clientMutationId } }"', "a PR merge"),
        ]:
            with self.subTest(command):
                self.assertIn(expected, self.denied(command))

    def test_a_guard_that_went_missing_denies(self):
        home = tempfile.mkdtemp(prefix="awa-codex-broken-")
        self.addCleanup(shutil.rmtree, home, True)
        with contextlib.redirect_stdout(io.StringIO()):
            install.main(["--codex-dir", home])
        os.unlink(os.path.join(home, install.FOLDER, "guard_git.py"))
        result = self.run_hook(payload("git status", self.outside), os.path.join(home, install.FOLDER, "guard.py"))
        self.assertIn("awa-guard-codex: the guard exited", json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"])

    def test_a_crash_in_the_hook_itself_exits_2_with_a_reason(self):
        broken = os.path.join(self.outside, "broken.py")
        with open(self.script, encoding="utf-8") as handle:
            source = handle.read().replace("    reason = decide(sys.stdin.read())", "    raise RuntimeError('boom')")
        self.assertIn("raise RuntimeError('boom')", source)
        with open(broken, "w", encoding="utf-8") as handle:
            handle.write(source)
        result = self.run_hook(payload("git status"), broken)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.startswith("awa-guard-codex: the hook failed"))


class RouteForm(unittest.TestCase):
    """The delegated route's cases through the installed hook, with a stand-in `gh` answering the
    guard's base read. The fixture runs repeat them against GitHub."""

    @classmethod
    def setUpClass(cls):
        cls.home = tempfile.mkdtemp(prefix="awa-codex-route-")
        cls.addClassCleanup(shutil.rmtree, cls.home, True)
        with contextlib.redirect_stdout(io.StringIO()):
            assert install.main(["--codex-dir", cls.home]) == 0
        cls.script = os.path.join(cls.home, install.FOLDER, "guard.py")
        cls.bin = os.path.join(cls.home, "bin")
        os.mkdir(cls.bin)
        with open(os.path.join(cls.bin, "gh"), "w", encoding="utf-8") as handle:
            handle.write('#!/bin/sh\necho "${FAKE_BASE:-develop}"\n')
        os.chmod(os.path.join(cls.bin, "gh"), 0o755)

    def verdict(self, command, base="develop"):
        env = dict(os.environ, PATH=self.bin + os.pathsep + os.environ.get("PATH", ""), FAKE_BASE=base)
        result = subprocess.run(["/usr/bin/python3", "-I", self.script], input=payload(command, self.home),
                                capture_output=True, text=True, timeout=60, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        if not result.stdout:
            return None
        return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]

    def test_the_one_form_into_develop_is_admitted(self):
        self.assertIsNone(self.verdict(ROUTE))

    def test_a_merge_between_feature_branches_passes(self):
        self.assertIsNone(self.verdict("gh pr merge 7 --squash", base="wave-3"))

    def test_every_other_form_is_refused(self):
        sha = "a" * 40
        for command, base, expected in [
            (ROUTE.replace("brandon@brandonperfetti.com", "someone-else@example.com"), "develop", "another author email"),
            (ROUTE + " --squash", "develop", "--squash, which the route does not use"),
            (ROUTE + " --admin", "develop", "--admin, which the route does not use"),
            (ROUTE.replace(" --match-head-commit " + sha, ""), "develop", "exactly once"),
            (ROUTE.replace(sha, sha[:7]), "develop", "not a full lowercase SHA"),
            (ROUTE + " --delete-branch", "develop", "--delete-branch, which the route does not use"),
            (ROUTE, "master", "a PR merge into master"),
            (ROUTE, "main", "a PR merge into main"),
            ("gh api -X PUT repos/o/r/pulls/7/merge", "develop", "a PR merge into develop"),
            (ROUTE + " 2>&1", "develop", "not a plain command on its own"),
            ("/opt/homebrew/bin/" + ROUTE, "develop", "not a plain command on its own"),
        ]:
            with self.subTest(command=command, base=base):
                reason = self.verdict(command, base)
                self.assertTrue(reason and reason.startswith("awa-guard-codex: "), reason)
                self.assertIn(expected, reason)


class Installer(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="awa-codex-install-")
        self.addCleanup(shutil.rmtree, self.home, True)
        self.hooks = os.path.join(self.home, "hooks.json")

    def run_install(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = install.main(["--codex-dir", self.home] + list(args))
        return code, out.getvalue()

    def read(self):
        with open(self.hooks, encoding="utf-8") as handle:
            return json.load(handle)

    def test_install_copies_both_files_registers_once_and_check_agrees(self):
        self.assertEqual(self.run_install("--check")[0], 1)
        self.assertEqual(self.run_install("--dry-run")[0], 0)
        self.assertFalse(os.path.exists(self.hooks))
        self.assertEqual(self.run_install()[0], 0)
        for name, source in install.SOURCES.items():
            with open(source, "rb") as a, open(os.path.join(self.home, install.FOLDER, name), "rb") as b:
                self.assertEqual(a.read(), b.read())
        group, = self.read()["hooks"]["PreToolUse"]
        self.assertEqual(group["matcher"], "Bash")
        hook, = group["hooks"]
        self.assertEqual((hook["type"], hook["timeout"]), ("command", 30))
        self.assertGreater(hook["timeout"], guard.TIMEOUT)
        self.assertEqual(self.run_install("--check")[0], 0)
        self.assertEqual(self.run_install(), (0, "Already installed.\n"))

    def test_the_default_home_is_named_through_HOME(self):
        self.assertEqual(install.hook_entry()["command"], '/usr/bin/python3 -I "$HOME/.codex/hooks/awa-guard/guard.py"')

    def test_install_only_adds_and_every_other_entry_is_left_as_it_was(self):
        ours = install.hook_entry(self.home)["command"]
        script = ours.split()[-1]
        others = [{"type": "command", "command": command} for command in (
            "echo other",
            "/usr/bin/python3 -I /old/hooks/awa-guard/guard.py",  # an older copy: never removed
            "/usr/bin/python3 /opt/audit_hook.py --watch hooks/awa-guard/guard.py",
            "/usr/bin/python3 -I '-cprint(1)' " + script,
            "/usr/bin/python3 -I /opt/audit.py<" + script,
            "/usr/bin/python3 -I /opt/audit.py;#" + script,
            ours + " ",  # one byte off is another command
            'echo "$HOME/.codex/hooks/awa-guard/guard.py" changed',
        )]
        before = {"description": "mine", "hooks": {
            "Stop": [{"hooks": others[:1]}, {"hooks": []}],
            "PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": ours}]}],
            "PreToolUse": [{"matcher": "apply_patch", "hooks": others[1:2]}, {"matcher": "Bash", "hooks": list(others)},
                           {"matcher": "Bash", "hooks": others[:1]}],
        }}
        with open(self.hooks, "w", encoding="utf-8") as handle:
            json.dump(before, handle)
        self.assertEqual(self.run_install()[0], 0)
        after = self.read()
        expected = json.loads(json.dumps(before))
        expected["hooks"]["PreToolUse"][1]["hooks"].append(install.hook_entry(self.home))  # the one addition
        self.assertEqual(after, expected)
        self.assertEqual(len([name for name in os.listdir(self.home) if name.startswith("hooks.json.bak-")]), 1)
        self.assertEqual(self.run_install("--check")[0], 0)
        self.assertEqual(self.run_install(), (0, "Already installed.\n"))
        self.assertEqual(self.read(), expected)

    def test_an_entry_with_our_command_and_other_settings_is_reported_not_rewritten(self):
        ours = install.hook_entry(self.home)
        for hooks in ([dict(ours, timeout=1)], [ours, ours], [dict(ours, statusMessage="x")]):
            with self.subTest(hooks=hooks):
                self.run_install()
                content = json.dumps({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": hooks}]}})
                with open(self.hooks, "w", encoding="utf-8") as handle:
                    handle.write(content)
                code, out = self.run_install("--check")
                self.assertEqual(code, 1)
                self.assertIn("edit it by hand", out)
                code, out = self.run_install()
                self.assertEqual(code, 0)
                self.assertIn("edit it by hand", out)
                self.assertNotIn("Already installed", out)
                with open(self.hooks, encoding="utf-8") as handle:
                    self.assertEqual(handle.read(), content)

    def test_our_command_under_another_matcher_or_event_does_not_count(self):
        ours = install.hook_entry(self.home)
        with open(self.hooks, "w", encoding="utf-8") as handle:
            json.dump({"hooks": {"PreToolUse": [{"matcher": "apply_patch", "hooks": [ours]}], "Stop": [{"hooks": [ours]}]}}, handle)
        self.assertEqual(self.run_install("--check")[0], 1)
        self.assertEqual(self.run_install()[0], 0)
        groups = self.read()["hooks"]["PreToolUse"]
        self.assertEqual(groups, [{"matcher": "apply_patch", "hooks": [ours]}, {"matcher": "Bash", "hooks": [ours]}])
        self.assertEqual(self.read()["hooks"]["Stop"], [{"hooks": [ours]}])

    def test_a_changed_byte_is_drift(self):
        self.run_install()
        with open(os.path.join(self.home, install.FOLDER, "guard_git.py"), "a", encoding="utf-8") as handle:
            handle.write("# drift\n")
        code, out = self.run_install("--check")
        self.assertEqual(code, 1)
        self.assertIn("guard_git.py", out)

    def test_a_hooks_file_changed_while_installing_is_left_as_the_other_writer_left_it(self):
        theirs = json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo theirs"}]}]}})
        real_merge = install.merge_hook

        def another_writer(config, codex_dir=None):  # runs after the installer has read hooks.json
            with open(self.hooks, "w", encoding="utf-8") as handle:
                handle.write(theirs)
            return real_merge(config, codex_dir)

        for before in (None, json.dumps({"hooks": {}})):  # a file that appears, and one that changes
            with self.subTest(before=before):
                shutil.rmtree(self.home)
                os.makedirs(self.home)
                if before is not None:
                    with open(self.hooks, "w", encoding="utf-8") as handle:
                        handle.write(before)
                with unittest.mock.patch.object(install, "merge_hook", side_effect=another_writer):
                    with self.assertRaises(SystemExit) as stop:
                        self.run_install()
                self.assertIn("changed", str(stop.exception))
                with open(self.hooks, encoding="utf-8") as handle:
                    self.assertEqual(handle.read(), theirs)
                self.assertEqual([name for name in os.listdir(self.home) if name.startswith(".install-")], [])
                self.assertEqual(self.run_install()[0], 0)  # a second run reads their file and adds to it
                self.assertEqual(self.read()["hooks"]["Stop"], json.loads(theirs)["hooks"]["Stop"])
                self.assertEqual(self.run_install("--check")[0], 0)

    def test_a_hooks_file_it_cannot_read_is_left_alone(self):
        for content in ("{not json", "[]", '{"hooks": []}', '{"hooks": {"PreToolUse": {}}}'):
            with self.subTest(content):
                with open(self.hooks, "w", encoding="utf-8") as handle:
                    handle.write(content)
                with self.assertRaises(SystemExit):
                    self.run_install()
                with open(self.hooks, encoding="utf-8") as handle:
                    self.assertEqual(handle.read(), content)


if __name__ == "__main__":
    unittest.main()
