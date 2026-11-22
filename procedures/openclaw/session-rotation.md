# OpenClaw conversation continuity

**Trigger:** Opening an authorized independent topic conversation, routine context maintenance,
context pressure, compaction, or recovery of an OpenClaw orchestrator.

**Owner:** The current orchestrator; Ashford owns control-plane maintenance routes.

**Implements:** A4 continuity and `clients/openclaw.md` *Seats and routes*.

**Stop:** Retain the checkpoint and current owner on an unsafe or unavailable operation;
name its restoration owner under B2 while independent work continues.

This procedure implements the canonical agreement; it never overrides Parts A–B, and
a rule here that contradicts one there is the rule that is wrong.

## Keep the conversation Brandon is using

Brandon may keep separate Camina conversations per topic or initiative. Keep each one going: let
the runtime compact in place, and keep the master document and one current checkpoint on disk good
enough for a fresh pickup: the objective, what shipped and what is open, holds, owners and
checkouts, pending results and the next action. Update that checkpoint; do not start a new handoff
chain for each observation. Context growth alone is no reason for a new session or an ownership
transfer.

A refused or no-op compaction is not a compaction. After any maintenance, check the key, title and
tools, reload the checkpoint and the agreement, and advance the next action.

**A same-key reset is recovery, not maintenance.** It can cancel unfinished children and drop
queued notices, so first settle children, callbacks and queued inputs and persist every decision.
Reset the exact key at a clean pause, deliver the checkpoint to the same conversation, and
reconcile it with `takeover`. On an ambiguous result, inspect live state before trying anything
again.

## Create a root conversation

For an authorized new topic, or the replacement below. A new topic carries only scope already
granted; existing conversations continue as they are.

1. Create an empty root for the lead's canonical agent ID through native `exec`, with no `key` so
   the server allocates one. Encode the values and quote the argument so a title is always data:

   ```js
   const params = JSON.stringify({ agentId: leadId, displayName: title });
   const quote = value => "'" + value.replaceAll("'", "'\\''") + "'";
   const result = await exec({
     command: "openclaw gateway call sessions.create --params " + quote(params) + " --json",
     title: "Create empty topic root"
   });
   ```

2. Read back the returned key, agent ID, title, operator provenance, depth zero, no `spawnedBy`,
   and empty history and pending inputs.
3. Send the kickoff with native `sessions_send`, then confirm the recipient has the tools the work
   needs, accepted it and advanced. A nested worker named Camina does not gain her tools.

If the returned identity was lost, a title match alone does not identify the root: inspect the
candidates, and if none is uniquely yours, stop and report rather than retry or send a kickoff.

## Exceptional root replacement

Only when evidence shows the conversation cannot recover in place. Save the A4 packet under the
initiative's `handoffs/`, or `_agent/handoffs/` for one-off work, create the replacement as
above, and transfer ownership once it has accepted and advanced. Archive the predecessor only when
no work, worktree or decision still lives there.
