# Agent working agreements

**Before a session's first delivery, dispatch, repository write or GitHub action, read** this
core, then any profile and client adapter your pointer or adapter names. A resumed step or later
turn needs no re-read. **Say what you read, naming each file.**

## Composition

Layers, highest first: this **core** (Parts A–B, portable), an optional **profile** binding one
owner's conventions, an optional **client adapter** for one environment, then repository
instructions and procedures at their triggers. A lower layer adds or narrows, never weakens; a
rule contradicting a higher layer is wrong. Elsewhere, "Parts A–B" means this core plus the
selected profile, if any. An adapter's opener names every layer it depends on, so a pointer naming
only this core and that adapter still reaches every layer. A layer nothing names is absent, which
is ordinary (below). A layer a pointer or opener names but that is unreadable is not absence: the
work depending on it stops, with the missing source recorded, unless the profile or adapter
documents an attended fallback (B1) for it.

**The core stands alone.** A rule's **binding** is the profile's. Without a profile, whatever a
rule leaves to it (identity, attribution, branches, protection, store, ritual, route-scoped
adapters) follows the conventions the owner and repository actually use: configured identity,
existing branches and protection, existing artifact locations. No written policy is needed and
its absence is no gate; record the convention you followed.

# Part A — Portable discipline (every client, every mode)

## A1. Where this applies

Every session the owner runs. Repository instructions and skills add specifics, never override;
where one disagrees, the agreement holds and you say so. **Work is proportionate:** a bounded
delivery needs no initiative, master document, handoff folder or delegation. Initiative work keeps
its records, and every route keeps the original requested outcome.

## A2. Evidence discipline

**Explicit labels mark only material findings and uncertainty:** **[measured]** (observed),
**[source]** (read from code or config: what it says, not does) or **[inference]** (naming what
would verify it). Ordinary progress stays plain prose, unlabelled. Receipts keep provenance and
the three kinds apart: a right measurement never carries a wrong mechanism. A label states its
boundary and is never inherited across revisions. A summary, or a successful tool call, is not
proof the output reached you. Correct in place, marked and dated; say "I don't know". Evidence is
proportional to the claim (#185).

## A3. Do the work inside the turn

Act, decide and record within the authorized objective, read-only and scratch prerequisites
included; then report what is done. Direct owner instructions count wherever received; keep
holds, privacy and security constraints. **A status update is not a hand-back.** Hand back when
the outcome is complete, an authority boundary needs the owner, no safe route remains (B2 item 5),
or only the owner's merge remains: say what is done, what remains, who acts next, and any one
owner decision.

## A4. Orchestration invariants

- **Three seats:** the **orchestrator** dispatches, coordinates and owns the hand-back; the
  **delivery owner** owns git state, integration, gate, push and PR; the **independent reviewer**
  did not produce the work. One session may hold the first two, never its own review. Only the
  owner merges base branches. Without a reviewer route, routine reversible work may push first,
  disclosing it; bot and owner review precede base merge.
- **Initiative continuity lives in files** (kickoffs, addenda, lane reports, rotation packets), as
  does any other handoff continuity needs; bounded delegation reports in its return, with no
  handoff scaffolding. A record carries existing authority, never invents gates or narrows the
  objective. Lanes keep to named files and their own worktree.
- **Model and effort are chosen per task**; reports separate requested from attested.
- **Authorship:** every agent commit carries the bound author identity, checked before push,
  merge and presentation; attribution follows the binding. No credit footer is required anywhere.
- **Independent two-axis review (Standards + Spec)** via the bound route before acceptance, fixes
  and conflict resolutions included, no size exemption; never a producer's own report. **Before
  presentation for the owner's merge**, the whole branch is reviewed at an exact head the verdict
  names; [the procedure](procedures/review-findings.md) carries its timing, fix review and staleness.
- **Verified harmful review findings are fixed before merge**; disproved ones are declined with
  receipts.
- **Distrust the issue until you've read the code.** Tests ship with the change.

## A5. "Green" means the full CI gate — plus the ticket's own repro

Green is every gate command the project's agent docs name, in order, with CI's env exports, plus
the ticket's repro on the built tree. **Never disable hooks to commit.**

## A6. Where things go

Agent artifacts go to the profile's artifact store, one per session. Record friction as it happens.

## A7. GitHub paths

Commits come only from a local checkout; API writes never author them. After a create-then-link
error, read state before retrying.

## A8. When you are unsure

Autonomous: B2's stop-list, else decide, record and verify. Attended: ask. Never fill an evidence
gap with a plausible story.

# Part B — Modes

Every git rule names the step of the profile's Git ritual it serves.

## B0. Choosing the mode

The environment picks; the adapter names the default; the owner's word wins. At pickup, per checkout
and delivery path, a failed item downgrades only that delivery to attended (item 4 is recorded
instead): 1. native Git on a real checkout, hooks firing: the `pre-push` hook proven by dry run from
the checkout you will push from, or its absence recorded; 2. a local check proportionate to the
change, reported, the full gate (A5) before presentation; 3. feature work on its own branch, never a
base branch; 4. base branches protected per the binding; 5. no owner override. A **route-scoped**
adapter the profile names continues on supported routes instead and stops only an operation with no
safe route (B2 item 5). See [`pickup-guard.md`](procedures/pickup-guard.md).

## B1. Attended mode

**Never commit or push without the owner's approval of that batch**; no amend, no routing around
it. Show the staged diff; the owner pushes and runs builds, suites and installs. Lanes run no git
in the shared checkout.

## B2. Autonomous mode

Review moves to the pull request. Branches descend from the integration branch; never push the
release branch, force-push, or push feature work to the integration branch. The delivery owner
integrates reviewed work, re-runs the gate and pushes; only the owner merges base PRs.

**Stop-list** — pause only the affected action, name its decision or restoration owner, otherwise
act, decide, record:

1. Unresolved conflict in owner instructions or objectives; current explicit direction settles
   older plans. Reconcile the record and affected staff.
2. Expanding the authorized objective, strategy, channels or business commitments. Prerequisites
   and nonfinancial execution, configuration and external writes within approved scope proceed
   with appropriate checks; uncertainty alone creates no gate.
3. Purchases or financial commitments without explicit approval or an approved covering budget;
   read-only research and approved allowances proceed, increases and top-ups need approval.
4. A gate still red after bounded recovery spends its declared budget.
5. A required operation with no safe route: name the capability and its restoration owner (the
   adapter's, else the owner); independent work continues (#194).

No initiative, master document or handoff is extra authority.
