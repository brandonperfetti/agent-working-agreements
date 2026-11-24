# Post-merge release delivery

**Trigger:** A repository records or exercises standing authority for post-merge release delivery.

**Owner:** Brandon grants authority. The named agent or role executes the repository runbook.

**Implements:** Git ritual steps 7–8 under A3, A4, A5 and B2.

**Stop:** Hold the affected action on missing authority, failed or unreadable qualification,
divergent history or conflicting publication. Brandon owns release-branch merges and tag repair.

This procedure implements [Parts A–B](../AGENT-WORKING-AGREEMENTS.md). It never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong.

## Record the grant

Record Brandon's approval in the repository's instructions and link its release runbook there.
Name the designated role, repository and release branch, eligible owner-merged PRs, existing
review and check requirements, allowed operations, publication identity and downstream outcomes.
Grant only the operations the repository uses. Use existing authorized credentials and the
repository's approved route. Once the grant is in force, the designated role may perform each
covered release without per-tag or per-Release approval. Where a grant is absent or an operation
lies outside its scope, Brandon acts or explicitly approves the operation for the named release.
Each repository grants its own authority.

## Execute the runbook

1. Verify the owner merge, repository, branch, exact merge commit and required review and gate
   evidence. Fetch and fast-forward only the local release branch in the authorized checkout.
   Confirm it equals the qualified commit. Stop on a different remote tip or divergence.
2. Follow the repository's tag naming and annotation rules. Read local and remote tag state
   before creation. Read back the annotated object, tagger, message and exact commit before a
   separate single-tag push. Check the push destination and recheck live state before writing.
   Never force, move, delete or recreate a published tag. A matching remote object resumes at
   verification. A conflicting object, including a different annotation for the same commit,
   goes to Brandon.
3. After any push result, read the remote tag object and peeled commit. If both match, continue.
   If either is missing, different or unreadable, preserve the evidence and bring it to Brandon
   before any retry.
4. Read the GitHub Release by tag before writing. Where a workflow owns creation, verify its
   output. Where the grant authorizes direct creation, use the confirmed existing tag, approved
   notes and authorized assets. Verify the record's tag, URL, publication state and intended
   assets. A matching published Release completes this step on repeat. An unexpected draft,
   conflicting record or unreadable result holds the write. After an ambiguous create, read
   state before considering a retry. Keep private artifacts out of public release assets.
5. Verify downstream checks for this exact release. On a missing, failed or incomplete outcome,
   preserve tag and Release identity, report the run and state, and use only the recovery the
   runbook authorizes. Close delivery after the downstream outcomes are verified.

Audit historical tags and notes separately. Publishing against an earlier tag needs a grant
that explicitly covers historical Releases or an explicit owner decision for that backfill.

The Git guard scans the commits a tag push would send. A permitted command establishes that
mechanical result only. The recorded grant, tag readback and review receipts establish release
authority and publication identity.
