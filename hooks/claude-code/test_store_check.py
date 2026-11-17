#!/usr/bin/python3
"""Tests for store_check.py. Run: /usr/bin/python3 test_store_check.py"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import store_check  # noqa: E402

SCRIPT = os.path.join(HERE, "store_check.py")


class StoreCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)  # the agent root of a disposable fleet
        self.store = os.path.join(self.root, "_agent")
        os.makedirs(os.path.join(self.store, "initiatives", "fleet-a", "analysis"))
        os.makedirs(os.path.join(self.store, "evidence"))
        self.cwd = os.path.join(self.root, ".worktrees", "repo")
        os.makedirs(self.cwd)
        self.state_dir = store_check.STATE_DIR
        store_check.STATE_DIR = os.path.join(self.root, "state")

    def tearDown(self):
        store_check.STATE_DIR = self.state_dir
        self.tmp.cleanup()

    def make(self, *parts, size=0):
        path = os.path.join(self.store, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(b"x" * size)
        return path

    def hook(self, event, session="s1"):
        return store_check.decide({"hook_event_name": event, "session_id": session, "cwd": self.cwd})

    def cli(self, *args):
        result = subprocess.run(
            [sys.executable, "-I", SCRIPT, "check", "--store", self.store, *args],
            capture_output=True, text=True,
        )
        return result.returncode, result.stdout

    # the walk

    def test_finds_the_store_above_a_worktree(self):
        self.assertEqual(store_check.find_store(self.cwd), self.store)

    def test_off_fleet_has_no_store_and_never_blocks(self):
        self.assertIsNone(store_check.find_store("/"))  # the filesystem root has no _agent/
        self.make("initiatives", "fleet-a", "node_modules", "a.js")  # this fleet's store is not above /
        for event in ("SessionStart", "Stop"):
            self.assertIsNone(store_check.decide({"hook_event_name": event, "session_id": "s", "cwd": "/"}))

    def test_lists_outermost_node_modules_only(self):
        self.make("initiatives", "fleet-a", "analysis", "run-1", "web", "node_modules", "react", "node_modules", "x.js")
        self.assertEqual(
            store_check.install_roots(self.store),
            [os.path.join(self.store, "initiatives", "fleet-a", "analysis", "run-1", "web", "node_modules")],
        )

    def test_a_node_modules_inside_an_app_bundle_is_exempt(self):
        self.make("evidence", "rollback", "T3 Code.app", "Contents", "Resources", "node_modules", "a.js")
        self.assertEqual(store_check.install_roots(self.store), [])

    def test_app_contents_copied_without_the_app_folder_are_not_exempt(self):
        path = self.make("evidence", "rollback", "previous-app-contents", "Resources", "node_modules", "a.js")
        self.assertEqual(store_check.install_roots(self.store), [os.path.dirname(path)])

    def test_a_symlinked_node_modules_is_not_followed(self):
        outside = os.path.join(self.root, "scratch", "node_modules")
        os.makedirs(os.path.join(outside, "pkg"))
        os.symlink(os.path.join(self.root, "scratch"), os.path.join(self.store, "evidence", "link"))
        self.assertEqual(store_check.install_roots(self.store), [])

    def test_a_symlink_named_node_modules_is_not_an_install(self):
        os.makedirs(os.path.join(self.root, "scratch", "pkg"))
        os.symlink(os.path.join(self.root, "scratch"), os.path.join(self.store, "evidence", "node_modules"))
        self.assertEqual(store_check.install_roots(self.store), [])

    def test_a_hard_linked_file_counts_once(self):
        first = self.make("evidence", "a.bin", size=300_000)
        for n in range(4):
            os.link(first, os.path.join(self.store, "evidence", "link{}.bin".format(n)))
        one = os.lstat(first).st_blocks * 512
        self.assertLess(store_check.disk_usage(os.path.join(self.store, "evidence"), float("inf")), 2 * one)

    # the CLI

    def test_cli_passes_a_clean_store(self):
        self.make("evidence", "receipt.json", size=100)
        self.assertEqual(self.cli(), (0, ""))

    def test_cli_fails_on_a_node_modules(self):
        self.make("initiatives", "fleet-a", "analysis", "node_modules", "a.js")
        code, out = self.cli()
        self.assertEqual(code, 1)
        self.assertIn("node_modules: " + os.path.join(self.store, "initiatives", "fleet-a"), out)

    def test_cli_fails_on_an_initiative_over_the_cap(self):
        self.make("initiatives", "fleet-a", "analysis", "big.bin", size=200_000)
        self.make("evidence", "small.bin", size=10)
        code, out = self.cli("--cap-gb", "0.0001")  # 100 kB
        self.assertEqual(code, 1)
        self.assertIn("over cap: " + os.path.join(self.store, "initiatives", "fleet-a"), out)
        self.assertNotIn("evidence", out)

    def test_cli_fails_when_the_size_walk_outruns_its_budget(self):
        self.make("evidence", "a.bin", size=10)
        code, out = self.cli("--budget", "-1")
        self.assertEqual(code, 1)
        self.assertIn("unmeasured: ", out)

    def test_cli_fails_when_a_positive_budget_expires_during_the_final_stat(self):
        path = self.make("initiatives", "fleet-a", "analysis", "receipt.json", size=100)
        clock = [0.0]
        original = os.lstat

        def slow_stat(name, *args, **kwargs):
            info = original(name, *args, **kwargs)
            if name == path:
                clock[0] += 2.0
            return info

        out = io.StringIO()
        with mock.patch.object(os, "lstat", side_effect=slow_stat), mock.patch.object(store_check.time, "monotonic", side_effect=lambda: clock[0]), mock.patch("sys.stdout", out), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(store_check.cli(["check", "--store", self.store, "--budget", "1"]), 1)
        self.assertIn("unmeasured: ", out.getvalue())

    @unittest.skipIf(os.geteuid() == 0, "root can read a mode-000 directory")
    def test_cli_fails_when_an_unreadable_tree_hides_an_install(self):
        path = self.make("evidence", "locked", "node_modules", "a.js", size=131_072)
        locked = os.path.dirname(os.path.dirname(path))
        os.chmod(locked, 0)
        try:
            code, out = self.cli("--cap-gb", "0.000065536")
            self.assertEqual(code, 1)
            self.assertIn("unmeasured: ", out)
            self.assertIn(locked, out)
        finally:
            os.chmod(locked, 0o700)

    def test_cli_reports_a_size_read_error_as_unmeasured(self):
        path = self.make("evidence", "receipt.json", size=100)
        original = os.lstat

        def fail_on_receipt(name, *args, **kwargs):
            if name == path:
                raise PermissionError(13, "Permission denied", path)
            return original(name, *args, **kwargs)

        out = io.StringIO()
        with mock.patch.object(os, "lstat", side_effect=fail_on_receipt), mock.patch("sys.stdout", out), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(store_check.cli(["check", "--store", self.store]), 1)
        self.assertIn("unmeasured: ", out.getvalue())
        self.assertIn(path, out.getvalue())

    def test_cli_keeps_its_other_findings_when_a_size_read_fails(self):
        install = os.path.dirname(self.make("initiatives", "fleet-a", "analysis", "node_modules", "a.js"))
        path = self.make("evidence", "receipt.json", size=100)
        self.make("reviews", "big.bin", size=200_000)  # walked after the tree that fails
        original = os.lstat

        def fail_on_receipt(name, *args, **kwargs):
            if name == path:
                raise FileNotFoundError(2, "No such file or directory", path)
            return original(name, *args, **kwargs)

        out = io.StringIO()
        with mock.patch.object(os, "lstat", side_effect=fail_on_receipt), mock.patch("sys.stdout", out), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(store_check.cli(["check", "--store", self.store, "--cap-gb", "0.0001"]), 1)
        lines = out.getvalue().splitlines()
        self.assertIn("node_modules: " + install, lines)
        self.assertTrue([line for line in lines if line.startswith("unmeasured: " + os.path.join(self.store, "evidence"))], lines)
        self.assertTrue([line for line in lines if line.startswith("over cap: " + os.path.join(self.store, "reviews"))], lines)

    @unittest.skipIf(os.geteuid() == 0, "root can read a mode-000 directory")
    def test_cli_lists_an_install_beside_a_folder_it_cannot_read(self):
        install = os.path.dirname(self.make("initiatives", "fleet-a", "analysis", "node_modules", "a.js"))
        locked = os.path.join(self.store, "evidence", "locked")
        os.makedirs(locked)
        os.chmod(locked, 0)
        try:
            code, out = self.cli()
        finally:
            os.chmod(locked, 0o700)
        self.assertEqual(code, 1)
        self.assertIn("node_modules: " + install, out.splitlines())
        self.assertTrue([line for line in out.splitlines() if line.startswith("unmeasured: ") and locked in line], out)

    def test_an_unreadable_hook_walk_leaves_the_snapshot_unchanged(self):
        self.hook("SessionStart")
        self.make("evidence", "node_modules", "a.js")
        with mock.patch.object(store_check, "install_roots", side_effect=PermissionError(13, "Permission denied", self.store)):
            self.assertIsNone(self.hook("Stop"))
        self.assertEqual(self.hook("Stop")["decision"], "block")

    def test_cli_with_no_store_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            result = subprocess.run([sys.executable, "-I", SCRIPT, "check"], cwd=elsewhere, capture_output=True)
        self.assertEqual(result.returncode, 2)

    # the hook pair

    def test_a_tree_made_this_session_blocks_once_with_the_fix(self):
        self.assertIsNone(self.hook("SessionStart"))
        self.make("initiatives", "fleet-a", "analysis", "repin", "node_modules", "a.js")
        reply = self.hook("Stop")
        self.assertEqual(reply["decision"], "block")
        self.assertIn(os.path.join("repin", "node_modules"), reply["reason"])
        self.assertIn("client scratch directory", reply["reason"])
        self.assertIn("receipts, logs and hashes", reply["reason"])
        self.assertIn("agent-workspace-layout.md", reply["reason"])
        self.assertIsNone(self.hook("Stop"), "reported once")

    def test_roots_past_the_tenth_are_named_at_the_next_stop(self):
        self.hook("SessionStart")
        roots = [os.path.dirname(self.make("evidence", "run-{:02d}".format(n), "node_modules", "a.js")) for n in range(11)]
        first = self.hook("Stop")
        self.assertEqual(first["decision"], "block")
        for root in roots[:10]:
            self.assertIn("- {}\n".format(root), first["reason"])
        self.assertNotIn(roots[10], first["reason"])
        self.assertIn("and 1 more", first["reason"])
        second = self.hook("Stop")
        self.assertEqual(second["decision"], "block")
        self.assertIn("- {}\n".format(roots[10]), second["reason"])
        self.assertNotIn(roots[0], second["reason"])
        self.assertIsNone(self.hook("Stop"))

    def test_trees_already_there_at_session_start_never_block(self):
        self.make("initiatives", "fleet-a", "analysis", "old", "node_modules", "a.js")
        self.hook("SessionStart")
        self.assertIsNone(self.hook("Stop"))

    def test_a_resume_or_compaction_keeps_the_first_snapshot(self):
        self.hook("SessionStart")
        self.make("initiatives", "fleet-a", "analysis", "new", "node_modules", "a.js")
        self.hook("SessionStart")  # compaction re-fires SessionStart
        self.assertEqual(self.hook("Stop")["decision"], "block")

    def test_stop_checks_the_recorded_store_after_moving_to_scratch(self):
        self.hook("SessionStart")
        self.make("evidence", "node_modules", "a.js")
        with tempfile.TemporaryDirectory() as scratch:
            payload = {"hook_event_name": "Stop", "session_id": "s1", "cwd": scratch}
            reply = store_check.decide(payload)
            self.assertEqual(reply["decision"], "block")
            self.assertIn(self.store, reply["reason"])
            self.assertIsNone(store_check.decide(payload))

    def test_stop_keeps_both_stores_when_the_session_changes_fleets(self):
        self.hook("SessionStart")
        with tempfile.TemporaryDirectory() as other:
            second = os.path.join(other, "_agent")
            os.makedirs(second)
            payload = {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": other}
            self.assertIsNone(store_check.decide(payload))
            self.make("evidence", "node_modules", "a.js")
            os.makedirs(os.path.join(second, "node_modules"))
            payload.update(hook_event_name="Stop", cwd="/")
            replies = [store_check.decide(payload), store_check.decide(payload)]
            self.assertTrue(all(reply and reply["decision"] == "block" for reply in replies))
            reasons = "\n".join(reply["reason"] for reply in replies)
            self.assertIn(self.store, reasons)
            self.assertIn(os.path.realpath(second), reasons)
            self.assertIsNone(store_check.decide(payload))

    def test_a_hook_installed_mid_session_snapshots_at_its_first_stop(self):
        self.make("initiatives", "fleet-a", "analysis", "old", "node_modules", "a.js")
        self.assertIsNone(self.hook("Stop"))
        self.make("initiatives", "fleet-a", "analysis", "new", "node_modules", "a.js")
        self.assertEqual(self.hook("Stop")["decision"], "block")

    def test_a_walk_past_its_budget_never_blocks(self):
        self.hook("SessionStart")
        self.make("initiatives", "fleet-a", "node_modules", "a.js")
        with mock.patch.object(store_check, "HOOK_WALK", -1):
            self.assertIsNone(self.hook("Stop"))
        self.assertEqual(self.hook("Stop")["decision"], "block", "the snapshot still holds")

    def test_a_start_walk_that_fails_leaves_no_baseline_and_the_stop_says_so(self):
        failures = {"out of time": mock.patch.object(store_check, "HOOK_WALK", -1),
                    "unreadable": mock.patch.object(store_check, "install_roots", side_effect=PermissionError(13, "Permission denied", self.store))}
        old = os.path.dirname(self.make("initiatives", "fleet-a", "analysis", "old", "node_modules", "a.js"))
        for session, failure in failures.items():
            with self.subTest(session):
                with failure:
                    self.assertIsNone(self.hook("SessionStart", session))
                    self.assertIsNone(self.hook("SessionStart", session), "a resume keeps the no-baseline record")
                reply = self.hook("Stop", session)
                self.assertEqual(reply["decision"], "block")
                self.assertIn("no baseline", reply["reason"])
                self.assertIn("- {}\n".format(old), reply["reason"])
                self.assertIsNone(self.hook("Stop", session), "what it listed is the baseline from here on")
                new = os.path.dirname(self.make("evidence", session.replace(" ", "-"), "node_modules", "a.js"))
                reply = self.hook("Stop", session)
                self.assertIn("- {}\n".format(new), reply["reason"])
                self.assertNotIn("no baseline", reply["reason"])

    def test_no_baseline_lists_ten_roots_and_points_at_the_cli_for_the_rest(self):
        for n in range(12):
            self.make("evidence", "run-{:02d}".format(n), "node_modules", "a.js")
        with mock.patch.object(store_check, "HOOK_WALK", -1):
            self.hook("SessionStart")
        reply = self.hook("Stop")
        self.assertEqual(reply["reason"].count("node_modules\n"), 10)
        self.assertIn("and 2 more", reply["reason"])
        self.assertIn("store_check.py check", reply["reason"])
        self.assertIsNone(self.hook("Stop"), "roots that may predate the session do not hold every stop")

    def test_no_baseline_and_a_stop_walk_that_fails_too_is_said_once(self):
        self.make("evidence", "node_modules", "a.js")
        with mock.patch.object(store_check, "HOOK_WALK", -1):
            self.hook("SessionStart")
            reply = self.hook("Stop")
            self.assertEqual(reply["decision"], "block")
            self.assertIn("no baseline", reply["reason"])
            self.assertIn("store_check.py check", reply["reason"])
            self.assertIsNone(self.hook("Stop"))
        self.assertIn(os.path.join("evidence", "node_modules"), self.hook("Stop")["reason"], "a later walk still lists what it sees")

    def test_no_baseline_and_a_store_with_no_installs_is_said_once(self):
        with mock.patch.object(store_check, "HOOK_WALK", -1):
            self.hook("SessionStart")
        reply = self.hook("Stop")
        self.assertEqual(reply["decision"], "block")
        self.assertIn("no baseline", reply["reason"])
        self.assertIn("no node_modules", reply["reason"])
        self.assertIsNone(self.hook("Stop"))

    def test_a_broken_payload_never_traps_the_agent(self):
        with mock.patch("sys.stdin", io.StringIO("not json")), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(store_check.main([]), 1)

    def test_the_hook_prints_its_reply_as_json(self):
        self.hook("SessionStart")
        self.make("initiatives", "fleet-a", "node_modules", "a.js")
        payload = json.dumps({"hook_event_name": "Stop", "session_id": "s1", "cwd": self.cwd})
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(payload)), mock.patch("sys.stdout", out):
            self.assertEqual(store_check.main([]), 0)
        self.assertEqual(json.loads(out.getvalue())["decision"], "block")


if __name__ == "__main__":
    unittest.main()
