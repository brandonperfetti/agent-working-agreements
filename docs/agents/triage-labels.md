# Triage Labels

Skills name an issue's triage state by role, one of five. This file gives the label string each
role carries on this repository's tracker, and tells a role's label from the others.

## The roles' labels

Each of the five roles is labelled by its own name: `needs-triage`, `needs-info`,
`ready-for-agent`, `ready-for-human` and `wontfix`. A skill that describes a role in other words
means the label named for that role.

Which of these labels exist is the tracker's to say. Read it there, not from a copy:

```bash
gh label list --repo brandonperfetti/agent-working-agreements
```

A skill that needs a role whose label is not on that list asks Brandon, who owns the tracker, to
create it. Creating a label definition is a write to the tracker that no rule gives an agent.
On a filing, an agent applies `agent-filed`, as B2 requires, and may apply a label that says what
kind of issue it is, such as `documentation`. A triage-state role's label is not an agent's to
apply on a filing; after one, it goes on only by relabelling an existing issue, which stays the
orchestrator's (B2).

## Telling a role from the other labels

A role's label on an issue is its triage state; `wontfix` is one. A label the first section does
not name is not a triage-state role. `documentation` and `question` say what kind of issue it is,
and `agent-filed` that an agent filed it, so Brandon can sweep them (B2); none of the three says
anything about its triage state.
