#!/usr/bin/python3
"""30-day retention for the `_agent/` store: heavy files to trash, receipts never touched (#328).

    /usr/bin/python3 -I store_retention.py --store PATH [--apply]

A dry run (the default) prints the plan and writes nothing. `--apply` acts:

1. **Trash.** A heavy file or tree whose newest modification time is more than 30 days old moves to
   `_trash/<run>/`, keeping its path relative to the store. Each move is a row of
   `evidence/store-retention/<run>/manifest.tsv` (path, kind, bytes, SHA-256, mtime, reason),
   written before the next move. A tree's SHA-256 is the digest of its sorted file listing, each
   line `path NUL size NUL sha256`.
2. **Compress.** A `.log` 7 to 30 days old is gzipped in place. Its size and SHA-256 go to
   `compressed.tsv` first, the `.gz` keeps the log's mtime, and the log is removed only once the
   `.gz` decompresses to the same SHA-256.
3. **Purge.** A trash batch this script made (it holds `.store-retention.json`) is deleted once it
   has sat in trash for 30 days, counted from the move. The manifest under `evidence/` stays.
   Anything else in `_trash/` is left for Brandon's `organize.sh --empty-trash`.

Heavy means one of these kinds, decided by name; every other file is a receipt and is never moved:
media (images, video, audio), served-response captures (`.html`, `.body`, `.rsc`, `.har`, ...),
archives, database copies, logs, and trees of build output, installs and app bundles. Markdown and
JSON are never heavy. `dist`, `build` and `out` count as build output only when they hold no
markdown and no hash file; otherwise they are walked like any folder.

Never touched, whatever the kind: anything changed in the last 72 hours (mtime or ctime); anything
open, or under a running process's working directory (`lsof`; one at the store or a folder directly
in it protects only itself); anything a receipt (markdown, JSON, text, TSV, CSV or YAML) that names
an open PR cites; `_trash/`, `evidence/store-retention/`, `.worktrees/` and any folder holding `.git`; symlinks,
which are never followed. `--apply` refuses to run when `lsof` or the open-PR lookup (`gh`) fails,
since it cannot then tell what is protected. Exit status: 0 done, 1 some action failed, 2 usage,
3 refused.
"""
import argparse
import datetime
import fcntl
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

DAY = 86400
TRASH_DAYS = 30
COMPRESS_DAYS = 7
RECENT_HOURS = 72
RECEIPT_SCAN_MAX = 4 * 1024 * 1024  # receipts larger than this are not scanned for citations
MARKER = ".store-retention.json"
REPORTS = os.path.join("evidence", "store-retention")
SKIP_DIRS = {"_trash", ".worktrees", ".git"}

MEDIA = {"png", "jpg", "jpeg", "gif", "webp", "heic", "tif", "tiff", "bmp",
         "mp4", "mov", "webm", "mkv", "avi", "m4v", "wav", "mp3", "m4a"}
SERVED = {"html", "htm", "body", "rsc", "har", "mhtml", "webarchive"}
ARCHIVE = {"zip", "tar", "tgz", "gz", "bz2", "xz", "7z", "rar", "dmg", "pkg", "jar",
           "apk", "aab", "ipa", "asar"}
DATABASE = re.compile(r"\.(sqlite3?|db)(-wal|-shm)?(\.bak[^/]*)?$", re.I)
LOG = re.compile(r"\.log(\.gz)?$", re.I)
HASH_FILE = re.compile(r"(\.(sha1|sha256|sha512|md5)$|^(sha256|sha512|md5)sums?$)", re.I)
TREE_ALWAYS = {".next", ".turbo", ".expo", ".pnpm-store", "Pods", ".venv", ".gradle",
               "DerivedData", ".svelte-kit", ".nuxt", ".output", ".parcel-cache"}
TREE_IF_NO_RECEIPTS = {"dist", "build", "out", "dist-storybook", "storybook-static"}
TREE_SUFFIX = {".app": "app bundle", ".xcarchive": "app bundle", ".framework": "app bundle",
               ".logarchive": "log"}


