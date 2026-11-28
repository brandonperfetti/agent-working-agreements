#!/usr/bin/python3
"""30-day retention for the `_agent/` store: heavy files to trash, receipts never touched (#328).

    /usr/bin/python3 -I store_retention.py --store PATH [--apply]

A dry run (the default) prints the plan and writes nothing. `--apply` acts:

1. **Trash.** A heavy file or tree whose newest modification time is more than 30 days old moves to
   `_trash/<run>/`, keeping its path relative to the store. Each move is a row of
   `evidence/store-retention/<run>/manifest.tsv` (path, kind, bytes, SHA-256, mtime, reason),
   written as it happens. A tree's SHA-256 is the digest of its sorted file listing, each line
   `path NUL size NUL sha256`.
2. **Compress.** A `.log` 7 to 30 days old is gzipped in place. Once the `.gz` decompresses to the
   log's SHA-256, its size and SHA-256 go to `compressed.tsv`, and only then is the log removed. The
   `.gz` keeps the log's mtime.
3. **Purge.** A trash batch this script made (it holds `.store-retention.json`) is deleted once it
   has sat in trash for 30 days, counted from the move, provided it holds only what its manifest
   lists, nothing in it changed in the last 72 hours, and no open PR's receipt cites one of its
   paths. The manifest under `evidence/` stays.
   Anything else in `_trash/` is left for Brandon's `organize.sh --empty-trash`.

**Heavy** means one of these kinds, decided by name; every other file stays:
- media: images, video, audio;
- served-response captures: `.body`, `.rsc`, `.har`, `.mhtml`, `.webarchive`, and `.html` or `.htm`
  of 256 KiB or more;
- archives, database copies and logs;
- trees of build output, installs and app bundles, taken whole.

A tree is taken whole only when it holds no `.git` anywhere. Some trees are taken even though
they hold package metadata:
- trees matched by an exact name (`node_modules`, `.next`, `Pods`, ...);
- a macOS app bundle: a `*.app` whose top level is only `Contents/` with an `Info.plist` and
  bundle entries.

Any other matched tree must hold no receipt anywhere:
- app contents copied without their `.app` folder (bundle entries only, with `Resources/app.asar`
  or `MacOS/`);
- an `*.app` that is not a bundle;
- a `*.framework`, `*.xcarchive` or `*.logarchive`;
- `dist`, `build`, `out`, `dist-storybook` and `storybook-static`. A tree that fails
is walked like any folder. A **receipt** is markdown, JSON (with `.jsonl` and `.ndjson`), text,
TSV, CSV, YAML or a hash file.

**Never touched**, whatever the kind:
- anything changed in the last 72 hours (mtime or ctime);
- anything open, or under a running process's working directory, as `lsof` shows. A working
  directory at the store, or in a folder directly in it, protects only itself.
- anything a receipt that names an open PR cites, or anything inside what it cites: by a path, by
  a path relative to the receipt or a folder above it (URL-encoded or not), or by the name of a
  heavy file. A receipt names a PR by its URL, `owner/repo#n` or `repo#n`, or by a short form
  (`pr-n`, `prn`, `PR #n`, `pull/n`) right after the repository's name; in its file name, a short
  form alone counts too. Receipts are read whole, compressed ones too. One that cannot be read, or
  a citing one over 64 MiB, keeps everything in its folder. A citation of the store or of a layout
  folder (`evidence/`, `initiatives/<x>/`, `initiatives/<x>/reviews/`, ...) protects nothing below
  it, and an unreadable receipt in one keeps only what sits directly beside it.
- `_trash/`, `evidence/store-retention/`, `.worktrees/`, any folder holding `.git`, and symlinks,
  which are never followed.

`--apply` refuses to run when:
- `lsof` fails;
- the open-PR lookup (`gh`) fails or reaches its 1000-result limit;
- `_trash`, `evidence` or the report folder is a symlink.

A record that cannot be written stops the run: a move whose manifest row fails is moved back, and a
purge is recorded before it deletes. Exit status: 0 done, 1 an action failed or the run stopped,
2 usage, 3 refused.
"""
import argparse
import bz2
import codecs
import datetime
import fcntl
import gzip
import hashlib
import json
import lzma
import os
import re
import shutil
import subprocess
import tempfile
import sys
import time
import urllib.parse
import zlib

