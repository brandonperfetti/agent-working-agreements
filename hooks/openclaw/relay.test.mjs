// Tests for the OpenClaw relay: node --test hooks/openclaw/relay.test.mjs
import assert from "node:assert/strict";
import { chmodSync, existsSync, mkdtempSync, readFileSync, realpathSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const LOG_FILE = join(mkdtempSync(join(tmpdir(), "awa-guard-log-")), "log.jsonl");
process.env.AWA_GUARD_GIT_LOG = LOG_FILE;
writeFileSync(LOG_FILE, "", { mode: 0o600 });
const { commandOf, decide, runGuard, sessionInput, verdict, PLUGIN_ID } = await import("./relay.mjs");
const { checkFiles, checkInspection, install, isUnset, patchFor, readList, SOURCES } = await import("./install.mjs");
const { default: plugin, record } = await import("./awa-guard-git.mjs");
const PASS = (route) => ({ block: false, reasonCode: "allowed", route });

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
  assert.deepEqual(verdict({ code: 0, stdout: "" }), PASS("guard"));
  assert.deepEqual(verdict({ code: 0, stdout: " \n" }), PASS("guard"));
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
  assert.deepEqual(await decide("exec", { command: "git status", workdir: "/w" }, pass), PASS("guard"));
  assert.deepEqual(await decide("local_shell", { command: ["bash", "-lc", "ls"], cwd: "/c" }, pass), PASS("guard"));
  assert.deepEqual(await decide("unknown_tool", { cmd: "pwd" }, pass), PASS("guard"));
  assert.deepEqual(await decide("exec", { command: "git push", workdir: "." }, pass), PASS("guard"));
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
  assert.deepEqual(await decide("apply_patch", { input: "+ gh pr merge <N> --merge" }, never), PASS("text"));
  assert.deepEqual(await decide("message", { text: "merged the GitHub PR" }, never), PASS("text"));
  assert.deepEqual(await decide("sessions_spawn", { agentId: "coder", task: "review, then merge the GitHub PR" }, never), PASS("text"));
  assert.equal((await decide("sessions_spawn", { runtime: "acp", task: "merge the GitHub PR" }, never)).block, true);
  assert.deepEqual(await decide("web_search", { query: "git merge conflicts" }, never), PASS("text"));
  const plan = [{ step: "merge the GitHub PR after review", status: "pending" }];
  assert.deepEqual(await decide("update_plan", { plan }, never), PASS("text"));
  assert.deepEqual(await decide("progress_card", { steps: plan }, never), PASS("text"));
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
    assert.deepEqual(await decide("process", params, never), PASS("session"), JSON.stringify(params));
  }
  assert.equal(sessionInput({ literal: "a", hex: ["0x62", "zz"], keys: ["c", "Space", "Enter"] }), "\n\nabc \n");
});

