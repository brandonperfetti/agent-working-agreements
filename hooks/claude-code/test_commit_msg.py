#!/usr/bin/python3
"""End-to-end tests for hooks/git/commit-msg: real `git commit`s in a scratch repository whose
`core.hooksPath` is this repository's hooks/git folder. Kept beside the Claude Code hook tests so
the one `unittest discover` of the CI gate runs them."""
import importlib.machinery
import importlib.util
import os
import shlex
import subprocess
import tempfile
import unittest
from unittest import mock

import guard_git

HOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "git")
AUTHOR_EMAIL = "brandon@brandonperfetti.com"
OTHER = "someone@example.com"
TRAILER = "Co-Authored-By: Claude <noreply@anthropic.com>"
DECLARED = "Agent: Claude Code \u00b7 claude-opus-5-5 \u00b7 medium"
BANNED_WORDS = "Co-Authored-By, session or chat link, or generated-with"


def load_commit_msg():
    """The hook as a module: it has no .py suffix, so the loader is named."""
    path = os.path.join(HOOKS_DIR, "commit-msg")
    loader = importlib.machinery.SourceFileLoader("commit_msg_hook", path)
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module


# (message, the verdict's start or None): one table for both copies of the check.
DECLARATION_CASES = (
    ("fix: x", None),
    ("fix: x\n\n" + DECLARED, None),
    ("fix: x\n\nReviewed-by: B <b@c>\n" + DECLARED, None),
    ("fix: x\n\nAgent: Camina (OpenClaw) \u00b7 gpt-5.5", None),
    ("fix: x\n\nAgent: Camina (OpenClaw) \u00b7 gpt-5.5 \u00b7 high", None),
    ("fix: x\n\nAgent: Codex \u00b7 gpt-6.1-sol", "an Agent: line reads exactly"),  # only OpenClaw omits the effort
    ("fix: x\n\nAgent: Claude Code \u00b7 claude-opus-5-5 (requested)", "an Agent: line reads exactly"),
    ("fix: x\n\nAgent: Codex \u00b7 gpt-5.5-codex (requested) \u00b7 high", None),
    ("fix: x\n\nAgent: Claude Code \u00b7 claude-opus-5-5[1m] \u00b7 xhigh (requested)", None),
    ("fix: x\n\n" + DECLARED + "  ", None),  # trailing blanks are not shape
    ("fix: x\n\nagents: two of them", None),  # a word, not the key
    ("fix: x\n\n" + DECLARED + "\n" + DECLARED, "one Agent: line per commit, not 2"),
    ("fix: x\n\n" + DECLARED + "\n\n# " + DECLARED, "one Agent: line per commit, not 2"),
    ("fix: x\n\nAgent: Claude Code", "an Agent: line reads exactly"),
    ("fix: x\n\nagent: Claude Code \u00b7 claude-opus-5-5 \u00b7 medium", "an Agent: line reads exactly"),
    ("fix: x\n\nAgent:Claude Code \u00b7 claude-opus-5-5 \u00b7 medium", "an Agent: line reads exactly"),
    ("fix: x\n\nAgent: Claude Code - claude-opus-5-5 - medium", "an Agent: line reads exactly"),
    ("fix: x\n\nAgent: Claude Code \u00b7 claude opus \u00b7 medium", "an Agent: line reads exactly"),
    ("fix: x\n\nAgent: Claude Code \u00b7 claude-opus-5-5 \u00b7 medium \u00b7 extra", "an Agent: line reads exactly"),
    ("fix: x\n\nAgent: Claude Code \u00b7 claude-opus-5-5 (served) \u00b7 medium", "an Agent: line reads exactly"),
    ("fix: x\n\n> " + DECLARED, "an Agent: line reads exactly"),  # a prefix is still that line's start
    ("fix: x\n\n" + DECLARED + "\n" + TRAILER, "no Co-Authored-By"),
    ("fix: x\n\n" + DECLARED + "\nGenerated with Claude Code", "no Co-Authored-By"),
    ("fix: x\n\n\U0001f916 Generated with [Claude Code](https://claude.com/claude-code)", "no Co-Authored-By"),
    ("fix: x\n\nGenerated with: aider", "no Co-Authored-By"),
    ("fix: x\n\nThis commit was generated with\na tool", "no Co-Authored-By"),  # the phrase ends its line
    ("fix: x\n\n_Generated with Claude Code_", "no Co-Authored-By"),  # an underscore before it is emphasis, not a word (#280)
    ("fix: x\n\nPosted by an agent on Brandon Perfetti's behalf.", "no Co-Authored-By"),
    ("fix: x\n\nhttps://claude.ai/code/session_01AbC", "no Co-Authored-By"),
    ("fix: x\n\nSee https://chatgpt.com/share/abc for the chat", "no Co-Authored-By"),
    ("fix: x\n\nhttps://claude.ai/share/0a1b2c", "no Co-Authored-By"),
    ("fix: x\n\n" + DECLARED + "\n**Agent**: Claude Code", "one Agent: line per commit, not 2"),
    ("fix: x\n\n" + DECLARED + "\nAgent (Claude Code): opus", "one Agent: line per commit, not 2"),
    ("fix: x\n\n_Agent_: Claude Code \u00b7 claude-opus-5-5 \u00b7 medium", "an Agent: line reads exactly"),
    ("fix: x\n\nagent behaviour: unchanged", None),  # prose that starts with the word is not a declaration
)