DAY = 86400
TRASH_DAYS = 30
COMPRESS_DAYS = 7
RECENT_HOURS = 72
HTML_MIN = 256 * 1024
RECEIPT_KEEP_MAX = 64 * 1024 * 1024  # a citing receipt larger than this protects its whole folder
PR_LIMIT = 1000  # gh search's ceiling: a full page means PRs may be missing
MARKER = ".store-retention.json"
LOCK = ".store-retention.lock"
REPORTS = os.path.join("evidence", "store-retention")
SKIP_DIRS = {"_trash", ".worktrees", ".git"}
# The store's layout folders (procedures/agent-workspace-layout.md). A receipt that names one of
# these, or an initiative's folder, names a home for many things, not the things in it.
LAYOUT = {"analysis", "authorizations", "evidence", "experiments", "friction", "handoffs",
          "initiatives", "learnings", "mboxes", "notes", "plans", "pull-requests", "quarantine",
          "rationale", "reviews", "tickets", "tools", "worktrees"}

MEDIA = {"png", "jpg", "jpeg", "gif", "webp", "heic", "tif", "tiff", "bmp",
         "mp4", "mov", "webm", "mkv", "avi", "m4v", "wav", "mp3", "m4a"}
SERVED = {"body", "rsc", "har", "mhtml", "webarchive"}
SERVED_IF_LARGE = {"html", "htm"}
ARCHIVE = {"zip", "tar", "tgz", "gz", "bz2", "xz", "7z", "rar", "dmg", "pkg", "jar",
           "apk", "aab", "ipa", "asar"}
COMPRESSED = {"gz", "bz2", "xz"}
RECEIPT_EXT = {"md", "json", "jsonl", "ndjson", "txt", "tsv", "csv", "yml", "yaml"}
DATABASE = re.compile(r"\.(sqlite3?|db)(-wal|-shm)?(\.bak[^/]*)?$", re.I)
LOG = re.compile(r"\.log(\.gz)?$", re.I)
HASH_FILE = re.compile(r"(\.(sha1|sha256|sha512|md5)$|^(sha256|sha512|md5)sums?$)", re.I)
TREE_EXACT = {"node_modules": "install", ".pnpm-store": "install", ".venv": "install",
              "Pods": "install", ".next": "build output", ".turbo": "build output",
              ".expo": "build output", ".gradle": "build output", "DerivedData": "build output",
              ".svelte-kit": "build output", ".nuxt": "build output", ".output": "build output",
              ".parcel-cache": "build output"}
TREE_SUFFIX = {".app": "app bundle", ".xcarchive": "app bundle", ".framework": "app bundle",
               ".logarchive": "log"}
BUNDLE_TOP = {"Contents", ".DS_Store"}
CONTENTS_TOP = {"Info.plist", "PkgInfo", "MacOS", "Resources", "Frameworks", "Helpers", "PlugIns",
                "Library", "SharedSupport", "XPCServices", "_CodeSignature", "CodeResources",
                "embedded.provisionprofile", ".DS_Store"}
TREE_BUILD = {"dist", "build", "out", "dist-storybook", "storybook-static"}


class Refused(Exception):
    """A safety check could not run, so nothing may change."""


def ext(name):
    return name.rsplit(".", 1)[1].lower() if "." in name else ""


def is_receipt(name):
    """Markdown, JSON, text, TSV, CSV, YAML or a hash file, compressed or not."""
    if ext(name) in COMPRESSED:
        name = name.rsplit(".", 1)[0]
    return ext(name) in RECEIPT_EXT or bool(HASH_FILE.search(name))


def file_kind(name, size):
    """The heavy kind of a file, or None: it stays."""
    if is_receipt(name):
        return None
    if LOG.search(name):
        return "log"
    if DATABASE.search(name):
        return "database"
    e = ext(name)
    if e in MEDIA:
        return "media"
    if e in SERVED or (e in SERVED_IF_LARGE and size >= HTML_MIN):
        return "served capture"
    if e in ARCHIVE:
        return "archive"
    return None


def listing(path):
    try:
        return set(os.listdir(path))
    except OSError:
        return None


def is_bundle(path, name):
    """A macOS app bundle, or an app's contents copied without their `.app` folder."""
    if name.endswith(".app"):
        top = listing(path)
        return bool(top) and top <= BUNDLE_TOP and os.path.isfile(
            os.path.join(path, "Contents", "Info.plist")) and is_bundle(
            os.path.join(path, "Contents"), "Contents")
    top = listing(path)
    return bool(top) and top <= CONTENTS_TOP and "Info.plist" in top and (
        os.path.isfile(os.path.join(path, "Resources", "app.asar"))
        or os.path.isdir(os.path.join(path, "MacOS")))


def tree_match(path, name):
    """(kind, strict) for a folder that may be taken whole, or None to walk into it. A strict
    match is taken only when it holds no receipt anywhere."""
    if name in TREE_EXACT:
        return TREE_EXACT[name], False
    if is_bundle(path, name):
        return "app bundle", not name.endswith(".app")  # loose contents: no receipt anywhere
    for suffix, kind in TREE_SUFFIX.items():
        if name.endswith(suffix):
            return kind, True
    if name in TREE_BUILD:
        return "build output", True
    return None


