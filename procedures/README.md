# Procedures

The mechanics behind the rules in [`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md).
The agreement holds the invariant and a one-line pointer; a procedure holds the steps, the edge
cases and the measurements, and is read when its trigger occurs, not at session start. A procedure
never overrides Parts A–B, and a rule here that contradicts one there is the rule that is wrong.

Every procedure opens with four fields — **Trigger**, **Owner**, **Implements**, **Stop** — and
`scripts/check-structure.sh` checks that each file here is listed below and in the agreement's
*Triggers* table (a client-specific one under `<client>/` is linked from that client's appendix
instead), carries those fields, and holds no hash or line-number pin of a mutable file.

| Procedure | Implements | Trigger |
| --- | --- | --- |
| [`evidence-capture.md`](evidence-capture.md) | A2 | labelling from irreproducible bytes, trusting a probe, quoting a file |
| [`orchestration-seats.md`](orchestration-seats.md) | A4 | dispatching a lane, holding more than one seat, running an initiative |
| [`rule-zero-check.md`](rule-zero-check.md) | A4 | before a push, merge, presentation or `git am` |
| [`review-findings.md`](review-findings.md) | A4 | a delivery ready for review; a bot or reviewer finding |
| [`agent-workspace-layout.md`](agent-workspace-layout.md) | A6 | writing any artifact; a scratch clone |
| [`github-paths.md`](github-paths.md) | A7 | touching an issue, a PR or the GitHub API |
| [`pickup-guard.md`](pickup-guard.md) | B0 | picking up a delivery |
| [`attended-delivery.md`](attended-delivery.md) | B1 | an attended delivery |
| [`autonomous-delivery.md`](autonomous-delivery.md) | B2 | an autonomous delivery |
| [`openclaw/managed-worktrees.md`](openclaw/managed-worktrees.md) | `clients/openclaw.md` | pickup of an OpenClaw delivery: create, refresh, clean up |
| [`openclaw/native-sandbox-breaker.md`](openclaw/native-sandbox-breaker.md) | `clients/openclaw.md` | dormant: the exact Bubblewrap prelaunch signature |

The text in these files was moved out of the agreement verbatim on 2026-10-27 (PR 2 of the
hardening, epic #185), minus the lines the core kept (`review-findings.md` skips A4's issue and
tests bullets; `autonomous-delivery.md` skips the stop-list). Where it says "above" or "below", it
means the agreement section it implements. Trimming it is later work, one procedure per PR, under
`AGENTS.md`'s amendment rules.
