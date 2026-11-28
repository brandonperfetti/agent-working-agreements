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
        self.put("evidence/old/served/page.rsc", 40)
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
        self.put("evidence/app/Old.app/Contents/Info.plist", 40)
        self.put("evidence/app/Old.app/Contents/Resources/package.json", 40)
        self.age("evidence/app/Old.app", 40)
        self.put("evidence/rollback/Contents/Resources/app.asar", 40)
        self.put("evidence/rollback/Contents/Info.plist", 40)
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
                 "evidence/old/served/page.rsc": "served capture",
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
                     "a.jsonl", "a.js", "a.pdf", "a.html"):
            self.assertIsNone(sr.file_kind(name, 10), name)
        for name, kind in (("a.PNG", "media"), ("a.mp4", "media"), ("a.rsc", "served capture"),
                           ("a.dmg", "archive"), ("a.db", "database"), ("a.log.gz", "log")):
            self.assertEqual(sr.file_kind(name, 10), kind, name)
        self.assertEqual(sr.file_kind("a.html", sr.HTML_MIN), "served capture")

    def test_lookalike_trees_are_walked_not_taken(self):
        # Review of e82e1ed: a folder matched by name was taken whole with its receipts or .git.
        self.put("projects/site.app/.git/HEAD", 40)
        self.put("projects/site.app/shot.png", 40)
        self.put("projects/dist/.git/HEAD", 40)
        self.put("analysis/why-node_modules-bloat/findings.md", 40)
        self.put("analysis/why-node_modules-bloat/data.json", 40)
        self.put("analysis/why-node_modules-bloat/chart.png", 40)
        self.put("evidence/sansfaux.app/review.md", 40)
        self.put("evidence/sansfaux.app/hashes.sha256", 40)
        self.put("evidence/run1/out/result.json", 40)
        self.put("evidence/app/node_modules/pkg/.git/HEAD", 40)
        self.put("evidence/app/node_modules/pkg/index.js", 40)
        self.put("rationale/proto.html", 40, b"<html>" * 10)
        self.put("evidence/big.html", 40, b"x" * sr.HTML_MIN)
        for rel in ("projects", "analysis", "evidence", "rationale"):
            self.age(rel, 40)
        self.assertEqual(self.run_job(prs=()), 0, self.lines)
        for rel in ("projects/site.app/.git/HEAD", "projects/site.app/shot.png",
                    "projects/dist/.git/HEAD", "analysis/why-node_modules-bloat/findings.md",
                    "analysis/why-node_modules-bloat/data.json", "evidence/sansfaux.app/review.md",
                    "evidence/sansfaux.app/hashes.sha256", "evidence/run1/out/result.json",
                    "evidence/app/node_modules/pkg/.git/HEAD", "rationale/proto.html"):
            self.assertTrue(os.path.exists(self.p(rel)), rel)
        rows = self.manifest(self.reports()[0])
        self.assertEqual(set(rows), {"analysis/why-node_modules-bloat/chart.png", "evidence/big.html"})

    def test_receipts_deep_in_lookalike_trees_stay(self):
        # Re-review of c10dcf6: a tree matched by name was taken with receipts below its top.
        self.put("notes/why-node_modules-bloat/analysis/report.md", 40)
        self.put("proto/demo.app/notes/decision.md", 40)
        self.put("proto/demo.app/shot.png", 40)
        self.put("evidence/run-42/out/results/summary.json", 40)
        self.put("evidence/run-43/dist/events.jsonl", 40)
        self.put("evidence/Fake.app/Contents/Info.plist", 40)
        self.put("evidence/Fake.app/notes.md", 40)
        for rel in ("notes", "proto", "evidence"):
            self.age(rel, 40)
        self.assertEqual(self.run_job(prs=()), 0, self.lines)
        for rel in ("notes/why-node_modules-bloat/analysis/report.md",
                    "proto/demo.app/notes/decision.md", "evidence/run-42/out/results/summary.json",
                    "evidence/run-43/dist/events.jsonl", "evidence/Fake.app/notes.md"):
            self.assertTrue(os.path.exists(self.p(rel)), rel)
        self.assertEqual(set(self.manifest(self.reports()[0])), {"proto/demo.app/shot.png"})

    def test_citation_forms(self):
        self.put("evidence/r-pr-7.md", 40, b"Folder `evidence/my run/`, link [s](shot%20one.png),"
                 b" and login-fail.png from the build; also see evidence/deep/a/b/kept.png.")
        self.put("evidence/my run/shot.png", 40)
        self.put("evidence/shot one.png", 40)
        self.put("evidence/run-44/build/login-fail.png", 40)
        self.age("evidence/run-44/build", 40)
        self.put("evidence/deep/a/b/kept.png", 40)
        self.put("evidence/deep/a/b/other.png", 40)
        self.put("evidence/deep/a/sibling.png", 40)
        self.assertEqual(self.run_job(), 0, self.lines)
        for rel in ("evidence/my run/shot.png", "evidence/shot one.png",
                    "evidence/run-44/build/login-fail.png", "evidence/deep/a/b/kept.png"):
            self.assertTrue(os.path.exists(self.p(rel)), rel)
        # a cited deep path protects itself, not the folders above it
        self.assertEqual(set(self.manifest(self.reports()[0])),
                         {"evidence/deep/a/b/other.png", "evidence/deep/a/sibling.png"})

    def test_citation_forms_round_three(self):
        # Round-3 review of 27cadf3: folder citations with a space in these forms were missed.
        self.put("proj/reviews/r-pr-7.md", 40, b"Tree: `_agent/proj/My Run/node_modules/pkg/i.js`."
                 b" Screens are in _agent/proj/My Shots. Also `../Old Shots/` and"
                 b" `_agent/Client Shots/`. Wait... and so on.")
        self.put("proj/My Run/node_modules/pkg/i.js", 40)
        self.age("proj/My Run/node_modules", 40)
        self.put("proj/My Shots/a.png", 40)
        self.put("proj/Old Shots/a.png", 40)
        self.put("Client Shots/a.png", 40)
        self.put("proj/elsewhere/z.png", 40)  # `...` must not cite the receipt's parent
        self.assertEqual(self.run_job(), 0, self.lines)
        for rel in ("proj/My Run/node_modules", "proj/My Shots/a.png", "proj/Old Shots/a.png",
                    "Client Shots/a.png"):
            self.assertTrue(os.path.exists(self.p(rel)), rel)
        self.assertEqual(set(self.manifest(self.reports()[0])), {"proj/elsewhere/z.png"})

    def test_bundle_shaped_folder_with_receipts_is_walked(self):
        self.put("proj/teardown/Info.plist", 40)
        self.put("proj/teardown/MacOS/bin", 40)
        self.put("proj/teardown/Resources/findings.md", 40)
        self.put("proj/teardown/Library/notes.json", 40)
        self.age("proj", 40)
        self.assertEqual(self.run_job(prs=()), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("proj/teardown/Resources/findings.md")))
        self.assertTrue(os.path.exists(self.p("proj/teardown/Library/notes.json")))

    def test_compressed_receipts_stay(self):
        self.put("evidence/events.jsonl.gz", 40)
        self.put("evidence/report.csv.gz", 40)
        self.put("evidence/x.json.server.log.gz", 40)
        self.assertEqual(self.run_job(prs=()), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("evidence/events.jsonl.gz")))
        self.assertTrue(os.path.exists(self.p("evidence/report.csv.gz")))
        self.assertEqual(set(self.manifest(self.reports()[0])), {"evidence/x.json.server.log.gz"})

    def test_compressed_receipt_in_a_tree_holds_it(self):
        # Round-4 review of 927ffb8.
        self.put("run/out/events.jsonl.gz", 40)
        self.put("run/out/shot.png", 40)
        self.put("old.zip", 40)  # a heavy file at the store's top level
        self.age("run", 40)
        self.assertEqual(self.run_job(prs=()), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("run/out/events.jsonl.gz")))
        self.assertEqual(set(self.manifest(self.reports()[0])), {"run/out/shot.png", "old.zip"})

    def test_hash_file_receipt_cites(self):
        # Review of e16af5d: hash files had dropped out of the receipts read for citations.
        self.put("h/r-pr-7.sha256", 40, b"o/r#7\nabc  shot2.png\n")
        self.put("h/shot2.png", 40)
        self.assertEqual(self.run_job(), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("h/shot2.png")))

    def test_receipt_reading_coderabbit_preflight(self):
        # CodeRabbit preflight of 65e9e3e: compressed, long and unreadable receipts.
        os.makedirs(self.p("a"))
        with gzip.open(self.p("a/r.md.gz"), "wb") as handle:
            handle.write(b"o/r#7 cites a/zipped.png")
        os.utime(self.p("a/r.md.gz"), (NOW - 40 * DAY,) * 2)
        self.put("a/zipped.png", 40)
        self.put("b/long.md", 40, b"x" * (5 * 1024 * 1024) + b" o/r#7 cites b/late.png")
        self.put("b/late.png", 40)
        self.put("c/locked.md", 40, b"o/r#7 cites c/shot.png")
        self.put("c/shot.png", 40)
        self.put("d/free.png", 40)
        locked = os.geteuid() != 0
        if locked:
            os.chmod(self.p("c/locked.md"), 0)
            self.addCleanup(os.chmod, self.p("c/locked.md"), 0o644)
        self.assertEqual(self.run_job(), 0, self.lines)
        for rel in ("a/zipped.png", "b/late.png", "c/shot.png"):
            self.assertTrue(os.path.exists(self.p(rel)), rel)
        self.assertFalse(os.path.exists(self.p("d/free.png")))
        if locked:
            with open(os.path.join(self.p(sr.REPORTS), self.reports()[0], "report.md")) as handle:
                self.assertIn("receipt not read, its folder kept: c/locked.md", handle.read())

    def test_lone_unreadable_receipt_keeps_its_folder(self):
        # Review of c86fd18: with no readable citing receipt, the unreadable one protected nothing.
        if os.geteuid() == 0:
            self.skipTest("root reads any file")
        self.put("c/locked.md", 40, b"o/r#7 cites c/shot.png")
        self.put("c/shot.png", 40)
        self.put("d/free.png", 40)
        os.chmod(self.p("c/locked.md"), 0)
        self.addCleanup(os.chmod, self.p("c/locked.md"), 0o644)
        self.assertEqual(self.run_job(), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("c/shot.png")))
        self.assertFalse(os.path.exists(self.p("d/free.png")))

    def test_corrupt_compressed_receipt_keeps_its_folder(self):
        os.makedirs(self.p("e"))
        with open(self.p("e/r.md.gz"), "wb") as handle:
            handle.write(gzip.compress(b"o/r#7 cites e/shot.png")[:12] + b"\xff" * 40)
        os.utime(self.p("e/r.md.gz"), (NOW - 40 * DAY,) * 2)
        self.put("e/shot.png", 40)
        self.assertEqual(self.run_job(), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("e/shot.png")))

    def test_compressed_log_keeps_its_mode(self):
        path = self.put("logs/mid.log", 15, b"line\n")
        os.chmod(path, 0o644)
        self.age("logs/mid.log", 15)
        self.assertEqual(self.run_job(prs=()), 0, self.lines)
        self.assertEqual(os.lstat(self.p("logs/mid.log.gz")).st_mode & 0o777, 0o644)

    def test_short_pr_forms_and_ancestor_relative_folders(self):
        # Whole-branch review of fe1674f.
        self.put("pull-requests/2026-10-26-r-pr7.md", 40, b"Review notes: see shots/b.png")
        self.put("pull-requests/shots/b.png", 40)
        self.put("reviews/x.md", 40, b"Review of r PR #7: see `late/c.png`")
        self.put("reviews/late/c.png", 40)
        self.put("initiatives/x/reviews/review.md", 40,
                 b"https://github.com/o/r/pull/7 - captures are in `screenshots/` and `my shots/`.")
        self.put("initiatives/x/screenshots/a.png", 40)
        self.put("initiatives/x/my shots/a.png", 40)
        self.put("initiatives/x/other/a.png", 40)
        self.put("reviews/old.md", 40, b"pr-70 and PR #71 are closed: see gone.png")
        self.put("reviews/gone.png", 40)
        self.assertEqual(self.run_job(), 0, self.lines)
        for rel in ("pull-requests/shots/b.png", "reviews/late/c.png",
                    "initiatives/x/screenshots/a.png", "initiatives/x/my shots/a.png"):
            self.assertTrue(os.path.exists(self.p(rel)), rel)
        self.assertEqual(set(self.manifest(self.reports()[0])),
                         {"initiatives/x/other/a.png", "reviews/gone.png"})

    def test_short_forms_need_the_repository_name(self):
        # Whole-branch review of 9dace62: a bare `PR #7` named any repository's PR 7.
        self.put("evidence/notes.md", 40, b"other/repo PR #7 merged; see `_agent/initiatives/`,"
                 b" `_agent/evidence/` and shot.png. PR #7 again, pr-7 too.")
        self.put("evidence/shot.png", 40)
        self.put("initiatives/x/evidence/a.png", 40)
        self.assertEqual(self.run_job(), 0, self.lines)
        self.assertEqual(set(self.manifest(self.reports()[0])),
                         {"evidence/shot.png", "initiatives/x/evidence/a.png"})

    def test_repository_name_with_punctuation_before_a_short_form(self):
        # Focused-safety review of cba742a.
        for folder, ref in (("a", b"`r` PR #7:"), ("b", b"**r** PR #7"), ("c", b"r: PR #7"),
                            ("d", b"o/r/pull/7"), ("e", b"bar: PR #7")):
            self.put(folder + "/notes.md", 40, ref + b" see " + folder.encode() + b"-shot.png")
            self.put(folder + "/" + folder + "-shot.png", 40)
        self.assertEqual(self.run_job(), 0, self.lines)
        self.assertEqual(set(self.manifest(self.reports()[0])), {"e/e-shot.png"})

    def test_layout_folder_citations_protect_nothing_below(self):
        self.put("initiatives/x/reviews/r-pr-7.md", 40, b"Captures: `_agent/initiatives/x/evidence/`,"
                 b" `evidence/`, `initiatives/x/`, `reviews/` and `_agent/evidence/run-9/`.")
        self.put("initiatives/x/evidence/a.png", 40)
        self.put("initiatives/x/reviews/d.png", 40)
        self.put("evidence/b.png", 40)
        self.put("evidence/run-9/c.png", 40)
        self.assertEqual(self.run_job(), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("evidence/run-9/c.png")))
        self.assertEqual(set(self.manifest(self.reports()[0])),
                         {"initiatives/x/evidence/a.png", "initiatives/x/reviews/d.png",
                          "evidence/b.png"})

    def test_unreadable_receipt_in_a_layout_folder_keeps_only_its_siblings(self):
        if os.geteuid() == 0:
            self.skipTest("root reads any file")
        self.put("evidence/locked.md", 40, b"o/r#7")
        self.put("evidence/a.png", 40)
        self.put("evidence/run/b.png", 40)
        os.chmod(self.p("evidence/locked.md"), 0)
        self.addCleanup(os.chmod, self.p("evidence/locked.md"), 0o644)
        self.assertEqual(self.run_job(), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("evidence/a.png")))
        self.assertEqual(set(self.manifest(self.reports()[0])), {"evidence/run/b.png"})

    def test_batch_cited_after_the_move_is_kept(self):
        self.put("shots/a.png", 40)
        self.run_job(prs=())
        (first,) = self.reports()
        self.put("notes/r.md", 40, b"o/r#7 needs shots/a.png")
        self.run_job(now=NOW + 31 * DAY)
        self.assertTrue(os.path.isdir(self.p(os.path.join("_trash", first))))

    def test_tree_changed_since_the_plan_is_left(self):
        self.put("x/dist/bundle.png", 40)
        self.age("x/dist", 40)
        plan = sr.build_plan(self.store, NOW, sr.InUse(self.store, (set(), set())), [])
        (item,) = plan.trash
        self.put("x/dist/NOTES.md", 40)  # a receipt written after the plan
        os.makedirs(self.p(sr.REPORTS + "/r"))
        failures = sr.apply_plan(self.store, NOW, plan,
                                 lambda: sr.InUse(self.store, (set(), set())), "r",
                                 self.p(sr.REPORTS + "/r"), self.lines.append)
        self.assertTrue(os.path.exists(self.p("x/dist/NOTES.md")))
        self.assertIn("now holds .git or a receipt", failures[0])

    def test_someone_elses_gz_tmp_is_untouched(self):
        self.put("logs/mid.log", 15, b"line\n")
        self.put("logs/mid.log.gz.tmp", 15, b"not ours")
        self.assertEqual(self.run_job(prs=()), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("logs/mid.log.gz")))
        with open(self.p("logs/mid.log.gz.tmp"), "rb") as handle:
            self.assertEqual(handle.read(), b"not ours")
        self.assertEqual(sorted(os.listdir(self.p("logs"))), ["mid.log.gz", "mid.log.gz.tmp"])

    def test_failed_move_back_stops_the_run(self):
        self.put("p/a.zip", 40)
        self.put("p/b.zip", 40)
        real_row, real_rename = sr.Table.row, os.rename
        moves = []

        def failing_row(table, *cells):
            if cells[0] != "path" and table.handle.name.endswith("manifest.tsv"):
                raise sr.RecordError(28, "No space left on device")
            return real_row(table, *cells)

        def rename(src, dst):
            moves.append(src)
            if len(moves) > 1:
                raise OSError(28, "No space left on device")
            return real_rename(src, dst)

        sr.Table.row, sr.os.rename = failing_row, rename
        self.addCleanup(setattr, sr.Table, "row", real_row)
        self.addCleanup(setattr, sr.os, "rename", real_rename)
        self.assertEqual(self.run_job(prs=()), 1)
        self.assertTrue(os.path.exists(self.p("p/b.zip")))  # never reached
        with open(os.path.join(self.p(sr.REPORTS), self.reports()[0], "report.md")) as handle:
            self.assertIn("moving p/a.zip back failed", handle.read())

    def test_purge_leaves_a_batch_holding_unlisted_files(self):
        self.put("shots/a.png", 40)
        self.run_job(prs=())
        (first,) = self.reports()
        stray = self.p(os.path.join("_trash", first, "notes.md"))
        with open(stray, "w") as handle:
            handle.write("added after the move")
        os.utime(stray, (NOW, NOW))
        self.run_job(now=NOW + 31 * DAY, prs=())
        self.assertTrue(os.path.exists(stray))
        with open(os.path.join(self.p(sr.REPORTS), self.reports()[-1], "report.md")) as handle:
            self.assertIn("purge left _trash/" + first, handle.read())

    def test_failed_manifest_write_moves_back_and_stops(self):
        self.put("shots/a.png", 40)
        self.put("shots/b.png", 40)
        real = sr.Table.row

        def failing(table, *cells):
            if cells[0] != "path" and table.handle.name.endswith("manifest.tsv"):
                raise sr.RecordError(28, "No space left on device")
            return real(table, *cells)

        sr.Table.row = failing
        self.addCleanup(setattr, sr.Table, "row", real)
        self.assertEqual(self.run_job(prs=()), 1)
        self.assertTrue(os.path.exists(self.p("shots/a.png")))
        self.assertTrue(os.path.exists(self.p("shots/b.png")))
        with open(os.path.join(self.p(sr.REPORTS), self.reports()[0], "report.md")) as handle:
            self.assertIn("stopped, nothing more changed", handle.read())

    def test_cited_name_with_a_space_is_kept(self):
        self.put("evidence/r-pr-7.md", 40, b"See shots/final shot.png and Screen Shot 1.png.")
        self.put("evidence/shots/final shot.png", 40)
        self.put("evidence/Screen Shot 1.png", 40)
        self.put("evidence/shots/other.png", 40)
        self.assertEqual(self.run_job(), 0, self.lines)
        self.assertTrue(os.path.exists(self.p("evidence/shots/final shot.png")))
        self.assertTrue(os.path.exists(self.p("evidence/Screen Shot 1.png")))
        self.assertFalse(os.path.exists(self.p("evidence/shots/other.png")))

    def test_symlinked_trash_is_refused(self):
        outside = os.path.join(self.root, "outside")
        os.makedirs(os.path.join(outside, "old"))
        with open(os.path.join(outside, "old", sr.MARKER), "w") as handle:
            handle.write('{"moved_at": 0}')
        os.symlink(outside, self.p("_trash"))
        self.put("shots/a.png", 40)
        self.assertEqual(self.run_job(), 3)
        self.assertTrue(os.path.exists(self.p("shots/a.png")))
        self.assertTrue(os.path.exists(os.path.join(outside, "old", sr.MARKER)))
        self.assertEqual(os.listdir(outside), ["old"])

    def test_symlinked_report_folder_is_refused(self):
        outside = os.path.join(self.root, "outside")
        os.makedirs(outside)
        os.symlink(outside, self.p("evidence"))
        self.put("shots/a.png", 40)
        self.assertEqual(self.run_job(), 3)
        self.assertTrue(os.path.exists(self.p("shots/a.png")))
        self.assertEqual(os.listdir(outside), [])

    def test_lsof_failing_at_the_recheck_is_reported(self):
        self.put("shots/a.png", 40)
        calls = []

        def flaky():
            calls.append(1)
            if len(calls) > 1:
                raise sr.Refused("lsof could not run")
            return set(), set()

        status = sr.run(self.store, True, now=NOW, in_use=flaky, prs=lambda: [],
                        out=self.lines.append)
        self.assertEqual(status, 1)
        self.assertTrue(os.path.exists(self.p("shots/a.png")))
        with open(os.path.join(self.p(sr.REPORTS), self.reports()[0], "report.md")) as handle:
            self.assertIn("stopped, nothing more changed: lsof could not run", handle.read())

    def test_pr_search_at_its_limit_is_refused(self):
        calls = []

        def fake(args):
            calls.append(args)
            return {"login": "me"} if args[0] == "api" else [
                {"number": n, "repository": {"nameWithOwner": "o/r"}} for n in range(sr.PR_LIMIT)]

        real, sr.gh_json = sr.gh_json, fake
        self.addCleanup(setattr, sr, "gh_json", real)
        with self.assertRaises(sr.Refused):
            sr.open_prs()


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