test("session input is checked before an unrelated command can reach the guard", async () => {
  const never = async () => assert.fail("session stdin must not be replaced by the command field");
  for (const tool of ["process", "gateway_process"]) {
    for (const command of [{ command: "true" }, { cmd: "true" }, { command: ["true"] }]) {
      for (const input of [
        { action: "write", data: "git push --force origin feature\n" },
        { action: "paste", text: "gh pr merge 4 --admin\n" },
        { action: "send-keys", literal: "git status", keys: ["Enter"] },
        { action: "send-keys", hex: ["67", "68", "20"], keys: ["Enter"] },
      ]) {
        const decision = await decide(tool, { sessionId: "s", ...command, ...input }, never);
        assert.equal(decision.block, true);
        assert.equal(decision.reasonCode, "session-input");
      }
    }
    const unreadable = await decide(tool, { command: 7, data: "git status" }, never);
    assert.equal(unreadable.reasonCode, "command-unreadable", "unreadable command handling stays first");
    for (const options of [{ kind: "code_mode_exec" }, { inputKind: "javascript" }]) {
      assert.deepEqual(await decide(tool, { command: "true", data: "git status" }, never, options), PASS("code-mode"));
    }
    const seen = [];
    const pass = async (command, cwd) => { seen.push([command, cwd]); return { code: 0, stdout: "" }; };
    assert.deepEqual(await decide(tool, { action: "write", command: "true", data: "y\n", workdir: "/fixture" }, pass), PASS("guard"));
    assert.deepEqual(seen, [["true", "/fixture"]]);
    assert.deepEqual(await decide(tool, { action: "poll", sessionId: "s" }, never), PASS("session"));
    const refused = await decide(tool, { action: "write", command: "git push", data: "y\n" }, async () => DENY("original guard reason"));
    assert.equal(refused.reason, `${PLUGIN_ID}: original guard reason`);
  }
  const command = "gh pr merge 4 --repo a/b --merge --match-head-commit " + "a".repeat(40) + " --author-email brandon@brandonperfetti.com";
  let seen;
  assert.deepEqual(await decide("exec", { command, workdir: "/fixture", data: "git status" }, async (input, cwd) => { seen = [input, cwd]; return { code: 0, stdout: "" }; }), PASS("guard"));
  assert.deepEqual(seen, [command, "/fixture"], "ordinary exec handoff is unchanged");
});

test("decide refuses an exec env that changes git or gh, and passes other env", async () => {
  const seen = [];
  const pass = async (command) => { seen.push(command); return { code: 0, stdout: "" }; };
  for (const env of [{ GH_REPO: "a/b" }, { GIT_DIR: "/x" }, { PATH: "/tmp/bin" }, { GITHUB_TOKEN: "t" }, ["GH_REPO=a/b"], "GH_REPO=a/b"]) {
    const decision = await decide("exec", { command: "gh pr merge 1 --squash", env }, pass);
    assert.equal(decision.block, true, JSON.stringify(env));
  }
  assert.deepEqual(await decide("exec", { command: "npm test", env: { NODE_ENV: "test" } }, pass), PASS("guard"));
  assert.deepEqual(seen, ["npm test"]);
});

test("decide leaves a Code Mode cell to its nested calls", async () => {
  const never = async () => assert.fail("the guard is not run");
  const cell = { command: 'const r = await exec({command: "gh pr merge 1 --admin"});' };
  assert.deepEqual(await decide("exec", cell, never, { kind: "code_mode_exec" }), PASS("code-mode"));
  assert.deepEqual(await decide("exec", cell, never, { inputKind: "javascript" }), PASS("code-mode"));
  const nested = await decide("exec", { command: "gh pr merge 1 --admin" }, async () => DENY("no"), {});
  assert.equal(nested.block, true);
});