class Tree:
    """What a walk of one tree found; symlinks are not followed, and an unreadable folder raises."""

    def __init__(self, path):
        info = os.lstat(path)
        self.size, self.mtime, self.ctime = 0, info.st_mtime, info.st_ctime
        self.git = self.receipt = False
        self.heavy_names = set()  # names a receipt may cite a file inside the tree by
        for top, dirs, files in os.walk(path, onerror=raise_error):
            for name in dirs + files:
                st = os.lstat(os.path.join(top, name))
                self.mtime, self.ctime = max(self.mtime, st.st_mtime), max(self.ctime, st.st_ctime)
                if name == ".git":
                    self.git = True
                if name in files:
                    self.size += st.st_size
                    self.receipt = self.receipt or is_receipt(name)
                    if file_kind(name, st.st_size):
                        self.heavy_names.add(name)

    def whole(self, strict):
        return not self.git and not (strict and self.receipt)


def raise_error(error):
    raise error


def sha256_stream(handle):
    digest = hashlib.sha256()
    for block in iter(lambda: handle.read(1 << 20), b""):
        digest.update(block)
    return digest.hexdigest()


def sha256_file(path):
    with open(path, "rb") as handle:
        return sha256_stream(handle)


def sha256_tree(path):
    lines = []
    for top, dirs, files in os.walk(path, onerror=raise_error):
        dirs.sort()
        for name in sorted(files):
            full = os.path.join(top, name)
            rel = os.path.relpath(full, path)
            if os.path.islink(full):
                lines.append("{}\0link\0{}\n".format(rel, os.readlink(full)))
            else:
                lines.append("{}\0{}\0{}\n".format(rel, os.lstat(full).st_size, sha256_file(full)))
    return hashlib.sha256("".join(lines).encode("utf-8", "surrogateescape")).hexdigest()


def inside(path, root):
    return path.startswith(root + os.sep)


def with_ancestors(paths, store):
    """Each path and every folder above it, up to the store."""
    out = set()
    for path in paths:
        while inside(path, store):
            out.add(path)
            path = os.path.dirname(path)
    return out


def under_any(path, roots):
    """True when path is one of roots or inside one."""
    while path not in roots:
        parent = os.path.dirname(path)
        if parent == path:
            return False
        path = parent
    return True


class InUse:
    """Paths lsof shows open or as a working directory, and the tests against them."""

    def __init__(self, store, pair):
        open_files, cwds = pair
        self.held = with_ancestors(open_files | cwds, store)  # a tree holding an open path
        self.cwds = {path for path in cwds if path != store and os.path.dirname(path) != store}

    def __call__(self, path):
        return path in self.held or under_any(path, self.cwds)


def real_dir(store, rel):
    """store/rel, refused if it or a folder on the way is a symlink or leaves the store."""
    path = store
    for part in rel.split(os.sep):
        path = os.path.join(path, part)
        if os.path.islink(path):
            raise Refused("{} is a symlink".format(path))
    if os.path.lexists(path) and not os.path.isdir(path):
        raise Refused("{} is not a folder".format(path))
    if os.path.exists(path) and not inside(os.path.realpath(path), store):
        raise Refused("{} leaves the store".format(path))
    return path


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
            if path == store or inside(path, store):
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
    try:
        return json.loads(result.stdout or b"null")
    except ValueError as error:
        raise Refused("gh {} gave no JSON: {}".format(" ".join(args[:2]), error))


def open_prs():
    """[(owner/repo, number)] of every open PR the gh user wrote, is involved in, or owns the
    repository of; Refused when a search fills its page, since PRs may then be missing."""
    login = gh_json(["api", "user"])["login"]
    prs = set()
    for who in (["--author", "@me"], ["--involves", "@me"], ["--owner", login]):
        found = gh_json(["search", "prs", "--state", "open", "--limit", str(PR_LIMIT),
                         "--json", "number,repository"] + who)
        if len(found) >= PR_LIMIT:
            raise Refused("gh search prs {} returned {} results, its limit".format(who[0], PR_LIMIT))
        prs.update((pr["repository"]["nameWithOwner"], pr["number"]) for pr in found)
    return sorted(prs)


