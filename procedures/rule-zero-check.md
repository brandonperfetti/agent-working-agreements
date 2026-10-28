# RULE ZERO verification

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. Rewritten 2026-10-27 when
RULE ZERO became the author-identity rule; the no-attribution grep it carried before is in this
file's history.

**Trigger:** A delivery is about to be pushed, merged or presented, or an mbox series is about to
be applied.

**Owner:** The delivery owner.

**Implements:** A4 — RULE ZERO (Brandon's author identity on every commit an agent makes).

**Stop:** A commit at any other author email is a send-back, never a push.

---

**The author is read, not inferred.** Before a delivery is pushed or merged, and again before it
is presented, read the author email of every commit the delivery adds:

```sh
git log --format='%ae' <base>..HEAD
```

For an mbox series on the attended path, read the address in each patch's `From:` line instead,
before approval, since `git am` preserves the patch author and is itself the commit.

**Added** means not on `origin/develop` or `origin/master`, fetched and read before the delivery
is pushed or merged — a lane or wave branch, the branch of feature work with no initiative, or
release-cut work pushed straight to `develop` — so a lane's own earlier commits still count.

**The comparison is the email alone**, against `brandon@brandonperfetti.com`, exactly. The name
is not compared: it varies by machine and clone (the changelog's 2026-09-29 entry on #79 records
the measurement). A commit at any other email is a send-back: reject or regenerate. Forward only:
a commit already on a base branch stays as it is, and a mismatch found there goes in the
delivery's review record, never back to the lane.

**The identity rule overrides any environment default.** A harness that would commit as a bot or
service account, or as the user of another machine, is configured or worked around so the commit
carries Brandon's email; the client file records what is known of its default. A provenance line
on a PR or issue names the initiative, the role and the mode, never the client or the product, and
says who read the evidence, which A2 wants.

**Attribution is not checked.** A `Co-Authored-By` line, a generated-with footer or a session
trailer may be present or absent; neither state is a finding (Brandon, 2026-10-27). A trailer
never established that a commit came through a reviewed lane: the two-axis review record under
`reviews/`, the gate evidence under `evidence/` and the PR trail do; report those.
