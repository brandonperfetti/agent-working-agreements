// OpenClaw plugin: runs before every tool call and blocks what hooks/claude-code/guard_git.py
// denies (relay.mjs). A standalone file, loaded through plugins.load.paths; its id is its name.
// A handler that throws or times out blocks the call (OpenClaw's before_tool_call failure policy);
// a plugin that is not loaded blocks nothing, which is why the route's canary runs before a merge.
import { appendFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { decide, PLUGIN_ID, redact, runGuard } from "./relay.mjs";

const LOG = process.env.AWA_GUARD_GIT_LOG || join(homedir(), ".openclaw", "logs", `${PLUGIN_ID}.jsonl`);

async function record(event, ctx, decision) {
  // Blocks and merge-bearing calls only, so the log holds the route's evidence and not every
  // command (which can carry secrets in assignments).
  const text = JSON.stringify(event.params ?? {});
  if (!decision.block && !/merge/i.test(text)) return;
  const line = {
    at: new Date().toISOString(),
    agent: ctx?.agentId,
    session: ctx?.sessionKey,
    runId: event.runId ?? ctx?.runId,
    tool: event.toolName,
    kind: event.toolKind ?? ctx?.toolKind,
    block: decision.block,
    reason: decision.reason,
    params: redact(event.params).slice(0, 600),
  };
  try {
    await appendFile(LOG, JSON.stringify(line) + "\n", { mode: 0o600 });
  } catch {
    // the log is evidence, not the control
  }
}

export default {
  id: PLUGIN_ID,
  name: "AWA guard_git relay",
  description: "Blocks tool calls that hooks/claude-code/guard_git.py denies; fails closed.",
  register(api) {
    api.on(
      "before_tool_call",
      async (event, ctx) => {
        const decision = await decide(event.toolName, event.params, runGuard, {
          kind: event.toolKind ?? ctx?.toolKind,
          inputKind: event.toolInputKind ?? ctx?.toolInputKind,
        });
        await record(event, ctx, decision);
        return decision.block ? { block: true, blockReason: decision.reason } : undefined;
      },
      { priority: 1000, timeoutMs: 15000 },
    );
  },
};
