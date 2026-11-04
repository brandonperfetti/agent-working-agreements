#!/usr/bin/python3
"""Tests for install.py and agreements_after_compact.py. Run: /usr/bin/python3 test_install.py"""
import contextlib
import io
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import install  # noqa: E402

OTHER_SETTINGS = {
    "theme": "dark",
    "includeCoAuthoredBy": False,
    "hooks": {
        "PreToolUse": [
            {"matcher": "Edit", "hooks": [{"type": "command", "command": "echo edit"}]},
        ],
        "Stop": [{"hooks": [{"type": "command", "command": "say done"}]}],
    },
}


def commands(settings, event):
    return [h["command"] for g in settings["hooks"].get(event, []) for h in g["hooks"]]


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.claude = self.tmp.name
        self.settings_path = os.path.join(self.claude, "settings.json")

    def tearDown(self):
        self.tmp.cleanup()

    def run_install(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = install.main(["--claude-dir", self.claude] + list(args))
        return code, out.getvalue()

    def write_settings(self, settings):
        with open(self.settings_path, "w") as handle:
            json.dump(settings, handle, indent=2)

    def read_settings(self):
        with open(self.settings_path) as handle:
            return json.load(handle)

    def test_fresh_install_copies_and_registers(self):
        self.assertEqual(self.run_install()[0], 0)
        for script in ("guard_git.py", "agreements_after_compact.py", "look_again.py"):
            self.assertTrue(os.path.exists(os.path.join(self.claude, "hooks", script)))
        settings = self.read_settings()
        self.assertEqual(settings["hooks"]["PreToolUse"][0]["matcher"], "Bash")
        self.assertEqual(settings["hooks"]["PreToolUse"][0]["hooks"][0]["onFailure"], "block")
        self.assertEqual(settings["hooks"]["SessionStart"][0]["matcher"], "compact")
        self.assertNotIn("matcher", settings["hooks"]["Stop"][0])
        self.assertIn("look_again.py", settings["hooks"]["Stop"][0]["hooks"][0]["command"])
        self.assertEqual(self.run_install("--check")[0], 0)

    def test_a_custom_claude_dir_registers_its_own_hooks(self):
        self.run_install()
        command = self.read_settings()["hooks"]["Stop"][0]["hooks"][0]["command"]
        script = os.path.join(os.path.abspath(self.claude), "hooks", "look_again.py")
        self.assertEqual(shlex.split(command), ["/usr/bin/python3", "-I", script])
        self.assertIn('"$HOME/.claude/hooks/look_again.py"', install.hook_entry("look_again.py", {})["command"])

    def test_keeps_other_settings_and_hooks(self):
        self.write_settings(OTHER_SETTINGS)
        self.run_install()
        settings = self.read_settings()
        self.assertEqual(settings["theme"], "dark")
        self.assertIs(settings["includeCoAuthoredBy"], False)
        self.assertIn("echo edit", commands(settings, "PreToolUse"))
        self.assertEqual(commands(settings, "Stop")[0], "say done")
        self.assertIn("look_again.py", commands(settings, "Stop")[1])
        self.assertEqual(len(settings["hooks"]["Stop"]), 1, "joins the existing matcherless group")
        backups = [name for name in os.listdir(self.claude) if ".bak-" in name]
        self.assertEqual(len(backups), 1)

    def test_rerun_registers_once(self):
        self.write_settings(OTHER_SETTINGS)
        self.run_install()
        first = self.read_settings()
        code, out = self.run_install()
        self.assertEqual((code, self.read_settings()), (0, first))
        self.assertIn("Already installed", out)
        guards = [c for c in commands(first, "PreToolUse") if "guard_git.py" in c]
        self.assertEqual(len(guards), 1)

    def test_existing_entry_is_updated_in_place(self):
        stale = {"type": "command", "command": "python3 ~/.claude/hooks/guard_git.py"}
        self.write_settings({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [stale]}]}})
        self.run_install()
        hooks = self.read_settings()["hooks"]["PreToolUse"]
        self.assertEqual(len(hooks), 1)
        hooks_dir = os.path.join(self.claude, "hooks")
        self.assertEqual(hooks[0]["hooks"], [install.hook_entry("guard_git.py", install.HOOKS[0][3], hooks_dir)])

    def test_a_hook_whose_name_ends_in_ours_is_left_alone(self):
        theirs = {"type": "command", "command": "python3 ~/bin/my_guard_git.py --strict"}
        self.write_settings({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [theirs]}]}})
        self.run_install()
        self.assertEqual(self.read_settings()["hooks"]["PreToolUse"][0]["hooks"][0], theirs)
        self.assertEqual(len(commands(self.read_settings(), "PreToolUse")), 2)

    def test_a_hook_that_only_names_our_script_is_left_alone(self):
        theirs = [
            {"type": "command", "command": "echo guard_git.py"},
            {"type": "command", "command": "python3 -c 'print(\"guard_git.py\")'"},
            {"type": "command", "command": "python3 ~/bin/lint.py guard_git.py"},
        ]
        self.write_settings({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": list(theirs)}]}})
        self.run_install()
        hooks = self.read_settings()["hooks"]["PreToolUse"][0]["hooks"]
        self.assertEqual(hooks[:3], theirs)
        self.assertEqual(len(hooks), 4)

    def test_runs_script_reads_the_executed_script(self):
        for command, runs in (
            ('/usr/bin/python3 -I "$HOME/.claude/hooks/guard_git.py"', True),
            ("python3 ~/.claude/hooks/guard_git.py", True),
            ("python3 -W ignore -I guard_git.py", True),
            ("~/.claude/hooks/guard_git.py", True),
            ("echo guard_git.py", False),
            ("python3 -m guard_git.py", False),
            ("python3 ~/bin/my_guard_git.py", False),
            ("python-lint guard_git.py", False),
            ("python3 'unbalanced", False),
        ):
            with self.subTest(command=command):
                self.assertEqual(install.runs_script(command, "guard_git.py"), runs)

    def test_settings_symlink_is_written_through(self):
        target = os.path.join(self.claude, "dotfiles-settings.json")
        with open(target, "w") as handle:
            json.dump({"theme": "dark"}, handle)
        os.symlink(target, self.settings_path)
        self.run_install()
        self.assertTrue(os.path.islink(self.settings_path))
        with open(target) as handle:
            self.assertIn("PreToolUse", json.load(handle)["hooks"])

    def test_a_linked_hook_copy_is_replaced_not_written_through(self):
        clone = os.path.join(self.claude, "clone-guard_git.py")
        with open(clone, "w") as handle:
            handle.write("# a clone's tracked file\n")
        os.makedirs(os.path.join(self.claude, "hooks"))
        os.symlink(clone, os.path.join(self.claude, "hooks", "guard_git.py"))
        self.run_install()
        self.assertFalse(os.path.islink(os.path.join(self.claude, "hooks", "guard_git.py")))
        with open(clone) as handle:
            self.assertEqual(handle.read(), "# a clone's tracked file\n")

    def test_unexpected_shape_is_left_alone(self):
        for settings in (
            [],
            {"hooks": None},
            {"hooks": {"PreToolUse": {}}},
            {"hooks": {"PreToolUse": ["x"]}},
            {"hooks": {"PreToolUse": [{"hooks": None}]}},
            {"hooks": {"PreToolUse": [{"hooks": [{"command": None}]}]}},
        ):
            with self.subTest(settings=settings):
                self.write_settings(settings)
                with self.assertRaises(SystemExit):
                    self.run_install()
                self.assertEqual(self.read_settings(), settings)

    def test_non_ascii_is_kept_as_written(self):
        self.write_settings({"note": "café →"})
        self.run_install()
        with open(self.settings_path, encoding="utf-8") as handle:
            self.assertIn("café →", handle.read())

    def test_dry_run_and_check_write_nothing(self):
        self.write_settings(OTHER_SETTINGS)
        before = self.read_settings()
        self.assertEqual(self.run_install("--dry-run")[0], 0)
        self.assertEqual(self.run_install("--check")[0], 1)
        self.assertEqual(self.read_settings(), before)
        self.assertFalse(os.path.exists(os.path.join(self.claude, "hooks")))

    def test_check_sees_an_edited_copy(self):
        self.run_install()
        with open(os.path.join(self.claude, "hooks", "guard_git.py"), "a") as handle:
            handle.write("# local edit\n")
        code, out = self.run_install("--check")
        self.assertEqual(code, 1)
        self.assertIn("guard_git.py", out)

    def test_invalid_settings_are_left_alone(self):
        with open(self.settings_path, "w") as handle:
            handle.write("{not json")
        with self.assertRaises(SystemExit):
            self.run_install()
        with open(self.settings_path) as handle:
            self.assertEqual(handle.read(), "{not json")

    def test_settings_mode_is_kept(self):
        self.write_settings(OTHER_SETTINGS)
        os.chmod(self.settings_path, 0o600)
        self.run_install()
        self.assertEqual(os.stat(self.settings_path).st_mode & 0o777, 0o600)


class CompactHookTest(unittest.TestCase):
    def test_restates_rule_zero(self):
        script = os.path.join(HERE, "agreements_after_compact.py")
        out = subprocess.run(
            ["/usr/bin/python3", "-I", script], capture_output=True, text=True, check=True
        ).stdout
        output = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "SessionStart")
        self.assertIn("brandon@brandonperfetti.com", output["additionalContext"])


if __name__ == "__main__":
    unittest.main()
