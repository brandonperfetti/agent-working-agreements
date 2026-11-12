#!/usr/bin/python3
"""Table tests for guard_git.py. Run: /usr/bin/python3 hooks/claude-code/test_guard_git.py"""
import json
import os
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
    "git push -ofoo origin master",
    "git push --force-w origin feature",
    "git push --push-o --dry-run --force origin feature:feature",
    "git push --mirr",
    "git push origin --del master",
    "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=push.default GIT_CONFIG_VALUE_0=matching git push origin",
    'git -c core.hooksPath=/tmp/none commit -m "fix: x"',
    'git -c trailer.credit.key=Co-Authored-By commit -m "fix: x"',
    'git --config-env=core.editor=E commit -m "fix: x"',
    'GIT_CONFIG_COUNT=1 git commit -m "fix: x"',
    "git merge --no-verify topic",
    "git merge -qsort --no-verify --no-ff --no-edit topic",
    "git push -vofoo origin main",
    "git -c remote.origin.push=foreign:master push origin",
    "git --config-env=push.default=P push origin feature",
    "git -c remote.origin.push=foreign:master push origin",
    "git --config-env=push.default=P push origin feature",
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
    "{ git push --force origin feature; }",
    "{ git push origin master; }",
    "echo master | xargs git push origin",
    "printf 'master\\n' | xargs -n 1 git push --force origin",
    "xargs git push origin <<EOF\nmaster\nEOF",
    'git commit --no-verify -m "fix: x"',
    'git commit -n -m "fix: x"',
    'git commit -anm "fix: x"',
    'git commit --no-v -m "fix: x"',
    'git commit -mtrim --no-verify',
    "git commit -m --dry-run -n --allow-empty",
    "if git push --force origin feature; then echo ok; fi",
    "while git push origin master; do :; done",
    "git commit -u -n",
    "git commit -S -n -m x",
    "xargs env git push origin <<EOF\nmaster\nEOF",
    "xargs --max-args 1 git push --force origin",
    "printf master | xargs -I{} sh -c 'git push origin {}'",
    "echo 1 | xargs -I {} gh pr merge {}",
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
    "git push -ofleet origin feature",
    "git push -o fleet origin feature",
    "git push -vo fleet origin feature",
    "git push --push-o fleet origin feature",
    "git push --push-option=fleet origin feature",
    "git push -ofoo origin feature",
    "git push -vofoo origin feature",
    "git merge topic",
    "git merge --no-ff -m 'merge topic' topic",
    "git merge -n topic",
    "git merge -qsort topic",
    "git commit -m fix > -m",
    "git commit > log -m fix",
    'git commit -m "fix: >note" > log.txt',
    'git commit -m fix > ">log"',
    "git commit -m fix 2>&1 | tail -1",
    "git commit -m fix & >log echo -n ok",
    'git commit -m "fix: display comments posted by an agent"',
    'git -c user.name="Brandon Perfetti" commit -m "fix: x"',
    'git -c core.quotepath=off commit -m "fix: x"',
    "git push origin feature 2>&1 | tail -5",
    "git push --dry-run origin master",
    "git push -n --force origin feature",
    'git commit -m "docs: never git push --force"',
    "git commit -mn",
    'git commit -am "fix: -n"',
    'git commit -uno -m "fix: x"',
    "echo xargs git",
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
    "./scripts/check.sh && git commit -F - <<'EOF'\nfix: x\n\ngh pr merge 3\nEOF",
    "./scripts/a.sh; ./b.zsh && git commit -F - <<'EOF'\nfix: x\ngit push -f\nEOF",
    "ls -la",
    "",
]


def make_repo(root, name, branch, email=guard_git.AUTHOR_EMAIL):
    path = os.path.join(root, name)
    subprocess.run(["git", "init", "-q", "-b", branch, path], check=True)
    git(path, "config", "user.name", "Test")
    git(path, "config", "user.email", email)
    git(path, "config", "core.hooksPath", os.path.join(path, ".no-hooks"))  # fixtures commit trailers on purpose
    git(path, "config", "commit.gpgsign", "false")
    # A resolvable HEAD and the branches the push shapes name: the guard reads real history now.
    git(path, "-c", "user.email=" + guard_git.AUTHOR_EMAIL, "commit", "-q", "--allow-empty", "-m", "init")
    for other in ("develop", "wave-1", "feature-master", "master-notes"):
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


