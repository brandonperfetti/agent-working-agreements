# OpenClaw — history and evidence

Measurements, source readings with their hashes, the route census, superseded claims and the
migration dispositions that `clients/openclaw.md` carried until 2026-10-27. Nothing here is startup
reading; a rule cites a learning or an issue, and the receipts live here or under
`_agent/evidence/`. Text is verbatim as moved; headings say where it came from.

## From *Startup and mode*: acceptance narrative

**Configured native agent root.** On Brandon's native macOS OpenClaw installation, the configured
agent root is `~/dev/sansfaux`, currently resolving for the live account to
`/Users/brandonperfetti/dev/sansfaux`. Its authoritative protected instruction-source root working
tree is `$AGENT_ROOT/agent-working-agreements/`; its artifact store is `$AGENT_ROOT/_agent/`. That
working tree is protected from delivery mutations and kept current with released `master` by the
release refresh in
[Instruction-source isolation and freshness][iso] below.

After a workspace's reviewed `AGENTS.md` pointer is replaced, the first approved acceptance session
for that role selects `$AGENT_ROOT/_agent/` at startup on a provisional basis so it can execute the
ordinary create/readback canary. This startup selection is independent of the later acceptance
verdict and remains fixed for that session under A6. Declare the mapping operationally accepted for
the role only after the session reports the exact instruction path and hashes, names that selected
store, and passes the canary through its supported tool route. A partial pointer application affects
only fresh sessions started from the changed subset. Existing sessions remain bound to the concrete
artifact store they selected at startup; they do not switch or dual-write mid-session.

The former workspace instruction-source checkout and the prior workspace artifact store remain
preserved as independent rollback roots. Do not merge, mirror, symlink, move, delete, or rewrite
either history as part of this mapping. The complete machine-local agreement replaced by the older
workspace pointer also remains preserved intact. The cutover steps this appendix carried until the
2026-09-24 amendment for issue #54 remain readable at `29b6360:clients/openclaw.md`, lines 104–130.
If the pointer, Parts A–B, or this appendix is unreachable in the active session, stop the affected
work with the missing instruction-source capability recorded; do not automatically downgrade it to
B1. After changing a pointer, require the fresh-session observation above before declaring it
effective; do not assume arbitrary external-file injection or automatic refresh.

**Default mode: autonomous.** The capability guard (B0) is still evaluated for the unit B0 names;
that Camina coordinates several deliveries in one conversation does not widen it. In OpenClaw, an
unavailable capability is evidence about its affected operation: it does not switch the delivery or
team to B1, and the team stops at that operation with the exact missing safe route. This is a
canonical policy decision, not a claim that every capability has been measured. Any retained
workspace-local layer adds client mechanics only; it never copies or overrides Parts A–B. B2 still
reserves merging to Brandon alone. [learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]

## From *Runtime and workspace*: wrapper selector and route census (2026-10-24)

Resolve the active workspace and target checkout from live inventory; do not assume every specialist
shares main's CWD. When delegation is needed, use canonical role IDs and the supported native or
OpenClaw delegation mechanism available to that session; `sessions_spawn` is one available
OpenClaw mechanism, not a universal requirement. Put A4's RULE ZERO first. Then include only the
role, deliverable, mode, file fence and role-based model tier, and the selector that resolves that
tier where the mechanism accepts a caller's selection.

