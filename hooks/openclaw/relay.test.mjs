// Tests for the OpenClaw relay: node --test hooks/openclaw/relay.test.mjs
import assert from "node:assert/strict";
import { chmodSync, mkdtempSync, realpathSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

process.env.AWA_GUARD_GIT_LOG = join(mkdtempSync(join(tmpdir(), "awa-guard-log-")), "log.jsonl");
const { commandOf, decide, redact, runGuard, sessionInput, verdict, PLUGIN_ID } = await import("./relay.mjs");
const { checkFiles, checkInspection, install, isUnset, patchFor, readList, SOURCES } = await import("./install.mjs");
const plugin = (await import("./awa-guard-git.mjs")).default;

const GUARD = join(dirname(fileURLToPath(import.meta.url)), "..", "claude-code", "guard_git.py");
const NO_REPO = mkdtempSync(join(tmpdir(), "awa-guard-norepo-"));
const real = (command, cwd) => runGuard(command, cwd, { guard: GUARD, noRepoDir: NO_REPO });
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
  assert.deepEqual(await decide("exec", { command: "git push", workdir: "." }, pass), { block: false });
  assert.deepEqual(seen, [["git status", "/w"], ["ls", "/c"], ["pwd", undefined], ["git push", undefined]]);
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
  const named = { repository_full_name: "brandonperfetti/agent-working-agreements", pr_number: 123 };
  assert.equal((await decide("mcp__github__merge_pull_request", named, never)).block, true);
  assert.equal((await decide("process", { action: "write", data: "gh pr merge 4 --admin\n" }, never)).block, true);
  assert.equal((await decide("mcp_call", { query: "mergePullRequest", url: "https://api.github.com/graphql" }, never)).block, true);
  assert.deepEqual(await decide("apply_patch", { input: "+ gh pr merge <N> --merge" }, never), { block: false });
  assert.deepEqual(await decide("message", { text: "merged the GitHub PR" }, never), { block: false });
  assert.deepEqual(await decide("sessions_spawn", { agentId: "coder", task: "review, then merge the GitHub PR" }, never), { block: false });
  assert.equal((await decide("sessions_spawn", { runtime: "acp", task: "merge the GitHub PR" }, never)).block, true);
  assert.deepEqual(await decide("web_search", { query: "git merge conflicts" }, never), { block: false });
});

test("decide blocks shell-session input that names git or gh, and passes other input", async () => {
  const never = async () => assert.fail("the guard is not run");
  for (const params of [
    { action: "write", sessionId: "s", data: "git push --force origin feature\n" },
    { action: "send-keys", sessionId: "s", literal: "gh pr view 1", keys: ["Enter"] },
    { action: "send-keys", sessionId: "s", hex: ["67", "69", "74", "20", "70"] },
    { action: "paste", sessionId: "s", text: "ls\ngit push\n" },
    { action: "send-keys", sessionId: "s", keys: ["git", "Space", "push", "Space", "--force", "Enter"] },
    { action: "send-keys", sessionId: "s", keys: ["g", "i", "t", "Space", "p"] },
    { action: "send-keys", sessionId: "s", hex: ["0x67", "0x68", "0x20"] },
    { action: "send-keys", sessionId: "s", literal: "g", hex: ["69"], keys: ["t", "Space"] },
    { action: "send-keys", sessionId: "s", keys: ["C-gh", "Space", "pr", "Space", "merge", "Enter"] },
    { action: "send-keys", sessionId: "s", keys: ["M-git", "Space", "push", "Enter"] },
    { action: "send-keys", sessionId: "s", keys: ["S-g", "S-i", "S-t", "Space"] },
    { action: "write", sessionId: "s", data: "GIT push --force\n" },
  ]) {
    assert.equal((await decide("process", params, never)).block, true, JSON.stringify(params));
    assert.equal((await decide("gateway_process", params, never)).block, true, `gateway_process ${JSON.stringify(params)}`);
  }
  for (const params of [
    { action: "poll", sessionId: "s", timeout: 1000 },
    { action: "write", sessionId: "s", data: "y\n" },
    { action: "send-keys", sessionId: "s", keys: ["C-c"] },
    { action: "send-keys", sessionId: "s", keys: ["Up", "Up", "Enter"] },
    { action: "send-keys", sessionId: "s", keys: ["C-c", "^g", "C-h", "M-x", "S-Tab", "kpenter"] },
    { action: "paste", sessionId: "s", text: "digit github-free text" },
  ]) {
    assert.deepEqual(await decide("process", params, never), { block: false }, JSON.stringify(params));
  }
  assert.equal(sessionInput({ literal: "a", hex: ["0x62", "zz"], keys: ["c", "Space", "Enter"] }), "\n\nabc \n");
});

