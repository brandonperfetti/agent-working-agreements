// The decision behind the awa-guard-git OpenClaw plugin: every shell command an OpenClaw agent
// runs goes to hooks/claude-code/guard_git.py, unchanged, and anything but a clean pass blocks.
// The guard owns the rules (force-pushes, release-branch pushes, RULE ZERO, PR merges into a
// protected base save the delegated route's one form); this file only carries a command to it
// and reads its verdict, failing closed. It imports nothing from OpenClaw, so it is tested alone.
import { spawn } from "node:child_process";
import { homedir } from "node:os";
import { basename, dirname, isAbsolute, join } from "node:path";

export const PLUGIN_ID = "awa-guard-git";
export const INSTALL_DIR = join(homedir(), ".openclaw", "hooks", "awa-guard");
export const GUARD = join(INSTALL_DIR, "guard_git.py");
export const PYTHON = "/usr/bin/python3";
export const GUARD_TIMEOUT_MS = 10000;

// Shell tools by name, OpenClaw's and Codex-native ones alike: one of these with no command the
// relay can read is blocked, never passed.
export const SHELL_TOOLS = new Set([
  "exec", "bash", "shell", "local_shell", "exec_command", "shell_command", "unified_exec",
  "gateway_exec", "container.exec",
]);
// Tools whose parameters are text: a file, a patch, a message or a search. A merge named in them is
// prose, not a call. Every other tool that names GitHub and a merge (an MCP tool such as Kody's
// execute, a process write) is blocked: no API call is an equivalent route.
export const TEXT_TOOLS = new Set([
  "read", "write", "edit", "apply_patch", "message", "sessions_send", "sessions_spawn", "memory_write",
  "memory_search", "memory_get", "web_search", "web_fetch", "session_status", "tool_search",
]);
// Tools that send input to a running shell session: OpenClaw's, and the Codex harness's twin.
export const SESSION_TOOLS = new Set(["process", "gateway_process"]);
const SHELL_BINARIES = new Set(["bash", "sh", "zsh"]);
const MERGE = /merge/i;
const GITHUB = /(^|[^A-Za-z0-9_-])gh([^A-Za-z0-9_-]|$)|github|pulls?\b|pull_?request/i;
const SHELL_WORD = /(^|[^A-Za-z0-9_-])(git|gh)([^A-Za-z0-9_-]|$)/;

export function shellQuote(word) {
  return /^[A-Za-z0-9_./@=:+,%-]+$/.test(word) ? word : "'" + word.replaceAll("'", "'\\''") + "'";
}

/** The command a tool call would run: a string, null when a command field cannot be read, or
 * undefined when the call carries no command field at all. */
export function commandOf(params) {
  for (const key of ["command", "cmd"]) {
    if (!Object.hasOwn(params, key)) continue;
    const value = params[key];
    if (typeof value === "string") return value;
    if (Array.isArray(value) && value.length > 0 && value.every((w) => typeof w === "string")) {
      // `bash -lc '<script>'` runs the script; anything else is an argv, quoted back into words.
      if (value.length === 3 && SHELL_BINARIES.has(basename(value[0])) && /^-[A-Za-z]*c[A-Za-z]*$/.test(value[1])) {
        return value[2];
      }
      return value.map(shellQuote).join(" ");
    }
    return null;
  }
  return undefined;
}

/** The text a `process` call sends to a running session's stdin: write's `data`, send-keys'
 * `literal` and `hex`, paste's `text`. Named keys carry no command text. */
export function sessionInput(params) {
  const str = (v) => (typeof v === "string" ? v : "");
  // send-keys sends literal, then hex bytes, then keys, with nothing between them (OpenClaw's
  // encodeKeySequence): a hex byte may carry a `0x` prefix, and a key token that is not a named
  // key is sent as its own text.
  const list = (v) => (Array.isArray(v) ? v : typeof v === "string" ? [v] : []).filter((x) => typeof x === "string");
  const hex = list(params.hex).map((h) => h.trim().toLowerCase().replace(/^0x/, "")).filter((h) => /^[0-9a-f]{1,2}$/.test(h));
  const bytes = Buffer.from(hex.map((h) => Number.parseInt(h, 16))).toString("latin1");
  const keys = list(params.keys).map(keyText).join("");
  return [str(params.data), str(params.text), str(params.literal) + bytes + keys].join("\n");
}

// A key token as text: Space is a space, any other named or modified key a line break (enough to
// end a word), anything else its own characters.
function keyText(raw) {
  const token = raw.trim();
  if (/^space$/i.test(token)) return " ";
  if (token.length > 1 && (/^(\^|[CMS]-)/i.test(token) || NAMED_KEY.test(token))) return "\n";
  return token;
}
const NAMED_KEY = /^(enter|return|tab|escape|esc|backspace|bspace|delete|del|insert|ins|up|down|left|right|home|end|pageup|pagedown|pgup|pgdn|f\d{1,2})$/i;

