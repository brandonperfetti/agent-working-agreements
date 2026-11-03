# OpenClaw conversation continuity

**Trigger:** Opening an authorized independent topic conversation, routine context maintenance,
context pressure, compaction, or recovery of an OpenClaw orchestrator.

**Owner:** The current orchestrator; Ashford owns control-plane maintenance routes.

**Implements:** A4 continuity and `clients/openclaw.md` context checkpoints.

**Stop:** Retain the checkpoint and current owner on an unsafe or unavailable operation;
name its restoration owner under B2 while independent work continues.

This procedure implements the canonical agreement; it never overrides Parts A–B, and
a rule here that contradicts one there is the rule that is wrong.

## Keep ongoing conversations stable

Brandon may keep separate Camina conversations for different topics or initiatives, with staff
and lanes delegated from each. Preserve the conversation he is using through ordinary context
maintenance, with current receipts and pointers on disk. Open a new authorized topic with
[Create a root conversation](#create-a-root-conversation).

Prefer the runtime's automatic in-place compaction. Context growth alone does not require a new
sidebar session, ownership transfer or collector retarget. Use supported idle compaction when
maintenance is needed; use a same-key reset only for recovery at a verified clean pause.
Exceptional root replacement is the last branch below.

## Checkpoint and inspect

1. Measure the current session's reported used-context tokens / capacity. Record key, runtime
   identity, timestamp, route, numerator, denominator and source. Refresh stale or missing
   telemetry; retain an unknown reading honestly rather than treating it as zero.
2. Checkpoint decisions and work around 30%; refresh the recovery packet around 40%. At 60%,
   assess actual pressure and the supported maintenance route at the next safe pause. These
   are planning heuristics, not provider quality cliffs or mandatory new-session thresholds.
3. Keep the MPD and one concise current checkpoint sufficient for pickup: owner-authorized
   objective, shipped versus open work, holds, exact owners/checkouts, pending results and
   decisions, receipt pointers, continuation route and next bounded action. Update existing
   records rather than creating a new handoff chain for each observation.

## Compact and continue in place

Let automatic compaction preserve the conversation. For manual maintenance, verify the actual
runtime supports it: built-in OpenClaw and a native provider CLI can have different capabilities.
A refused or no-op request is not a successful compaction.

Run manual lifecycle operations only after foreground activity and queued inputs have settled.
The orchestrator may arrange an idle maintenance handoff to a qualified staff root; finish the
bounded turn instead of waiting on an operation that requires that same turn to become idle.
The maintainer retains the checkpoint pointer and owns resumption through a supported route.
Use existing completion/continuation paths rather than adding a persistent watcher.

Record the operation's result and recheck key, visible title, root provenance and required tools.
Use reported compaction evidence or context reduction to distinguish compaction from admission.
Reload the checkpoint, current agreement and triggered sources, reconcile live work, and actually
advance its next action. Preserve the same continuation binding and verify it remains usable.

## Same-key reset for recovery

A reset can cancel unfinished native children, invalidate inherited memory audiences and discard
queued notices. First settle affected children, staff callbacks, active runs and queued inputs;
persist every needed decision/result and establish who will resume the checkpoint afterward.
Keep independent delivery owners and worktrees intact.

Use the supported in-place reset on the exact key, with an expected current session identity
where available. A lifecycle revision can change even when the session ID stays the same.
Recheck the key and title, empty/new active context, root provenance and available tools.
Then deliver the checkpoint kickoff to that same conversation through a supported attributed
route, reload governing sources, apply `takeover` reconciliation and verify actual advancement.
Reconcile continuation references to runtime identity if needed; an unchanged session key alone
does not prove every old callback remains valid.

On a partial, refused or ambiguous result, inspect live state before another operation. Preserve
the checkpoint and name the affected route's restoration owner; avoid repeated reset attempts.

## Create a root conversation

These steps serve an authorized independent topic or initiative and, unchanged, the creation
step of an exceptional root replacement (below). An ordinary topic needs no evidence of a broken
predecessor, no retirement and no ownership transfer: existing conversations continue as they
are, and the new one carries only scope Brandon or the authorizing owner already granted.

1. Select the lead's canonical agent ID; omit `key` so the server allocates a fresh key rather
   than adopting a caller-selected entry. Retain the returned key and session ID as authoritative.
2. Create an empty root through native `exec`, preserving its exec marker. With `leadId` and
   `title` already held as data in Code Mode, JSON-encode them and shell-quote the single argument:

   ```js
   const params = JSON.stringify({ agentId: leadId, displayName: title });
   const quote = value => "'" + value.replaceAll("'", "'\\''") + "'";
   const result = await exec({
     command: "openclaw gateway call sessions.create --params " + quote(params) + " --json",
     title: "Create empty topic root"
   });
   ```

   Pass no message, task, attachments or parent. Keep task values out of shell source except
   through the encoder and quoting function; apostrophes, quotes, backslashes and shell-like text
   remain literal data.
3. Read back the returned key/session ID, selected agent ID, exact title, operator rather than
   system/spawn provenance, depth zero, no `spawnedBy`, empty history and `pendingInputs.total` of 0.
   A dashboard `parentSessionKey` may link to the agent's Home for navigation; distinguish that
   link from actual spawn lineage using provenance, depth and `spawnedBy` before kickoff.
4. Deliver the kickoff through native attributed `sessions_send`, using the team dispatch
   procedure's structured preflight. Verify the recipient has the required current control and
   messaging tools and receipt access, then its acceptance and actual first advancement. A nested
   worker retains its own tool boundaries; naming it Camina does not grant chief-of-staff tools.

On an ambiguous result, inspect live state before any retry. If the returned identity was lost,
list recent roots for the selected agent and exact title, then inspect candidate identities,
provenance, history and pending inputs. A title match alone does not prove identity. If creation
cannot be uniquely reconciled, stop and report the uncertainty; do not retry or send a kickoff.
Having no first-class native creation tool is not, by itself, a failure of this CLI route. When
an operation is actually refused or unavailable, stop that operation, report its exact result and
name its restoration owner per `clients/openclaw.md`; independent work continues.

## Exceptional root replacement

Use a new root when measured evidence shows the existing conversation cannot safely recover
through its supported in-place routes. Record the reason and preserve the A4 packet under the
initiative's `handoffs/`, or `_agent/handoffs/` for one-off work. Retain the predecessor until
the replacement is accepted and actually advances the authorized objective.

Create the replacement per [Create a root conversation](#create-a-root-conversation), delivering
the saved kickoff. After its acceptance and actual advancement, explicitly transfer ownership and
the continuation binding; reconcile the existing continuation route and observe its actual pickup.

Once no spawned work is running or queued, no worktree remains in use by the predecessor, and
no decision lives only there, archive it through the supported lifecycle route and move the
current label to the accepted owner. Retain an older root only for a named live dependency with
an owner and next check; a generic read-only fallback is not indefinite sidebar retention.
