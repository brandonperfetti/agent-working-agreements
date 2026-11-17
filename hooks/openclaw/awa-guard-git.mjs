// OpenClaw plugin: runs before every tool call and blocks what hooks/claude-code/guard_git.py
// denies (relay.mjs). A standalone file, loaded through plugins.load.paths; its id is its name.
// A handler that throws or times out blocks the call (OpenClaw's before_tool_call failure policy);
// a plugin that is not loaded blocks nothing, which is why the route's canary runs before a merge.
import { appendFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { decide, PLUGIN_ID, runGuard, SHELL_TOOLS, SESSION_TOOLS, TEXT_TOOLS } from "./relay.mjs";

const LOG = process.env.AWA_GUARD_GIT_LOG || join(homedir(), ".openclaw", "logs", `${PLUGIN_ID}.jsonl`);

const ROUTES = new Set(["guard", "code-mode", "shell", "session", "text", "other"]);
const REASONS = new Set([
  "allowed", "guard-error", "guard-exit", "guard-denied", "guard-unreadable",
  "command-unreadable", "exec-env", "shell-command-missing", "session-input", "non-shell-merge",
]);

// Only fixed classifications cross the log boundary. Qualification commands and their output
// belong in separate receipts, never in this operational log.
export async function record(toolName, decision) {
  const block = decision.block === true;
  const { route, reasonCode } = decision;
  if (!block && route !== "guard") return;
  const line = {
    at: new Date().toISOString(),
    block,
    tool: SHELL_TOOLS.has(toolName) ? "shell" : SESSION_TOOLS.has(toolName) ? "session" : TEXT_TOOLS.has(toolName) ? "text" : "unknown",
    route: ROUTES.has(route) ? route : "unknown",
    reason: REASONS.has(reasonCode) ? reasonCode : "unknown",
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
        await record(event.toolName, decision);
        return decision.block ? { block: true, blockReason: decision.reason } : undefined;
      },
      { priority: 1000, timeoutMs: 15000 },
    );
  },
};
