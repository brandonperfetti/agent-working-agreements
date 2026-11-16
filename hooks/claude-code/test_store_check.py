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

    def test_trees_already_there_at_session_start_never_block(self):
        self.make("initiatives", "fleet-a", "analysis", "old", "node_modules", "a.js")
        self.hook("SessionStart")
        self.assertIsNone(self.hook("Stop"))

    def test_a_resume_or_compaction_keeps_the_first_snapshot(self):
        self.hook("SessionStart")
        self.make("initiatives", "fleet-a", "analysis", "new", "node_modules", "a.js")
        self.hook("SessionStart")  # compaction re-fires SessionStart
        self.assertEqual(self.hook("Stop")["decision"], "block")

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