test("the real guard: a read passes, a force-push and the canary block", async () => {
  assert.deepEqual(verdict(await real("git status")), PASS("guard"));
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

// Read the actual appendFile output, with an offset so each case owns its observed rows.
const logOffset = () => readFileSync(LOG_FILE, "utf8").length;
const logRows = (offset) => readFileSync(LOG_FILE, "utf8").slice(offset).trim().split("\n").filter(Boolean).map(JSON.parse);
function assertLogSchema(rows) {
  for (const row of rows) {
    assert.deepEqual(Object.keys(row).sort(), ["at", "block", "reason", "route", "tool"]);
    assert.equal(new Date(row.at).toISOString(), row.at);
    assert.equal(typeof row.block, "boolean");
    assert.ok(["shell", "session", "text", "unknown"].includes(row.tool));
    assert.ok(["guard", "code-mode", "shell", "session", "text", "other", "unknown"].includes(row.route));
    assert.ok(["allowed", "guard-error", "guard-exit", "guard-denied", "guard-unreadable", "command-unreadable", "exec-env", "shell-command-missing", "session-input", "non-shell-merge", "unknown"].includes(row.reason));
  }
}

test("the persisted log excludes quoted assignment and secret-flag values", async () => {
  const marker = ["log", "probe", "value"].join("-");
  const offset = logOffset();
  const seen = [];
  for (const quote of ["'", '\"']) {
    for (const command of [
      `env ${quote}PASSWORD=first ${marker}${quote} task # merge`,
      `wget ${quote}--password${quote} ${quote}${marker}${quote} https://example.test/merge-report`,
    ]) {
      for (const blocked of [false, true]) {
        const decision = await decide("exec", { command, workdir: "/fixture" }, async (input, cwd) => {
          seen.push([input, cwd]);
          return blocked ? DENY(`guard reason containing ${marker}: ${input}`) : { code: 0, stdout: "" };
        });
        assert.equal(decision.block, blocked);
        if (blocked) assert.ok(decision.reason.includes(marker), "user-facing guard reason stays intact");
        await record("exec", decision);
        assert.deepEqual(seen.at(-1), [command, "/fixture"], "the guard receives the original command");
      }
    }
  }
  const rows = logRows(offset);
  assert.equal(rows.length, 8);
  assertLogSchema(rows);
  assert.equal(rows.filter((row) => row.block).length, 4);
  assert.ok(rows.every((row) => row.route === "guard" && row.tool === "shell"));
  const persisted = readFileSync(LOG_FILE, "utf8").slice(offset);
  assert.equal(persisted.includes(marker), false);
  assert.equal(persisted.includes("PASSWORD"), false);
  assert.equal(persisted.includes("example.test"), false);
});

test("the log discards arbitrary event, context, environment and identifier fields", async () => {
  const marker = ["arbitrary", "event", "value"].join("-");
  const hooks = [];
  plugin.register({ on: (_name, handler) => hooks.push(handler) });
  const offset = logOffset();
  const fields = {
    agentId: marker, sessionKey: marker, runId: marker, toolKind: marker, toolInputKind: marker,
    at: marker, route: marker, reasonCode: marker, reason: marker, error: marker,
    identifier: marker, metadata: { value: marker }, env: { [marker]: marker },
  };
  const result = await hooks[0]({ ...fields, toolName: `mcp_${marker}`, params: { ...fields, query: "github merge" } }, fields);
  assert.equal(result.block, true);
  assert.ok(result.blockReason.includes(marker), "the existing non-shell block message is preserved");
  assert.equal(await hooks[0]({ ...fields, toolName: "read", params: { ...fields, path: marker } }, fields), undefined);
  const rows = logRows(offset);
  assert.equal(rows.length, 1, "an allowed non-shell read is not recorded");
  assert.deepEqual(rows[0], { at: rows[0].at, block: true, tool: "unknown", route: "other", reason: "non-shell-merge" });
  assertLogSchema(rows);
  assert.equal(readFileSync(LOG_FILE, "utf8").slice(offset).includes(marker), false);
});

test("the logger allowlist rejects arbitrary classifications and guard errors", async () => {
  const marker = ["untrusted", "classification", "value"].join("-");
  const offset = logOffset();
  for (const value of [marker, { value: marker }, [marker], null, undefined, "toString", "__proto__"]) {
    await record(value, { block: true, route: value, reasonCode: value, reason: marker, params: marker, runId: marker });
  }
  const results = [{ error: marker }, { code: marker, stdout: "" }, { code: 0, stdout: marker }, DENY(marker)];
  for (const result of results) {
    const decision = verdict(result);
    assert.equal(decision.block, true);
    await record("exec", decision);
  }
  const rows = logRows(offset);
  assert.equal(rows.length, 11);
  assertLogSchema(rows);
  assert.ok(rows.slice(0, 7).every((row) => row.tool === "unknown" && row.route === "unknown" && row.reason === "unknown"));
  assert.deepEqual(rows.slice(7).map((row) => row.reason), ["guard-error", "guard-exit", "guard-unreadable", "guard-denied"]);
  assert.equal(readFileSync(LOG_FILE, "utf8").slice(offset).includes(marker), false);
  assert.equal(statSync(LOG_FILE).mode & 0o777, 0o600);
});

test("metadata logging preserves allow, block and delegated route decisions", async () => {
  const offset = logOffset();
  const route = "gh pr merge 4 --repo a/b --merge --match-head-commit " + "a".repeat(40) + " --author-email brandon@brandonperfetti.com";
  const inputs = [];
  const pass = async (command, cwd) => { inputs.push([command, cwd]); return { code: 0, stdout: "" }; };
  const never = async () => assert.fail("guard should not run");
  for (const [tool, params, runner, options, blocked, classification] of [
    ["exec", { command: "git status", workdir: "/fixture" }, pass, {}, false, "guard"],
    ["gateway_exec", { command: route, cwd: "/fixture" }, pass, {}, false, "guard"],
    ["exec", { command: "gh pr merge --help" }, async () => DENY("canary"), {}, true, "guard"],
    ["exec", {}, never, {}, true, "shell"],
    ["exec", { command: 7 }, never, {}, true, "shell"],
    ["exec", { command: "git status", env: { GH_REPO: "a/b" } }, never, {}, true, "shell"],
    ["process", { action: "write", data: "git status" }, never, {}, true, "session"],
    ["message", { text: "github merge" }, never, {}, false, "text"],
    ["exec", { command: "nested tool code" }, never, { kind: "code_mode_exec" }, false, "code-mode"],
    ["unrecognized", {}, never, {}, false, "other"],
  ]) {
    const decision = await decide(tool, params, runner, options);
    assert.equal(decision.block, blocked);
    assert.equal(decision.route, classification);
    await record(tool, decision);
  }
  assert.deepEqual(inputs, [["git status", "/fixture"], [route, "/fixture"]]);
  const rows = logRows(offset);
  assert.equal(rows.length, 7);
  assertLogSchema(rows);
  assert.deepEqual(rows.map((row) => row.reason), ["allowed", "allowed", "guard-denied", "shell-command-missing", "command-unreadable", "exec-env", "session-input"]);
  assert.equal(readFileSync(LOG_FILE, "utf8").slice(offset).includes("--match-head-commit"), false);
});

test("unavailable log parents leave enforcement intact without creating a fallback log", async () => {
  const dir = mkdtempSync(join(tmpdir(), "awa-guard-log-failure-"));
  const notDirectory = join(dir, "not-a-directory");
  writeFileSync(notDirectory, "fixture\n");
  const priorLog = readFileSync(LOG_FILE, "utf8");
  const priorEnv = process.env.AWA_GUARD_GIT_LOG;
  try {
    for (const [index, target] of [join(dir, "missing", "log.jsonl"), join(notDirectory, "log.jsonl")].entries()) {
      process.env.AWA_GUARD_GIT_LOG = target;
      const isolated = await import(new URL(`./awa-guard-git.mjs?log-failure-${index}`, import.meta.url));
      const hooks = [];
      isolated.default.register({ on: (_name, handler) => hooks.push(handler) });
      const result = await hooks[0]({ toolName: "exec", params: {} }, {});
      assert.equal(result.block, true);
      assert.match(result.blockReason, /^awa-guard-git: a shell tool call with no command/);
      assert.equal(await hooks[0]({ toolName: "read", params: { path: "a" } }, {}), undefined);
      await assert.doesNotReject(() => isolated.record("exec", PASS("guard")));
      assert.equal(existsSync(target), false);
    }
  } finally {
    process.env.AWA_GUARD_GIT_LOG = priorEnv;
  }
  assert.equal(existsSync(join(dir, "missing")), false, "logging creates no parent");
  assert.equal(statSync(notDirectory).isFile(), true);
  assert.equal(readFileSync(LOG_FILE, "utf8"), priorLog, "there is no fallback to the original log");
});