SHA = "0123456789abcdef0123456789abcdef01234567"
EXACT = "gh pr merge 7 --repo o/r --merge --match-head-commit {} --author-email {}".format(
    SHA, guard_git.AUTHOR_EMAIL
)


class RouteFormTest(unittest.TestCase):
    """Into develop only the delegated route's one form passes; it is a form check, not eligibility
    (review-findings.md, Base merges). Releases and unknown bases stay refused in every form."""

    PASSES = (
        EXACT,
        "gh pr merge 7 -R o/r -m --match-head-commit {} -A {}".format(SHA, guard_git.AUTHOR_EMAIL),
        "gh pr merge --repo=o/r --merge --match-head-commit={} --author-email={} 7".format(SHA, guard_git.AUTHOR_EMAIL),
        "gh -R o/r pr merge 7 --merge --match-head-commit {} --author-email {}".format(SHA, guard_git.AUTHOR_EMAIL),
        "gh pr merge 7 -mR o/r --match-head-commit {} -A {}".format(SHA, guard_git.AUTHOR_EMAIL),
        "gh pr merge --repo o/r --merge --match-head-commit {} --author-email {} -- 7".format(SHA, guard_git.AUTHOR_EMAIL),
        "GH_TOKEN=x " + EXACT,
        "env GH_PROMPT_DISABLED=1 " + EXACT,
        EXACT + " 2>&1",
        EXACT + " >out.txt 2>&1",
        "{ " + EXACT + "; }",
        "(" + EXACT + ")",
    )

    REFUSED = (
        # A flag missing.
        "gh pr merge 7 --repo o/r --match-head-commit {} --author-email {}".format(SHA, guard_git.AUTHOR_EMAIL),
        "gh pr merge 7 --repo o/r --merge --author-email {}".format(guard_git.AUTHOR_EMAIL),
        "gh pr merge 7 --repo o/r --merge --match-head-commit {}".format(SHA),
        "gh pr merge 7 --merge --match-head-commit {} --author-email {}".format(SHA, guard_git.AUTHOR_EMAIL),
        "GH_REPO=o/r gh pr merge 7 --merge --match-head-commit {} --author-email {}".format(SHA, guard_git.AUTHOR_EMAIL),
        # Duplicated or conflicting values: gh keeps the last, the guard reads none.
        EXACT + " -m",
        EXACT + " --match-head-commit {}".format(SHA),
        EXACT + " --match-head-commit " + "f" * 40,
        EXACT + " -A {}".format(guard_git.AUTHOR_EMAIL),
        EXACT + " --author-email other@example.com",
        EXACT + " -R o/r",
        EXACT + " --repo x/y",
        EXACT.replace("--merge", "--merge=false"),
        EXACT.replace("--merge", "--merge=true"),
        # Another method, a bypass, a later merge, a branch deletion or a custom message.
        EXACT + " --squash",
        EXACT + " -s",
        EXACT + " --rebase",
        EXACT + " -r",
        EXACT + " --admin",
        EXACT + " --auto",
        EXACT + " --disable-auto",
        EXACT + " --delete-branch",
        EXACT + " -d",
        EXACT.replace("--merge", "-ms"),
        EXACT.replace("--merge", "-md"),
        EXACT + " --body 'Co-authored-by: x <x@example.com>'",
        EXACT + " -b x",
        EXACT + " --body-file msg.txt",
        EXACT + " -F msg.txt",
        EXACT + " --subject x",
        EXACT + " -t x",
        # A head that is not a full lowercase SHA, another identity, a repository or PR not named plainly.
        EXACT.replace(SHA, SHA[:12]),
        EXACT.replace(SHA, SHA.upper()),
        EXACT.replace(SHA, SHA + "8"),
        EXACT.replace(SHA, "g" * 40),
        EXACT.replace(guard_git.AUTHOR_EMAIL, "Brandon@brandonperfetti.com"),
        EXACT.replace(guard_git.AUTHOR_EMAIL, "other@example.com"),
        EXACT.replace("--repo o/r", "--repo o"),
        EXACT.replace("--repo o/r", "--repo https://github.com/o/r"),
        EXACT.replace("merge 7", "merge"),
        EXACT.replace("merge 7", "merge '#7'"),
        EXACT.replace("merge 7", "merge https://github.com/o/r/pull/7"),
        EXACT.replace("merge 7", "merge feature-branch"),
        EXACT.replace("merge 7", "merge 7 8"),
        # Not a command on its own: something beside it could retarget the PR after the base read.
        "gh pr edit 7 --base master && " + EXACT,
        "gh pr edit 7 --base master; " + EXACT,
        EXACT + "; echo done",
        EXACT + " | cat",
        "echo $(" + EXACT + ")",
        "eval " + EXACT,
        "bash -c '" + EXACT + "'",
        "zsh -lc '" + EXACT + "'",
        "echo 7 | xargs " + EXACT.replace(" 7 ", " "),
        "(" + EXACT + ") && gh pr edit 7 --base master",
        EXACT + " &",
        "nohup " + EXACT + " &",
        EXACT + " & gh pr edit 7 --base master",
        EXACT + "\ngh pr edit 7 --base master",
        # The API stays refused into develop, whatever head precondition it carries.
        "gh api -X PUT repos/o/r/pulls/7/merge -f sha={} -f merge_method=merge".format(SHA),
        "gh api graphql -f query='mutation { mergePullRequest(input: {pullRequestId: \"x\", expectedHeadOid: \"%s\"}) { clientMutationId } }'" % SHA,
        # The live probe stays a refusal.
        "gh pr merge --help",
        EXACT + " --help",
        EXACT + " -h",
    )

    def check(self, command, base):
        with mock.patch.object(guard_git, "gh_read", return_value=base) as read:
            return guard_git.check_command(command, "/tmp"), read

    def test_the_exact_form_into_develop_passes(self):
        for command in self.PASSES:
            with self.subTest(command=command):
                self.assertIsNone(self.check(command, "develop")[0])

    def test_every_other_form_into_develop_is_refused(self):
        for command in self.REFUSED:
            with self.subTest(command=command):
                self.assertIsNotNone(self.check(command, "develop")[0])

    def test_the_exact_form_into_a_release_or_unknown_base_is_refused(self):
        for base in ("main", "master", None):
            for command in self.PASSES:
                with self.subTest(base=base, command=command):
                    reason, _ = self.check(command, base)
                    self.assertIsNotNone(reason)
                    self.assertIn(base or "could not be read", reason)

    def test_the_lookup_reads_the_named_pr_and_repository(self):
        _, read = self.check(EXACT, "develop")
        self.assertEqual(
            read.call_args[0][0],
            ["pr", "view", "7", "--repo", "o/r", "--json", "baseRefName", "--jq", ".baseRefName"],
        )

    def test_a_refusal_names_the_form(self):
        payload = json.dumps({"tool_input": {"command": EXACT + " --squash"}, "cwd": "/tmp"})
        with mock.patch.object(guard_git, "gh_read", return_value="develop"), mock.patch(
            "sys.stdin", __import__("io").StringIO(payload)
        ), mock.patch("builtins.print") as printed:
            guard_git.main()
        decision = json.loads(printed.call_args[0][0])["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn("--match-head-commit <40-hex head>", decision["permissionDecisionReason"])


class MergeBaseTest(unittest.TestCase):
    """Merges into develop, main or master stay with Brandon outside the route's one form; others
    pass (2026-10-30; the develop form, 2026-11-12)."""

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

    def test_a_dangling_or_option_like_value_is_refused(self):
        for command in ("git commit -m > /dev/null -m --no-verify", 'git commit -m >"some log" -m --no-verify', 'git commit -m ">note" -n',
                        "git commit -F >msg -n", 'git commit -m "<subject" -n', 'git merge -m ">merge" --no-verify topic',
                        'git commit -m "> note" --no-verify', 'git merge -m "> merge" --no-verify topic', 'git commit -m "<subject" > log.txt',
                        ">log git commit -m '> note' --no-verify", 'git commit -m "2>1 is true"', "git commit -m"):
            with self.subTest(command=command):
                self.assertIn("option values cannot be read", guard_git.check_command(command, self.mine) or "")

    def test_commit_identity_is_the_hooks_to_read(self):
        # The commit-msg hook reads the author git resolves; the guard predicts nothing and so never
        # false-denies `--author=Brandon` or a repo-local identity it cannot see.
        for directory, command in (
            (self.other, 'git commit -m "fix: x"'),
            (self.mine, 'git commit --author="X <{}>" -m x'.format(self.OTHER)),
            (self.mine, "git commit --author=Brandon -m x"),
            (self.other, "git commit --dry-run"),
        ):
            with self.subTest(directory=os.path.basename(directory), command=command):
                self.assertIsNone(guard_git.check_command(command, directory))
        for command in ("git commit -n -- file",
                        "git commit -m fix > -m --no-verify", "git commit -m fix 2> -F -n",
                        'echo ">" & git commit -m fix -n', 'echo ok & >log git commit -m fix -n'):
            with self.subTest(command=command):
                self.assertIn("commit-msg hook", guard_git.check_command(command, self.mine) or "")
        for command in ("git commit -m -- -n --allow-empty", 'git commit --author -- -n -m x', "git commit --pathspec-from-file --dry-run -n -m x",
                        "git commit -m --no-verify", "git commit -m --author -m clean"):
            with self.subTest(command=command):
                self.assertTrue(guard_git.check_command(command, self.mine))  # refused or denied: never allowed
        self.assertIsNone(guard_git.check_command("git commit -m x -- -n", self.mine))  # after `--`, `-n` is a path

    def test_push_reads_every_unpushed_author_and_message(self):
        commit_as(self.mine, self.OTHER)  # an older foreign commit under a clean tip
        commit_as(self.mine, guard_git.AUTHOR_EMAIL)
        self.assertIn(self.OTHER, guard_git.check_command("git push origin feature", self.mine) or "")
        git(self.mine, "branch", "-q", "tag")  # a branch called tag is a source, not the `tag <name>` marker
        self.assertIn(self.OTHER, guard_git.check_command("git push origin tag:topic", self.mine) or "")
        self.assertIn(self.OTHER, guard_git.check_command("git push origin tag", self.mine) or "")
        git(self.mine, "tag", "tag")  # and a tag called tag, pushed with the marker, is scanned too
        self.assertIn(self.OTHER, guard_git.check_command("git push origin tag tag", self.mine) or "")
        git(self.mine, "config", "remote.origin.push", "feature:topic")
        self.assertIn("chosen by", guard_git.check_command("git push origin", self.mine) or "")
        self.assertIn("chosen by", guard_git.check_command("git push origin feature", self.mine) or "")
        self.assertIn(self.OTHER, guard_git.check_command("git push origin feature:feature", self.mine) or "")  # explicit: read as written
        git(self.mine, "config", "--unset", "remote.origin.push")
        git(self.mine, "config", "push.default", "matching")
        self.assertIn("chosen by", guard_git.check_command("git push origin", self.mine) or "")
        git(self.mine, "config", "push.default", "simple")

    def test_push_destination_and_remote_are_the_ones_git_would_use(self):
        commit_as(self.mine, self.OTHER)
        # Known only to another remote: still new to origin, so still scanned.
        other_remote = os.path.join(self.tmp.name, "fork.git")
        subprocess.run(["git", "init", "-q", "--bare", other_remote], check=True)
        git(self.mine, "remote", "add", "fork", other_remote)
        git(self.mine, "push", "-q", "fork", "feature")
        self.assertIn(self.OTHER, guard_git.check_command("git push origin feature:topic", self.mine) or "")
        self.assertIsNone(guard_git.check_command("git push fork feature", self.mine))  # fork has it
        for command in ("git push {} feature".format(other_remote), "git push --repo=origin feature", "git push git@github.com:o/r.git feature"):
            with self.subTest(command=command):
                self.assertIn("named by URL", guard_git.check_command(command, self.mine) or "")
        for spelling in ("true", "yes", "1", "on"):
            git(self.mine, "config", "remote.origin.mirror", spelling)
            self.assertIn("mirror", guard_git.check_command("git push origin", self.mine) or "")
        git(self.mine, "config", "--unset", "remote.origin.mirror")
        subprocess.run(["git", "-C", self.mine, "config", "--add", "remote.origin.mirror", ""], check=False)  # valueless: true to git
        # a valueless key is written as `mirror` with no `=`; git --bool reads it as true
        with open(os.path.join(self.mine, ".git", "config"), "a") as handle:
            handle.write("[remote \"origin\"]\n\tmirror\n")
        self.assertIn("mirror", guard_git.check_command("git push origin", self.mine) or "")
        git(self.mine, "config", "--unset-all", "remote.origin.mirror")
        # The remote a bare push uses: pushRemote, then pushDefault, before @{push} or origin.
        git(self.mine, "config", "branch.feature.pushRemote", "fork")
        self.assertIsNone(guard_git.check_command("git push", self.mine))  # fork already has feature
        git(self.mine, "config", "branch.feature.pushRemote", other_remote)
        self.assertIn("named by URL", guard_git.check_command("git push", self.mine) or "")
        git(self.mine, "config", "--unset", "branch.feature.pushRemote")
        git(self.mine, "config", "remote.pushDefault", "fork")
        self.assertIsNone(guard_git.check_command("git push", self.mine))
        git(self.mine, "config", "--unset", "remote.pushDefault")
        # push.default=upstream with the feature branch tracking the release branch: the bare push lands on master.
        git(self.mine, "push", "-q", "origin", "feature:master")
        git(self.mine, "fetch", "-q", "origin")
        git(self.mine, "branch", "-q", "--set-upstream-to=origin/master", "feature")
        git(self.mine, "config", "push.default", "upstream")
        self.assertIn("release branch", guard_git.check_command("git push", self.mine) or "")
        git(self.mine, "config", "push.default", "simple")
        git(self.mine, "branch", "-q", "--unset-upstream", "feature")
        # Tags only: the tainted HEAD is not sent, a clean tag is.
        git(self.mine, "commit", "-q", "--allow-empty", "--amend", "--reset-author", "-m", "fix: clean")
        git(self.mine, "tag", "v-clean")
        commit_as(self.mine, self.OTHER)  # a tainted HEAD above the tag
        self.assertIsNone(guard_git.check_command("git push --tags origin", self.mine))
        self.assertIn(self.OTHER, guard_git.check_command("git push origin feature", self.mine) or "")
        git(self.mine, "commit", "-q", "--allow-empty", "--amend", "--reset-author", "-m", "fix: x\n\nCo-Authored-By: A <a@b>")
        git(self.mine, "push", "-q", "origin", "HEAD~1:refs/heads/other")  # the foreign commit is now on a remote
        self.assertIn("attribution trailer", guard_git.check_command("git push origin feature", self.mine) or "")
        git(self.mine, "commit", "-q", "--allow-empty", "--amend", "-m", "fix: clean")
        self.assertIsNone(guard_git.check_command("git push origin feature", self.mine))

    def test_push_scan_reads_the_repository_the_command_selects(self):
        commit_as(self.other, self.OTHER)  # `other` holds a foreign commit; cwd is the clean repo
        git(self.other, "remote", "add", "origin", os.path.join(self.tmp.name, "remote.git"))
        for command in (
            "GIT_DIR={0}/.git GIT_WORK_TREE={0} git push origin feature".format(self.other),
            "git --git-dir={0}/.git --work-tree={0} push origin feature".format(self.other),
            "git --git-dir {0}/.git push origin feature".format(self.other),
        ):
            with self.subTest(command=command):
                self.assertIn(self.OTHER, guard_git.check_command(command, self.mine) or "")
        git(self.other, "branch", "-q", "master")
        self.assertIn("release branch", guard_git.check_command("git --git-dir={0}/.git push origin HEAD:master".format(self.other), self.mine) or "")
        git(self.other, "checkout", "-q", "master")
        self.assertIn("release branch", guard_git.check_command("GIT_DIR={0}/.git GIT_WORK_TREE={0} git push origin".format(self.other), self.mine) or "")
        sentinel = os.path.join(self.tmp.name, "must-not-write")
        self.assertTrue(guard_git.check_command("git push -- origin --output={} feature".format(sentinel), self.mine))
        self.assertFalse(os.path.exists(sentinel))

    def test_a_failed_push_scan_denies(self):
        with mock.patch.object(guard_git, "git_lines", return_value=None):
            self.assertIn("could not be read", guard_git.check_command("git push origin feature", self.mine) or "")

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
