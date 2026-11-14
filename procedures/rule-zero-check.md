# RULE ZERO verification

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. RULE ZERO itself is in
[`../profiles/sansfaux.md`](../profiles/sansfaux.md).

**Trigger:** A delivery is about to be pushed, merged or presented, or an mbox series is about to
be applied.

**Owner:** The delivery owner.

**Implements:** A4 — RULE ZERO (Brandon's author identity on every commit an agent makes, and one
agent declaration per item, with no other attribution line).

**Stop:** A commit at any other author email, or carrying a banned line or a malformed or second
declaration, is a send-back, never a push.

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
carries Brandon's email; the client file records what is known of its default. Beyond the one
declaration, no provenance or credit footer is required on a PR, issue or reply; its body cites the
receipts inline — the review record, the gate evidence, the issue — which A2 wants.

**The declaration is one line, and nothing else attributes** (Brandon, 2026-11-14, replacing the
no-attribution override of #226 and absorbing #245's agent label). New work carries
`Agent: <client> · <model id> · <effort>` — OpenClaw `Agent: Camina (OpenClaw) · <model>` — with
the served model where it is attested, otherwise the requested one marked `(requested)`, and an
unattested effort marked the same way: a git trailer on a commit, the closing line of a PR body,
issue body, comment or thread reply, on Brandon's repositories and others' alike. In the range above,
read the messages of the commits the delivery adds for the banned lines:

```sh
git log --format='%B' <base>..HEAD | grep -inE '^[#>*+[:blank:]-]*(co-authored-by|[a-z-]*-session)[[:blank:]]*:|generated with|^[#>*+[:blank:]-]*posted by an agent([^[:alnum:]_]|$)|claude\.ai/(chat|code/session)|chatgpt\.com/(c|share)/|chat\.openai\.com/(c|share)/'
```

and list each commit's declaration lines, any case and any prefix:

```sh
git rev-list <base>..HEAD | while read -r c; do git log -1 --format='%B' "$c" | grep -iE '^[#>*+[:blank:]-]*agent[[:blank:]]*:' | sed "s/^/$c /"; done
```

A banned match, a commit with two lines, or a line not in the shape above is a send-back. A
missing declaration is not, in the hooks or in this read; the profile still asks new work for one.
On a Mac with the hooks installed (`hooks/git/README.md`), git's `commit-msg` hook refuses such a
commit as it is made, and the Claude Code guard's push-time scan refuses to push one it can see (a
best-effort read against the destination's tracking refs); this read before presentation is the
complete check, the one that does not depend on where the commit was made or what the guard could
see. Read an mbox series' message bodies the same way before approval, and a PR body, issue, comment
or thread reply before it is posted: none of the banned lines, and the one declaration as its
closing line. A commit already on a base branch stays as it is, recorded like an email mismatch.
A trailer never established that a commit came through a reviewed lane: the two-axis review record
under `reviews/`, the gate evidence under `evidence/` and the PR trail do; report those.
