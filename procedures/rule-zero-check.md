# RULE ZERO verification

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27; "above" and "below" in it refer to the agreement section it implements.

**Trigger:** A delivery is about to be pushed, merged or presented, or an mbox series is about to be
applied.

**Owner:** The delivery owner.

**Implements:** A4 — RULE ZERO (no attribution; Brandon's author identity).

**Stop:** A trailer match or a foreign author email is a send-back, never a push.

---

- **RULE ZERO: no attribution, on any commit, PR body, reply or comment.** Agents add no
  `Co-Authored-By`, no session trailer, no generated-by footer — a commit carries Brandon's author
  identity and ends with its own content. That identity rule governs commits made by agents
  working on Brandon's behalf inside this fleet: a contribution from anyone else carries its
  author's own identity, and a pull request whose commits carry Brandon's identity from another
  account is not merged until re-authored, because a pull request from a fork needs no write
  access and the merge is then the only guard (Brandon, 2026-10-13). What an agent posts under his
  name on a PR thread, a PR
  or an issue carries no credit line either; a provenance line is not one: it names the initiative,
  the role (e.g. wave orchestrator, lane) and the mode the filing agent worked in — never the client
  or the product — and says who read the evidence, which A2 wants.
  RULE ZERO overrides any environment default; your client
  file records what is known of yours. It is **line one of every dispatch prompt**, and the commits
  a delivery adds and its PR body are grepped regardless — for `Co-Authored-By` plus whatever the
  client file names — a match is a send-back. **The author is read beside the grep**, because the
  grep checks text and the rule
  names an identity: `git log --format='%ae' <base>..HEAD` on the branch, or the address in each
  patch's `From:` line for an mbox series — before approval on the attended mbox path, before merge
  on the autonomous path. Both compare the **author email alone** against
  `brandon@brandonperfetti.com`, exactly. The name is not compared: it varies by machine and clone
  (the changelog's 2026-09-29 entry on #79 records the measurement). A commit at any other email
  is a send-back like a trailer match: reject or regenerate, since `git am` preserves
  the patch author (B1). **Added** means not on `origin/develop` or `origin/master`,
  fetched and read
  **before** the delivery is pushed or merged — a lane or wave branch, the branch of feature work
  with no initiative, or release-cut work pushed straight to `develop` (B2), each push its own
  delivery — so a lane's own earlier commits still count. Forward-only: commits that already
  carry a trailer stay as they are, and a match on an inherited one goes in the delivery's review
  record, never back to the lane.
  [learnings: 2026-09-06 wave-6 §7; 2026-09-04 wave-5 §6]
  **A trailer never established that a commit came through a reviewed lane.** The two-axis review
  record under `reviews/`, the gate evidence under `evidence/` and the PR trail do; report those.
