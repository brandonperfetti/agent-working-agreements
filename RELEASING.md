# Release the working agreement

Use the [standing grant](AGENTS.md#release-tags) and [shared procedure](procedures/post-merge-release.md).
The orchestrator may fast-forward local `master`, publish one annotated tag for the qualified
owner merge, create or verify its GitHub Release and verify the back-merge. This grant covers
routine releases under these instructions and the shared procedure's mode rules. Brandon merges
`develop → master` in GitHub.

1. Read the merged PR and its [release acceptance](procedures/review-findings.md#acceptance-and-staleness).
   Confirm Brandon merged this repository's `develop` into `master`. Match the accepted head to
   the merged PR head and the merge commit's second parent. Verify the required `check` succeeded
   on that PR head or its GitHub test merge, with the run bound to this PR and head. Stop on
   missing, failed or stale evidence. Record the PR, accepted head, check and exact merge OID.
   Fetch origin. If the merge differs from the remote tip, stop. Fast-forward local `master` with
   `git merge --ff-only origin/master` from a clean checkout on `master`. Coordinate with the
   checkout's owner if it is in use. Stop if the fast-forward fails. Confirm
   both `HEAD` and `origin/master` equal the recorded commit. Summarize what goes into force from
   that commit's `CHANGELOG.md` delta against its first parent and link the release PR.
2. Use `vYYYY.MM.DD` for the merge date in America/Los_Angeles. Later distinct releases that day
   take `.1`, then `.2`, in order. Inspect existing tags and their targets first so a resumed
   release reuses its tag and a conflict never takes a fresh suffix. On a remote-only tag, fetch
   and inspect that exact object. An existing tag must be annotated, point at the verified merge,
   carry Brandon's tagger email, and have the expected name and message. Compare local and remote
   object IDs and peeled commits. An unpushed local tag needs provenance from this release
   attempt before use. If identity is uncertain, stop and report it.
3. For a new tag, use `git tag -a <tag> <merge-commit> -F <message-file>` under RULE ZERO. The
   annotation explains what goes into force and closes with one `Agent:` line. Read
   `git cat-file -p refs/tags/<tag>` for the target, type, name, tagger and message. Record
   `git rev-parse refs/tags/<tag>` and the peeled commit. Immediately before pushing, confirm
   the live `master` tip still matches and `git remote get-url --push --all origin` returns
   exactly the fetch URL for `brandonperfetti/agent-working-agreements`. Confirm tag state again.
   Push in a separate, standalone call so the guard can read the created object.

   ```bash
   git push --no-follow-tags origin refs/tags/<tag>:refs/tags/<tag>
   ```

4. Read `git ls-remote origin 'refs/tags/<tag>' 'refs/tags/<tag>^{}'` and compare both IDs with
   the receipt. A confirmed match lets the run continue without another push. Missing or divergent
   state after a push, or an unreadable result, goes to Brandon before any retry.
5. Query the repository's Releases, including drafts, for the exact tag. Confirm absence from a
   successful read before creating. Immediately before creating, recheck the tag object and
   peeled commit against the receipt. Use the prepared notes and the existing tag.

   ```bash
   gh release create <tag> --repo brandonperfetti/agent-working-agreements \
     --verify-tag --title <tag> --notes-file <file>
   ```

   Publish stable notes with the default source archives and no uploaded assets. Read the
   Release back by tag and compare its URL, tag, title, notes, draft and prerelease flags and
   asset list. Recheck the remote tag object and peeled commit. A matching existing Release
   completes this step. If creation returns an unclear result, read the Release and tag before
   another write. A draft, mismatch or unreadable result goes to Brandon.
6. Check the [back-merge workflow](.github/workflows/backmerge.yml) run for the exact merge SHA,
   triggered by the push to `master`. Close only with a successful run, the commit confirmed as
   an ancestor of freshly fetched `origin/develop`, and no open repository `master → develop`
   fallback PR. A pending run leaves verification open. Bring any other unresolved state to
   Brandon with the run link if available and the ancestry and fallback PR results. Preserve
   the tag and Release. Brandon handles any repair.

## Historical Releases and rollback

Historical Release publication requires an explicit grant for the backfill. Audit each existing
tag and prepare notes from that revision's first-parent changelog delta and annotation. Record
eligibility and disposition before publishing. Use the existing immutable tags.

Brandon decides rollback. In `~/dev/sansfaux/agent-working-agreements`, check out the selected tag
and run the installers present at that revision. A hook whose installer is absent stays as it was.

```bash
git checkout <tag>
/usr/bin/python3 hooks/claude-code/install.py
/usr/bin/python3 hooks/codex/install.py
node hooks/openclaw/install.mjs
```

Run each installer's `--check`, start a new session, and for OpenClaw reload the plugin and run
its [canary](hooks/openclaw/README.md). The OpenClaw protected root stays on that tag until Brandon
ends rollback.
