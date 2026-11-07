#!/usr/bin/python3
"""Table tests for guard_git.py. Run: /usr/bin/python3 hooks/claude-code/test_guard_git.py"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
    "/bin/zsh -s <<EOF\ngh pr merge 1\nEOF",
    "bash<<EOF\ngit push -f\nEOF",
    "sh<<'EOF'\ngit push -f\nEOF",
    '"bash" <<EOF\ngit push -f\nEOF',
    "'/bin/sh' <<EOF\ngit push -f\nEOF",
    "cd /tmp && sh <<'EOF'\ngit push origin master\nEOF",
    "gh pr merge 12",
    "gh pr merge --squash --auto",
    "gh -R owner/repo pr merge 1",
    "gh pr --repo owner/repo merge 1",
    "GH_TOKEN=x gh pr merge 1",
    "gh api -X PUT repos/o/r/pulls/1/merge",
    "git push origin :",
    "gh api --method PUT repos/o/r/pulls/1/merge",
    "gh api repos/o/r/merges -f base=master -f head=develop",
    "gh api graphql -f query='mutation { mergePullRequest(input: {}) { clientMutationId } }'",
]

# A commit whose message arrives on stdin is denied as uncheckable, whatever the body says: the
# guard does not model the shell's stdin. The text after `<<` never reaches it as a command either.
UNCHECKABLE_STDIN = [
    "git commit -F - <<'EOF'\nfix: don't run this\ngit push --force\ngh pr merge 1\nEOF",
    "./scripts/check.sh && git commit -F - <<'EOF'\nfix: x\n\ngh pr merge 3\nEOF",
    "./scripts/a.sh; ./b.zsh && git commit -F - <<'EOF'\nfix: x\ngit push -f\nEOF",
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
    "cat <<EOF > notes.md\ngit push origin master\nEOF",
    "ls -la",
    "",
]


def make_repo(root, name, branch, email=guard_git.AUTHOR_EMAIL):
    path = os.path.join(root, name)
    subprocess.run(["git", "init", "-q", "-b", branch, path], check=True)
    git(path, "config", "user.name", "Test")
    git(path, "config", "user.email", email)
    git(path, "-c", "user.email=" + guard_git.AUTHOR_EMAIL, "commit", "-q", "--allow-empty", "-m", "init")  # a resolvable HEAD
    for other in ("develop", "wave-1", "feature-master", "master-notes"):  # the branches the push shapes name
        if other != branch:
            git(path, "branch", other)
    return path


def git(path, *args):
    subprocess.run(["git", "-C", path] + list(args), check=True, capture_output=True)


def commit_as(path, email):
    git(path, "-c", "user.email=" + email, "commit", "-q", "--allow-empty", "-m", "test")


class GuardTest(unittest.TestCase):
    def setUp(self):
        # Every PR merge here reads as one into develop; MergeBaseTest varies the base.
        patcher = mock.patch.object(guard_git, "gh_read", return_value="develop")
        patcher.start()
        self.addCleanup(patcher.stop)

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

    def test_stdin_messages_are_uncheckable_and_hide_nothing(self):
        for command in UNCHECKABLE_STDIN:
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.on_feature) or ""
                self.assertIn("cannot be checked", reason)
                self.assertNotIn("force", reason)  # the body's text is data, not a command

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

        # `--help` is denied with no lookup, so no real gh call decides this test.
        decision = json.loads(run("gh pr merge --help"))["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertEqual(run("git status"), "")


class MergeBaseTest(unittest.TestCase):
    """Merges into develop, main or master stay with Brandon; others pass (2026-10-30)."""

    MERGES = (
        "gh pr merge 12",
        "gh pr merge --squash",
        "gh -R owner/repo pr merge 1",
        "gh api -X PUT repos/o/r/pulls/1/merge",
        "gh api -X put repos/o/r/pulls/1/merge",
    )

    def check(self, command, base):
        with mock.patch.object(guard_git, "gh_read", return_value=base) as read:
            return guard_git.check_command(command, "/tmp"), read

    def test_protected_or_unknown_base_is_blocked(self):
        for base in ("develop", "main", "master", None):
            for command in self.MERGES:
                with self.subTest(base=base, command=command):
                    reason, _ = self.check(command, base)
                    self.assertIsNotNone(reason)
                    self.assertIn(base or "could not be read", reason)

    def test_feature_base_passes(self):
        for base in ("feat/claude-code-hooks", "wave-2", "wave-2-lane-a", "develop-notes"):
            for command in self.MERGES:
                with self.subTest(base=base, command=command):
                    self.assertIsNone(self.check(command, base)[0])

    def test_the_lookup_reads_the_pr_the_merge_names(self):
        jq = ["--json", "baseRefName", "--jq", ".baseRefName"]
        for command, args in (
            ("gh pr merge 7 --squash", ["pr", "view", "7"] + jq),
            ("gh pr merge", ["pr", "view"] + jq),
            ("gh -R owner/repo pr merge 7", ["pr", "view", "7", "--repo", "owner/repo"] + jq),
            ("gh pr merge --repo=o/r 7", ["pr", "view", "7", "--repo", "o/r"] + jq),
            ("gh pr merge --body 'merge 12' -t subj 7", ["pr", "view", "7"] + jq),
            ("gh pr merge -sb 42 7", ["pr", "view", "7"] + jq),
            ("gh pr merge -sb42 7", ["pr", "view", "7"] + jq),
            ("gh pr merge -dR o/r 7", ["pr", "view", "7", "--repo", "o/r"] + jq),
            ("gh pr merge -- 7", ["pr", "view", "7"] + jq),
            ("gh api -X PUT repos/o/r/pulls/3/merge", ["api", "repos/o/r/pulls/3", "--jq", ".base.ref"]),
            ("gh api -XPUT /repos/o/r/pulls/3/merge", ["api", "/repos/o/r/pulls/3", "--jq", ".base.ref"]),
            (
                "gh api -X PUT -f commit_title=repos/o/r/pulls/2/merge repos/o/r/pulls/1/merge",
                ["api", "repos/o/r/pulls/1", "--jq", ".base.ref"],
            ),
            (
                "gh api --hostname ghe.example.com --method=PUT repos/o/r/pulls/4/merge",
                ["api", "repos/o/r/pulls/4", "--hostname", "ghe.example.com", "--jq", ".base.ref"],
            ),
        ):
            with self.subTest(command=command):
                _, read = self.check(command, "feature")
                self.assertEqual(read.call_args[0][0], args)

    def test_env_prefix_reaches_the_lookup(self):
        for command, env in (
            ("GH_TOKEN=x gh pr merge 1", {"GH_TOKEN": "x"}),
            ("export GH_REPO=o/r && gh pr merge 3", {"GH_REPO": "o/r"}),
            ("export GH_REPO=o/r; GH_HOST=h gh pr merge 3", {"GH_REPO": "o/r", "GH_HOST": "h"}),
            ("export GH_REPO=o/r; eval gh pr merge 3", {"GH_REPO": "o/r"}),
            ("GH_REPO=o/r bash -c 'gh pr merge 3'", {"GH_REPO": "o/r"}),
        ):
            with self.subTest(command=command):
                _, read = self.check(command, "feature")
                self.assertEqual(read.call_args[0][2], env)

    def test_probe_and_unresolvable_merges_stay_blocked_without_a_lookup(self):
        for command in (
            "gh pr merge --help",
            "gh pr merge -h",
            "gh pr merge --auto --squash 7",
            "gh api graphql -f query='mutation { mergeBranch(input: {}) { clientMutationId } }'",
            "gh api graphql -f query='mutation { enqueuePullRequest(input: {}) { clientMutationId } }'",
            "gh api -X PUT -f x=repos/o/r/pulls/1/merge repos/o/r/pulls/1/merged",
            "gh api graphql -f query='mutation { mergePullRequest(input: {}) { clientMutationId } }'",
            "gh api repos/o/r/merges -f base=feature -f head=other",
            "gh api -X PUT /pulls/1/merge",
        ):
            with self.subTest(command=command):
                reason, read = self.check(command, "feature")
                self.assertIsNotNone(reason)
                read.assert_not_called()

    def test_a_failed_read_is_none(self):
        self.assertIsNone(guard_git.gh_read(["definitely-not-a-gh-command"], "/tmp", {}))


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
            (self.mine, "export GIT_AUTHOR_EMAIL={}; git commit -m x".format(self.OTHER), True),
            (self.mine, 'export GIT_AUTHOR_EMAIL={}; bash -c "git commit -m y"'.format(self.OTHER), True),
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

    def test_commit_rejects_an_attribution_trailer(self):
        trailer = "Co-Authored-By: Claude <noreply@anthropic.com>"
        with open(os.path.join(self.mine, "msg.txt"), "w") as handle:
            handle.write("fix: x\n\n" + trailer + "\n")
        for command, blocked in (
            ('git commit -m "fix: x"', False),
            ('git commit -m "fix: x" -m "{}"'.format(trailer), True),
            ('git commit -m "fix: x\n\n{}"'.format(trailer), True),
            ('git commit --message="fix: x" --trailer "{}"'.format(trailer), True),
            ('git commit -m "fix: x" --trailer="Claude-Session: abc"', True),
            ('git commit -m "fix: x" -m "Generated with Claude Code"', True),
            ("git commit -F msg.txt", True),
            ("git commit -Fmsg.txt", True),
            ('git commit -m"fix: x" -m"{}"'.format(trailer), True),
            ("git commit -F - <<'EOF'\nfix: x\n\n{}\nEOF".format(trailer), True),
            ("git commit --file=- <<EOF\nfix: x\n{}\nEOF".format(trailer), True),
            ("git commit -F - <<'EOF'\nfix: x\n\nmentions co-authored-by in prose\nEOF", False),
            ("cat <<'EOF' > notes.md\n{}\nEOF".format(trailer), False),
            ("git commit -F - <<'EOF'\nfix: x\n EOF\n{}\nEOF".format(trailer), True),
            ("git commit -F- <<'EOF'\nfix: x\n{}\nEOF".format(trailer), True),
            ("git status && cat <<EOF # commit -F -\n{}\nEOF".format(trailer), False),
            ('git commit -am "fix: x\n\n{}"'.format(trailer), True),
            ("git commit -aF msg.txt", True),
            ('git commit -tform -m "{}"'.format(trailer), True),
            ('git commit -t form -m "fix: x"', False),
            ('git commit -u -m "{}"'.format(trailer), True),
            ('git commit -m x --trailer "Co-Authored-By=A <a@b>"', True),
            ('git commit -m x --trail "Co-Authored-By: A <a@b>"', True),
            ('git commit --mess "fix: clean"', False),
            ('git commit --dry --mess "{}"'.format(trailer), False),
            ('git commit --m "{}"'.format(trailer), True),
            ('git commit -m x --trailer "Reviewed-by=A <a@b>"', False),
            ("git commit -aF- <<'EOF'\nfix: x\n{}\nEOF".format(trailer), True),
            ("git commit -F - <<'END-MSG'\nfix: x\n{}\nEND-MSG".format(trailer), True),
            ("git commit -F - <<<'{}'".format(trailer), True),
            ("git commit -F - <<<'fix: clean'", False),
            ("printf '%s\\n' x '' '{}' | git commit -F -".format(trailer), True),
            ("printf 'fix: clean' | git commit -F -", True),
            ("git commit --dry-run -F - <<'EOF'\n{}\nEOF".format(trailer), False),
            ("echo git commit -F - <<'EOF'\n{}\nEOF".format(trailer), False),
            ("git commit -F - <<'EOF'\nfix: x\n\tEOF\n{}\nEOF".format(trailer), True),
            ('git commit -n -m "{}"'.format(trailer), True),
            ("git commit -n -F - <<'EOF'\n{}\nEOF".format(trailer), True),
            ("git commit -F - <<'EOF'\nfix: clean\nEOF\ngit commit -F - <<'EOF'\n{}\nEOF".format(trailer), True),
            ("git commit -F - <<'EOF'\nfix: clean\nEOF\ncat msg.txt | git commit -F -", True),
            ("git commit -F - <<<''", False),
            ("git commit -m \"$(cat <<'EOF'\nfix: x\n{}\nEOF\n)\"".format(trailer), True),
            ("git commit --allow-empty -C --output=/tmp/guard-should-not-write", True),  # option-like: nothing was read, so it is uncheckable (and git refuses it)
            ('git commit -m x --trailer "Co-Authored-By = A <a@b>"', True),
            ('git commit -m x --trailer "Co-Authored-By : A <a@b>"', True),
            ('git commit -m "fix: x\n\nCo-Authored-By : A <a@b>"', True),
            ("git commit --dry-run -m \"$(cat <<'EOF'\n{}\nEOF\n)\"".format(trailer), False),
            ("echo git commit -m \"$(cat <<'EOF'\n{}\nEOF\n)\"".format(trailer), False),
            ("git commit -F - <<'END.MSG'\nfix: clean\nEND.MSG", False),
            ("git commit -F - <<'END.MSG'\nfix: x\n{}\nEND.MSG".format(trailer), True),
            ("git commit -F - <<'END MSG'\nfix: clean\nEND MSG", False),
            ("git commit -F - <<'END MSG'\nfix: x\n{}\nEND MSG".format(trailer), True),
            ("git commit -F - <<E\\OF\nfix: clean\nEOF", False),
            ('git commit -F - <<E"OF"\nfix: clean\nEOF', False),
            ("git commit -F - <<'END;MSG'\nfix: clean\nEND;MSG", False),
            ("git commit --author 'Brandon | Perfetti <brandon@brandonperfetti.com>' -m \"$(cat <<'EOF'\nfix: x\n\n{}\nEOF\n)\"".format(trailer), True),
            ("git commit --author 'B; P <brandon@brandonperfetti.com>' -m \"$(cat <<'EOF'\nfix: x\n{}\nEOF\n)\"".format(trailer), True),
            ("git commit -m \"docs: git commit -F -\" <<'EOF'\n{}\nEOF".format(trailer), False),
            ('git commit -m --dry-run -m "{}"'.format(trailer), True),
            ('git commit -m "{}" --dry-run'.format(trailer), False),
            ("M='x'; git commit -F - <<EOF\nfix: $M\nEOF", True),
            ("git commit -F - <<EOF\nfix: plain unquoted tag, no expansion\nEOF", False),
            ('M="x"; git commit -F - <<<"fix: $M"', True),
            ("git commit -F - <<<\"fix: literal\"", False),
            ("M='x'; git commit -F - <<<''\"$M\"", True),
            ("git commit -F - <<<'fix: 'clean", False),
            ("git commit -F - <<<'fix: '\"clean\"", False),
            ("git commit -F - <<<''{}".format(trailer.replace(" ", "\\ ")), True),
            ("git commit -F - <<EOF\nfix: $*\nEOF", True),
            ("git commit -F - <<EOF\nfix: $1 and $@\nEOF", True),
            ("git commit -F - <<EOF\nfix: costs \\$5\nEOF", False),
            ("M='x'; git commit -F - <<EOF\nfix: \\\\$M\nEOF", True),  # two backslashes: `\\\\$M` expands
            ("M='x'; git commit -F - <<EOF\nfix: \\\\\\$M\nEOF", False),  # three: literal backslash + literal $
            ('M="x"; git commit -F - <<<"fix: \\\\$M"', True),
            ('git commit -F - <<<"fix: \\$5 literal"', False),
            ("git commit --author 'Brandon | Perfetti <brandon@brandonperfetti.com>' -F - <<'EOF'\nfix: clean\nEOF", False),
            ("git commit --author 'Brandon | Perfetti <brandon@brandonperfetti.com>' -F - <<'EOF'\nfix: x\n{}\nEOF".format(trailer), True),
            ('git commit -au -m "{}"'.format(trailer), True),
            ("git commit -F - <<-EOF\n\tfix: x\n\t{}\n\tEOF".format(trailer), True),
            ('git commit -m "docs: mention co-authored-by in prose"', False),
            ("git commit --dry-run -F msg.txt", False),
        ):
            stdin_fed = (
                re.search(r"git commit\b(?![^\n]*--dry-run)[^\n#]*(?:\s-[a-zA-Z]*F\s*-(?:\s|$)|-F-|--file=-|<<<)", command) is not None
                and "$(cat" not in command and not command.startswith("echo ") and "docs: git commit" not in command
            )
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine)
                if stdin_fed:  # the narrowed guard never reads stdin: denied whatever the body says
                    self.assertIn("cannot be checked", reason or "")
                    continue
                self.assertEqual(reason is not None, blocked, reason)
                if blocked:
                    self.assertTrue("attribution trailer" in reason or "cannot be checked" in reason, reason)

    def test_commit_reads_a_reused_message(self):
        git(self.mine, "commit", "-q", "--allow-empty", "-m", "fix: y\n\nCo-Authored-By: X <x@example.com>")
        for command, blocked in (
            ("git commit --allow-empty -C HEAD --reset-author", True),
            ("git commit --allow-empty --reuse-message=HEAD", True),
            ("git commit --allow-empty -c HEAD", True),
            ("git commit --allow-empty -C HEAD~0", True),
        ):
            with self.subTest(command=command):
                self.assertIn("attribution trailer", guard_git.check_command(command, self.mine) or "")
        for command, blocked in (
            ("git commit --amend --no-edit", True),
            ("git commit --amend", True),
            ('git commit --amend -m "fix: clean"', False),
            ("git commit --amend -F - <<'EOF'\nfix: clean\nEOF", True),  # stdin: uncheckable
        ):
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine)
                self.assertEqual(reason is not None, blocked, reason)
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        self.assertIsNone(guard_git.check_command("git commit --allow-empty -C HEAD", self.mine))
        self.assertIsNone(guard_git.check_command("git commit --amend --no-edit", self.mine))

    def test_fixup_reads_the_target_not_head(self):
        git(self.mine, "commit", "-q", "--allow-empty", "-m", "fix: tainted\n\nCo-Authored-By: X <x@example.com>")
        git(self.mine, "commit", "-q", "--allow-empty", "-m", "fix: clean head")
        # clean HEAD, tainted target
        self.assertIn("attribution trailer", guard_git.check_command("git commit --allow-empty --fixup=amend:HEAD~1", self.mine) or "")
        self.assertIn("attribution trailer", guard_git.check_command("git commit --allow-empty --fixup reword:HEAD~1", self.mine) or "")
        self.assertIsNone(guard_git.check_command("git commit --allow-empty --fixup=HEAD~1", self.mine))
        # tainted HEAD, clean target: a legitimate repair passes
        git(self.mine, "commit", "-q", "--allow-empty", "-m", "fix: tainted again\n\nClaude-Session: abc")
        self.assertIsNone(guard_git.check_command("git commit --amend --allow-empty --fixup=amend:HEAD~1 --no-edit", self.mine))

    def test_special_message_files_and_timeouts_are_uncheckable(self):
        trailer = "Co-Authored-By: A <a@b>"
        for command in ("git commit -F /dev/stdin", "git commit -F /dev/null", "git commit --file=/dev/stdin"):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")
        with mock.patch.object(guard_git, "git_lines", return_value=guard_git.TIMEOUT):
            commit_as(self.mine, guard_git.AUTHOR_EMAIL)
            self.assertIn("could not be read in time", guard_git.check_command("git push origin feature", self.mine) or "")
            self.assertIn("cannot be checked", guard_git.check_command("git commit --amend --no-edit", self.mine) or "")
            self.assertIn("author cannot be checked", guard_git.check_command('git commit -m "fix: clean"', self.mine) or "")  # identity read timed out
        with mock.patch.object(guard_git, "git_lines", return_value=[]):
            self.assertIsNone(guard_git.check_command("git push origin feature", self.mine))

    def test_here_string_quoting_forms(self):
        trailer = "Co-Authored-By: A <a@b>"
        for command in (
            'git commit -F - <<<"fix: \\"quoted\\" x\n{}"'.format(trailer),
            'git commit -F - <<<"fix: \\"quoted\\" clean"',
            "git commit -F - <<<$'fix: x\\n{}'".format(trailer),
            "git commit -F - <<<$'fix: clean'",
        ):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")

    def test_quoted_redirection_text_hides_nothing(self):
        for command in (
            "cat <<'EOF'\nexample <<END\nEOF\ngit push --force origin feature",
            "echo '<<EOF'\ngit push --force origin feature",
            'echo "<<EOF"; git push --force origin feature',
            "cat <<'EOF'\nexample <<END\nEOF\ngit push origin master",
            "cat <<'EOF'\nexample <<END\nEOF\ngh pr merge 1",
            "echo 'docs:\n<<EOF'\ngit push --force origin feature",
            "echo ok # <<EOF\ngit push origin master",
            "echo ok # <<EOF\ngh pr merge 1",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(guard_git.check_command(command, self.mine))

    def test_only_simple_stdin_shapes_are_read(self):
        trailer = "Co-Authored-By: A <a@b>"
        # several redirections, several commands or a non-stdin descriptor on the line: uncheckable
        for command in (
            "git commit -F - <<A <<B\nclean\nA\n{}\nB".format(trailer),
            "git commit -F - <<A <<B\n{}\nA\nclean\nB".format(trailer),
            "git commit -F - <<A; cat <<B\n{}\nA\nclean\nB".format(trailer),
            "git commit -F - <<A 2<<B\n{}\nA\nclean\nB".format(trailer),
            "git commit -F - <<'EOF' && echo done\nclean\nEOF",
        ):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")
        # two stdin commits on two lines: both uncheckable, neither hides the other
        self.assertIn("cannot be checked", guard_git.check_command("git commit -F - <<'EOF'\nclean one\nEOF\ngit commit -F - <<'EOF'\nclean two\nEOF", self.mine) or "")
        # the empty quoted delimiter is legal shell, and stdin all the same: uncheckable either way
        self.assertIn("cannot be checked", guard_git.check_command("git commit -F - <<''\nfix: clean\n\n", self.mine) or "")
        self.assertIn("cannot be checked", guard_git.check_command("git commit -F - <<''\n{}\n\n".format(trailer), self.mine) or "")

    def test_substituted_expansions_are_uncheckable(self):
        reason = guard_git.check_command('MSG="x"; git commit -m "$(cat <<EOF\n$MSG\nEOF\n)"', self.mine) or ""
        self.assertIn("cannot be checked", reason)
        # an unquoted delimiter is not the exact literal form: not readable here either
        self.assertIn("cannot be checked", guard_git.check_command('git commit -m "$(cat <<EOF\nfix: literal\nEOF\n)"', self.mine) or "")

    def test_exact_substitution_form(self):
        trailer = "Co-Authored-By: A <a@b>"
        clean = 'git commit -m "$(cat <<\'EOF\'\nfix: clean\n\nbody\nEOF\n)"'
        self.assertIsNone(guard_git.check_command(clean, self.mine))
        self.assertIsNone(guard_git.check_command(clean.replace("\'EOF\'", '"EOF"'), self.mine))
        self.assertIsNone(guard_git.check_command('./check.sh && ' + clean, self.mine))
        self.assertIsNone(guard_git.check_command(clean + " --dry-run", self.mine))  # argv parsed after the body
        self.assertIn("attribution trailer", guard_git.check_command('git commit -m "$(cat <<\'EOF\'\nfix: x\n\n{}\nEOF\n)"'.format(trailer), self.mine) or "")
        self.assertIn("attribution trailer", guard_git.check_command('git commit -m "$(cat <<\'EOF\'\nfix: x\n\n{}\nEOF\n)" --no-verify'.format(trailer), self.mine) or "")
        self.assertIsNone(guard_git.check_command("git add . && " + clean, self.mine))  # `.` here is an argument, not the shell builtin
        self.assertIsNone(guard_git.check_command('git commit -m "fix: x" && echo "$(cat <<\'EOF\'\nnotes\nEOF\n)"', self.mine))  # echo's substitution
        self.assertIsNone(guard_git.check_command(clean + " && git push origin feature", self.mine))
        for tail in (" && git push origin feature", "; git status", " || true"):
            with self.subTest(tail=tail):
                command = 'git commit -m "$(cat <<\'EOF\'\nfix: x\n\n{}\nEOF\n)"{}'.format(trailer, tail)
                self.assertIn("attribution trailer", guard_git.check_command(command, self.mine) or "")
        # a stray heredoc after the closing quote feeds nothing the message uses: the -m text decides
        self.assertIsNone(guard_git.check_command(clean + " <<'X'\nmore\nX", self.mine))
        for command in (
            'git commit -m "$(cat hooks/claude-code/test_guard_git.py <<\'EOF\'\nclean\nEOF\n)"',  # an operand: cat reads the file
            'git commit -m "$(cat <<\'EOF\' | tr a-z A-Z\nclean\nEOF\n)"',
            'git commit -m "$(cat <<\'EOF\'\nclean\nEOF\n) extra"',
        ):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")

    def test_continuations_and_redirects_hide_nothing(self):
        for command in (
            "cat <<EOF\nEO\\\nF\ngit push --force origin feature",
            "cat <<EOF\nEO\\\nF\ngit push origin master",
            "cat <<EOF\nEO\\\nF\ngh pr merge 1",
        ):
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine) or ""
                self.assertTrue(reason and "cannot be checked" not in reason, reason)
        self.assertIn("cannot be checked", guard_git.check_command("git commit -F - <<'EOF' < hooks/claude-code/test_guard_git.py\nclean\nEOF", self.mine) or "")
        self.assertIn("cannot be checked", guard_git.check_command("git commit -F - < hooks/claude-code/test_guard_git.py", self.mine) or "")

    def test_arithmetic_escapes_and_shell_readers_hide_nothing(self):
        for command in (
            "echo $((1<<3))\ngit push --force origin feature",
            "(( x = 1<<3 ))\ngit push origin master",
            'echo "$((1<<3))"\ngh pr merge 1',
            "echo a\\\\\ngit push -f origin feature",
            "dash <<EOF\ngit push -f origin feature\nEOF",
            "source /dev/stdin <<EOF\ngit push -f origin feature\nEOF",
            ". /dev/stdin <<EOF\ngit push -f origin feature\nEOF",
        ):
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine) or ""
                self.assertTrue(reason and "cannot be checked" not in reason, reason)
        for command in ("echo $((1<<3)) && git push origin feature", "echo a\\\ngit push origin feature", "./check.sh <<EOF\ngit push -f\nEOF"):
            with self.subTest(command=command):
                self.assertIsNone(guard_git.check_command(command, self.mine))
        self.assertIsNone(guard_git.check_command("git status \u00b2.txt <<EOF\nx\nEOF", self.mine))  # a non-ASCII digit is no descriptor

    def test_push_checks_every_unpushed_author_not_the_first(self):
        commit_as(self.mine, self.OTHER)  # an older foreign commit under a clean tip
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        self.assertIn(self.OTHER, guard_git.check_command("git push origin feature", self.mine) or "")
        self.assertIn(self.OTHER, guard_git.check_command("git push origin feature ^refs/heads/missing", self.mine) or "")
        self.assertIn("could not be read", guard_git.check_command("git push origin nonexistent-branch", self.mine) or "")

    def test_comments_end_at_the_line_and_hide_nothing(self):
        for command in ("echo first # note\\\ngit push -f origin feature", "echo first # note\\\ngit push origin master", "true # <<EOF\\\ngh pr merge 1"):
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine) or ""
                self.assertTrue(reason and "cannot be checked" not in reason, reason)
        for command in ("echo first # note\\\ngit push origin feature", 'git commit -m "fix #12"', "git commit -m 'fix: x' # done", 'git commit -m "$(cat <<\'EOF\'\nfix: x\n\n# not a comment\nEOF\n)"'):
            with self.subTest(command=command):
                self.assertIsNone(guard_git.check_command(command, self.mine))

    def test_unreadable_revisions_and_lexed_dollars_are_uncheckable(self):
        for command in ('git commit -m "a\\\\$M"', 'git commit -m x --trailer "\\\\$T"', "git commit -m 'costs $5'",
                        'git commit -C "$SHA"', "git commit -C nonexistent-rev", "git commit --fixup=amend:$SHA", "git commit -c -- -m x"):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")

    def test_retained_and_abbreviated_authors_are_checked(self):
        commit_as(self.mine, self.OTHER)  # HEAD now carries a foreign author
        for command in ("git commit --amend --no-edit", 'git commit -C HEAD', 'git commit --reuse-message=HEAD', 'git commit -m "fix: x" --auth="Some One <{}>"'.format(self.OTHER),
                        "git commit -CHEAD", "git commit -aC HEAD", 'git commit --amend -m --reset-author'):
            with self.subTest(command=command):
                self.assertIn(self.OTHER, guard_git.check_command(command, self.mine) or "")
        for command in ("git commit --amend --no-edit --reset-author", 'git commit -C HEAD --author="Brandon Perfetti <{}>"'.format(guard_git.AUTHOR_EMAIL)):
            with self.subTest(command=command):
                self.assertIsNone(guard_git.check_command(command, self.mine))
        self.assertIn("cannot be checked", guard_git.check_command("git commit -C nonexistent-rev --no-edit", self.mine) or "")

    def test_configured_trailers_are_uncheckable(self):
        git(self.mine, "config", "trailer.credit.key", "Co-Authored-By")
        self.assertIn("cannot be checked", guard_git.check_command('git commit -m "fix: x" --trailer "credit=A <a@b>"', self.mine) or "")
        self.assertIn("cannot be checked", guard_git.check_command('git --config-env=trailer.x.key=V commit -m "fix: x" --trailer "x=A <a@b>"', self.mine) or "")
        self.assertIn("cannot be checked", guard_git.check_command('git -c include.path=/tmp/x commit -m "fix: x" --trailer "x=A <a@b>"', self.mine) or "")
        with mock.patch.object(guard_git, "git_lines", return_value=guard_git.TIMEOUT):
            self.assertIn("author cannot be checked", guard_git.check_command('git commit -m "fix: x"', self.mine) or "")
        self.assertIn("cannot be checked", guard_git.check_command('git --config-env trailer.x.key=V commit -m "fix: x" --trailer "x=A <a@b>"', self.mine) or "")
        self.assertIsNone(guard_git.check_command('git commit -m "fix: x"', self.mine))  # no --trailer: the setting adds nothing

    def test_r8_routes_are_closed(self):
        trailer = "Co-Authored-By: A <a@b>"
        two = 'git commit -m "$(cat <<\'A\'\nfix: x\nA\n)" -m "$(cat <<\'B\'\n{}\nB\n)"'.format(trailer)
        self.assertIn("cannot be checked", guard_git.check_command(two, self.mine) or "")
        self.assertIn("attribution trailer", guard_git.check_command('git commit --dry-run -m clean && git commit -m "$(cat <<\'EOF\'\nfix: x\n\n{}\nEOF\n)"'.format(trailer), self.mine) or "")
        for command in ('git -c trailer.credit.key=Co-Authored-By commit -m clean --trailer "credit=A <a@b>"',
                        'GIT_CONFIG_COUNT=1 git commit -m clean --trailer "credit=A <a@b>"',
                        "git commit -F <(cat hooks/claude-code/test_guard_git.py)", "git commit -F",
                        "git commit", "git commit -c HEAD", "git commit --amend", "git commit --fixup=amend:HEAD", "git commit --squash=HEAD", "git commit -a"):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")
        for command in ("git commit --amend --no-edit", 'git commit --amend -m "fix: x"', "git commit --fixup=HEAD", 'git commit --squash=HEAD -m "fix: x" --no-edit', 'git commit -C HEAD --no-edit'):
            with self.subTest(command=command):
                self.assertIsNone(guard_git.check_command(command, self.mine))

    def test_configured_push_targets_and_xargs_are_uncheckable(self):
        for command in ("xargs git push origin <<EOF\nmaster\nEOF", "echo master | xargs git push origin", "echo 1 | xargs gh pr merge",
                        "git -c push.default=matching push", "git -c remote.origin.push=refs/heads/*:refs/heads/* push origin"):
            with self.subTest(command=command):
                self.assertTrue(guard_git.check_command(command, self.mine), command)
        self.assertIsNone(guard_git.check_command("git push", self.mine))
        git(self.mine, "config", "push.default", "matching")
        self.assertIn("chosen by", guard_git.check_command("git push", self.mine) or "")
        self.assertIsNone(guard_git.check_command("git push origin feature", self.mine))  # a named refspec is read as before
        git(self.mine, "config", "push.default", "simple")
        git(self.mine, "config", "remote.origin.push", "refs/heads/*:refs/heads/*")
        self.assertIn("chosen by", guard_git.check_command("git push origin", self.mine) or "")

    def test_substitutions_in_unquoted_heredoc_bodies_run(self):
        for command in ("cat > /dev/null <<EOF\n$(git push --force origin master)\nEOF", "cat <<EOF\n`git push origin master`\nEOF", "cat <<EOF\n$(cd . && gh pr merge 1)\nEOF"):
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine) or ""
                self.assertTrue(reason and "cannot be checked" not in reason, reason)
        for command in ("cat <<'EOF'\n$(git push --force origin master)\nEOF", "cat <<EOF\n$(git status)\nEOF", "cat <<EOF\nprice $(( 1<<3 ))\nEOF"):
            with self.subTest(command=command):
                self.assertIsNone(guard_git.check_command(command, self.mine))

    def test_ansi_c_quotes_hide_no_heredoc(self):
        for command in ("echo $'a\\' <<EOF b'\ngit push --force origin master\nEOF", "echo $'a\n<<EOF b'\ngit push -f origin feature\nEOF", "echo $'a\\'\n<<EOF b'\ngit push origin master\nEOF"):
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine) or ""
                self.assertTrue(reason and "cannot be checked" not in reason, reason)
        self.assertIsNone(guard_git.check_command("echo $'a\nb' && git push origin feature", self.mine))

    def test_expanding_message_values_are_uncheckable(self):
        for command in ('git commit -m "$(cat msg.txt)"', 'git commit -m "$MSG"', "git commit -m 'fix: $X'",
                        'git commit -m "fix: `cat x`"', 'git commit -m x --trailer "$T"', 'git commit -m "${M}"'):
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine) or ""
                self.assertIn("cannot be checked", reason)
        self.assertIsNone(guard_git.check_command('git commit -m "fix: costs 5 dollars" -m "body"', self.mine))
        for command in ("dash -c 'git push -f origin feature'", "mksh -c 'git push origin master'", "ash <<EOF\ngit push -f origin feature\nEOF"):
            with self.subTest(command=command):
                self.assertTrue(guard_git.check_command(command, self.mine))

    def test_editor_and_template_routes_are_uncheckable(self):
        for command in ('git commit -e -m "fix: x"', 'git commit -t tmpl', 'git commit --template=tmpl -a',
                        'GIT_EDITOR=./add-trailer.sh git commit -m "fix: x"', 'git -c core.editor=./e.sh commit -m "fix: x"',
                        'git -c commit.template=tmpl commit -m "fix: x"', 'export EDITOR=./e.sh; git commit -m "fix: x"'):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")
        self.assertIsNone(guard_git.check_command('git commit -m "fix: x" --no-edit', self.mine))
        self.assertIsNone(guard_git.check_command('git commit -t tmpl -m "fix: x"', self.mine))  # -m keeps the editor closed
        for command in ('git commit -em "fix: x"', 'git commit -ae -m "fix: x"', 'git commit --edi -m "fix: x"', 'git commit -aem "fix: x"'):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")
        self.assertIsNone(guard_git.check_command('git commit -am "fix: x"', self.mine))
        self.assertIsNone(guard_git.check_command('git commit -Sdeadbeef -m "fix: x"', self.mine))
        self.assertIsNone(guard_git.check_command('git commit -ue -m "fix: x"'.replace("-ue", "-uno"), self.mine))

    def test_shell_readers_before_separators_and_herestrings_before_commits(self):
        for command in ("cat <<'EOF' | sh; true\ngit push -f origin feature\nEOF", "cat <<'EOF' | bash)\ngit push origin master\nEOF"):
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine) or ""
                self.assertTrue(reason and "cannot be checked" not in reason, reason)
        trailer = "Co-Authored-By: A <a@b>"
        command = 'cat <<<x | git commit -m "$(cat <<\'EOF\'\nfix: x\n\n{}\nEOF\n)"'.format(trailer)
        self.assertTrue(guard_git.check_command(command, self.mine))

    def test_quoted_continuations_stay_text(self):
        for command in (
            'git commit -m "$(cat <<\'EOF\'\nfix: x\n\nSigned\\\nCo-Authored-By: X <x@y>\nEOF\n)"',
            "git commit -m 'fix: x\n\nSigned\\\nCo-Authored-By: X <x@y>'",
        ):
            with self.subTest(command=command):
                self.assertIn("attribution trailer", guard_git.check_command(command, self.mine) or "")
        self.assertIsNone(guard_git.check_command('git commit -m "fix: x \\\nmore"', self.mine))
        self.assertIsNone(guard_git.check_command("git commit \\\n  -m 'fix: y'", self.mine))
        for command in ("git commit -m $'fix: x\\n\\nCo-Authored-By: X <x@y>'", "git commit -m $'\\x66ix: x\\n\\nCo-Authored-By: X <x@y>'", "git commit -m $'fix: clean'"):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")

    def test_message_file_written_earlier_in_the_command_is_uncheckable(self):
        path = os.path.join(self.mine, "msg.txt")
        with open(path, "w") as handle:
            handle.write("fix: clean\n")
        self.assertIsNone(guard_git.check_command("git commit -F msg.txt", self.mine))
        for command in (  # anything run before the commit could rewrite the file: only a first-command -F is read
            "cat msg.txt && git commit -F msg.txt",
            "./prepare.sh && git commit -F msg.txt",
            "cd . && git commit -F msg.txt",
            "printf 'fix\\n\\nCo-Authored-By: X <x@y>' > msg.txt && git commit -F msg.txt",
            "printf 'fix' >msg.txt; git commit -F msg.txt",
            "cp other msg.txt && git commit --file=msg.txt",
            "printf 'x' > ./msg.txt && git commit -F msg.txt",
            "printf 'x' > 1.txt && git commit -F 1.txt",
            "F=msg.txt; printf 'x' > $F; git commit -F msg.txt",
            "F=msg.txt; printf 'x' >$F; git commit -F msg.txt",
            "printf 'Co-Authored-By: x'>msg.txt && git commit -F msg.txt",
            "F=msg.txt; cp evil.txt $F; git commit -F msg.txt",
            "cp evil.txt m*.txt; git commit -F msg.txt",
            "printf 'x' > msg.txt; bash -c 'git commit -F msg.txt'",
            "printf 'x' > msg.txt; eval 'git commit -F msg.txt'",
            "printf 'x' >msg.txt && git commit -F ./msg.txt",
        ):
            with self.subTest(command=command):
                self.assertIn("cannot be checked", guard_git.check_command(command, self.mine) or "")

    def test_heredoc_bodies_are_data_not_more_heredocs(self):
        nested = "cat msg | git commit -F -\ncat <<'EOF' > notes\ngit commit -F - <<'X'\nclean\nX\nEOF\ngit push origin feature"
        found = guard_git.heredocs(nested)
        self.assertEqual([h[1] for h in found], ["git commit -F - <<'X'\nclean\nX\n"])
        self.assertIn("git push origin feature", guard_git.drop_heredocs(nested))
        self.assertIn("cannot be checked", guard_git.check_command(nested, self.mine) or "")

    def test_optional_value_options_end_a_cluster(self):
        git(self.mine, "commit", "-q", "--allow-empty", "-m", "fix: y\n\nCo-Authored-By: X <x@example.com>")
        for command in ("git commit --amend -unormal --no-edit", "git commit --amend -Skey --no-edit", "git commit --amend -aunormal --no-edit", "git commit --am --no-edit", "git commit --amen --no-e"):
            with self.subTest(command=command):
                self.assertIn("attribution trailer", guard_git.check_command(command, self.mine) or "")
        self.assertIsNone(guard_git.check_command('git commit --amend -unormal -m "fix: clean"', self.mine))

    def test_uncheckable_stdin_message_is_denied_with_its_own_reason(self):
        for command in (
            "cat msg.txt | git commit -F -",
            "M='x'; git commit -F - <<EOF\nfix: $M\nEOF",
            'M="x"; git commit -F - <<<"fix: $M"',
            "git commit -F - <<'EOF'\nfix: clean\nEOF\ncat msg.txt | git commit -F -",
        ):
            with self.subTest(command=command):
                reason = guard_git.check_command(command, self.mine) or ""
                self.assertIn("cannot be checked", reason)
                self.assertNotIn("carrying an attribution trailer", reason)
        reason = guard_git.check_command('git commit -m "fix: x" -m "Co-Authored-By: A <a@b>"', self.mine) or ""
        self.assertIn("carrying an attribution trailer", reason)
        self.assertNotIn("cannot be checked", reason)

    def test_main_advice_matches_the_reason(self):
        import io, json as json_
        cases = (
            ('git commit -m x -m "Co-Authored-By: A <a@b>"', "no Co-Authored-By, session or generated-with line"),
            ("cat msg.txt | git commit -F -", "must be readable here"),
            ('GIT_EDITOR=./e.sh git commit -m "fix: x"', "editor or template route"),
            ("git commit -C nonexistent-rev --no-edit", "author could not be read"),
            ("git -c user.email={} commit -m x".format(self.OTHER), "every agent commit carries the author email"),
        )
        for command, advice in cases:
            with self.subTest(command=command):
                payload = json_.dumps({"tool_input": {"command": command}, "cwd": self.mine})
                with mock.patch.object(sys, "stdin", io.StringIO(payload)), mock.patch("sys.stdout", new_callable=io.StringIO) as out:
                    guard_git.main()
                decision = json_.loads(out.getvalue())["hookSpecificOutput"]
                self.assertEqual(decision["permissionDecision"], "deny")
                self.assertIn(advice, decision["permissionDecisionReason"])

    def test_commit_message_is_checked_when_the_identity_read_fails(self):
        with mock.patch.object(guard_git, "git_lines", return_value=None):
            reason = guard_git.check_command('git commit -m "fix: x" -m "Co-Authored-By: A <a@b>"', self.mine)
            self.assertIn("attribution trailer", reason or "")
            self.assertIsNone(guard_git.check_command('git commit -m "fix: clean"', self.mine))

    def test_push_rejects_unpushed_commits_with_a_trailer(self):
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        self.assertIsNone(guard_git.check_command("git push -u origin feature", self.mine))
        git(self.mine, "commit", "-q", "--allow-empty", "-m", "fix: y\n\nCo-Authored-By: X <x@example.com>")
        self.assertIn("attribution trailer", guard_git.check_command("git push origin feature", self.mine) or "")
        self.assertIsNone(guard_git.check_command("git push --dry-run origin feature", self.mine))
        git(self.mine, "push", "-q", "origin", "feature")
        git(self.mine, "fetch", "-q", "origin")
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        self.assertIsNone(guard_git.check_command("git push origin feature", self.mine))

    def test_push_rejects_option_like_revisions(self):
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        sentinel = os.path.join(self.tmp.name, "guard-r3-must-not-exist")
        # After `--`, git reads `--output=…` as a refspec; before it, git rejects it as an unknown
        # option itself, so only the positional form reaches the log read.
        self.assertIn("option-like revision", guard_git.check_command("git push -- origin --output={}".format(sentinel), self.mine) or "")
        self.assertIn("option-like revision", guard_git.check_command("git push -- origin -r:feature", self.mine) or "")
        self.assertFalse(os.path.exists(sentinel))

    def test_commits_a_remote_already_has_pass(self):
        commit_as(self.mine, self.OTHER)
        git(self.mine, "push", "-q", "origin", "feature")
        git(self.mine, "fetch", "-q", "origin")
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        self.assertIsNone(guard_git.check_command("git push origin feature", self.mine))


if __name__ == "__main__":
    unittest.main()
