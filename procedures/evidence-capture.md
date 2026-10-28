# Evidence capture

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27; "above" and "below" in it refer to the agreement section it implements.

**Trigger:** A claim is about to be labelled `[measured]` from bytes that cannot be reproduced, a
probe's negative result is about to be believed, a file is about to be quoted as `[source]`, or a
recorded claim turns out to be wrong.

**Owner:** Whoever makes the claim.

**Implements:** A2 — Evidence discipline.

**Stop:** None; capture never blocks delivery.

---

- **Preserve [measured] evidence — classified first.** Irreproducible bytes are preserved in
  `evidence/`, named for what they prove, before summarizing. Retrievable evidence gets a stable
  locator, SHA-256, and relevant excerpt — or the search terms plus absence; do not copy a
  retrievable artifact merely to prove a claim. A summary is not evidence.
- **The generalization boundary is part of the label** — "[measured] on the first item" is never
  written as "[measured] on all N". A label is **never inherited across revisions**: re-measure or
  downgrade. [learnings: 2026-09-04 wave-5 §2]
- **The instrument is part of the claim.** Positive-control a probe before believing its negatives;
  grep a "green" run for skip markers before calling assertions proven; name every required env
  export in a gate line. **A tool call that succeeded is not proof its whole output reached you** —
  reads and command output truncate silently; check for a truncation notice, and re-read in slices
  before quoting a file as `[source]`. [learnings: 2026-08-30 §1; 2026-09-04 wave-5 §1, §8]
- **A reviewer's [inference] is never promoted into shipped code or docs** — measure it or leave it
  labelled. [learnings: 2026-09-04 wave-5 §9]
- **Correct in place, marked and dated.** Quote the old text, say it shouldn't be relied on, state
  what was observed vs concluded. Never silently swap. [learnings: 2026-08-30 §12]