# "generated with" inside a longer word is prose, not a footer (#280). Both copies pass these: the
# guard's copy moved with its pin (test_guard_git.InvariantTest).
LONGER_WORD_CASES = (
    "chore: x\n\nThe files were regenerated with new defaults.",
    "docs: note\n\nThe migration was generated without a token.",
    "fix: x\n\nIDs are generated within the worker, not by the client.",
    "fix: x\n\nGENERATED WITHOUT a seed",
)


class AttributionCheckTest(unittest.TestCase):
    """The check itself, in both hooks that carry it: the commit-msg hook and the push-time guard."""

    def test_both_copies_agree_on_every_case(self):
        copies = {"commit-msg": load_commit_msg().attribution_problem, "guard_git": guard_git.attribution_problem}
        for name, check in copies.items():
            for message, verdict in DECLARATION_CASES:
                with self.subTest(copy=name, message=message):
                    problem = check(message)
                    if verdict is None:
                        self.assertIsNone(problem)
                    else:
                        self.assertTrue((problem or "").startswith(verdict), problem)

    def test_both_copies_share_their_patterns(self):
        hook = load_commit_msg()
        for name in ("BANNED", "DECLARATION", "AGENT_LINE"):  # CLIENT, MODEL and EFFORT build AGENT_LINE
            with self.subTest(pattern=name):
                self.assertEqual(getattr(hook, name).pattern, getattr(guard_git, name).pattern)
                self.assertEqual(getattr(hook, name).flags, getattr(guard_git, name).flags)

    def test_the_footer_phrase_inside_a_longer_word_is_prose(self):
        copies = {"commit-msg": load_commit_msg().attribution_problem, "guard_git": guard_git.attribution_problem}
        for name, check in copies.items():
            for message in LONGER_WORD_CASES:
                with self.subTest(copy=name, message=message):
                    self.assertIsNone(check(message))