def pr_pattern(prs):
    """A Pattern matching a reference to any of the PRs, or None for none. In text: its URL,
    owner/repo#n, repo#n, or a short form (`PR #n`, `pr-n`, `pull/n`) right after the repository's
    name. In a receipt's file name, a short form alone also counts. Each is one case-insensitive
    regex with a repository's numbers in one group."""
    if not prs:
        return None
    numbers = {}
    for repo, number in prs:
        numbers.setdefault(repo, set()).add(str(number))
    short = r"(?:pr[-_ ]?#?|pull[-_/])"
    text, any_number = [], set()
    for repo, found in sorted(numbers.items()):
        name = re.escape(repo.split("/")[-1])
        group = "(?:{})".format("|".join(sorted(found, key=lambda n: (-len(n), n))))
        any_number |= found
        text.append(r"(?:github\.com/{repo}/pull/|{repo}#|(?<![\w.-]){name}#"
                    r"|(?<![\w.-]){name}[-_ ]+{short}){group}".format(
                        repo=re.escape(repo), name=name, short=short, group=group))
    group = "(?:{})".format("|".join(sorted(any_number, key=lambda n: (-len(n), n))))
    text = "(?:{})(?!\\d)".format("|".join(text))
    name = "(?:{}|(?<![a-z0-9]){}{}(?!\\d))".format(text, short, group)
    names = [repo.split("/")[-1].lower() for repo in numbers]
    return Pattern(re.compile(text, re.I), re.compile(name, re.I), names)


class Pattern:
    """The two regexes, with a cheap test first: every text form holds a repository's name."""

    def __init__(self, text, name, names):
        self.text, self.name, self.names = text, name, names

    def in_text(self, chunk):
        low = chunk.lower()
        return any(name in low for name in self.names) and bool(self.text.search(chunk))

    def in_name(self, name):
        return bool(self.name.search(name))


# A path with a slash, or a bare file name with an extension (read against the receipt's folder).
# Path characters in a run; one character class, so the scan is linear in the text. A token with a
# slash is a path; one without is a bare file name only if it has an extension.
PATH_RUN = re.compile(r"[~\w.@+/-]+")
BARE_NAME = re.compile(r"[\w@+-][\w.@+-]*\.[A-Za-z0-9]{2,10}")
TOKEN_MAX = 4096


def path_tokens(text):
    for token in PATH_RUN.findall(text):
        if len(token) <= TOKEN_MAX and ("/" in token or BARE_NAME.fullmatch(token)):
            yield token


OPENERS = {"gz": gzip.open, "bz2": bz2.open, "xz": lzma.open}


def read_receipt(path, pattern):
    """(text, whole) when the receipt names an open PR, by its name or anywhere in it, compressed
    or not; (None, True) when it does not. Past RECEIPT_KEEP_MAX the text is cut, and whole is
    False."""
    hit = pattern.in_name(os.path.basename(path))
    decoder = codecs.getincrementaldecoder("utf-8")("replace")
    kept, size, tail = [], 0, ""
    with OPENERS.get(ext(path), open)(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 22), b""):
            chunk = decoder.decode(block)
            hit = hit or pattern.in_text(tail + chunk)
            tail = chunk[-1024:]
            if size < RECEIPT_KEEP_MAX:
                kept.append(chunk)
            size += len(chunk)
    if not hit:
        return None, True
    return "".join(kept), size <= RECEIPT_KEEP_MAX