class Refused(Exception):
    """A safety check could not run, so nothing may change."""


def ext(name):
    return name.rsplit(".", 1)[1].lower() if "." in name else ""


def file_kind(name):
    """The heavy kind of a file by name, or None for a receipt."""
    low = name.lower()
    if low.endswith((".md", ".json")) or HASH_FILE.search(name):
        return None
    if LOG.search(name):
        return "log"
    if DATABASE.search(name):
        return "database"
    e = ext(name)
    if e in MEDIA:
        return "media"
    if e in SERVED:
        return "served capture"
    if e in ARCHIVE:
        return "archive"
    return None


def tree_kind(path, name):
    """The heavy kind of a folder taken whole, or None to walk into it."""
    if name in TREE_ALWAYS:
        return "build output"
    if "node_modules" in name:
        return "install"
    for suffix, kind in TREE_SUFFIX.items():
        if name.endswith(suffix):
            return kind
    if os.path.isfile(os.path.join(path, "Resources", "app.asar")):
        return "app bundle"  # an app's contents copied without their .app folder
    if name in TREE_IF_NO_RECEIPTS:
        return "build output?"  # confirmed only if the walk finds no receipt inside
    return None


def raise_error(error):
    raise error


def tree_stats(path):
    """(bytes, newest mtime, newest change time, holds a receipt) of a tree; symlinks not followed."""
    info = os.lstat(path)
    size, newest, changed, receipt = 0, info.st_mtime, info.st_ctime, False
    for top, dirs, files in os.walk(path, onerror=raise_error):
        for name in dirs + files:
            st = os.lstat(os.path.join(top, name))
            newest, changed = max(newest, st.st_mtime), max(changed, st.st_ctime)
            if name in files:
                size += st.st_size
                if name.lower().endswith(".md") or HASH_FILE.search(name):
                    receipt = True
    return size, newest, changed, receipt


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_tree(path):
    lines = []
    for top, dirs, files in os.walk(path):
        dirs.sort()
        for name in sorted(files):
            full = os.path.join(top, name)
            rel = os.path.relpath(full, path)
            if os.path.islink(full):
                lines.append("{}\0link\0{}\n".format(rel, os.readlink(full)))
            else:
                lines.append("{}\0{}\0{}\n".format(rel, os.lstat(full).st_size, sha256_file(full)))
    return hashlib.sha256("".join(lines).encode("utf-8", "surrogateescape")).hexdigest()


def with_ancestors(paths, store):
    """Each path and every folder above it, up to the store."""
    out = set()
    for path in paths:
        while path.startswith(store + os.sep):
            out.add(path)
            path = os.path.dirname(path)
    return out


def under_any(path, roots):
    """True when path is one of roots or inside one."""
    while path.startswith(os.sep) and path not in roots:
        parent = os.path.dirname(path)
        if parent == path:
            return False
        path = parent
    return path in roots


# ---- what is in use and what is cited

def lsof_paths(store):
    """(open files, working directories) under the store, from lsof; Refused if lsof fails."""
    try:
        result = subprocess.run(["lsof", "-n", "-P", "-w", "-F", "fn"], capture_output=True,
                                timeout=300)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Refused("lsof could not run: {}".format(error))
    lines = result.stdout.decode("utf-8", "surrogateescape").splitlines()
    if not any(line.startswith("n") for line in lines):
        raise Refused("lsof listed no open files (exit {})".format(result.returncode))
    open_files, cwds, fd = set(), set(), ""
    for line in lines:
        if line.startswith("f"):
            fd = line[1:]
        elif line.startswith("n"):
            path = line[1:]
            if path.endswith(" (deleted)"):
                path = path[: -len(" (deleted)")]
            if path == store or path.startswith(store + os.sep):
                (cwds if fd == "cwd" else open_files).add(path)
    return open_files, cwds


