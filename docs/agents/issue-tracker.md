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

Agents may read, list, and comment on issues through `gh`. They may file an
actionable issue under A7 when the working agreement permits it, but must apply the
`agent-filed` label and identify the agent provenance in the issue body.

Closing an issue is not an agent decision. Agents do not close issues, merge pull
requests, or flip releases; Brandon makes those calls.

## Reference an issue from a pull request

Read the issue's own acceptance text before writing any reference line. Put each
reference on its own line in the pull request body:

- A feature PR into `develop` uses `Refs #N`.
- The release PR from `develop` into `master` uses `Closes #N`.

Do not use `Fixes` or `Closes` on a `develop`-bound PR. A `Closes #N` line on
the release PR records the intended closure, but the issue closes only when Brandon
merges that PR into `master`.
