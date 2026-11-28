"""Fixture-tree tests for store_retention.py (#328). Nothing here reads or writes the real store."""
import contextlib
import gzip
import hashlib
import io
import os
import plistlib
import shutil
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import store_retention as sr  # noqa: E402

DAY = sr.DAY
# A change time can't be set, so the clock runs 100 days ahead: every fixture's ctime is then
# 100 days old, and its mtime is whatever the test sets relative to NOW.
NOW = time.time() + 100 * DAY
PR = ("o/r", 7)


def sha(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp())
        self.store = os.path.join(self.root, "_agent")
        os.makedirs(self.store)
        self.addCleanup(shutil.rmtree, self.root)
        self.open_files, self.cwds = set(), set()
        self.lines = []

    def put(self, rel, days, data=b"x"):
        path = os.path.join(self.store, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
        self.age(rel, days)
        return path

    def age(self, rel, days):
        """Set rel, and everything inside it, to `days` old."""
        path = os.path.join(self.store, rel)
        when = NOW - days * DAY
        for top, dirs, files in os.walk(path):
            for name in dirs + files:
                os.utime(os.path.join(top, name), (when, when))
        os.utime(path, (when, when))

    def p(self, rel):
        return os.path.join(self.store, rel)

    def run_job(self, apply=True, now=NOW, prs=(PR,)):
        return sr.run(self.store, apply, now=now,
                      in_use=lambda: (set(self.open_files), set(self.cwds)),
                      prs=lambda: list(prs), out=self.lines.append)

    def snapshot(self):
        seen = {}
        for top, dirs, files in os.walk(self.root):
            for name in dirs + files:
                path = os.path.join(top, name)
                st = os.lstat(path)
                seen[os.path.relpath(path, self.root)] = (st.st_size, st.st_mtime)
        return seen

    def reports(self):
        base = self.p(sr.REPORTS)
        return sorted(os.listdir(base)) if os.path.isdir(base) else []

    def manifest(self, run):
        with open(os.path.join(self.p(sr.REPORTS), run, "manifest.tsv")) as handle:
            rows = [line.rstrip("\n").split("\t") for line in handle][1:]
        return {row[0]: row for row in rows}


class Retention(Fixture):
    def build(self):
        self.put("evidence/old/shot.png", 40, b"png bytes")
        self.put("evidence/old/receipt.md", 40)
        self.put("evidence/old/data.json", 40)
        self.put("evidence/old/notes.txt", 40)
        self.put("evidence/old/tarballs.sha256", 40)
        self.put("evidence/old/pkg.tar.gz", 40, b"tar bytes")
        self.put("evidence/old/served/page.html", 40)
        self.put("evidence/old/agent.sqlite.bak-1", 40)
        self.put("evidence/young/shot.png", 1)
        self.put("evidence/open/run.png", 40)
        self.open_files.add(self.p("evidence/open/run.png"))
        self.put("initiatives/x/handoffs/clip.mp4", 40)
        self.cwds.add(self.p("initiatives/x/handoffs"))
        self.cwds.add(self.store)  # a shell at the store root protects only the root
        self.put("analysis/pr/review.md", 40,
                 b"Receipt for https://github.com/o/r/pull/7: see screens/a.png and `b-cited.png`.")
        self.put("analysis/pr/screens/a.png", 40)
        self.put("analysis/pr/b-cited.png", 40)
        self.put("analysis/pr/screens/c.png", 40)
        self.put("analysis/closed/review.md", 40, b"https://github.com/o/r/pull/70 cites shot.png")
        self.put("analysis/closed/shot.png", 40)
        self.put("experiments/app/node_modules/pkg/package.json", 40)
        self.put("experiments/app/node_modules/pkg/README.md", 40)
        self.age("experiments/app/node_modules", 40)
        self.put("experiments/app/package.json", 40)
        self.put("experiments/site/dist/bundle.js", 40)
        self.age("experiments/site/dist", 40)
        self.put("experiments/notes/dist/README.md", 40)
        self.put("experiments/notes/dist/bundle.js", 40)
        self.put("experiments/notes/dist/shot.png", 40)
        self.put("evidence/app/Old.app/Contents/MacOS/Old", 40)
        self.age("evidence/app/Old.app", 40)
        self.put("evidence/rollback/Contents/Resources/app.asar", 40)
        self.age("evidence/rollback/Contents", 40)
        self.put("evidence/clone/.git/HEAD", 40)
        self.put("evidence/clone/shot.png", 40)
        self.put(".worktrees/w/shot.png", 40)
        self.put("logs/old.log", 40)
        self.put("logs/mid.log", 15, b"line\n" * 1000)
        self.put("logs/fresh.log", 3)
        self.put("_trash/manual/left.png", 400)
        outside = os.path.join(self.root, "outside.png")
        with open(outside, "wb") as handle:
            handle.write(b"o")
        os.utime(outside, (NOW - 400 * DAY,) * 2)
        os.symlink(outside, self.p("evidence/old/link.png"))

    def test_never_moved(self):
        self.build()
        mid_sha = sha(self.p("logs/mid.log"))
        self.assertEqual(self.run_job(), 0, self.lines)
        for rel in ["evidence/old/receipt.md", "evidence/old/data.json", "evidence/old/notes.txt",
                    "evidence/old/tarballs.sha256", "evidence/young/shot.png",
                    "evidence/open/run.png", "initiatives/x/handoffs/clip.mp4",
                    "analysis/pr/screens/a.png", "analysis/pr/b-cited.png",
                    "experiments/app/package.json", "experiments/notes/dist/README.md",
                    "experiments/notes/dist/bundle.js", "evidence/clone/shot.png",
                    ".worktrees/w/shot.png", "logs/fresh.log", "_trash/manual/left.png"]:
            self.assertTrue(os.path.exists(self.p(rel)), rel)
        self.assertTrue(os.path.islink(self.p("evidence/old/link.png")))
        self.assertTrue(os.path.exists(os.path.join(self.root, "outside.png")))
        gz = self.p("logs/mid.log.gz")
        self.assertFalse(os.path.exists(self.p("logs/mid.log")))
        with gzip.open(gz, "rb") as handle:
            self.assertEqual(hashlib.sha256(handle.read()).hexdigest(), mid_sha)
        self.assertAlmostEqual(os.lstat(gz).st_mtime, NOW - 15 * DAY, delta=1)
        (run,) = self.reports()
        with open(os.path.join(self.p(sr.REPORTS), run, "compressed.tsv")) as handle:
            self.assertIn(mid_sha, handle.read())

    def test_old_heavy_files_trashed_with_manifest(self):
        self.build()
        shot_sha = sha(self.p("evidence/old/shot.png"))
        self.assertEqual(self.run_job(), 0, self.lines)
        (run,) = self.reports()
        rows = self.manifest(run)
        moved = {"evidence/old/shot.png": "media", "evidence/old/pkg.tar.gz": "archive",
                 "evidence/old/served/page.html": "served capture",
                 "evidence/old/agent.sqlite.bak-1": "database",
                 "analysis/pr/screens/c.png": "media", "analysis/closed/shot.png": "media",
                 "experiments/app/node_modules": "install",
                 "experiments/site/dist": "build output",
                 "experiments/notes/dist/shot.png": "media",
                 "evidence/app/Old.app": "app bundle", "evidence/rollback/Contents": "app bundle",
                 "logs/old.log": "log"}
        self.assertEqual(set(rows), set(moved))
        for rel, kind in moved.items():
            self.assertEqual(rows[rel][1], kind, rel)
            self.assertFalse(os.path.lexists(self.p(rel)), rel)
            self.assertTrue(os.path.lexists(self.p(os.path.join("_trash", run, rel))), rel)
            self.assertRegex(rows[rel][3], "^[0-9a-f]{64}$")
        self.assertEqual(rows["evidence/old/shot.png"][3], shot_sha)
        self.assertEqual(rows["evidence/old/shot.png"][2], str(len(b"png bytes")))

    def test_second_run_does_nothing_new(self):
        self.build()
        self.run_job()
        before = {k: v for k, v in self.snapshot().items() if sr.REPORTS not in k}
        self.assertEqual(self.run_job(), 0, self.lines)
        after = {k: v for k, v in self.snapshot().items() if sr.REPORTS not in k}
        self.assertEqual(before, after)
        second = self.reports()[1]
        self.assertEqual(self.manifest(second), {})
        for table in ("compressed.tsv", "purged.tsv"):
            with open(os.path.join(self.p(sr.REPORTS), second, table)) as handle:
                self.assertEqual(len(handle.readlines()), 1, table)

    def test_trash_purged_after_thirty_days_manifest_kept(self):
        self.build()
        self.run_job()
        (first,) = self.reports()
        batch = self.p(os.path.join("_trash", first))
        self.run_job(now=NOW + 29 * DAY)
        self.assertTrue(os.path.isdir(batch))
        self.run_job(now=NOW + 31 * DAY)
        self.assertFalse(os.path.exists(batch))
        self.assertTrue(os.path.exists(os.path.join(self.p(sr.REPORTS), first, "manifest.tsv")))
        self.assertTrue(os.path.exists(self.p("_trash/manual/left.png")))
        last = self.reports()[-1]
        with open(os.path.join(self.p(sr.REPORTS), last, "purged.tsv")) as handle:
            self.assertIn("_trash/" + first, handle.read())

    def test_open_file_in_trash_holds_its_batch(self):
        self.build()
        self.run_job()
        (first,) = self.reports()
        self.open_files.add(self.p(os.path.join("_trash", first, "evidence/old/shot.png")))
        self.run_job(now=NOW + 31 * DAY)
        self.assertTrue(os.path.isdir(self.p(os.path.join("_trash", first))))

    def test_dry_run_changes_nothing(self):
        self.build()
        before = self.snapshot()
        self.assertEqual(self.run_job(apply=False), 0)
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(any("would trash" in line and "evidence/old/shot.png" in line
                            for line in self.lines))
        self.assertTrue(any("would compress" in line for line in self.lines))
        self.assertIn("Nothing changed.", self.lines[-1])

    def test_refuses_when_lsof_fails(self):
        self.build()
        def kept(snapshot):  # all but the report and the lock a refused run leaves
            return {k: v for k, v in snapshot.items()
                    if "store-retention" not in k and k != "_agent/_trash" and k != "_agent/evidence"}

        before = kept(self.snapshot())

        def broken():
            raise sr.Refused("lsof could not run")

        status = sr.run(self.store, True, now=NOW, in_use=broken, prs=lambda: [PR],
                        out=self.lines.append)
        self.assertEqual(status, 3)
        self.assertEqual(before, kept(self.snapshot()))
        (run,) = self.reports()
        with open(os.path.join(self.p(sr.REPORTS), run, "report.md")) as handle:
            self.assertIn("Refused", handle.read())


class Guards(Fixture):
    def test_recent_change_time_is_kept(self):
        # Real clock: mtime 40 days back, but the file was written (ctime) just now.
        self.put("evidence/copied.png", 0)
        when = time.time() - 40 * DAY
        os.utime(self.p("evidence/copied.png"), (when, when))
        sr.run(self.store, True, now=time.time(), in_use=lambda: (set(), set()),
               prs=lambda: [], out=self.lines.append)
        self.assertTrue(os.path.exists(self.p("evidence/copied.png")))

    def test_lsof_sees_an_open_file(self):
        if not shutil.which("lsof"):
            self.skipTest("no lsof")
        path = self.put("evidence/held.log", 40)
        with open(path, "ab"):
            open_files, _ = sr.lsof_paths(self.store)
        self.assertIn(path, open_files)

    def test_store_must_be_named_agent(self):
        other = os.path.join(self.root, "store")
        os.makedirs(other)
        with self.assertRaises(SystemExit) as caught, \
                contextlib.redirect_stderr(io.StringIO()):
            sr.main(["--store", other])
        self.assertEqual(caught.exception.code, 2)

    def test_kinds(self):
        for name in ("a.md", "a.json", "a.txt", "a.sha256", "SHA256SUMS", "latest-mac.yml",
                     "a.jsonl", "a.js", "a.pdf"):
            self.assertIsNone(sr.file_kind(name), name)
        for name, kind in (("a.PNG", "media"), ("a.mp4", "media"), ("a.rsc", "served capture"),
                           ("a.dmg", "archive"), ("a.db", "database"), ("a.log.gz", "log")):
            self.assertEqual(sr.file_kind(name), kind, name)


class LaunchAgent(unittest.TestCase):
    def test_plist_renders(self):
        with open(os.path.join(HERE, "ai.sansfaux.agent-store-retention.plist")) as handle:
            text = handle.read().replace("@HOME@", "/Users/someone")
        self.assertNotIn("@", text.replace("@HOME@", ""))
        plist = plistlib.loads(text.encode())
        self.assertEqual(plist["Label"], "ai.sansfaux.agent-store-retention")
        args = plist["ProgramArguments"]
        self.assertEqual(args[:2], ["/usr/bin/python3", "-I"])
        self.assertTrue(args[2].endswith("/scripts/store-retention/store_retention.py"))
        self.assertEqual(args[3:], ["--store", "/Users/someone/dev/sansfaux/_agent", "--apply"])
        self.assertEqual(plist["StartCalendarInterval"]["Day"], 1)


if __name__ == "__main__":
    unittest.main()
