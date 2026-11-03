#!/usr/bin/python3
"""Table tests for guard_git.py. Run: /usr/bin/python3 hooks/claude-code/test_guard_git.py"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guard_git  # noqa: E402

BLOCKED_ANYWHERE = [
    "git push --force",
    "git push -f origin feature",
    "git push -fu origin feature",
    "git push --force-with-lease origin feature",
    "git push --force-with-lease=feature:abc origin feature",
    "git push origin +feature",
    "git push --mirror",
    "git push origin master",
    "git push origin main",
    "git push origin HEAD:master",
    "git push origin HEAD:refs/heads/master",
    "git push origin feature:refs/heads/main",
    "git push origin :master",
    "git push origin --delete master",
    "git push --all origin",
    "git push origin 'refs/heads/*:refs/heads/*'",
    "git push origin master 2>&1 | tail -5",
    "git -c core.quotepath=off push origin master",
    "/usr/bin/git push -f",
    "FOO=1 git push -f",
    "env FOO=1 git push -f",
    "command git push -f",
    "echo ok; git push origin master",
    "git status && git push -f",
    "git status\ngit push -f",
    "(cd /tmp && git push -f)",
    "echo $(git push -f)",
    'bash -c "git push -f"',
    "zsh -lc 'git status && git push origin master'",
    "eval git push -f",
    "echo don't; git push -f",
    "bash <<EOF\ngit push -f\nEOF",
    "gh pr merge 12",
    "gh pr merge --squash --auto",
    "gh -R owner/repo pr merge 1",
    "gh pr --repo owner/repo merge 1",
    "GH_TOKEN=x gh pr merge 1",
    "gh api -X PUT repos/o/r/pulls/1/merge",
    "gh api --method PUT repos/o/r/pulls/1/merge",
    "gh api repos/o/r/merges -f base=master -f head=develop",
    "gh api graphql -f query='mutation { mergePullRequest(input: {}) { clientMutationId } }'",
]

ALLOWED_ANYWHERE = [
    "git push origin feature",
    "git push -u origin wave-1",
    "git push origin develop",
    "git push origin HEAD:develop",
    "git push origin feature-master",
    "git push origin master-notes",
    "git push --no-force-with-lease origin feature",
    "git push origin feature 2>&1 | tail -5",
    "git push --dry-run origin master",
    "git push -n --force origin feature",
    'git commit -m "docs: never git push --force"',
    "git log --grep='gh pr merge'",
    'echo "git push -f"',
    "echo git push -f",
    "grep -r 'git push --force' .",
    "git fetch origin master",
    "git pull origin master",
    "git branch -f topic",
    "gh pr view 12",
    "gh pr list --state merged",
    'gh pr create --title "gh pr merge" --body "git push -f"',
    "gh api repos/o/r/pulls/1/merge",
    "gh api repos/o/r/pulls/1",
    "git commit -F - <<'EOF'\nfix: don't run this\ngit push --force\ngh pr merge 1\nEOF",
    "cat <<EOF > notes.md\ngit push origin master\nEOF",
    "ls -la",
    "",
]


def make_repo(root, name, branch, email=guard_git.AUTHOR_EMAIL):
    path = os.path.join(root, name)
    subprocess.run(["git", "init", "-q", "-b", branch, path], check=True)
    git(path, "config", "user.name", "Test")
    git(path, "config", "user.email", email)
    return path


def git(path, *args):
    subprocess.run(["git", "-C", path] + list(args), check=True, capture_output=True)


def commit_as(path, email):
    git(path, "-c", "user.email=" + email, "commit", "-q", "--allow-empty", "-m", "test")


class GuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.on_master = make_repo(cls.tmp.name, "on-master", "master")
        cls.on_main = make_repo(cls.tmp.name, "on-main", "main")
        cls.on_feature = make_repo(cls.tmp.name, "on-feature", "feature")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_blocked(self):
        for command in BLOCKED_ANYWHERE:
            with self.subTest(command=command):
                self.assertIsNotNone(guard_git.check_command(command, self.on_feature))

    def test_allowed(self):
        for command in ALLOWED_ANYWHERE:
            with self.subTest(command=command):
                self.assertIsNone(guard_git.check_command(command, self.on_feature))

    def test_bare_push_reads_the_current_branch(self):
        for command in ("git push", "git push origin", "git push origin HEAD", "git push origin @"):
            with self.subTest(command=command):
                self.assertIsNotNone(guard_git.check_command(command, self.on_master))
                self.assertIsNotNone(guard_git.check_command(command, self.on_main))
                self.assertIsNone(guard_git.check_command(command, self.on_feature))

    def test_cd_and_dash_c_change_the_checkout(self):
        for command in (
            "cd {} && git push".format(self.on_master),
            "git -C {} push".format(self.on_master),
            "cd ../on-master && git push",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(guard_git.check_command(command, self.on_feature))

    def test_pickup_probe_survives_on_a_base_branch(self):
        command = "git push --dry-run origin HEAD"
        self.assertIsNone(guard_git.check_command(command, self.on_master))

    def test_hook_output_is_a_deny(self):
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guard_git.py")

        def run(command):
            payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": self.on_feature}
            return subprocess.run(
                ["/usr/bin/python3", "-I", script],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                check=True,
            ).stdout

        decision = json.loads(run("gh pr merge 1"))["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertEqual(run("git status"), "")


class AuthorTest(unittest.TestCase):
    """RULE ZERO: commits and pushes carry Brandon's author email."""

    OTHER = "someone@example.com"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.mine = make_repo(self.tmp.name, "mine", "feature")
        self.other = make_repo(self.tmp.name, "other", "feature", self.OTHER)
        remote = os.path.join(self.tmp.name, "remote.git")
        subprocess.run(["git", "init", "-q", "--bare", remote], check=True)
        git(self.mine, "remote", "add", "origin", remote)

    def tearDown(self):
        self.tmp.cleanup()

    def test_commit_reads_the_identity_git_would_use(self):
        brandon = guard_git.AUTHOR_EMAIL
        for directory, command, blocked in (
            (self.mine, 'git commit -m "fix: x"', False),
            (self.other, 'git commit -m "fix: x"', True),
            (self.mine, "git -c user.email={} commit -m x".format(self.OTHER), True),
            (self.mine, "GIT_AUTHOR_EMAIL={} git commit -m x".format(self.OTHER), True),
            (self.mine, "env GIT_AUTHOR_EMAIL={} git commit -m x".format(self.OTHER), True),
            (self.mine, 'git commit --author="X <{}>" -m x'.format(self.OTHER), True),
            (self.other, 'git commit --author "B <{}>" -m x'.format(brandon), False),
            (self.other, "git -c user.email={} commit -m x".format(brandon), False),
            (self.other, "git commit --dry-run", False),
            (self.mine, 'git commit -m "GIT_AUTHOR_EMAIL={}"'.format(self.OTHER), False),
        ):
            with self.subTest(directory=os.path.basename(directory), command=command):
                reason = guard_git.check_command(command, directory)
                self.assertEqual(reason is not None, blocked, reason)

    def test_push_reads_the_authors_of_unpushed_commits(self):
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        self.assertIsNone(guard_git.check_command("git push -u origin feature", self.mine))
        commit_as(self.mine, self.OTHER)
        for command in ("git push", "git push origin feature", "git push origin HEAD:develop"):
            with self.subTest(command=command):
                self.assertIn(self.OTHER, guard_git.check_command(command, self.mine))
        for command in ("git push --dry-run origin feature", "git push origin --delete old"):
            with self.subTest(command=command):
                self.assertIsNone(guard_git.check_command(command, self.mine))

    def test_tags_push_reads_commits_only_a_tag_reaches(self):
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        git(self.mine, "push", "-q", "origin", "feature")
        git(self.mine, "checkout", "-q", "-b", "side")
        commit_as(self.mine, self.OTHER)
        git(self.mine, "tag", "v-other")
        git(self.mine, "checkout", "-q", "feature")
        git(self.mine, "branch", "-q", "-D", "side")
        self.assertIsNone(guard_git.check_command("git push origin feature", self.mine))
        for command in (
            "git push --tags",
            "git push --tags origin feature",
            "git push origin v-other",
            "git push origin tag v-other",
        ):
            with self.subTest(command=command):
                self.assertIn(self.OTHER, guard_git.check_command(command, self.mine) or "")

    def test_commits_a_remote_already_has_pass(self):
        commit_as(self.mine, self.OTHER)
        git(self.mine, "push", "-q", "origin", "feature")
        git(self.mine, "fetch", "-q", "origin")
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        self.assertIsNone(guard_git.check_command("git push origin feature", self.mine))


if __name__ == "__main__":
    unittest.main()