**Model selectors (A4's tiers).** Which selector resolves each A4 role tier for an OpenClaw
specialist is not recorded here — **unmeasured**; measure and record. The shared Claude Code
wrapper takes no caller selector and pins its own exact model [source:
`~/.openclaw/workspace/docs/team-operating-model.md` lines 198–199, read 2026-10-26, SHA-256
`f728ac8aad65abf94e9a7a352f96373ee0f1e3e66c46c24d406b9f2867524153`, quoted below], so a dispatch
through it names its role tier, passes no selector, and records the model the wrapper pins (A4).
Those two lines read exactly, line break kept:

```text
Invoke the wrapper without `--model` or `--fallback-model`; the wrapper pins the exact
model and rejects caller-supplied model selection. Transmitting relevant in-scope local
```

**Claude routes and intentional exceptions.** The same source applies its wrapper rule only where
a role has a supported Claude route; without one, the affected substantive operation stops and
reports the missing route, which is not a failed Claude invocation [source: same file, lines
204–206, same read and SHA-256]. The 2026-10-23 role-local normalization covered Camina and ten
specialist role sources, not the four roles below [source, issue #177].

Search boundary [measured, 2026-10-24]: a case-insensitive `claude|wrapper` search of only six
top-level files in each `~/.openclaw/workspace-<role>/`: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`,
`USER.md`, `HEARTBEAT.md` and `MEMORY.md`. All other files and subdirectories were excluded, among
them `DREAMS.md`, `memory/`, `media/`, `avatars/`, `avatar-candidates*/`, `drafts/` and `_agent/`.
"Only" and "no" about wrapper text below mean within that boundary, not across the workspace. Of
the 14 `workspace-*/SOUL.md` files, those of `finance`, `marketing` and `openclaw-admin` do not
name `claude-with-max.sh`, and `assistant`'s names it only conditionally [measured]. Configuration
facts come from `~/.openclaw/openclaw.json` [source: read 2026-10-24, SHA-256
`bf567245857808ffeef414e2904ee5b5873948eacde98ff639df54bba2b62ec6`]. Pilot and Slack-class facts
come from `~/.openclaw/workspace/memory/2026-10-24.md` lines 121 and 131 [source: read 2026-10-24;
lines 1–137 SHA-256 `267584c20d41942f872ecff7aed128158e2d16e8aa5baf4906afad40b3eb4459`]. Each
entry covers only the role it names:

- **`assistant` (Cortana):** the only wrapper text is `SOUL.md` lines 113–115 [measured; file
  SHA-256 `1d96e6b2ebdb047194e14a3ad73c90d9a9830d967edc7a549ba3ed8e95b625a8`], which say the role
  does not currently use Claude Code and that any future capability goes only through
  `scripts/agent/claude-with-max.sh`, never bare `claude` [source]. Its config entry, lines
  211–242, sets primary `openai/gpt-5.6-luna`, lists only `openai/gpt-5.6-luna` (runtime `codex`)
  and `openai/gpt-5.6-terra` (runtime `openclaw`), and has `tools.alsoAllow` of `memory_write`
  only [source]. That text grants no route; the role's runtime route is **unmeasured**.
- **`finance` (Graham):** no wrapper text; the only `claude` match is `AGENTS.md` line 20's pointer
  to a repository's `CLAUDE.md` [measured]. Its config entry, lines 628–695, sets primary
  `openai/gpt-5.6-sol`, its `modelPolicy.allow` is only `openai/gpt-6-astra` and
  `openai/gpt-5.6-sol`, and it has `tools.alsoAllow` of `memory_write` only [source]. The role
  is an intentional GPT-only pilot [source: memory lines 121 and 131].
- **`marketing` (Sloane):** no wrapper text; the only `claude` match is the same `AGENTS.md`
  line 20 pointer [measured]. Its config entry, lines 696–763, sets primary `openai/gpt-5.6-sol`,
  its `modelPolicy.allow` is only `openai/gpt-5.6-sol` and `openai/gpt-6-astra`, and it has
  `tools.alsoAllow` of `memory_write` only [source].
- **`finance` and `marketing` Slack class:** their `toolsBySender` rules, lines 676–693 and
  744–761, cover the same two Slack senders, and each sender rule both denies `group:runtime` and
  allows `gateway_exec` through its own `alsoAllow` [source]. For `finance`, that `gateway_exec`
  allow is stale, and its authenticated Slack canary exposed no executable tools and made zero
  Claude calls [source: memory line 121]. That class has no supported Claude route [source: memory
  line 131]. Substantive filesystem-grounded work arriving through it therefore stops at the
  missing route [inference, from the stop rule at lines 204–206 above applied to that source; not
  inferred from the configured grants; what would verify it: an authenticated canary from one of
  those two senders, to each role, that requests substantive filesystem-grounded work and
  observes the missing-route stop, with no Claude call]. `marketing`'s route outside that class is
  **unmeasured**.
- **`openclaw-admin` (Ashford):** no match for either term in the six searched files [measured].
  Its unsearched `_agent/` does contain `claude` or `wrapper` matches [measured], so that no-match
  statement holds only within the stated boundary. Its config entry, lines 588–627, sets primary
  `openai/gpt-5.6-sol`, lists only `openai/gpt-5.6-*` models, and has `tools.alsoAllow` of
  `memory_write` only [source]. Its route status remains **unmeasured**; measure and record. Do
  not infer it from the other entries.

No runtime route, present or absent, is inferred here from missing wrapper text or configuration
alone. This list is not a census: whether other roles outside the role-local wrapper contract
exist, and the route status of any that do, is **unmeasured**; the entries above cover only the
four roles they name.

OpenClaw does not relax either mode's topology. Attended lanes use one of B1's two shapes: an
mbox lane runs git only in its isolated clone, and a lane delivering uncommitted edits may edit its
named files in the shared checkout but runs no git there. The delivery owner, a specialist
dispatched as a sub-agent included, alone controls the shared checkout's git state: it stages a
batch and commits after Brandon's batch approval, and applies an mbox series with `git am` only
after that approval, since `git am` is the commit (A4, B1). Autonomous specialists use B2's
dedicated-worktree shape. For this agreement repository,
the amendment exemption in its README means an autonomous amendment uses one isolated feature
worktree branched from `develop`, rather than a wave branch; do not invent a wave merely to obtain
isolation.

## From *Staff operating model*: the prose the seat table replaced

This is an OpenClaw-only operating model. It does not change B0's guard, B1/B2's delivery rules,
the Part B ritual, or another client's appendix.

OpenClaw fills A4's three seats, and Brandon's, with distinct roles [decision 2026-10-23, Brandon,
issue #173]:

- **Camina — orchestrator.** Holds A4's orchestrator duties, preserves continuity across the
  conversation, and synthesizes the decision-ready hand-back. While a delivery specialist is
  assigned, Camina does not execute that delivery's repository mechanics; the orchestrating session
  fills the delivery-owner seat only when no specialist is assigned.
- **Judy (coder), or the assigned delivery specialist — delivery owner.** Holds A4's
  delivery-owner duties, and implementation and diagnostics of the delivery's authorized routine,
  reversible repository work.
- **Amos (reviewer), or the assigned reviewer — independent reviewer.** Holds A4's
  independent-reviewer duties; neither a lane's nor the delivery owner's own report is that review.
- **Brandon — merge.** Brandon alone merges into `develop`, `master`, or `main`.

A4 is the authority for each seat's complete duties, but for A6's one-off close record, which A6
assigns to the agent closing a delivery with no initiative; this list binds OpenClaw roles to them.

Work outside the authorized routine, reversible boundary escalates rather than staying with the
specialist, and administration outside it retains its existing authorization and stop conditions.

The OpenClaw agent team owns installs, builds, test suites, and verification for authorized,
routine, reversible repository work through a ready B2 pull request; an authorized B2-qualified
specialist lane is the default delivery path. Progress and status updates are informational and
non-blocking: sending one neither requests owner approval nor creates an approval checkpoint.
If a required safe route is unavailable, the team records that capability evidence and stops at the
affected operation with the precise missing route. It does not fall back to B1 or make Brandon the
command runner. [learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3]

Keep five decisions separate:

1. **Staff authority** — the owner has authorized the lane to decide and proceed within its scope.
2. **Lane capability** — B0 is evaluated for the selected lane's exact checkout and delivery path;
   a parent session unable to use that path does not downgrade the lane.
3. **Risk and reversibility** — only routine, reversible repository work may proceed on that
   authority.
4. **Delivery topology** — OpenClaw's autonomous default uses B2's dedicated-worktree shape;
   B1's lane shapes apply only when Brandon explicitly selects attended delivery.
5. **Human approval** — Brandon alone merges into `develop`, `master`, or `main`.

An authorized autonomous specialist owns authorized routine, reversible repository work through
the ready B2 pull request. Brandon alone accepts and merges into `develop`, `master`, or
`main`; he is not the command runner for that delivery. Every existing stop remains in force,
including destructive, irreversible, production, credentialed, financial, and externally published
actions; those stops are not delegated with the lane.

Within an authorized B2 delivery, commits, pushes, pull-request creation or updates, review
responses, and integration of reviewed lane work are routine delivery work and require no
per-batch owner approval. This is not authority for a B2 stop-list action or for a merge into
`develop`, `master`, or `main`; Brandon's ready-PR acceptance and manual merge remain the human
acceptance boundary.

Within an assigned B2 feature branch, an authorized lane may create a lane branch from that
feature branch. The delivery owner may integrate the lane's reviewed work back into that feature
branch only after a completed A4 two-axis review. B1 deliveries retain B1's lane shapes (mbox or
uncommitted edits). Neither lane-branch composition nor feature-branch ownership permits an agent
merge into `develop`, `master`, or `main`.

Every delivery retains a completed A4 two-axis verdict, the relevant diff and gate evidence, and
Brandon's decision context. Routine reversible work may present those required items in the
smallest sufficient packet; higher-risk or more substantive work adds scrutiny and evidence. This
scales ceremony around A4; it does not waive or replace A4's review requirement.

The B2 readiness boundary is unchanged: Brandon receives a ready feature PR with its A4 verdict,
relevant diff and gate evidence, and material decisions. This section adds no second acceptance
ceremony.

**Restoration owners (B2 stop-list item 5)** [decision 2026-10-27, Brandon, #194]: **Ashford** for
OpenClaw control-plane capability (dispatch allow-lists, tool exposure, routes, configuration, the
instruction-source pointer and its reachability); **Bull** for host and runtime capability; the
**delivery owner** for repository and worktree capability, the protected root's post-release refresh
included. Camina routes the stop and keeps continuity; a stop that names its owner is complete and
needs no packet.

## From *Bubblewrap circuit breaker*: pinned evidence

(none)

## From *Instruction-source isolation and freshness*: source readings and captures

OpenClaw documentation sources, all from the installed 2026.10.6 docs at
`<runtime>/lib/node_modules/openclaw/docs/`, where `<runtime>` is
`~/.openclaw/runtime/2026.10.6-release-41c5d94f722c-2026-10-22T19-49-54.000Z`, read
2026-10-25: `gateway/config-runtime.md` (SHA-256
`ee38d26c0cb37439c7c4b0ac71f826b8564a2559b6c451109cee7485568b60c8`),
`concepts/managed-worktrees.md` (SHA-256
`ecdbbfd79164e46e8883297680c975d13ff9d7cda149511c52be52dd6560d18d`),
`help/environment.md` (SHA-256
`adb51f50950f3d94814c19fd03164d0c100bf72ac749aaaa17cbd072da6411b8`),
`install/nix.md` (SHA-256
`db205205042c5351c47f94bb37385308706ae50f7389edd0dc175c5bc5ceeca8`),
`install/uninstall.md` (SHA-256
`74a52dab06de3ad3a96461b88eb51a04873f220f8a604d4abc9e2b50876be434`), and
`cli/gateway/query.md` (SHA-256
`2d179b4159fff0a1cef8c958ccbb96d386e5b5d1ed013c763a6211461dc33c65`).
Installed runtime source, all in `<runtime>/lib/node_modules/openclaw/dist/`:
`profile-utils-BsmgdpgZ.mjs` (SHA-256
`99679c5ce486640d779cb56e8a64b099a49a479c76d6e691242f52f0abd6c3bd`),
`state-dir-CYkBUd_G.mjs` (SHA-256
`f18c1153a532214e9efb50e1f4b99a5a6af2c41229292c4895c328747093c3e1`),
`profile-D1GpjMFM.mjs` (SHA-256
`fcf1469bb3923ec0e0bda20aa7317710827f9dc536282ab407e5aa97deb83224`),
`argv-invocation-BHqD0obO.mjs` (SHA-256
`3d2d71e1932e07791f918c94d1e6a997d32bfa9c794148dd5f503b81bc57aec9`),
`help-CRbQOEKD.mjs` (SHA-256
`1c0d1eaf0682cc773797b483888fda3b6c180f231243f62c0f08e3e67e4d7cd2`),
`run-command-CrXOzzsc.mjs` (SHA-256
`b252fb2a80021189666fd3ff8a3808e6d35a5efc94c77473a5ea846a7b91a71a`),
`entry.js` (SHA-256
`84d9ae4527bb46be0eece8f95cafefa40559cba8bd921e1358998b331cea0d08`),
`paths-BP0DYpE8.mjs` (SHA-256
`25900721157f35508fdd0f49b65ba6be8ad50f9fe259209929543e0cf50accff`), and, read 2026-10-26,
`base-ref-B9lkLpLz.mjs` (SHA-256
`b4723d93a05b4c97c3b82c20ada3e46a34c3ead7215d1d195e8ff37080b35c0d`) and
`service-BAfHLKXG.mjs` (SHA-256
`ebd36bea37c2c403e6f0376e432e5d68268bde54c047c3bada395143c6dc46ae`),
whose generated filenames and line references identify this exact installed build.

[measured 2026-10-26T03:55:06Z, this host, OpenClaw 2026.10.6 (41c5d94); the earlier
2026-10-25 reading has no capture located, so this replaces it; raw captures `gateway-status.json`,
`openclaw.json.copy`, `worktrees-list.json`, `gateway-status.err` and `worktrees-list.err`
preserved at
`/Users/brandonperfetti/dev/sansfaux/_agent/evidence/2026-10-25-agent-working-agreements-pr-181-gateway-worktree-inventory/`]
`openclaw gateway status --json` (empty stderr; output SHA-256
`2dbd291d1021280837b9192200db23fe75992968b642d93f4788b6629d34c81f`) reported a loaded launchd
service from `~/Library/LaunchAgents/ai.openclaw.gateway.plist` with
`"OPENCLAW_PROFILE": "default"`, `"OPENCLAW_STATE_DIR":
"/Users/brandonperfetti/.openclaw"` and `"OPENCLAW_CONFIG_PATH":
"/Users/brandonperfetti/.openclaw/openclaw.json"` under `service.command.environment`, and
`service.command.programArguments` contained only the recorded Bun and `dist/index.js` paths,
`--no-install`, `gateway`, `--port` and `18789`, with neither `--profile` nor a
root/profile-selecting `--dev`; thus its effective profile is that environment's `default`.
It also reported `config.daemon.path` set to
`/Users/brandonperfetti/.openclaw/openclaw.json`. That file, read in the same pass (SHA-256
`87027a892fc01a1464c5dc492389f196ef1494b2a01a03a79ac0dcd81fc668a3`), contains no `worktreeRoot`
string.

[superseded 2026-10-25] An earlier revision continued: "`openclaw worktrees list --json` (empty
stderr; output SHA-256 `3a25f8eae2dcf7c05707413dd65845a14330f7fad1365a23c3214b9fc5c040d0`)
recorded this delivery's worktree as …". That reading came from the capture whose bindings were
not recorded, `worktrees-list.json` with `worktrees-list.err` in the gateway-inventory directory
above, which stays preserved unchanged. It is superseded by the bound capture below and must not
be relied upon for the inventory claim. [measured 2026-10-25] That directory holds no argv,
invocation manifest or record of the state directory, config path or profile the invocation was
bound to; its `worktrees-list.json` SHA-256 equals that of the bound capture's `stdout.json`.
[inference] Equal bytes do not show which state directory, config or profile the earlier invocation
selected, so the earlier capture cannot support the inventory claim on its own; only the bound
capture does. No later reading can verify the earlier invocation's bindings, because they were never
recorded.

[measured 2026-10-26T04:37:53Z, this host, OpenClaw 2026.10.6 (41c5d94); raw captures
`argv.txt`, `argv-flag-check.txt`, `invocation-manifest.txt`, `run.sh`, `stdout.json`,
`stderr.txt`, `exit-status.txt`, `captured-at-utc.txt`, `openclaw-version.txt` and `SHA256SUMS`
preserved at
`/Users/brandonperfetti/dev/sansfaux/_agent/evidence/2026-10-25-agent-working-agreements-pr-181-bound-worktrees-list/`]
One `openclaw worktrees list --json` invocation ran with the call-local bindings
`OPENCLAW_STATE_DIR=/Users/brandonperfetti/.openclaw`,
`OPENCLAW_CONFIG_PATH=/Users/brandonperfetti/.openclaw/openclaw.json` and
`OPENCLAW_PROFILE=default`; its actual argv was
`/Users/brandonperfetti/.openclaw/bin/openclaw worktrees list --json`, with neither `--profile`
nor `--dev`. Its `invocation-manifest.txt` records those three call-local bindings exactly,
including `OPENCLAW_PROFILE=default` and the config path; `SHA256SUMS` records that manifest as
`f0d0408d0f68f42f38eb6dee5b312d88fa0d223b9658237a488d58293cdd0283`.
It exited 0 with zero-byte stderr (stdout SHA-256
`3a25f8eae2dcf7c05707413dd65845a14330f7fad1365a23c3214b9fc5c040d0`) and listed 26 entries, 17
active and 9 carrying `removedAt`. It recorded this delivery's
worktree as `"repoFingerprint": "3be5ac1eed078a0d"`, `"path":
"/Users/brandonperfetti/.openclaw/worktrees/3be5ac1eed078a0d/awa-180-protected-root-worktrees"`,
with `id`, `branch` and `repoRoot` set. That is one record; it does not cover every managed
worktree. [inference] The effective root here is the default
`/Users/brandonperfetti/.openclaw/worktrees`, outside `$AGENT_ROOT/_agent/`; what would verify it:
the service state directory still resolves to `/Users/brandonperfetti/.openclaw`, the service config
at `config.daemon.path` has no `worktreeRoot` key, and the recorded inventory path for a newly
created managed worktree lies under that root. Resolve it again for each delivery rather than
reusing this value.

[measured 2026-09-23] PR #41 merged at `b733b59982736285d078ee9f67209bcce2fea957` on
2026-09-22T20:18:10Z, but the protected instruction-source root working tree remained six commits
behind until the next day.

[corrected 2026-10-26] An earlier revision labelled that claim "[measured
2026-10-25, Git 2.56.0, a scratch repository; recorded in commit
`adef2b1e7d6f2d3a4572d68802a6ed24edd661b7`]", which must not be relied upon: no raw output of
that scratch-repository run was preserved, and that commit only introduced the wording, so it
locates the claim's history, not a measurement. If that status command exits nonzero, cannot be
run, or prints any output, stop, and retain and report the worktree and branch with its exit
status and output. Only exit 0 with empty output permits cleanup to continue. Then pick the
removal route from OpenClaw's registered inventory. Run:

## From *Pickup guard and delivery audit*: pinned evidence

(none)

## Evidence store (former wording)

**Configured native store.** For a fresh role started from a replaced pointer under the approved
acceptance procedure in [Startup and mode][startup], the native artifact store resolves
provisionally at session startup to `/Users/brandonperfetti/dev/sansfaux/_agent/`; that same store is
retained whether the later role verdict passes or fails. For a role whose pointer is still unchanged,
and on any other host, use the concrete durable `_agent/` store selected by the active workspace
policy and record its location with the capture; do not infer this Mac path across hosts. An active
session remains bound to the store it selected at startup even if a workspace pointer changes later.
Never switch stores or write the same artifact to both stores mid-session.

Use the selected store's `evidence/` and `analysis/` subdirectories per A2 and A6. Date-name
artifacts and label claims `[measured]`, `[source]`, or `[inference]`.

**Scratch clones (A6, "Clones").** The task-authorized scratch root in the Gateway
executable-check conditions above is not a place for a scratch clone: it exists for one eligible
check and is removed when that check completes [source: this appendix]. Where a scratch clone goes
on this host, and whether specialists share a scratch space, is **unmeasured** — measure and
record. Never under `_agent/`.

## Migration dispositions

The complete machine-local agreement that preceded the canonical route carried rules that Parts
A–B now supersede. They are deliberately **not carried forward**, for these reasons:

- **A — autonomy:** the local autonomous default is superseded by the canonical OpenClaw
  autonomous default, B0's per-checkout capability evidence, and B2's Brandon-only merge boundary;
  an unavailable operation stops at its missing safe route rather than downgrading the team to B1.
- **B — specialist commits:** a dispatched lane specialist committing, staging or running any
  other git in the shared checkout is not carried forward. Attended sessions use B1's two lane
  shapes — an mbox series committed in the lane's isolated clone, or uncommitted edits to named
  files in the shared checkout with no git run there — and the delivery owner (A4) alone keeps the
  shared checkout's git state, staging, committing and applying with `git am` per B1; autonomous
  sessions use B2's dedicated-worktree shape. A delivery owner dispatched as a sub-agent is not a
  lane and keeps those A4 shared-checkout git-state duties.
- **C — builds and tests:** OpenClaw's autonomous team owns installs, builds, tests, and
  verification through the ready B2 PR; an unavailable safe route stops that operation with its
  evidence, while B1 applies only when Brandon explicitly selects attended delivery.
- **D — evidence:** the local requirement to retain raw capture for every measured claim is
  superseded by A2's classification. Only the OpenClaw evidence-store mapping above remains.
- **E — remote commit APIs:** the local permission is removed; A7's checkout-Git-only rule remains
  unchanged.
- **F — asking Brandon:** the local generic ask rule is superseded by A8 and B2's stop-list.

Staff consultation, process restart behavior, Claude wrapper behavior, and Bubblewrap recovery's
fuller five-step pattern (`docs/team-operating-model.md` on the OpenClaw host) stay in the fleet
documents or wrappers that already own them; only the one-strike circuit breaker above, the part
that applies in-session, lives here. Do not copy them into this appendix or a replacement local
agreement.

[iso]: ../procedures/openclaw/managed-worktrees.md#instruction-source-isolation-and-freshness
[startup]: ../clients/openclaw.md#host-and-startup
