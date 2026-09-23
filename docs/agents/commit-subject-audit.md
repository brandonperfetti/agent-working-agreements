# Active-repository commit-subject audit

[measured 2026-09-23] Audit for issue #27 after the OpenClaw canonical-source
cutover.

## Scope and method

For this audit, an **active repository** is a non-archived repository with a
primary top-level checkout in the live Sans Faux workspace and evidence of owner
activity during 2026 or unfinished work in that checkout. Linked worktrees and
additional clones of the same remote count once.

[measured 2026-09-23] The live workspace contained four unique top-level remotes
meeting that rule. For each one, the audit fetched its current default branch,
listed tracked `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING*`, and `README.md` files,
and searched tracked Markdown, JSON, and YAML for `commit subject`,
`commit message`, `commit convention`, `conventional commit`, and
`type(scope)`. Recent non-merge subjects were then read as evidence of practice,
never as repository authority.

The following were excluded:

- [measured] the instruction-source clone, delivery worktrees, and the
  `cache/claude-skills-check` clone, because their remotes are already counted;
- [measured] the repository under `_agent/experiments/`, because it is experiment
  evidence, not an active project checkout; and
- [source, workspace instructions] Next Foundry, because it is reference-only and
  has no checkout in this live workspace.

## Results and dispositions

| Repository | Evidence that it is active | Explicit owner document | Disposition |
| --- | --- | --- | --- |
| `brandonperfetti/agent-working-agreements` | [measured] `master` advanced to `7bc6c9b` on 2026-09-23 through release PR #53. | [source, `7bc6c9b`] Root `AGENTS.md` requires `type(scope): description`, adds `(#issue)` when applicable, and preserves Git/GitHub-generated subjects. | [decision 2026-09-23, audit] Complete; no follow-up. |
| `brandonperfetti/claude-skills` | [measured] `develop` advanced to `b82ac0f` on 2026-09-19; this repository is also the active canonical skill source. | [source, `366c84e`] No authoring rule was found. Matches elsewhere only describe how skills inspect or reference commit messages. [measured] Recent non-merge history consistently uses Conventional Commit-shaped subjects such as `fix(trend-scan): ...`, `docs(coderabbit-response): ...`, and `chore(release): ...`. | [measured] Follow-up [claude-skills #116](https://github.com/brandonperfetti/claude-skills/issues/116) asks the repository to decide and record its own rule. |
| `brandonperfetti/github-commit-dashboard` | [measured] The live checkout is on `feature/harden-contribution-helpers` with uncommitted work; issue #1 was updated on 2026-08-30. | [source, `2a39ce9`] No `AGENTS.md`, `CLAUDE.md`, or `CONTRIBUTING.md` exists, and the tracked search returned no authoring rule. [measured] Recent subjects use short sentence-style descriptions, but their verb form is mixed. | [measured] Follow-up [github-commit-dashboard #3](https://github.com/brandonperfetti/github-commit-dashboard/issues/3) asks the repository to choose and record a local rule without disturbing the current worktree. |
| `brandonperfetti/brandonperfetti` | [measured] The non-archived profile repository's `master` advanced to `244928b` on 2026-03-26 and has a primary workspace checkout. | [source, `244928b`] `README.md` is the only owner document and contains no commit-subject rule. [measured] The two available owner subjects use different shapes: `Remove dynamic injection workflow.` and `feat: rebuild profile README with current Notion workspace data`. | [decision 2026-09-23, audit] No follow-up now. Two sparse, inconsistent subjects do not justify a new instruction file solely for this rule; revisit when regular feature delivery resumes. |

## Interim rule

Until every repository above has an explicit convention or a recorded decision
not to add one, an OpenClaw session working in a repository with no stated
commit-subject convention follows that repository's own observed history. It
does not import the retired machine-local R07 default
(`type(scope): description (#issue)`), `agent-working-agreements`' local rule, or
any other global default. When history is mixed, use the most recent comparable
non-merge subject and call out the ambiguity in the delivery record.

[source, issue #27] This audit and both follow-ups are explicitly non-blocking
for issues #23 and #24 and for the completed quiet cutover.
