# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the label
strings this repository's tracker uses, names the other labels the triage and friction work reads,
and says who creates a label and who applies one.

**This repo keeps the defaults**: each role's label string equals its canonical role name.

| Canonical role    | Label in our tracker | Meaning                                  |
| ----------------- | -------------------- | ---------------------------------------- |
| `needs-triage`    | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`      | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent` | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human` | `ready-for-human`    | Requires human implementation            |
| `wontfix`         | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (for example "apply the AFK-ready triage label"), use the label
string from this table.

## Friction and sweep labels

These are not triage-state roles. They say what kind of issue it is, or how the daily friction
sweep treats it.

| Label              | Meaning                                                                |
| ------------------ | ---------------------------------------------------------------------- |
| `friction`         | A workflow cost promoted from a `friction/` record; the sweep reads it |
| `needs-brandon`    | Waits on a decision only Brandon makes; the sweep skips it             |
| `friction-skipped` | The sweep does not re-investigate it until the label is removed        |
| `quick-win`        | One small PR closes it, with no decision needed                        |
| `agent-filed`      | An agent filed it, so Brandon can sweep it (B2)                        |

`needs-brandon` is not `ready-for-human`. `needs-brandon` means the next step is a decision and
only Brandon makes it; `ready-for-human` means the work is decided and a human implements it. A
friction issue that needs Brandon's decision gets `needs-brandon`, a comment with the reason and
one recommendation, and no triage role in its place.

The promotion rule, its bar and the form are
[`procedures/agent-workspace-layout.md`](../../procedures/agent-workspace-layout.md)'s; the form
is [`.github/ISSUE_TEMPLATE/friction.yml`](../../.github/ISSUE_TEMPLATE/friction.yml).

## What the tracker actually has

Which labels exist is the tracker's to say. Read it there, not from a copy:

```bash
gh label list --repo brandonperfetti/agent-working-agreements --limit 100
```

Measured 2026-11-14: of the five roles, only `ready-for-agent` and `wontfix` are defined;
`needs-triage`, `needs-info` and `ready-for-human` are not. `friction`, `needs-brandon`,
`friction-skipped`, `quick-win` and `ready-for-agent` were created that day, with Brandon's
approval, for the first friction sweep. The tracker also has `agent-filed`, `route-suspended`,
the work types `type:epic`, `type:task` and `type:spike`, and GitHub's stock labels (`bug`,
`documentation`, `question` and the rest).

Read the groups as separate vocabularies. A work type or stock label on an issue says nothing
about its triage state.

## Who creates a label, and who applies one

- **A missing label is Brandon's to create**, or an agent's on his explicit approval, as on
  2026-11-14. A skill that needs a role whose label is not on `gh label list` asks him.
- **On a filing, an agent applies `agent-filed`** and a kind label, such as `documentation` or,
  for a promoted friction item, `friction`. A triage-state role's label is not an agent's to
  apply on a filing.
- **A triage-state label, `needs-brandon` or `friction-skipped` goes on by relabelling an
  existing issue**, which is the orchestrator's (B2), cited in a comment.

The tables above name the label strings; they grant no one the right to create or apply a label.
