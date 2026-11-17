# Sans Faux studio profile

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first,
then this profile, then your client adapter below.** This profile binds the core to Brandon's
studio; it adds and narrows, never weakens, and a rule here that contradicts one there is the rule
that is wrong. Every file under `clients/` requires it; name it with the core and your adapter.

This is the working agreement between Brandon and every agent he works with under the **Sans
Faux** studio. It sits above each project's own `AGENTS.md` / `CLAUDE.md`; project scope never
percolates up, working style never down. Paths are relative to the `sansfaux/` root, where
`_agent/` and `organize.sh` sit. History lives in [`../CHANGELOG.md`](../CHANGELOG.md) and
`_agent/`; how this repository changes is [`../AGENTS.md`](../AGENTS.md)'s to say.

## Bindings

| Core term | Sans Faux binding |
| --- | --- |
| `owner` | Brandon Perfetti; he merges releases and every merge no active route covers, by hand in the host's UI |
| `delegated merge route` | **active for Claude Code and OpenClaw only** — the head-bound route of [`review-findings.md`](../procedures/review-findings.md#base-merges), for routine work into `develop` of `agent-working-agreements` and `claude-skills`, merged by Claude Code with the installed `hooks/claude-code` guard, qualified 2026-11-13 on Claude Code 2.1.322 (#269: fixture record `_agent/initiatives/fleet-mega-s03-adoption/evidence/2026-11-13-develop-route-fixture-qualification.md`, review `…/reviews/2026-11-13-develop-route-fixture-review.md`), or by OpenClaw's delivery owner in an OpenClaw-runtime turn's Code Mode `exec` or a claude-cli turn's `mcp__openclaw__exec`, with the installed `hooks/openclaw` relay and its canary refused with `awa-guard-git:` through the same tool right before each merge, qualified 2026-11-16 on OpenClaw 2026.11.1 (#272: fixture record `…/evidence/2026-11-16-awa-272-openclaw-route-fixture-qualification.md`, review `…/reviews/2026-11-16-awa-272-openclaw-route-review.md`); suspended in a repository while it has an open issue labelled `route-suspended` (checked before every delegated merge; an unreadable check counts as suspended) until Brandon closes it; no tool of an OpenClaw Codex-harness turn is the merge tool (`gateway_exec` is checked by the relay implementation but has not been measured live; it is not a qualified delegated merge route), so a delivery owner whose work ran in one may make the merge step from one of those two turns, through its named tool, which runs its own canary and re-reads the PR's head and base first ([`clients/openclaw.md`](../clients/openclaw.md)), and Brandon merges where neither is available or the canary or any route condition fails; Codex and T3-hosted Codex are not qualified, so Brandon merges for them until a reviewed change here names each |
| `author identity` | `brandon@brandonperfetti.com`, exactly — RULE ZERO below |
| `attribution` | one agent declaration line per item, and nothing else — RULE ZERO below |
| `integration branch` | `develop` |
| `release branch` | `master` |
| `artifact store` | the agent root's `_agent/` — A6 below |
| `review route` | `code-review` (Standards + Spec); CodeRabbit is the PR bot — A4 below |
| `tracker` | GitHub Issues plus `users/brandonperfetti/projects/2` — A7 below |

## Studio authority

- **A1.** Applies to every session Brandon runs, on any of his repositories, wherever the checkout
  lives. A skill never overrides the agreement (Brandon, 2026-10-12). Skills come from the
  `brandonperfetti-skills` plugin; read the one a task, trigger or procedure names before acting,
  confirmed in your client's skill and connector listing.
- **Initiatives.** Orchestrated multi-wave work lives in `_agent/initiatives/<project>-<slug>/`.
  Its `MASTER-PRIORITY-DOCUMENT.md` is the spine, born from an attended Genesis, §0 recording the
  mode; leads advance approved work across waves. Bounded work outside one needs none of it (A1).
- **RULE ZERO: Brandon's identity, one honest declaration.** An agent's commit on his behalf has the
  author email `brandon@brandonperfetti.com`, exactly; an outside contribution keeps its author's,
  and a PR carrying his identity from another account is not merged until re-authored (Brandon,
  2026-10-13). **New work declares its agent once**, as a commit trailer or the closing line of a PR
  or issue body, comment or reply: `Agent: <client> · <model id> · <effort>` (OpenClaw:
  `Agent: Camina (OpenClaw) · <model>`), the served model if attested, else marked `(requested)`. No
  `Co-Authored-By`, generated-with or promotional footer, session or chat link, or second
  declaration (Brandon, 2026-11-14); a bot's own text, such as CodeRabbit's PR summary, is not an
  agent credit. Read each message and author before push, merge, presentation.
- **Review and merge.** [`review-findings.md`](../procedures/review-findings.md) carries where
  verdicts go, reviewer escalation, release carry-forward, the paid allowance, the bot's outcomes
  and delegated-merge conditions; close-out is where the big finds happen [learnings: 2026-08-30 §9].
- **A5.** Never reason about a running dev server as though your edit is in it. Shared-database
  tiers in parallel workers snapshot their baseline by id and unwind fixtures in `try/finally`.
- **A6.** Initiative work goes in its initiative folder, one-off work in `_agent/`'s one-off
  folders, never loose; never a clone in `_agent/`. The layout, friction path and clone rule are
  [`agent-workspace-layout.md`](../procedures/agent-workspace-layout.md)'s (#185).
- **A7.** `gh` is primary. The GitHub MCP and Kody's `@brandonperfetti/github` never author commits.
  Board intake and Status moves: [`github-paths.md`](../procedures/github-paths.md).
- **B0.** Never ask Brandon the mode at session start. Base protection by role: `develop` blocks
  force-pushes and deletions with no PR rule; `master` requires a PR and the gate. Where the core,
  this profile or an adapter is named but unreachable, every client but OpenClaw continues the
  affected delivery under attended rules (B1); OpenClaw stops it, as its adapter says (core
  *Composition*). **Route-scoped adapter:** `clients/openclaw.md`
  [learnings: 2026-10-18 openclaw-autonomy-and-recovery §1, §3].
- **B2.** [`autonomous-delivery.md`](../procedures/autonomous-delivery.md) carries the preflight,
  the CodeRabbit round, `agent-filed` issues and wave-close learnings; Brandon is never made the
  command runner (#194).

## The Git ritual

**Read this before writing, following or amending any rule that touches a push, a branch or a
merge.** It is what Brandon does, on **every** repo, in his words. Where a rule and this section
disagree, the rule is wrong.

1. **Feature work branches off `develop`**, with nested feature, bugfix and lane branches as needed.
2. **That branch opens a PR into `develop`.** The review bot reviews it; findings are worked **on
   the feature branch**; it merges into `develop` as the `delegated merge route` binding says.
3. **When `develop` is ready to ship, a PR is opened from `develop` into `master`.** Its **head is
   `develop`** — there is no release branch. Release branches were **rejected** (Brandon,
   2026-09-12): they add a step to every release to buy a constraint he does not want.
4. **The bot reviews that PR too, and its findings are worked by pushing to `develop`** — the head
   branch, the only one that updates the PR. Re-review until clean. This is why `develop` accepts
   pushes (B0 item 4); it is the ritual, not an edge case.
5. **Release-cut work lands on `develop` the same way** — the version bump, the CHANGELOG section
   rename and any built artifact, reviewed on that PR. The only per-repo difference is whether a
   repo has a version to bump at all.
6. **Brandon merges the release PR, by hand in the host's UI,** and any `develop` merge no active
   route covers. The delivery owner merges reviewed lanes.
7. **Brandon tags on `master`**, where the repo publishes releases; the tag fires the release
   workflow.
8. **The back-merge carries `master` home to `develop`** — a direct push by the workflow, why
   item 4's integration profile keeps accepting pushes.

**The test for any rule about git:** name the step above it applies to.

## Triggers

| When | Read |
| --- | --- |
| You label a claim from irreproducible bytes, trust a probe, or quote a file | [`evidence-capture.md`](../procedures/evidence-capture.md) |
| You dispatch a lane, hold more than one seat, or run an initiative | [`orchestration-seats.md`](../procedures/orchestration-seats.md) |
| You are about to push, merge, present, or apply an mbox series | [`rule-zero-check.md`](../procedures/rule-zero-check.md) |
| A delivery is ready for review, a bot or reviewer finding needs an outcome, or a PR is about to merge | [`review-findings.md`](../procedures/review-findings.md) |
| You create, adopt, move or retire a worktree, or close out a delivery | [`worktree-lifecycle.md`](../procedures/worktree-lifecycle.md) |
| You work or delegate through T3 | [`t3-adapter.md`](../procedures/t3-adapter.md) |
| You write any artifact, or need a scratch clone | [`agent-workspace-layout.md`](../procedures/agent-workspace-layout.md) |
| You touch an issue, a PR, or the GitHub API | [`github-paths.md`](../procedures/github-paths.md) |
| You pick up a delivery (first commit on a checkout, each repository) | [`pickup-guard.md`](../procedures/pickup-guard.md) |
| The delivery is attended | [`attended-delivery.md`](../procedures/attended-delivery.md) |
| The delivery is autonomous | [`autonomous-delivery.md`](../procedures/autonomous-delivery.md) |

## Client adapters (read only yours)

B0 decides the mode. In T3, use the actual provider adapter plus `procedures/t3-adapter.md`.

| You are | Read | Default mode |
| --- | --- | --- |
| Claude Code | [`clients/claude-code.md`](../clients/claude-code.md) | autonomous |
| Cowork (Claude desktop, over the device bridge) | [`clients/cowork.md`](../clients/cowork.md) | attended |
| Codex (ChatGPT desktop, local shell) | [`clients/codex.md`](../clients/codex.md) | autonomous |
| OpenClaw (Camina) | [`clients/openclaw.md`](../clients/openclaw.md) | autonomous |

Where your client is not listed, read the closest match, say so, and record what differed; a new
client earns a file once its guard items are measured.
