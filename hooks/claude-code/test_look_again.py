#!/usr/bin/python3
"""Tests for look_again.py. Run: /usr/bin/python3 test_look_again.py"""
import datetime
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import look_again  # noqa: E402

START = 1_800_000_000.0  # a fixed epoch; each test sets file times relative to it


def stamp(epoch):
    return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class LookAgainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.transcript = os.path.join(self.root, "session.jsonl")
        self.entries = []
        self.calls = 0
        look_again.STATE_DIR = os.path.join(self.root, "state")
        self.skip = look_again.SKIP

    def tearDown(self):
        look_again.SKIP = self.skip
        self.tmp.cleanup()

    def file(self, name, mtime):
        path = os.path.join(self.root, name)
        with open(path, "w") as handle:
            handle.write(name)
        os.utime(path, (mtime, mtime))
        return path

    def tool(self, name, args, at, error=False):
        self.calls += 1
        use_id = "toolu_{}".format(self.calls)
        self.entries.append(
            {"type": "assistant", "timestamp": stamp(at - 1),
             "message": {"content": [{"type": "tool_use", "id": use_id, "name": name, "input": args}]}}
        )
        self.entries.append(
            {"type": "user", "timestamp": stamp(at),
             "message": {"content": [{"type": "tool_result", "tool_use_id": use_id, "is_error": error}]}}
        )

    def prompt(self, at, kind="human", meta=False, text="next question"):
        entry = {"type": "user", "timestamp": stamp(at), "message": {"role": "user", "content": text}}
        if kind:
            entry["origin"] = {"kind": kind}
        if meta:
            entry["isMeta"] = True
        self.entries.append(entry)

    def decide(self, active=False):
        with open(self.transcript, "w") as handle:
            for entry in self.entries:
                handle.write(json.dumps(entry) + "\n")
        return look_again.decide(
            {"session_id": "s1", "transcript_path": self.transcript, "stop_hook_active": active}
        )

    def test_unchanged_file_lets_the_agent_stop(self):
        path = self.file("plan.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        self.assertIsNone(self.decide())

    def test_file_changed_after_the_read_blocks_once(self):
        path = self.file("plan.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.utime(path, (START + 60, START + 60))
        reply = self.decide()
        self.assertEqual(reply["decision"], "block")
        self.assertIn(path, reply["reason"])
        last_look = datetime.date.fromtimestamp(START + 10)
        if last_look != datetime.date.today():
            self.assertIn(last_look.isoformat(), reply["reason"], "not today: dated")
        self.assertIsNone(self.decide(active=True), "the same change is reported once")

    def test_reading_it_again_clears_it(self):
        path = self.file("plan.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.utime(path, (START + 60, START + 60))
        self.tool("Read", {"file_path": path}, START + 70)
        self.assertIsNone(self.decide())

    def test_the_agents_own_write_is_not_a_change(self):
        path = self.file("compose.yaml", START + 20)
        self.tool("Read", {"file_path": path}, START + 10)
        self.tool("Edit", {"file_path": path}, START + 21)
        self.assertIsNone(self.decide())

    def test_a_bash_command_naming_the_file_counts_as_seen(self):
        path = self.file("compose.yaml", START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.utime(path, (START + 30, START + 30))
        self.tool("Bash", {"command": "sed -i '' 's/16/17/' compose.yaml"}, START + 31)
        self.assertIsNone(self.decide())

    def test_a_bash_command_naming_another_file_of_the_same_name_does_not_count(self):
        os.mkdir(os.path.join(self.root, "a"))
        path = self.file(os.path.join("a", "config.json"), START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.utime(path, (START + 30, START + 30))
        self.tool("Bash", {"command": "cat /elsewhere/b/config.json"}, START + 31)
        self.tool("Bash", {"command": "cat b/config.json config.json.bak"}, START + 32)
        self.assertIn(path, self.decide()["reason"])

    def test_a_bash_command_naming_its_path_counts_as_seen(self):
        os.mkdir(os.path.join(self.root, "a"))
        path = self.file(os.path.join("a", "config.json"), START)
        for command in ("cat {}".format(path), "cat a/config.json", "cd x && cat ../a/config.json"):
            self.entries = []
            self.tool("Read", {"file_path": path}, START + 10)
            os.utime(path, (START + 30, START + 30))
            self.tool("Bash", {"command": command}, START + 31)
            self.entries[-1]["cwd"] = os.path.join(self.root, "x") if "cd x" in command else self.root
            self.assertIsNone(self.decide(), command)

    def test_files_past_the_list_are_named_at_the_next_stop(self):
        paths = [self.file("f{:02}.md".format(n), START) for n in range(look_again.MAX_LISTED + 2)]
        for path in paths:
            self.tool("Read", {"file_path": path}, START + 10)
            os.utime(path, (START + 60, START + 60))
        first = self.decide()["reason"]
        self.assertIn("and 2 more", first)
        second = self.decide(active=True)["reason"]
        for path in paths[-2:]:
            self.assertNotIn(path, first)
            self.assertIn(path, second)
        self.assertIsNone(self.decide(active=True))

    def test_a_bare_name_in_the_session_directory_is_that_directory_s_file(self):
        os.mkdir(os.path.join(self.root, "a"))
        path = self.file(os.path.join("a", "config.json"), START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.utime(path, (START + 30, START + 30))
        self.tool("Bash", {"command": "cat config.json"}, START + 31)
        self.entries[-1]["cwd"] = self.root
        self.assertIn(path, self.decide()["reason"])

    def test_a_file_the_agent_removed_in_bash_is_not_reported(self):
        for command in ("rm draft.md", "git mv draft.md old.md", "cat x && unlink draft.md"):
            self.entries = []
            path = self.file("draft.md", START)
            self.tool("Read", {"file_path": path}, START + 10)
            self.tool("Bash", {"command": command}, START + 20)
            os.remove(path)
            self.assertIsNone(self.decide(), command)

    def test_a_file_named_in_bash_then_deleted_elsewhere_is_reported(self):
        for command in ("wc -l draft.md", "rm -f draft.md.bak && cat draft.md",
                        "sed -i x draft.md; rm -rf node_modules", "git rm --cached draft.md",
                        "jq . a > tmp && mv tmp draft.md", "git mv old.md draft.md",
                        "mv tmp draft.md 2>/dev/null", "mv -f tmp draft.md >log # done",
                        "mv tmp draft.md \\\n  && echo ok"):
            self.entries = []
            path = self.file("draft.md", START)
            self.tool("Read", {"file_path": path}, START + 10)
            self.tool("Bash", {"command": command}, START + 20)
            os.remove(path)
            self.assertIn("now gone", self.decide()["reason"], command)
            os.remove(os.path.join(look_again.STATE_DIR, "s1.json"))

    def test_a_dash_c_that_does_not_change_directory_keeps_the_match_strict(self):
        os.mkdir(os.path.join(self.root, "a"))
        path = self.file(os.path.join("a", "config.json"), START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.utime(path, (START + 30, START + 30))
        self.tool("Bash", {"command": "grep -C 3 port config.json"}, START + 31)
        self.entries[-1]["cwd"] = self.root
        self.assertIn(path, self.decide()["reason"])

    def test_the_last_block_names_every_file_left(self):
        count = look_again.MAX_LISTED * look_again.MAX_BLOCKS + 5
        paths = [self.file("f{:02}.md".format(n), START) for n in range(count)]
        for path in paths:
            self.tool("Read", {"file_path": path}, START + 10)
            os.utime(path, (START + 60, START + 60))
        reasons = [self.decide(active=look > 0)["reason"] for look in range(look_again.MAX_BLOCKS)]
        self.assertNotIn("more", reasons[-1])
        for path in paths:
            self.assertTrue(any(path + " (" in reason for reason in reasons), path)
        self.assertIsNone(self.decide(active=True))

    def test_a_file_touched_before_the_last_prompt_does_not_count(self):
        path = self.file("AGENTS.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        self.prompt(START + 20)
        os.utime(path, (START + 60, START + 60))
        self.assertIsNone(self.decide())

    def test_hook_feedback_messages_and_notifications_are_not_prompts(self):
        path = self.file("plan.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        self.prompt(START + 20, kind="peer", meta=True)
        self.prompt(START + 21, kind="task-notification")
        self.prompt(START + 22, meta=True)
        self.prompt(START + 23, kind=None, text="<system-reminder>\nThe session you started finished.")
        self.prompt(START + 24, kind=None, text="<ci-monitor-event>check failed</ci-monitor-event>")
        os.utime(path, (START + 60, START + 60))
        self.assertIn(path, self.decide()["reason"])

    def test_a_file_touched_after_the_prompt_counts(self):
        path = self.file("plan.md", START)
        self.prompt(START + 5)
        self.tool("Read", {"file_path": path}, START + 10)
        os.utime(path, (START + 60, START + 60))
        self.assertIn(path, self.decide()["reason"])

    def test_a_typed_prompt_after_an_injected_notice_still_counts(self):
        path = self.file("plan.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        self.prompt(START + 20, text=[{"type": "text", "text": "<system-reminder>context</system-reminder>"},
                                      {"type": "text", "text": "next question"}])
        os.utime(path, (START + 60, START + 60))
        self.assertIsNone(self.decide())

    def test_a_gone_file_named_again_in_bash_is_reported_once(self):
        path = self.file("draft.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.remove(path)
        self.assertIn("now gone", self.decide()["reason"])
        self.tool("Bash", {"command": "test -e draft.md || echo gone"}, START + 20)
        self.assertIsNone(self.decide(active=True))

    def test_a_prompt_without_origin_still_counts(self):
        path = self.file("plan.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        self.prompt(START + 20, kind=None, text="Background: the task from another session")
        os.utime(path, (START + 60, START + 60))
        self.assertIsNone(self.decide())

    def test_a_file_gone_again_after_it_came_back_is_reported_again(self):
        path = self.file("draft.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.remove(path)
        self.assertIn("now gone", self.decide()["reason"])
        self.prompt(START + 20)
        self.file("draft.md", START + 25)
        self.tool("Read", {"file_path": path}, START + 30)
        os.remove(path)
        self.assertIn("now gone", self.decide()["reason"])

    def test_a_removed_folder_is_cleanup_not_a_change(self):
        folder = os.path.join(self.root, "worktree")
        os.mkdir(folder)
        path = self.file(os.path.join("worktree", "draft.md"), START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.remove(path)
        os.rmdir(folder)
        self.assertIsNone(self.decide())

    def test_claude_code_temp_tree_is_skipped(self):
        self.assertIn("/private/tmp/claude-{}/".format(os.getuid()), look_again.SKIP)
        look_again.SKIP = look_again.SKIP + (os.path.join(self.root, "scratch") + os.sep,)
        os.mkdir(os.path.join(self.root, "scratch"))
        path = self.file(os.path.join("scratch", "notes.md"), START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.utime(path, (START + 60, START + 60))
        self.assertIsNone(self.decide())

    def test_a_deleted_file_is_reported(self):
        path = self.file("draft.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        os.remove(path)
        self.assertIn("now gone", self.decide()["reason"])

    def test_a_failed_read_is_ignored(self):
        path = self.file("plan.md", START + 60)
        self.tool("Read", {"file_path": path}, START + 10, error=True)
        self.assertIsNone(self.decide())

    def test_a_chain_of_stops_is_sent_back_at_most_max_blocks_times(self):
        path = self.file("app.log", START)
        self.tool("Read", {"file_path": path}, START + 10)
        for look in range(look_again.MAX_BLOCKS):
            os.utime(path, (START + 100 + look, START + 100 + look))
            self.assertEqual(self.decide(active=look > 0)["decision"], "block")
        os.utime(path, (START + 200, START + 200))
        reply = self.decide(active=True)
        self.assertNotIn("decision", reply)
        self.assertIn("stopping anyway", reply["systemMessage"])

    def test_a_new_stop_chain_starts_the_count_again(self):
        path = self.file("app.log", START)
        self.tool("Read", {"file_path": path}, START + 10)
        for look in range(look_again.MAX_BLOCKS + 1):
            os.utime(path, (START + 100 + look, START + 100 + look))
            self.decide(active=True)
        os.utime(path, (START + 300, START + 300))
        self.assertEqual(self.decide(active=False)["decision"], "block")

    def test_sidechain_entries_are_skipped(self):
        path = self.file("plan.md", START)
        self.tool("Read", {"file_path": path}, START + 10)
        for entry in self.entries:
            entry["isSidechain"] = True
        os.utime(path, (START + 60, START + 60))
        self.assertIsNone(self.decide())

    def test_a_missing_transcript_lets_the_agent_stop(self):
        reply = look_again.decide({"session_id": "s1", "transcript_path": os.path.join(self.root, "none")})
        self.assertIsNone(reply)

    def test_the_script_never_traps_the_agent_on_bad_input(self):
        run = subprocess.run(
            [sys.executable, os.path.join(HERE, "look_again.py")],
            input="not json", capture_output=True, text=True,
        )
        self.assertEqual(run.returncode, 1)
        self.assertEqual(run.stdout, "")
        self.assertIn("look_again:", run.stderr)


if __name__ == "__main__":
    unittest.main()
