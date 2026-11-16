// Tests for the OpenClaw relay: node --test hooks/openclaw/relay.test.mjs
import assert from "node:assert/strict";
import { chmodSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

process.env.AWA_GUARD_GIT_LOG = join(mkdtempSync(join(tmpdir(), "awa-guard-log-")), "log.jsonl");
const { commandOf, decide, runGuard, verdict, PLUGIN_ID } = await import("./relay.mjs");
const { checkFiles, checkInspection, install, patchFor, SOURCES } = await import("./install.mjs");
const plugin = (await import("./awa-guard-git.mjs")).default;

const GUARD = join(dirname(fileURLToPath(import.meta.url)), "..", "claude-code", "guard_git.py");
const real = (command, cwd) => runGuard(command, cwd, { guard: GUARD });
const DENY = (reason) => ({
  code: 0,
  stdout: JSON.stringify({ hookSpecificOutput: { hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: reason } }),
});

test("commandOf reads a string, an argv and a shell's -c script", () => {
  assert.equal(commandOf({ command: "git status" }), "git status");
  assert.equal(commandOf({ cmd: "ls" }), "ls");
  assert.equal(commandOf({ command: ["gh", "pr", "view", "1"] }), "gh pr view 1");
  assert.equal(commandOf({ command: ["echo", "a b", "it's"] }), "echo 'a b' 'it'\\''s'");
  assert.equal(commandOf({ command: ["/bin/bash", "-lc", "gh pr merge 1 2>&1"] }), "gh pr merge 1 2>&1");
  assert.equal(commandOf({ command: ["zsh", "-c", "x"] }), "x");
  assert.equal(commandOf({ path: "a" }), undefined);
});

test("commandOf returns null for a command field it cannot read", () => {
  assert.equal(commandOf({ command: 7 }), null);
  assert.equal(commandOf({ command: [] }), null);
  assert.equal(commandOf({ command: ["gh", 1] }), null);
  assert.equal(commandOf({ cmd: { sh: "x" } }), null);
});

test("verdict passes only exit 0 with empty stdout", () => {
  assert.deepEqual(verdict({ code: 0, stdout: "" }), { block: false });
  assert.deepEqual(verdict({ code: 0, stdout: " \n" }), { block: false });
  for (const result of [
    { code: 1, stdout: "" },
    { code: 2, stdout: "" },
    { code: null, stdout: "" },
    { error: "spawn ENOENT" },
    { error: "timed out after 10 ms" },
    { code: 0, stdout: "not json" },
    { code: 0, stdout: "{}" },
    { code: 0, stdout: JSON.stringify({ hookSpecificOutput: { permissionDecision: "allow" } }) },
    { code: 0, stdout: JSON.stringify({ hookSpecificOutput: { permissionDecision: "deny" } }) },
  ]) {
    const decision = verdict(result);
    assert.equal(decision.block, true, JSON.stringify(result));
    assert.ok(decision.reason.startsWith(`${PLUGIN_ID}: `));
  }
});

test("verdict carries the guard's reason", () => {
  const decision = verdict(DENY("Blocked by ~/.claude/hooks/guard_git.py: this is a PR merge. x"));
  assert.equal(decision.block, true);
  assert.match(decision.reason, /^awa-guard-git: Blocked by .*awa-guard\/guard_git\.py: this is a PR merge\. x$/);
});

test("decide sends a shell command and its directory to the guard", async () => {
  const seen = [];
  const pass = async (command, cwd) => { seen.push([command, cwd]); return { code: 0, stdout: "" }; };
  assert.deepEqual(await decide("exec", { command: "git status", workdir: "/w" }, pass), { block: false });
  assert.deepEqual(await decide("local_shell", { command: ["bash", "-lc", "ls"], cwd: "/c" }, pass), { block: false });
  assert.deepEqual(await decide("unknown_tool", { cmd: "pwd" }, pass), { block: false });
  assert.deepEqual(seen, [["git status", "/w"], ["ls", "/c"], ["pwd", undefined]]);
  const denied = await decide("exec", { command: "gh pr merge 1" }, async () => DENY("no"));
  assert.equal(denied.block, true);
});

test("decide blocks a shell tool or command it cannot read", async () => {
  const never = async () => assert.fail("the guard is not run");
  for (const [tool, params] of [["exec", {}], ["bash", { script: "x" }], ["exec", { command: 3 }], ["write", { command: ["a", 2] }], ["exec", null]]) {
    assert.equal((await decide(tool, params, never)).block, true, `${tool} ${JSON.stringify(params)}`);
  }
});

test("decide blocks a GitHub merge through a non-shell tool, and passes text tools", async () => {
  const never = async () => assert.fail("the guard is not run");
  const kody = { code: "export default async () => kody.github_pr_merge({ repo: 'a/b', number: 1 })" };
  assert.equal((await decide("kody-local-celld__execute", kody, never)).block, true);
  assert.equal((await decide("process", { action: "write", data: "gh pr merge 4 --admin\n" }, never)).block, true);
  assert.equal((await decide("mcp_call", { query: "mergePullRequest", url: "https://api.github.com/graphql" }, never)).block, true);
  assert.deepEqual(await decide("apply_patch", { input: "+ gh pr merge <N> --merge" }, never), { block: false });
  assert.deepEqual(await decide("message", { text: "merged the GitHub PR" }, never), { block: false });
  assert.deepEqual(await decide("web_search", { query: "git merge conflicts" }, never), { block: false });
});

test("decide leaves a Code Mode cell to its nested calls", async () => {
  const never = async () => assert.fail("the guard is not run");
  const cell = { command: 'const r = await exec({command: "gh pr merge 1 --admin"});' };
  assert.deepEqual(await decide("exec", cell, never, { kind: "code_mode_exec" }), { block: false });
  assert.deepEqual(await decide("exec", cell, never, { inputKind: "javascript" }), { block: false });
  const nested = await decide("exec", { command: "gh pr merge 1 --admin" }, async () => DENY("no"), {});
  assert.equal(nested.block, true);
});

test("the real guard: a read passes, a force-push and the canary block", async () => {
  assert.deepEqual(verdict(await real("git status")), { block: false });
  const force = verdict(await real("git push --force origin feature"));
  assert.equal(force.block, true);
  assert.match(force.reason, /force/);
  const canary = verdict(await real("gh pr merge --help"));
  assert.equal(canary.block, true);
  assert.match(canary.reason, /^awa-guard-git: Blocked by .*this is a PR merge\./);
  const chained = verdict(await real("cd /tmp && gh pr merge 1 --merge"));
  assert.equal(chained.block, true);
});

test("a missing guard, a failing interpreter and a slow guard all block", async () => {
  const dir = mkdtempSync(join(tmpdir(), "awa-guard-"));
  assert.equal(verdict(await runGuard("git status", undefined, { guard: join(dir, "absent.py") })).block, true);
  assert.equal(verdict(await runGuard("git status", undefined, { python: join(dir, "no-python") })).block, true);
  const slow = join(dir, "slow");
  writeFileSync(slow, "#!/bin/sh\nsleep 5\n");
  chmodSync(slow, 0o755);
  const started = Date.now();
  const decision = verdict(await runGuard("git status", undefined, { python: slow, timeoutMs: 200 }));
  assert.equal(decision.block, true);
  assert.match(decision.reason, /timed out/);
  assert.ok(Date.now() - started < 3000);
});

test("the plugin registers one before_tool_call handler that maps a block", async () => {
  const hooks = [];
  plugin.register({ on: (name, handler, options) => hooks.push({ name, handler, options }) });
  assert.equal(plugin.id, PLUGIN_ID);
  assert.equal(hooks.length, 1);
  assert.equal(hooks[0].name, "before_tool_call");
  assert.ok(hooks[0].options.timeoutMs > 10000, "the handler outlives the guard's own timeout");
  const result = await hooks[0].handler({ toolName: "exec", params: {} }, { agentId: "coder" });
  assert.equal(result.block, true);
  assert.match(result.blockReason, /^awa-guard-git: /);
  assert.equal(await hooks[0].handler({ toolName: "read", params: { path: "a" } }, {}), undefined);
});

test("install copies the three files and check sees a changed byte", () => {
  const target = join(mkdtempSync(join(tmpdir(), "awa-guard-install-")), "awa-guard");
  const digests = install(target);
  assert.deepEqual(Object.keys(digests).sort(), Object.keys(SOURCES).sort());
  assert.deepEqual(checkFiles(target), []);
  writeFileSync(join(target, "guard_git.py"), "tampered\n");
  assert.equal(checkFiles(target).length, 1);
  assert.equal(checkFiles(join(target, "nowhere")).length, 3);
});

test("checkInspection requires the plugin enabled, loaded from the target, with its hook", () => {
  const target = "/x/awa-guard";
  const plugin = { id: PLUGIN_ID, enabled: true, status: "loaded", source: "/x/awa-guard/awa-guard-git.mjs" };
  const good = { plugin, typedHooks: [{ name: "before_tool_call", priority: 1000 }] };
  assert.deepEqual(checkInspection(good, target), []);
  assert.equal(checkInspection({}, target).length, 1);
  assert.equal(checkInspection({ ...good, plugin: { ...plugin, id: "other" } }, target).length, 1);
  assert.equal(checkInspection({ ...good, plugin: { ...plugin, enabled: false, status: "disabled" } }, target).length, 2);
  assert.equal(checkInspection({ ...good, plugin: { ...plugin, source: "/y/awa-guard-git.mjs" } }, target).length, 1);
  assert.equal(checkInspection({ ...good, typedHooks: [] }, target).length, 1);
});

test("patchFor keeps the live allow list and adds the plugin once", () => {
  const patch = patchFor(["telegram", "codex"], "/x/awa-guard");
  assert.deepEqual(patch.plugins.allow, ["telegram", "codex", PLUGIN_ID]);
  assert.deepEqual(patch.plugins.load.paths, ["/x/awa-guard/awa-guard-git.mjs"]);
  assert.deepEqual(patch.plugins.entries, { [PLUGIN_ID]: { enabled: true } });
  assert.deepEqual(patchFor(["codex", PLUGIN_ID]).plugins.allow, ["codex", PLUGIN_ID]);
});
