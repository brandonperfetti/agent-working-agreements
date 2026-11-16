#!/usr/bin/env node
// Install the awa-guard-git relay for OpenClaw, check an installation, or print the config patch.
//
//   node hooks/openclaw/install.mjs                 copy the relay and guard_git.py into place
//   node hooks/openclaw/install.mjs --check         installed bytes equal this checkout, and
//                                                   OpenClaw loads the plugin with its hook
//   node hooks/openclaw/install.mjs --print-patch   the `openclaw config patch` JSON that loads it
//
// --target DIR replaces ~/.openclaw/hooks/awa-guard (tests); --no-live skips the OpenClaw read.
// The installer never edits OpenClaw's config: the patch is applied by the control-plane owner.
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { chmodSync, copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { INSTALL_DIR, PLUGIN_ID } from "./relay.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
export const SOURCES = {
  "awa-guard-git.mjs": join(HERE, "awa-guard-git.mjs"),
  "relay.mjs": join(HERE, "relay.mjs"),
  "guard_git.py": join(HERE, "..", "claude-code", "guard_git.py"),
};
export const ENTRY = "awa-guard-git.mjs";

export function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

export function install(target = INSTALL_DIR, sources = SOURCES) {
  mkdirSync(target, { recursive: true, mode: 0o700 });
  for (const [name, source] of Object.entries(sources)) {
    copyFileSync(source, join(target, name));
    chmodSync(join(target, name), 0o644);
  }
  return Object.fromEntries(Object.keys(sources).map((name) => [name, sha256(join(target, name))]));
}

/** Every way the installed files differ from the checkout's; empty when they match. */
export function checkFiles(target = INSTALL_DIR, sources = SOURCES) {
  const problems = [];
  for (const [name, source] of Object.entries(sources)) {
    const installed = join(target, name);
    if (!existsSync(installed)) problems.push(`${installed} is missing`);
    else if (sha256(installed) !== sha256(source)) problems.push(`${installed} differs from ${source}`);
  }
  return problems;
}

/** What `openclaw plugins inspect <id> --runtime --json` says is wrong with the plugin's
 * registration; empty when it is enabled, loaded from the target and holds its hook. */
export function checkInspection(inspection, target = INSTALL_DIR) {
  const entry = inspection && inspection.plugin;
  if (!entry || entry.id !== PLUGIN_ID) return [`OpenClaw reports no plugin ${PLUGIN_ID}`];
  const problems = [];
  if (entry.enabled !== true) problems.push(`${PLUGIN_ID} is not enabled`);
  if (entry.status !== "loaded") problems.push(`${PLUGIN_ID} status is ${entry.status}`);
  if (resolve(entry.source || "") !== resolve(join(target, ENTRY))) problems.push(`${PLUGIN_ID} loads from ${entry.source}, not ${join(target, ENTRY)}`);
  if (!(inspection.typedHooks || []).some((hook) => hook.name === "before_tool_call")) problems.push(`${PLUGIN_ID} registers no before_tool_call hook`);
  return problems;
}

/** The merge patch that loads the relay. `allow` and `paths` are the live plugins.allow and
 * plugins.load.paths lists, each kept whole with the relay added once: an array in a patch
 * replaces the live one. */
export function patchFor(allow, paths, target = INSTALL_DIR) {
  const entry = join(target, ENTRY);
  return {
    plugins: {
      allow: allow.includes(PLUGIN_ID) ? allow : [...allow, PLUGIN_ID],
      load: { paths: paths.some((p) => resolve(p) === entry) ? paths : [...paths, entry] },
      entries: { [PLUGIN_ID]: { enabled: true } },
    },
  };
}

/** One live config list, read through OpenClaw itself (its config file is JSON5, with includes):
 * an unset list is empty, and anything but a list or nothing is an error. */
export function readList(path, get = configGet) {
  const value = get(path);
  if (value === null || value === undefined) return [];
  if (Array.isArray(value) && value.every((v) => typeof v === "string")) return value;
  throw new Error(`OpenClaw's ${path} is not a list of strings`);
}

function openclaw(args) {
  return execFileSync(join(homedir(), ".openclaw", "bin", "openclaw"), args, { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"], timeout: 60000 });
}

function configGet(path) {
  let out;
  try {
    out = openclaw(["config", "get", path, "--json"]);
  } catch (error) {
    throw new Error(`openclaw config get ${path} failed: ${(error.stdout || error.message).trim()}`);
  }
  return out.trim() === "" ? undefined : JSON.parse(out);
}

function main(argv) {
  const flag = (name) => argv.includes(name);
  const at = argv.indexOf("--target");
  const target = at >= 0 ? resolve(argv[at + 1]) : INSTALL_DIR;
  if (flag("--print-patch")) {
    try {
      console.log(JSON.stringify(patchFor(readList("plugins.allow"), readList("plugins.load.paths"), target), null, 2));
    } catch (error) {
      console.error(`no patch printed: ${error.message}`);
      return 1;
    }
    return 0;
  }
  if (flag("--check")) {
    const problems = checkFiles(target);
    if (!flag("--no-live")) {
      try {
        const out = openclaw(["plugins", "inspect", PLUGIN_ID, "--runtime", "--json"]);
        problems.push(...checkInspection(JSON.parse(out), target));
      } catch (error) {
        problems.push(`OpenClaw's plugin inspection could not be read: ${error.message}`);
      }
    }
    for (const problem of problems) console.error(problem);
    if (problems.length === 0) console.log(`${PLUGIN_ID}: installed at ${target} and matches this checkout`);
    return problems.length === 0 ? 0 : 1;
  }
  for (const [name, digest] of Object.entries(install(target))) console.log(`${digest}  ${join(target, name)}`);
  return 0;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = main(process.argv.slice(2));
}