class Citations:
    """What the receipts that name an open PR cite."""

    def __init__(self, store, prs, receipts):
        self.store, self.texts, self.paths, self.unread = store, [], set(), []
        self.held, self.siblings = set(), set()
        pattern = pr_pattern(prs)
        if pattern is None:
            return
        for receipt in receipts:
            try:
                text, whole = read_receipt(receipt, pattern)
            except (OSError, EOFError, ValueError, lzma.LZMAError, zlib.error) as error:
                # what it cites is unknown, so everything beside it is kept
                self.keep_folder(os.path.dirname(receipt))
                self.unread.append("{}: {}".format(os.path.relpath(receipt, store), error))
                continue
            if text is None:
                continue
            if not whole:
                self.keep_folder(os.path.dirname(receipt))
            decoded = urllib.parse.unquote(text)
            self.texts.append((os.path.dirname(receipt), text + "\n" + decoded))
            self.paths.update(self.resolve(receipt, text + "\n" + decoded))
        self.held = with_ancestors(self.paths, store)

    def broad(self, folder):
        """True for the store, a layout folder in it, an initiative's folder, or a layout folder
        in an initiative: citing one of these protects nothing below it."""
        if folder == self.store:
            return True
        if not inside(folder, self.store):
            return False
        parts = os.path.relpath(folder, self.store).split(os.sep)
        if len(parts) == 1:
            return parts[0] in LAYOUT
        if parts[0] != "initiatives" or len(parts) > 3:
            return False
        return len(parts) == 2 or parts[2] in LAYOUT

    def keep_folder(self, folder):
        """Keep what is in folder; for a broad folder, only what sits directly in it."""
        (self.siblings if self.broad(folder) else self.paths).add(folder)

    def resolve(self, receipt, text):
        """Existing store paths the text names (a cited folder protects what is under it)."""
        here, store = os.path.dirname(receipt), self.store
        for token in path_tokens(text):
            token = token.rstrip("/.")
            if token.startswith("~"):
                bases = [os.path.expanduser(token)]
            elif token.startswith("/"):
                bases = [token]
            elif "/" not in token:
                bases = [os.path.join(here, token)]
            else:  # against the receipt's folder and each folder above it, then the agent root
                bases = [os.path.join(folder, token) for folder in self.above(here)]
                bases.append(os.path.join(os.path.dirname(store), token))
                if "_agent/" in token:
                    bases.append(os.path.join(store, token.rsplit("_agent/", 1)[1]))
            for base in bases:
                path = os.path.normpath(base)
                if (inside(path, store) and os.path.lexists(path)
                        and not (os.path.isdir(path) and self.broad(path))):
                    yield path

    def above(self, here):
        """here and each folder above it, up to and including the store."""
        folders = [here]
        while inside(folders[-1], self.store):
            folders.append(os.path.dirname(folders[-1]))
        return folders

    def __call__(self, path, names):
        """True when a citing receipt names path, a folder above it below the store's top level,
        or (names) a heavy file inside it."""
        if not self.texts and not self.paths and not self.siblings:
            return False
        if path in self.held or under_any(path, self.paths):
            return True
        if os.path.dirname(path) in self.siblings:
            return True
        for here, text in self.texts:  # a name with a space escapes the token pattern above
            if any(name in text for name in names):
                return True
            folder, tree = path, not os.path.isfile(path)
            while inside(folder, self.store):
                if self.broad(folder):
                    folder = os.path.dirname(folder)
                    continue
                top = os.path.dirname(folder) == self.store
                rels = {os.path.relpath(folder, base) for base in self.above(here)
                        if inside(folder, base)}
                rels.add(os.path.relpath(folder, here))
                for rel in rels:
                    if not rel.replace("/", "").strip("."):
                        continue  # `.` or `..` alone would match every ellipsis
                    if top and not rel.startswith(".."):
                        if names_whole(text, rel + "/"):  # a top-level folder, cited as one
                            return True
                    elif names_whole(text, rel) or (tree and folder == path and rel + "/" in text):
                        return True
                folder = os.path.dirname(folder)
        return False


ENDS = set(" \t\r\n`'\")]>,;:|*.?!")


def names_whole(text, rel):
    """True when text holds rel as a whole path: followed by an end, or by `/` and an end, so that
    a cited `a/b/c.png` does not cite the folders `a` or `a/b` above it."""
    at = text.find(rel)
    while at >= 0:
        rest = text[at + len(rel):at + len(rel) + 2]
        if not rest or rest[0] in ENDS or (rest[0] == "/" and (len(rest) < 2 or rest[1] in ENDS)):
            return True
        at = text.find(rel, at + 1)
    return False


# ---- the plan

class Candidate:
    def __init__(self, path, kind, size, mtime, ctime, names=None, strict=False):
        self.path, self.kind, self.size, self.strict = path, kind, size, strict
        self.mtime, self.ctime, self.is_file = mtime, ctime, names is None
        self.names = {os.path.basename(path)} if names is None else names


class Plan:
    def __init__(self):
        self.trash, self.compress, self.purge, self.errors = [], [], [], []
        self.kept = {"recent": 0, "in use": 0, "cited": 0}


def walk_store(store, errors):
    """(heavy candidates, receipts) under the store. A tree that cannot be read whole goes to
    errors and is left."""
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
                match = tree_match(entry.path, entry.name)
                if not match:
                    stack.append(entry.path)
                    continue
                try:
                    tree = Tree(entry.path)
                except OSError as error:
                    errors.append("unreadable, left: {}".format(error))
                    continue
                if tree.whole(match[1]):
                    candidates.append(Candidate(entry.path, match[0], tree.size, tree.mtime,
                                                tree.ctime, tree.heavy_names, match[1]))
                else:
                    stack.append(entry.path)
            elif entry.is_file():
                try:
                    st = entry.stat(follow_symlinks=False)
                except OSError as error:
                    errors.append("unreadable, left: {}".format(error))
                    continue
                kind = file_kind(entry.name, st.st_size)
                if kind:
                    candidates.append(Candidate(entry.path, kind, st.st_size, st.st_mtime,
                                                st.st_ctime))
                elif is_receipt(entry.name):
                    receipts.append(entry.path)
    return candidates, receipts