def gh_json(args):
    try:
        result = subprocess.run(["gh"] + args, capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Refused("gh could not run: {}".format(error))
    if result.returncode != 0:
        raise Refused("gh {} failed: {}".format(" ".join(args[:2]),
                                                result.stderr.decode(errors="replace").strip()))
    return json.loads(result.stdout or b"null")


def open_prs():
    """[(owner/repo, number)] of every open PR the gh user wrote or owns the repository of."""
    login = gh_json(["api", "user"])["login"]
    prs = set()
    for who in (["--author", "@me"], ["--owner", login]):
        for pr in gh_json(["search", "prs", "--state", "open", "--limit", "1000",
                           "--json", "number,repository"] + who):
            prs.add((pr["repository"]["nameWithOwner"], pr["number"]))
    return sorted(prs)


def pr_pattern(prs):
    """One regex matching a reference to any of the PRs: its URL, owner/repo#n or <repo>-pr-<n>."""
    alts = []
    for repo, number in prs:
        name = repo.split("/")[-1]
        alts.append(r"github\.com/{}/pull/{}".format(re.escape(repo), number))
        alts.append(r"{}#{}".format(re.escape(repo), number))
        alts.append(r"{}-pr-{}".format(re.escape(name), number))
    return re.compile("(?:{})(?!\\d)".format("|".join(alts))) if alts else None


# A path with a slash, or a bare file name with an extension (read against the receipt's folder).
PATHLIKE = re.compile(r"[~\w.@+-]*(?:/[\w.@+-]+)+/?|[\w@+-][\w.@+-]*\.[A-Za-z0-9]{2,10}")


def cited_paths(store, prs, receipts):
    """Store paths named by a receipt that refers to an open PR."""
    pattern = pr_pattern(prs)
    cited = set()
    if pattern is None:
        return cited
    agent_root = os.path.dirname(store)
    for receipt in receipts:
        try:
            with open(receipt, "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read(RECEIPT_SCAN_MAX)
        except OSError:
            continue
        if not pattern.search(text) and not pattern.search(os.path.basename(receipt)):
            continue
        here = os.path.dirname(receipt)
        for token in PATHLIKE.findall(text):
            token = token.rstrip("/.")
            if token.startswith("~"):
                bases = [os.path.expanduser(token)]
            elif token.startswith("/"):
                bases = [token]
            elif "/" not in token:
                bases = [os.path.join(here, token)]
            else:
                bases = [os.path.join(here, token), os.path.join(store, token),
                         os.path.join(agent_root, token)]
                if "_agent/" in token:
                    bases.append(os.path.join(store, token.rsplit("_agent/", 1)[1]))
            for base in bases:
                path = os.path.normpath(base)
                if path.startswith(store + os.sep) and os.path.lexists(path):
                    cited.add(path)
    return cited


# ---- the plan

class Plan:
    def __init__(self):
        self.trash, self.compress, self.purge, self.errors = [], [], [], []
        self.kept = {"recent": 0, "in use": 0, "cited": 0}


def walk_store(store, errors):
    """(heavy candidates, receipts) under the store. A candidate is (path, kind, bytes, newest
    mtime, newest ctime); a tree that cannot be read whole is reported in errors and left."""
    skip = {os.path.join(store, "_trash"), os.path.join(store, REPORTS)}
    candidates, receipts = [], []
    stack = [store]
    while stack:
        top = stack.pop()
        try:
            entries = sorted(os.scandir(top), key=lambda entry: entry.name)
        except OSError as error:
            errors.append("unreadable: {}".format(error))
            continue
        if top != store and any(entry.name == ".git" for entry in entries):
            continue  # a checkout or clone: never touched
        for entry in entries:
            if entry.is_symlink():
                continue
            if entry.is_dir():
                if entry.name in SKIP_DIRS or entry.path in skip:
                    continue
                kind = tree_kind(entry.path, entry.name)
                if not kind:
                    stack.append(entry.path)
                    continue
                try:
                    size, mtime, ctime, receipt = tree_stats(entry.path)
                except OSError as error:
                    errors.append("unreadable, left: {}".format(error))
                    continue
                if kind == "build output?":
                    if receipt:
                        stack.append(entry.path)
                        continue
                    kind = "build output"
                candidates.append((entry.path, kind, size, mtime, ctime))
            elif entry.is_file():
                kind = file_kind(entry.name)
                if kind:
                    st = entry.stat(follow_symlinks=False)
                    candidates.append((entry.path, kind, st.st_size, st.st_mtime, st.st_ctime))
                elif ext(entry.name) in ("md", "json", "txt", "tsv", "csv", "yml", "yaml"):
                    receipts.append(entry.path)
    return candidates, receipts


def trash_batches(store, now, open_or_above):
    """Batches this script made that have sat in trash past the window: [(path, moved_at)]."""
    trash = os.path.join(store, "_trash")
    due = []
    try:
        names = sorted(os.listdir(trash))
    except OSError:
        return due
    for name in names:
        batch = os.path.join(trash, name)
        if os.path.islink(batch) or not os.path.isdir(batch):
            continue
        try:
            with open(os.path.join(batch, MARKER)) as handle:
                moved_at = float(json.load(handle)["moved_at"])
        except (OSError, ValueError, KeyError, TypeError):
            continue  # not ours: Brandon's to empty
        if now - moved_at > TRASH_DAYS * DAY and batch not in open_or_above:
            due.append((batch, moved_at))
    return due


def broad(path, store):
    """The store or a folder directly in it: a working directory there protects nothing below."""
    return path == store or os.path.dirname(path) == store


def build_plan(store, now, in_use, prs):
    """The plan. in_use is (open files, working directories) and prs the open PRs."""
    open_files, cwds = in_use
    open_or_above = with_ancestors(open_files | cwds, store)
    cwds = {path for path in cwds if not broad(path, store)}
    plan = Plan()
    candidates, receipts = walk_store(store, plan.errors)
    cited = cited_paths(store, prs, receipts)
    cited_or_above = with_ancestors(cited, store)
    for path, kind, size, mtime, ctime in candidates:
        age = (now - mtime) / DAY
        if age <= COMPRESS_DAYS:
            continue  # young; this also covers a modification time in the last 72 hours
        if ctime > now - RECENT_HOURS * 3600:
            plan.kept["recent"] += 1
        elif path in open_or_above or under_any(path, cwds):
            plan.kept["in use"] += 1
        elif path in cited_or_above or under_any(path, cited):
            plan.kept["cited"] += 1
        elif age > TRASH_DAYS:
            plan.trash.append((path, kind, size, mtime))
        elif kind == "log" and path.lower().endswith(".log") and os.path.isfile(path):
            plan.compress.append((path, size, mtime))
    plan.purge = trash_batches(store, now, open_or_above)
    return plan


# ---- acting

def run_id(store, now):
    stem = datetime.datetime.fromtimestamp(now).strftime("%Y-%m-%d")
    name, n = stem, 1
    while (os.path.lexists(os.path.join(store, REPORTS, name))
           or os.path.lexists(os.path.join(store, "_trash", name))):
        n += 1
        name = "{}-{}".format(stem, n)
    return name


def iso(ts):
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S")


def compress_log(path):
    """Gzip path in place; (gz path, gz bytes). The log goes only after the round trip matches."""
    want = sha256_file(path)
    st = os.lstat(path)
    gz, tmp = path + ".gz", path + ".gz.tmp"
    if os.path.lexists(gz) or os.path.lexists(tmp):
        raise OSError("{} already exists".format(gz))
    with open(path, "rb") as source, gzip.open(tmp, "wb") as target:
        shutil.copyfileobj(source, target, 1 << 20)
    digest = hashlib.sha256()
    with gzip.open(tmp, "rb") as check:
        for block in iter(lambda: check.read(1 << 20), b""):
            digest.update(block)
    if digest.hexdigest() != want:
        os.remove(tmp)
        raise OSError("{}: gzip round trip did not match".format(path))
    os.utime(tmp, (st.st_atime, st.st_mtime))
    os.rename(tmp, gz)
    os.remove(path)
    return gz, os.lstat(gz).st_size, want


def apply_plan(store, now, plan, recheck, out):
    """Carry out plan; return the number of failed actions. recheck() gives a fresh in-use pair."""
    name = run_id(store, now)
    report_dir = os.path.join(store, REPORTS, name)
    os.makedirs(report_dir)
    batch = os.path.join(store, "_trash", name)
    failures = []
    open_files, cwds = recheck()
    fresh = with_ancestors(open_files | cwds, store)
    cwds = {path for path in cwds if not broad(path, store)}

    def busy(path):
        return path in fresh or under_any(path, cwds)

    moved = 0
    with open(os.path.join(report_dir, "manifest.tsv"), "w") as manifest:
        manifest.write("path\tkind\tbytes\tsha256\tmtime\treason\n")
        for path, kind, size, mtime in plan.trash:
            rel = os.path.relpath(path, store)
            try:
                if busy(path):
                    raise OSError("opened since the plan was made")
                st = os.lstat(path)
                if max(st.st_mtime, st.st_ctime) > now - RECENT_HOURS * 3600:
                    raise OSError("changed since the plan was made")
                digest = sha256_tree(path) if os.path.isdir(path) else sha256_file(path)
                if not os.path.isdir(batch):
                    os.makedirs(batch)
                    with open(os.path.join(batch, MARKER), "w") as marker:
                        json.dump({"moved_at": now, "manifest": os.path.relpath(
                            os.path.join(report_dir, "manifest.tsv"), store)}, marker)
                target = os.path.join(batch, rel)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                os.rename(path, target)
            except OSError as error:
                failures.append("trash {}: {}".format(rel, error))
                continue
            manifest.write("{}\t{}\t{}\t{}\t{}\t{}, {} days old\n".format(
                rel, kind, size, digest, iso(mtime), kind, int((now - mtime) / DAY)))
            manifest.flush()
            moved += 1
            out("trashed  {:<14} {:>12}  {}".format(kind, size, rel))

    compressed = 0
    with open(os.path.join(report_dir, "compressed.tsv"), "w") as table:
        table.write("path\tbytes\tsha256\tmtime\tgz_bytes\n")
        for path, size, mtime in plan.compress:
            rel = os.path.relpath(path, store)
            try:
                if busy(path):
                    raise OSError("opened since the plan was made")
                gz, gz_size, digest = compress_log(path)
            except OSError as error:
                failures.append("compress {}: {}".format(rel, error))
                continue
            table.write("{}\t{}\t{}\t{}\t{}\n".format(rel, size, digest, iso(mtime), gz_size))
            table.flush()
            compressed += 1
            out("compressed {:>12} -> {:>10}  {}".format(size, gz_size, rel))

    purged = 0
    with open(os.path.join(report_dir, "purged.tsv"), "w") as table:
        table.write("batch\tmoved_at\tbytes\n")
        for path, moved_at in plan.purge:
            rel = os.path.relpath(path, store)
            try:
                if path in fresh:
                    raise OSError("opened since the plan was made")
                size = tree_stats(path)[0]
                shutil.rmtree(path)
            except OSError as error:
                failures.append("purge {}: {}".format(rel, error))
                continue
            table.write("{}\t{}\t{}\n".format(rel, iso(moved_at), size))
            table.flush()
            purged += 1
            out("purged   {:>12}  {}".format(size, rel))

    with open(os.path.join(report_dir, "report.md"), "w") as report:
        report.write(summary(name, now, plan, moved, compressed, purged, failures))
    out("report: {}".format(os.path.relpath(report_dir, store)))
    return len(failures)


def summary(name, now, plan, moved, compressed, purged, failures):
    lines = [
        "# Store retention run {}".format(name), "",
        "Written {} by `scripts/store-retention/store_retention.py --apply`"
        " (agent-working-agreements#328).".format(iso(now)), "",
        "- Trashed: {} of {} planned, into `_trash/{}/` (`manifest.tsv`).".format(
            moved, len(plan.trash), name),
        "- Compressed: {} of {} logs (`compressed.tsv`).".format(compressed, len(plan.compress)),
        "- Purged: {} of {} trash batches past {} days (`purged.tsv`).".format(
            purged, len(plan.purge), TRASH_DAYS),
        "- Kept though heavy and old enough: {} in use, {} cited by an open PR's receipt;"
        " {} changed in the last {} hours.".format(
            plan.kept["in use"], plan.kept["cited"], plan.kept["recent"], RECENT_HOURS),
    ]
    if failures:
        lines += ["", "## Failed", ""] + ["- {}".format(f) for f in failures]
    return "\n".join(lines) + "\n"


def refusal(store, now, reason, out):
    """Record a refused --apply run in the store, as its report."""
    name = run_id(store, now)
    report_dir = os.path.join(store, REPORTS, name)
    os.makedirs(report_dir)
    with open(os.path.join(report_dir, "report.md"), "w") as report:
        report.write("# Store retention run {}\n\nRefused at {}: {}. Nothing was moved,"
                     " compressed or deleted.\n".format(name, iso(now), reason))
    out("refused: {}".format(reason))


def print_plan(store, plan, out):
    for path, kind, size, mtime in plan.trash:
        out("would trash    {:<14} {:>12}  {}".format(kind, size, os.path.relpath(path, store)))
    for path, size, mtime in plan.compress:
        out("would compress {:>12}  {}".format(size, os.path.relpath(path, store)))
    for path, moved_at in plan.purge:
        out("would purge    {}  (moved {})".format(os.path.relpath(path, store), iso(moved_at)))
    out("-- dry run: {} to trash ({} bytes), {} logs to compress, {} batches to purge; kept: {} in"
        " use, {} cited, {} recent. Nothing changed.".format(
            len(plan.trash), sum(item[2] for item in plan.trash), len(plan.compress),
            len(plan.purge), plan.kept["in use"], plan.kept["cited"], plan.kept["recent"]))


def run(store, apply, now=None, in_use=None, prs=None, out=print):
    """The whole job. in_use and prs are callables, replaced in tests; returns the exit status."""
    now = time.time() if now is None else now
    in_use = in_use or (lambda: lsof_paths(store))
    prs = prs or open_prs
    if not apply:
        try:
            pair = in_use()
        except Refused as error:
            out("warning: {}; the plan below protects no open file".format(error))
            pair = (set(), set())
        try:
            pr_list = prs()
        except Refused as error:
            out("warning: {}; the plan below protects no cited path".format(error))
            pr_list = []
        print_plan(store, build_plan(store, now, pair, pr_list), out)
        return 0
    os.makedirs(os.path.join(store, "_trash"), exist_ok=True)
    with open(os.path.join(store, "_trash", ".store-retention.lock"), "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            out("refused: another retention run holds the lock")
            return 3
        try:
            plan = build_plan(store, now, in_use(), prs())
        except Refused as error:
            refusal(store, now, str(error), out)
            return 3
        return 1 if apply_plan(store, now, plan, in_use, out) else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--store", required=True, help="the _agent/ directory")
    parser.add_argument("--apply", action="store_true", help="act; the default is a dry run")
    args = parser.parse_args(argv)
    if os.path.islink(args.store) or not os.path.isdir(args.store):
        parser.error("--store must be a directory, not a symlink: {}".format(args.store))
    store = os.path.realpath(args.store)
    if os.path.basename(store) != "_agent":
        parser.error("--store must be an _agent/ directory: {}".format(store))
    return run(store, args.apply)


if __name__ == "__main__":
    sys.exit(main())
