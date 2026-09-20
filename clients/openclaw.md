# OpenClaw (Camina)

**Read [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md) Parts A and B first, then
the target repository's instructions.** This appendix adds client mechanics only; it never overrides
Parts A–B. **Name this file when you acknowledge your reading** — "read the agreements and
`clients/openclaw.md`" — so a skipped read is visible.

## Startup and mode

The workspace-root `AGENTS.md` is the local pointer to the canonical agreement checkout and this
appendix. If that pointer, Parts A/B, or this appendix is unreachable in the active session,
downgrade to attended. Do not assume arbitrary external-file injection or automatic refresh.
After a pointer, configuration, or skill-loader change, require a fresh-session observation before
declaring it effective.

**Portable default: attended.** B0 decides the mode for the exact checkout and delivery path. This
Sans Faux workspace may carry an explicit autonomous override, but that local policy is not
portable proof: it still requires checkout-specific guard evidence and Brandon-only merge through
B2.

## Runtime and workspace

Resolve the active workspace and target checkout from live inventory; do not assume every specialist
shares main's CWD. When delegation is needed, use canonical role IDs and an explicit
`sessions_spawn` brief; include only the role, deliverable, mode, file fence, and selected
model/tier needed for that dispatch.

## Pickup guard and delivery audit

Record the checkout and HEAD, Git author identity, `core.hooksPath` and hook presence, an explicit
dry-run probe (or N/A when the repository installs no `pre-push` hook), the full gate result,
branch ownership, and target-protection audit. Parts A/B remain the authority for RULE ZERO,
no-force-push, and no-agent-merge; do not restate those rules here.

Attribution injection, arbitrary external injection, and exact reset/reload behavior remain
unmeasured. Require a delivery audit or controlled observation rather than assuming them. Record a
skill source/version when it materially affects delivery; skill precedence is not agreement
authority.

## Evidence

When reachable, preserve OpenClaw raw captures under
`/data/.openclaw/workspace/_agent/evidence/` and analysis under
`/data/.openclaw/workspace/_agent/analysis/`. Date-name artifacts and label claims
`[measured]`, `[source]`, or `[inference]`. Do not assume those locations are reachable from
every workspace; use A2's capture taxonomy when they are.