def trash_batches(store, now, in_use, errors, cited):
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
                marker = json.load(handle)
            moved_at = float(marker["moved_at"])
        except (OSError, ValueError, KeyError, TypeError):
            continue  # not ours: Brandon's to empty
        if now - moved_at > TRASH_DAYS * DAY and not in_use(batch):
            problem = batch_problem(store, batch, marker, now, cited)
            if problem:
                errors.append("purge left {}: {}".format(os.path.relpath(batch, store), problem))
            else:
                due.append((batch, moved_at))
    return due


def batch_problem(store, batch, marker, now, cited):
    """Why a batch may not be purged, or None: it must hold only what its manifest lists, nothing
    in it may have changed in the last 72 hours, and no open PR's receipt may cite one of its
    paths where it stood."""
    try:
        manifest = real_file(store, marker["manifest"])
        with open(manifest) as handle:
            listed = {line.split("\t", 1)[0] for line in list(handle)[1:]}
        tree = Tree(batch)
    except (OSError, KeyError, TypeError, Refused) as error:
        return "its manifest or contents cannot be read ({})".format(error)
    if max(tree.mtime, tree.ctime) > now - RECENT_HOURS * 3600:
        return "something in it changed in the last {} hours".format(RECENT_HOURS)
    for rel in sorted(listed):  # cited at its old path by a receipt written since the move
        if cited(os.path.join(store, rel), {os.path.basename(rel)}):
            return "an open PR's receipt cites {}".format(rel)
    for top, dirs, files in os.walk(batch):
        for name in files:
            rel = os.path.relpath(os.path.join(top, name), batch)
            if rel == MARKER:
                continue
            parts = rel.split(os.sep)
            if not any(os.sep.join(parts[:n]) in listed for n in range(1, len(parts) + 1)):
                return "it holds {}, which its manifest does not list".format(rel)
    return None


def real_file(store, rel):
    """store/rel when it is a regular file inside the store, not reached through a symlink."""
    folder = real_dir(store, os.path.dirname(rel)) if os.path.dirname(rel) else store
    path = os.path.join(folder, os.path.basename(rel))
    if os.path.islink(path) or not os.path.isfile(path):
        raise Refused("{} is not a file in the store".format(rel))
    return path


def build_plan(store, now, in_use, prs):
    """The plan. in_use is an InUse and prs the open PRs."""
    plan = Plan()
    candidates, receipts = walk_store(store, plan.errors)
    cited = Citations(store, prs, receipts)
    for item in candidates:
        age = (now - item.mtime) / DAY
        if age <= COMPRESS_DAYS:
            continue  # young; this also covers a modification time in the last 72 hours
        if item.ctime > now - RECENT_HOURS * 3600:
            plan.kept["recent"] += 1
        elif in_use(item.path):
            plan.kept["in use"] += 1
        elif cited(item.path, item.names):
            plan.kept["cited"] += 1
        elif age > TRASH_DAYS:
            plan.trash.append(item)
        elif item.kind == "log" and item.is_file and item.path.lower().endswith(".log"):
            plan.compress.append(item)
    plan.purge = trash_batches(store, now, in_use, plan.errors, cited)
    plan.cited = cited
    plan.errors += ["receipt not read, its folder kept: " + item for item in cited.unread]
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


def changed_since(path, now):
    st = os.lstat(path)
    return max(st.st_mtime, st.st_ctime) > now - RECENT_HOURS * 3600


def compress_log(path, record):
    """Gzip path in place, through a temporary file of this attempt's own. record(bytes, sha256,
    gz bytes) runs once the round trip matches and before the log is removed; a log that changed
    meanwhile is left as it was."""
    before = os.lstat(path)
    gz = path + ".gz"
    if os.path.lexists(gz):
        raise OSError("{} already exists".format(gz))
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path),
                               prefix="." + os.path.basename(path) + ".", suffix=".gz.tmp")
    os.close(fd)
    try:
        with open(path, "rb") as source:
            want = sha256_stream(source)
            source.seek(0)
            with gzip.open(tmp, "wb") as target:
                shutil.copyfileobj(source, target, 1 << 20)
        with gzip.open(tmp, "rb") as check:
            got = sha256_stream(check)
        after = os.lstat(path)
        if got != want or (after.st_size, after.st_mtime) != (before.st_size, before.st_mtime):
            raise OSError("the log changed or the gzip round trip did not match; left as it was")
        os.chmod(tmp, before.st_mode & 0o777)
        os.utime(tmp, (before.st_atime, before.st_mtime))
        record(before.st_size, want, os.lstat(tmp).st_size)
        os.rename(tmp, gz)
    finally:
        if os.path.lexists(tmp):
            os.remove(tmp)
    os.remove(path)


