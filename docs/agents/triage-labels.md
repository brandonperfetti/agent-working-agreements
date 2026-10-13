# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the
label strings this repository's issue tracker uses, or will use.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  | On GitHub   |
| -------------------------- | -------------------- | ---------------------------------------- | ----------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  | not created |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information | not created |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  | not created |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            | not created |
| `wontfix`                  | `wontfix`            | Will not be actioned                     | exists      |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding
label string from this table. Where the last column says **not created**, create the label
with `gh label create <name> --repo brandonperfetti/agent-working-agreements` the first time a
skill needs it, rather than assuming it is there.

## The labels the tracker has

[measured 2026-10-13, `gh label list`] Eleven labels, in three groups. None but `wontfix` is a
triage role, and none stands in for one:

| Group | Labels |
| --- | --- |
| Canonical triage | `wontfix` |
| Agent marker | `agent-filed`: an issue an agent filed, so Brandon can sweep them (the agreement's B2) |
| General-purpose | `accessibility`, `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question` |

[measured 2026-10-13, `gh issue list --state all`] In use on issues: `agent-filed`,
`documentation` and `question` (on issues that ask for a decision or a spike). A label already
on an issue says who filed it or what kind of issue it is, and nothing about its triage state.