class CommitMsgTest(unittest.TestCase):
    def setUp(self):
        # No global or system git config reaches these commits (a commit.gpgSign there would break them).
        clean = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}  # no inherited GIT_DIR or identity
        patcher = mock.patch.dict(os.environ, {**clean, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.tmp.name, "repo")
        subprocess.run(["git", "init", "-q", "-b", "feature", self.repo], check=True)
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", AUTHOR_EMAIL)
        self.git("config", "core.hooksPath", HOOKS_DIR)
        self.git("commit", "-q", "--allow-empty", "-m", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, **kwargs):
        env = dict(os.environ, **kwargs.pop("env", {}))
        return subprocess.run(["git", "-C", self.repo] + list(args), capture_output=True, text=True, env=env, timeout=30, **kwargs)

    def commit(self, *args, **kwargs):
        return self.git("commit", "-q", "--allow-empty", *args, **kwargs)

    def assert_denied(self, result, *words):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("RULE ZERO", result.stderr)
        for word in words:
            self.assertIn(word, result.stderr)

    def test_hook_is_executable_and_runs(self):
        self.assertTrue(os.access(os.path.join(HOOKS_DIR, "commit-msg"), os.X_OK))
        self.assertEqual(self.commit("-m", "fix: clean").returncode, 0)

    def test_trailers_are_denied_whatever_the_route(self):
        message_file = os.path.join(self.tmp.name, "msg.txt")
        with open(message_file, "w") as handle:
            handle.write("fix: x\n\n" + TRAILER + "\n")
        shell = "cd {} && git commit -q --allow-empty -F - <<'EOF'\nfix: x\n\n{}\nEOF".format(shlex.quote(self.repo), TRAILER)
        cases = (
            ("-m", "-m", "fix: x\n\n" + TRAILER),
            ("two -m", "-m", "fix: x", "-m", TRAILER),
            ("-F file", "-F", message_file),
            ("--trailer", "-m", "fix: x", "--trailer", "Co-Authored-By: A <a@b>"),
            ("--trailer key=value", "-m", "fix: x", "--trailer", "Co-Authored-By=A <a@b>"),
            ("session line", "-m", "fix: x\n\nClaude-Session: abc"),
            ("generated with", "-m", "fix: x\n\nGenerated with Claude Code"),
            ("generated with, ending its line", "-m", "fix: x\n\nThis was generated with\na tool"),
            ("agent label", "-m", "fix: x\n\nPosted by an agent on Brandon Perfetti's behalf."),
            ("list item", "-m", "fix: x\n\n- Posted by an agent on Brandon Perfetti's behalf."),
            ("list trailer", "-m", "fix: x\n\n* " + TRAILER),
        )
        for name, *args in cases:
            with self.subTest(route=name):
                self.assert_denied(self.commit(*args), BANNED_WORDS)
        result = subprocess.run(["bash", "-c", shell], capture_output=True, text=True)
        self.assert_denied(result)
        self.assertEqual(self.git("rev-list", "--count", "HEAD").stdout.strip(), "1")  # nothing was committed

    def test_one_well_formed_declaration_commits(self):
        cases = (
            ("-m", "-m", "fix: x\n\n" + DECLARED),
            ("--trailer", "-m", "fix: x", "--trailer", DECLARED),
            ("OpenClaw", "-m", "fix: x\n\nAgent: Camina (OpenClaw) \u00b7 gpt-5.5"),
            ("requested", "-m", "fix: x\n\nAgent: Codex \u00b7 gpt-5.5 (requested) \u00b7 high"),
        )
        for name, *args in cases:
            with self.subTest(route=name):
                result = self.commit(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
        trailers = self.git("log", "-1", "--format=%(trailers:key=Agent,valueonly)").stdout.strip()
        self.assertEqual(trailers, "Codex \u00b7 gpt-5.5 (requested) \u00b7 high")  # git reads it as a trailer

    def test_a_second_or_malformed_declaration_is_denied(self):
        cases = (
            ("two -m", "-m", "fix: x\n\n" + DECLARED, "-m", DECLARED),
            ("body and --trailer", "-m", "fix: x\n\n" + DECLARED, "--trailer", "Agent: Codex \u00b7 gpt-5.5 \u00b7 high"),
            ("no model", "-m", "fix: x\n\nAgent: Claude Code"),
            ("no effort", "-m", "fix: x\n\nAgent: Codex \u00b7 gpt-6.1-sol"),
            ("wrong separator", "-m", "fix: x\n\nAgent: Claude Code | claude-opus-5-5 | medium"),
            ("--trailer key=value", "-m", "fix: x", "--trailer", "Agent=Claude Code"),
        )
        for name, *args in cases:
            with self.subTest(route=name):
                self.assert_denied(self.commit(*args), "Agent: line")
        self.assert_denied(self.commit("-m", "fix: x\n\n" + DECLARED + "\n" + TRAILER), BANNED_WORDS)
        self.assert_denied(self.commit("-m", "fix: x\n\n" + DECLARED, env={"GIT_AUTHOR_EMAIL": OTHER}), OTHER)  # declared, still Brandon's
        self.assertEqual(self.git("rev-list", "--count", "HEAD").stdout.strip(), "1")  # nothing was committed

    def test_amend_and_reuse_reread_the_message(self):
        # A tainted commit made with --no-verify is the case the hook cannot stop; what reuses it can be.
        self.assertEqual(self.commit("--no-verify", "-m", "fix: x\n\n" + TRAILER).returncode, 0)
        self.assert_denied(self.commit("--amend", "--no-edit"))
        self.assert_denied(self.commit("-C", "HEAD"))
        self.assertEqual(self.commit("--amend", "-m", "fix: clean").returncode, 0)

    def test_author_is_the_one_git_resolved(self):
        self.assert_denied(self.commit("-m", "fix: x", env={"GIT_AUTHOR_EMAIL": OTHER}), OTHER)
        self.assert_denied(self.commit("--author=X <{}>".format(OTHER), "-m", "fix: x"), OTHER)
        self.assert_denied(self.git("-c", "user.email=" + OTHER, "commit", "-q", "--allow-empty", "-m", "fix: x"), OTHER)
        self.assertEqual(self.commit("--author=Brandon Perfetti <{}>".format(AUTHOR_EMAIL), "-m", "fix: x").returncode, 0)
        self.assertEqual(self.commit("--no-verify", "--author=X <{}>".format(OTHER), "-m", "fix: x").returncode, 0)
        self.assert_denied(self.commit("--amend", "--no-edit"), OTHER)  # the amend keeps that author
        self.assertEqual(self.commit("--amend", "--no-edit", "--reset-author").returncode, 0)

    def test_repository_hooks_still_run(self):
        repo_hooks = os.path.join(self.repo, ".git", "hooks")
        marker = os.path.join(self.tmp.name, "ran")
        for name in ("commit-msg", "pre-commit"):
            with open(os.path.join(repo_hooks, name), "w") as handle:
                handle.write("#!/bin/sh\necho {} >> {}\n".format(name, marker))
            os.chmod(os.path.join(repo_hooks, name), 0o755)
        os.symlink("chain-repo-hook", os.path.join(self.tmp.name, "pre-commit-link"))
        hooks_dir = os.path.join(self.tmp.name, "hooks")
        os.makedirs(hooks_dir)
        for name in ("commit-msg", "chain-repo-hook"):
            os.symlink(os.path.join(HOOKS_DIR, name), os.path.join(hooks_dir, name))
        os.symlink("chain-repo-hook", os.path.join(hooks_dir, "pre-commit"))  # as install.py lays it out
        self.git("config", "core.hooksPath", hooks_dir)
        self.assertEqual(self.commit("-m", "fix: clean").returncode, 0)
        with open(marker) as handle:
            self.assertEqual(sorted(handle.read().split()), ["commit-msg", "pre-commit"])
        with open(os.path.join(repo_hooks, "commit-msg"), "w") as handle:
            handle.write("#!/bin/sh\nexit 7\n")  # the repository's own verdict still counts
        self.assertEqual(self.commit("-m", "fix: clean").returncode, 1)
        with open(os.path.join(repo_hooks, "commit-msg"), "w") as handle:
            handle.write("#!/bin/sh\nprintf '\\n{}\\n' >> \"$1\"\n".format(TRAILER))  # a repository hook that adds one
        self.assert_denied(self.commit("-m", "fix: clean"), "repository's own hook")
        self.assert_denied(self.commit("-m", "fix: x\n\n" + TRAILER))  # ours runs first

    def test_hooks_never_chain_to_themselves(self):
        repo_hooks = os.path.join(self.repo, ".git", "hooks")
        for name in ("commit-msg", "chain-repo-hook"):
            os.symlink(os.path.join(HOOKS_DIR, name), os.path.join(repo_hooks, name))
        os.symlink("chain-repo-hook", os.path.join(repo_hooks, "pre-commit"))
        self.git("config", "--unset", "core.hooksPath")  # the repository's own hooks dir is the installed one
        result = self.commit("-m", "fix: clean")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_comment_prefixed_attribution_and_git_am(self):
        self.assert_denied(self.commit("--cleanup=verbatim", "-m", "fix: x\n\n# " + TRAILER))
        self.assert_denied(self.commit("-m", "fix: x\n\n> " + TRAILER))
        hooks_dir = os.path.join(self.tmp.name, "hooks")
        os.makedirs(hooks_dir)
        os.symlink(os.path.join(HOOKS_DIR, "commit-msg"), os.path.join(hooks_dir, "commit-msg"))
        os.symlink("commit-msg", os.path.join(hooks_dir, "applypatch-msg"))  # as install.py lays it out
        self.git("config", "core.hooksPath", hooks_dir)
        with open(os.path.join(self.repo, "file.txt"), "w") as handle:
            handle.write("content\n")  # a patch with a diff: `git am` refuses an empty one before any hook
        self.git("add", "file.txt")
        self.assertEqual(self.commit("-m", "feat: file").returncode, 0)
        patch = self.git("format-patch", "-1", "--stdout").stdout
        self.git("reset", "-q", "--hard", "HEAD~1")
        tainted = patch.replace("\n---\n", "\n\n" + TRAILER + "\n---\n", 1)
        path = os.path.join(self.tmp.name, "tainted.patch")
        with open(path, "w") as handle:
            handle.write(tainted)
        result = self.git("am", path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RULE ZERO", result.stderr + result.stdout)
        self.git("am", "--abort")
        foreign = patch.replace("From: ", "From: Other <{}>\nX-Was: ".format(OTHER), 1)  # the patch's author, not the applier's
        with open(path, "w") as handle:
            handle.write(foreign)
        result = self.git("am", path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(OTHER, result.stderr + result.stdout)
        self.git("am", "--abort")
        with open(path, "w") as handle:
            handle.write(patch)
        self.assertEqual(self.git("am", path).returncode, 0)  # the clean patch applies

    def test_the_whole_message_file_is_read_scissors_included(self):
        # The hook cannot tell whether git will discard what sits below a scissors line, so it reads
        # all of it: a kept attribution line is refused, and so is a `commit -v` whose diff carries one.
        scissors = "# ------------------------ >8 ------------------------"
        self.assert_denied(self.commit("--cleanup=verbatim", "-m", "fix: x\n" + scissors + "\n" + TRAILER))
        self.assert_denied(self.commit("--cleanup=verbatim", "-m", "fix: x\n" + scissors + "\nGenerated with Claude Code"))
        with open(os.path.join(self.repo, "notes.md"), "w") as handle:
            handle.write("Never add a line Generated with Claude Code.\n")
        self.git("add", "notes.md")
        # With -m the editor never opens, so -v appends nothing and the diff is not in the file.
        self.assertEqual(self.git("commit", "-q", "-v", "-m", "docs: notes").returncode, 0)

    def test_clean_messages_pass(self):
        for args in (("-m", "fix: costs $5 and `backticks`"), ("-m", "docs: never add a Co-Authored-By line"), ("-m", "fix: display comments posted by an agent"),
                     ("-m", "docs: note\n\nThe migration was generated without a token."),  # a longer word is prose (#280)
                     ("-m", "chore: x\n\nThe files were regenerated with new defaults."),  # on either side (#280)
                     ("-m", "fix: x", "--trailer", "Reviewed-by: B <b@c>")):  # "generated with" as words is a match anywhere, by design
            with self.subTest(args=args):
                result = self.commit(*args)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