class RecordError(OSError):
    """A record could not be written, so nothing more may change."""


class Table:
    """A TSV in the report folder; each row is on disk before row() returns."""

    def __init__(self, folder, name, header):
        try:
            self.handle = open(os.path.join(folder, name), "w")
        except OSError as error:
            raise RecordError(error.errno, "could not open {}: {}".format(name, error.strerror))
        self.row(*header)

    def row(self, *cells):
        try:
            self.handle.write("\t".join(str(cell) for cell in cells) + "\n")
            self.handle.flush()
            os.fsync(self.handle.fileno())
        except OSError as error:
            raise RecordError(error.errno, "could not write {}: {}".format(
                os.path.basename(self.handle.name), error.strerror))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.handle.close()


def trash_one(store, now, item, in_use, batch, manifest_path, manifest):
    """Move one item into the batch, then record it; a failed record moves it back."""
    if in_use(item.path):
        raise OSError("opened since the plan was made")
    if changed_since(item.path, now):
        raise OSError("changed since the plan was made")
    rel = os.path.relpath(item.path, store)
    if item.is_file:
        size, digest = os.lstat(item.path).st_size, sha256_file(item.path)
    else:
        tree = Tree(item.path)  # walked again: the tree may have changed since the plan
        if not tree.whole(item.strict):
            raise OSError("it now holds .git or a receipt")
        if max(tree.mtime, tree.ctime) > now - RECENT_HOURS * 3600:
            raise OSError("something in it changed since the plan was made")
        size, digest = tree.size, sha256_tree(item.path)
    if not os.path.isdir(batch):
        os.mkdir(batch)
        with open(os.path.join(batch, MARKER), "w") as marker:
            json.dump({"moved_at": now, "manifest": os.path.relpath(manifest_path, store)}, marker)
    target = os.path.join(batch, rel)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    folder, real_batch = os.path.realpath(os.path.dirname(target)), os.path.realpath(batch)
    if folder != real_batch and not inside(folder, real_batch):
        raise OSError("its trash folder leaves the batch")
    if os.path.lexists(target):
        raise OSError("already in the batch")
    os.rename(item.path, target)
    try:
        manifest.row(rel, item.kind, size, digest, iso(item.mtime),
                     "{}, {} days old".format(item.kind, int((now - item.mtime) / DAY)))
    except RecordError as error:
        try:
            os.rename(target, item.path)
        except OSError as back:
            raise RecordError(error.errno, "{}; and moving {} back failed: {}".format(
                error, rel, back))
        raise
    return size


def apply_plan(store, now, plan, refresh, name, report_dir, out):
    """Carry out plan; return the failures. refresh() gives a fresh InUse before each step. A
    record that cannot be written stops the run, so nothing changes without its record."""
    trash = os.path.join(store, "_trash")
    batch = os.path.join(trash, name)
    failures, done = [], {"trash": 0, "compress": 0, "purge": 0}
    try:
        in_use = refresh()
        path = os.path.join(report_dir, "manifest.tsv")
        with Table(report_dir, "manifest.tsv",
                   ["path", "kind", "bytes", "sha256", "mtime", "reason"]) as manifest:
            for item in plan.trash:
                rel = os.path.relpath(item.path, store)
                try:
                    size = trash_one(store, now, item, in_use, batch, path, manifest)
                except RecordError:
                    raise
                except OSError as error:
                    failures.append("trash {}: {}".format(rel, error))
                    continue
                done["trash"] += 1
                out("trashed  {:<14} {:>12}  {}".format(item.kind, size, rel))

        in_use = refresh()
        with Table(report_dir, "compressed.tsv",
                   ["path", "bytes", "sha256", "mtime", "gz_bytes"]) as table:
            for item in plan.compress:
                rel = os.path.relpath(item.path, store)
                try:
                    if in_use(item.path):
                        raise OSError("opened since the plan was made")
                    if changed_since(item.path, now):
                        raise OSError("changed since the plan was made")
                    compress_log(item.path, lambda size, digest, gz_size: table.row(
                        rel, size, digest, iso(item.mtime), gz_size))
                except RecordError:
                    raise
                except OSError as error:
                    failures.append("compress {}: {}".format(rel, error))
                    continue
                done["compress"] += 1
                out("compressed  {}".format(rel))

        in_use = refresh()
        with Table(report_dir, "purged.tsv", ["batch", "moved_at", "bytes"]) as table:
            for path, moved_at in plan.purge:
                rel = os.path.relpath(path, store)
                try:
                    if in_use(path):
                        raise OSError("opened since the plan was made")
                    if os.path.islink(path) or not inside(os.path.realpath(path),
                                                          os.path.realpath(trash)):
                        raise OSError("not a folder in the store's _trash")
                    with open(os.path.join(path, MARKER)) as handle:
                        problem = batch_problem(store, path, json.load(handle), now, plan.cited)
                    if problem:
                        raise OSError(problem)
                    size = Tree(path).size
                    table.row(rel, iso(moved_at), size)  # the record comes first
                    shutil.rmtree(path)
                except RecordError:
                    raise
                except (OSError, ValueError) as error:
                    failures.append("purge {}: {}".format(rel, error))
                    continue
                done["purge"] += 1
                out("purged   {:>12}  {}".format(size, rel))
    except (RecordError, Refused) as error:
        failures.append("stopped, nothing more changed: {}".format(error))
    try:
        write_report(report_dir, name, now, plan, done, failures)
    except OSError as error:
        out("could not write report.md: {}".format(error))
        failures.append(str(error))
    return failures


