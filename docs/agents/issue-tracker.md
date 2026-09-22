# Issue tracker: GitHub

Issues and specifications for this repository live in
[`brandonperfetti/agent-working-agreements` GitHub Issues](https://github.com/brandonperfetti/agent-working-agreements/issues).
Use the `gh` CLI for tracker operations.

## Read an issue or specification

When a commit message references `#N`, fetch the originating issue and its comments
before running the Spec axis of a review:

```bash
gh issue view N \
  --repo brandonperfetti/agent-working-agreements \
  --json number,title,state,body,labels,comments,url
```

The issue body is the initial specification. Read its acceptance criteria and every
later comment that corrects, narrows, or supersedes them; do not infer the current
specification from the title or PR body alone.

## Agent permissions

Agents may read, list, and comment on issues through `gh`. A7 designates `gh` as
the primary skill-driven surface and GitHub Issues as the tracker. B2 authorizes
agents to file findings through `writing-tickets`; those issues carry the
`agent-filed` label so Brandon can sweep them.

Closing is not a delivery agent's call. Closing or relabelling an existing issue
is orchestrator-only and must be cited. For issue-backed delivery, Brandon triggers
closure by merging the release PR. Brandon alone merges pull requests and flips
draft PRs to ready for review.

## Reference an issue from a pull request

Read the issue's own acceptance text before writing any reference line. Put each
reference on its own line in the pull request body:

- A feature PR into `develop` uses `Refs #N`.
- The release PR from `develop` into `master` uses `Closes #N`.

Do not use `Fixes` or `Closes` on a `develop`-bound PR. A `Closes #N` line on
the release PR records the intended closure, but the issue closes only when Brandon
merges that PR into `master`.