test("decide refuses an exec env that changes git or gh, and passes other env", async () => {
  const seen = [];
  const pass = async (command) => { seen.push(command); return { code: 0, stdout: "" }; };
  for (const env of [{ GH_REPO: "a/b" }, { GIT_DIR: "/x" }, { PATH: "/tmp/bin" }, { GITHUB_TOKEN: "t" }, ["GH_REPO=a/b"], "GH_REPO=a/b"]) {
    const decision = await decide("exec", { command: "gh pr merge 1 --squash", env }, pass);
    assert.equal(decision.block, true, JSON.stringify(env));
  }
  assert.deepEqual(await decide("exec", { command: "npm test", env: { NODE_ENV: "test" } }, pass), { block: false });
  assert.deepEqual(seen, ["npm test"]);
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

test("with no directory the guard runs outside any repository, never in the Gateway's", async () => {
  // A stub guard that reports where it was run: the payload's cwd, its own, and git's ceiling.
  const stub = join(mkdtempSync(join(tmpdir(), "awa-guard-stub-")), "where.py");
  writeFileSync(stub, [
    "import json, os, sys",
    "p = json.load(sys.stdin)",
    "r = '|'.join([p.get('cwd', ''), os.getcwd(), os.environ.get('GIT_CEILING_DIRECTORIES', '')])",
    "print(json.dumps({'hookSpecificOutput': {'permissionDecision': 'deny', 'permissionDecisionReason': r}}))",
  ].join("\n"));
  const where = async (cwd) => verdict(await runGuard("git push", cwd, { guard: stub, noRepoDir: NO_REPO })).reason.replace(`${PLUGIN_ID}: `, "").split("|");
  const [payload, own, ceiling] = await where(undefined);
  assert.equal(payload, NO_REPO);
  assert.equal(realpathSync(own), realpathSync(NO_REPO));
  assert.equal(ceiling, dirname(NO_REPO));
  const [given, , none] = await where("/some/checkout");
  assert.equal(given, "/some/checkout");
  assert.equal(none, process.env.GIT_CEILING_DIRECTORIES || "");
  const push = verdict(await real("git push"));
  assert.equal(push.block, true);
  assert.match(push.reason, /could not be resolved/);
  const missing = verdict(await runGuard("git status", undefined, { guard: GUARD, noRepoDir: join(NO_REPO, "absent") }));
  assert.equal(missing.block, true);
});

test("a missing guard, a failing interpreter and a slow guard all block", async () => {
  const dir = mkdtempSync(join(tmpdir(), "awa-guard-"));
  // Each case runs in a directory that exists, so it blocks for its own reason, not a missing cwd.
  const absent = verdict(await runGuard("git status", undefined, { guard: join(dir, "absent.py"), noRepoDir: NO_REPO }));
  assert.equal(absent.block, true);
  assert.match(absent.reason, /the guard exited 2/);
  const noPython = verdict(await runGuard("git status", undefined, { python: join(dir, "no-python"), noRepoDir: NO_REPO }));
  assert.equal(noPython.block, true);
  assert.match(noPython.reason, /could not run/);
  const slow = join(dir, "slow");
  writeFileSync(slow, "#!/bin/sh\nsleep 5\n");
  chmodSync(slow, 0o755);
  const started = Date.now();
  const decision = verdict(await runGuard("git status", undefined, { python: slow, timeoutMs: 200, noRepoDir: NO_REPO }));
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

test("patchFor keeps the live allow list and load paths, and adds the plugin once", () => {
  const patch = patchFor(["telegram", "codex"], ["/p/other.mjs"], "/x/awa-guard");
  assert.deepEqual(patch.plugins.allow, ["telegram", "codex", PLUGIN_ID]);
  assert.deepEqual(patch.plugins.load.paths, ["/p/other.mjs", "/x/awa-guard/awa-guard-git.mjs"]);
  assert.deepEqual(patch.plugins.entries, { [PLUGIN_ID]: { enabled: true } });
  const open = patchFor([], [], "/x/awa-guard");
  assert.equal(Object.hasOwn(open.plugins, "allow"), false, "an unrestricted allow list stays unset");
  assert.deepEqual(open.plugins.load.paths, ["/x/awa-guard/awa-guard-git.mjs"]);
  const again = patchFor(["codex", PLUGIN_ID], ["/x/awa-guard/awa-guard-git.mjs"], "/x/awa-guard");
  assert.deepEqual(again.plugins.allow, ["codex", PLUGIN_ID]);
  assert.deepEqual(again.plugins.load.paths, ["/x/awa-guard/awa-guard-git.mjs"]);
});

test("readList reads a live list through OpenClaw, and refuses anything else", () => {
  assert.deepEqual(readList("plugins.allow", () => ["a", "b"]), ["a", "b"]);
  assert.deepEqual(readList("plugins.load.paths", () => undefined), []);
  assert.deepEqual(readList("plugins.load.paths", () => null), []);
  assert.throws(() => readList("plugins.allow", () => ({ a: 1 })), /not a list/);
  assert.throws(() => readList("plugins.allow", () => { throw new Error("openclaw config get failed"); }), /failed/);
  const unset = JSON.stringify({ ok: false, error: { type: "cli_error", message: "Config path is valid but unset: plugins.allow. The runtime default applies" } });
  assert.equal(isUnset(unset), true);
  assert.equal(isUnset(JSON.stringify({ ok: false, error: { message: "Unknown config path: plugins.x" } })), false);
  assert.equal(isUnset("not json"), false);
});

test("the log keeps a credential's name, never its value", () => {
  const logged = redact({ command: "GH_TOKEN=s3cret gh pr view 1 && FOO='a b' ls", env: { GH_TOKEN: "s3cret", X: "y" } });
  assert.doesNotMatch(logged, /s3cret|a b|"y"/);
  assert.match(logged, /GH_TOKEN=…/);
  assert.match(logged, /"env":\{"GH_TOKEN":"…","X":"…"\}/);
  assert.equal(redact(undefined), "{}");
});