def write_report(report_dir, name, now, plan, done, failures):
    lines = [
        "# Store retention run {}".format(name), "",
        "Written {} by `scripts/store-retention/store_retention.py --apply`"
        " (agent-working-agreements#328).".format(iso(now)), "",
        "- Trashed: {} of {} planned, into `_trash/{}/` (`manifest.tsv`).".format(
            done["trash"], len(plan.trash), name),
        "- Compressed: {} of {} logs (`compressed.tsv`).".format(
            done["compress"], len(plan.compress)),
        "- Purged: {} of {} trash batches past {} days (`purged.tsv`).".format(
            done["purge"], len(plan.purge), TRASH_DAYS),
        "- Heavy and old enough, but kept: {} in use, {} cited by an open PR's receipt, {} changed"
        " in the last {} hours.".format(
            plan.kept["in use"], plan.kept["cited"], plan.kept["recent"], RECENT_HOURS),
    ]
    for title, items in (("Failed", failures), ("Left alone", plan.errors)):
        if items:
            lines += ["", "## " + title, ""] + ["- {}".format(item) for item in items]
    with open(os.path.join(report_dir, "report.md"), "w") as report:
        report.write("\n".join(lines) + "\n")


def print_plan(store, plan, out):
    for item in plan.trash:
        out("would trash    {:<14} {:>12}  {}".format(item.kind, item.size,
                                                       os.path.relpath(item.path, store)))
    for item in plan.compress:
        out("would compress {:>12}  {}".format(item.size, os.path.relpath(item.path, store)))
    for path, moved_at in plan.purge:
        out("would purge    {}  (moved {})".format(os.path.relpath(path, store), iso(moved_at)))
    for error in plan.errors:
        out("left           {}".format(error))
    out("-- dry run: {} to trash ({} bytes), {} logs to compress, {} batches to purge; kept: {} in"
        " use, {} cited, {} recent. Nothing changed.".format(
            len(plan.trash), sum(item.size for item in plan.trash), len(plan.compress),
            len(plan.purge), plan.kept["in use"], plan.kept["cited"], plan.kept["recent"]))


def dry_run(store, now, in_use, prs, out):
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
    print_plan(store, build_plan(store, now, InUse(store, pair), pr_list), out)
    return 0


def run(store, apply, now=None, in_use=None, prs=None, out=print):
    """The whole job. in_use and prs are callables, replaced in tests; returns the exit status."""
    now = time.time() if now is None else now
    in_use = in_use or (lambda: lsof_paths(store))
    prs = prs or open_prs
    if not apply:
        return dry_run(store, now, in_use, prs, out)
    try:
        trash = real_dir(store, "_trash")
        real_dir(store, REPORTS)
    except Refused as error:
        out("refused: {}".format(error))  # no report: its folder is the thing in doubt
        return 3
    os.makedirs(trash, exist_ok=True)
    with open(os.path.join(trash, LOCK), "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            out("refused: another retention run holds the lock")
            return 3
        name = run_id(store, now)
        report_dir = os.path.join(store, REPORTS, name)
        os.makedirs(report_dir)
        try:
            plan = build_plan(store, now, InUse(store, in_use()), prs())
        except Refused as error:
            with open(os.path.join(report_dir, "report.md"), "w") as report:
                report.write("# Store retention run {}\n\nRefused at {}: {}. Nothing was moved,"
                             " compressed or deleted.\n".format(name, iso(now), error))
            out("refused: {}".format(error))
            return 3
        failures = apply_plan(store, now, plan, lambda: InUse(store, in_use()), name,
                              report_dir, out)
        out("report: {}".format(os.path.relpath(report_dir, store)))
        return 1 if failures else 0


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
