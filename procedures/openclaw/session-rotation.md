# OpenClaw session rotation

This procedure carries mechanics for `clients/openclaw.md` and the rule it implements in
[`../../AGENT-WORKING-AGREEMENTS.md`](../../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts
A–B, and a rule here that contradicts one there is the rule that is wrong.

**Trigger:** Context-driven rotation of an OpenClaw orchestrator at a clean stopping point.

**Owner:** The current orchestrator; the client appendix records approved context thresholds.

**Implements:** A4 and `clients/openclaw.md` *Rotation*.

**Stop:** On refusal, system/spawn provenance or missing tools, stop with the exact result.

---

**Rotation:** Apply the client appendix's context thresholds automatically. At the handoff
threshold, finish the current bounded unit and rotate at a clean pause; at the backstop, take the
next safe stop instead of starting new work. Wave close, PR submission and PR merge are natural
pauses, not mandatory rotations or owner approval gates. Save an A4 packet under `handoffs/` that
begins with shipped-versus-open reconciliation and records the outcome, receipts, owners,
authority, constraints and exact next authorized action. Carry authority without inventing gates.

Choose a key absent from the session store. Use the current lead's canonical agent ID and matching
key prefix; the example below is for Camina (`main`).

Create an empty named root with:

```sh
openclaw gateway call sessions.create --params '{"key":"agent:main:<fresh-key>","agentId":"main","displayName":"<title>"}' --json
```

Before sending, verify the root is newly created and has no prior messages or context; if it was
adopted or is non-empty, stop.

Pass no message, task, attachments or parent. Inspect its provenance, then deliver the kickoff
through native attributed `sessions_send`, never CLI messaging. Point to the saved packet, include
its highlights and instruct the recipient to read it. Verify no `spawnedBy` or parent,
`spawnDepth` 0/absent, control/messaging tools, kickoff receipt and `createdActor.type` absent or
not `system` and `displayName` is set.

A harmless creation probe is not real-work pickup. For every handoff, verify that the recipient
accepts and actually advances the authorized next action, with a receipt linked from the packet.
Before retiring or archiving the old orchestrator, ensure nothing it spawned runs or is queued, it
owns no worktree in use, and no open decision lives only there. Brandon may archive it once these
conditions are met.

Never rotate through `sessions_spawn`. Automations failed default visibility; direct CLI agent
messaging was refused. On refusal, system/spawn provenance or missing tools, stop with the exact
result—no alternate route, marker changes or allowlist additions.
