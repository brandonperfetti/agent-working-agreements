# OpenClaw session rotation

This procedure carries mechanics for `clients/openclaw.md` and the rule it implements in
[`../../AGENT-WORKING-AGREEMENTS.md`](../../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts
A–B, and a rule here that contradicts one there is the rule that is wrong.

**Trigger:** Rotation of an OpenClaw orchestrator at wave close or an earlier clean stopping point.

**Owner:** The current orchestrator; Brandon sets the numeric context trigger.

**Implements:** A4 and `clients/openclaw.md` *Rotation*.

**Stop:** On refusal, system/spawn provenance or missing tools, stop with the exact result.

---

**Rotation:** Rotate at wave close, or earlier at a clean stopping point when context runs high;
Brandon sets the numeric trigger. Save the outcome, evidence, owners, approvals and exact next action
in the initiative handoff.

Create an empty named root with:

```sh
openclaw gateway call sessions.create --params '{"key":"agent:main:<fresh-key>","agentId":"main","displayName":"<title>"}' --json
```

Pass no message, task, attachments or parent. Inspect its provenance, then deliver the kickoff
through native attributed `sessions_send`, never CLI messaging. Verify no `spawnedBy` or parent,
depth `0` or absent, required control/messaging tools, kickoff receipt and `created_actor_type` is
not `system` and `displayName` is set.

The harmless probe passed; real-work pickup remains unproven. At the first real handoff, verify the
recipient accepts and advances the authorized next action before retiring the old orchestrator.

Never rotate through `sessions_spawn`. Automations failed default visibility; direct CLI agent
messaging was refused. On refusal, system/spawn provenance or missing tools, stop with the exact
result—no alternate route, marker changes or allowlist additions.