// exec's own `env` reaches the command but not the guard. A variable that changes what git or gh
// does, or which binary runs, is refused there; others pass, as they do as a command's prefix.
const GIT_ENV = /^(GIT_|GH_|GITHUB_)|^(PATH|HOME|XDG_CONFIG_HOME|XDG_CONFIG_DIRS|ZDOTDIR|BASH_ENV|ENV)$/;
function envProblem(env) {
  if (env === undefined || env === null) return null;
  if (typeof env !== "object" || Array.isArray(env)) return "an exec env the relay cannot read";
  const named = Object.keys(env).filter((k) => GIT_ENV.test(k));
  return named.length ? `exec's env sets ${named.join(", ")}, which the guard cannot see; set it in the command itself` : null;
}

function block(reason) {
  return { block: true, reason: `${PLUGIN_ID}: ${reason}` };
}

/** Read guard_git.py's answer: a pass is exit 0 with nothing on stdout, a denial is its deny JSON;
 * anything else blocks. */
export function verdict(result) {
  if (result.error) return block(`the guard could not run (${result.error}); hand it back rather than routing around this`);
  if (result.code !== 0) return block(`the guard exited ${result.code}; hand it back rather than routing around this`);
  const out = (result.stdout || "").trim();
  if (out === "") return { block: false };
  try {
    const decision = JSON.parse(out).hookSpecificOutput;
    if (decision && decision.permissionDecision === "deny" && typeof decision.permissionDecisionReason === "string") {
      return block(decision.permissionDecisionReason.replace("~/.claude/hooks/guard_git.py", GUARD));
    }
  } catch {
    // fall through: unreadable output blocks
  }
  return block("the guard's verdict could not be read; hand it back rather than routing around this");
}

/** Decide one tool call. `runGuard(command, cwd)` resolves to { code, stdout, error }. A Code Mode
 * cell (`kind` code_mode_exec, or JavaScript input) is not a shell command: each tool it calls
 * re-enters OpenClaw and this hook as its own call, and is decided there. */
export async function decide(toolName, params, runGuard, { kind, inputKind } = {}) {
  if (kind === "code_mode_exec" || inputKind === "javascript") return { block: false };
  const args = params && typeof params === "object" && !Array.isArray(params) ? params : {};
  const command = commandOf(args);
  if (command === null) return block("a shell command the relay cannot read");
  if (typeof command === "string") {
    const env = envProblem(args.env);
    if (env) return block(env);
    // Only an absolute directory names the checkout the command runs in: the hook is not told the
    // session's default directory, and a relative one would resolve against the Gateway's. Without
    // one the guard is run outside any repository (runGuard), so a check that needs one blocks.
    const cwd = [args.workdir, args.cwd].find((v) => typeof v === "string" && isAbsolute(v));
    return verdict(await runGuard(command, cwd));
  }
  if (SHELL_TOOLS.has(toolName)) return block("a shell tool call with no command the relay can read");
  if (SESSION_TOOLS.has(toolName) && SHELL_WORD.test(sessionInput(args))) {
    return block("input to a running shell session that names git or gh; run git and gh through exec, where the guard reads the whole command");
  }
  if (!TEXT_TOOLS.has(toolName)) {
    // The tool's own name counts: a merge tool's parameters need not say "merge".
    const text = `${toolName} ${JSON.stringify(args)}`;
    if (MERGE.test(text) && GITHUB.test(text)) {
      return block(`a GitHub merge through ${toolName}, not the shell; no API call is an equivalent route`);
    }
  }
  return { block: false };
}

/** Run guard_git.py on one command, as Claude Code's PreToolUse hook would. With no directory it
 * runs in `noRepoDir`, a directory outside any repository (git may not search above it), never in
 * the Gateway's own directory; a check that needs the checkout then blocks. */
export function runGuard(command, cwd, { guard = GUARD, python = PYTHON, timeoutMs = GUARD_TIMEOUT_MS, noRepoDir = INSTALL_DIR } = {}) {
  return new Promise((resolve) => {
    const dir = cwd || noRepoDir;
    const env = cwd ? process.env : { ...process.env, GIT_CEILING_DIRECTORIES: dirname(noRepoDir) };
    let child;
    try {
      child = spawn(python, ["-I", guard], { cwd: cwd ? undefined : noRepoDir, env, stdio: ["pipe", "pipe", "pipe"] });
    } catch (error) {
      resolve({ error: String(error && error.message ? error.message : error) });
      return;
    }
    let stdout = "";
    let settled = false;
    const finish = (result) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        resolve(result);
      }
    };
    const timer = setTimeout(() => {
      child.kill("SIGKILL");
      finish({ error: `timed out after ${timeoutMs} ms` });
    }, timeoutMs);
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.resume();
    child.on("error", (error) => finish({ error: error.message }));
    child.on("close", (code, signal) => finish(signal ? { error: `killed by ${signal}` } : { code, stdout }));
    child.stdin.on("error", () => {});
    child.stdin.end(JSON.stringify({ tool_input: { command }, cwd: dir }));
  });
}
