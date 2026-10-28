# GitHub paths

This procedure carries mechanics for a rule in
[`../AGENT-WORKING-AGREEMENTS.md`](../AGENT-WORKING-AGREEMENTS.md); it never overrides Parts A–B,
and a rule here that contradicts one there is the rule that is wrong. The text below was moved here
verbatim on 2026-10-27; "above" and "below" in it refer to the agreement section it implements.

**Trigger:** An agent is about to create, link, close or relabel an issue, open or update a PR, or
call the GitHub API through the MCP or Kody.

**Owner:** The orchestrator for tracker writes; the delivery owner for PR mechanics.

**Implements:** A7 — GitHub paths.

**Stop:** A create-then-link error: read the current state before any retry.

---

- **`gh` CLI** — what the skills use (issues, sub-issues, PRs). Primary for skill-driven work.
- **GitHub MCP** — the read/access layer and PR orchestration. **Its write tools (`push_files`,
  `create_or_update_file`) never author commits** — they bypass the local clone in both modes.
- **Kody's `@brandonperfetti/github` package** — the GitHub REST/GraphQL API for issues, PRs,
  checks, PR status and merge previews, for any client with Kody connected. **It never authors
  commits**, in both modes, for the GitHub MCP's reason: it bypasses the local clone. **Its
  `confirm: true` is per call and is not B1's per-batch approval** — it is the agent confirming
  its own call, not Brandon reviewing a batch — so in attended mode a Kody write is one of the
  API writes B1 allows no routing around. **The token it uses is fine-grained and scoped per
  repository, with one `secretName` per organisation**, because a call's reach is its token's, so
  the owner a call names matters as much as its `confirm: true`; **every call passes
  `secretName`**, because the package otherwise defaults to an OAuth lane, which may not be
  connected and, where it is, would leave two credentials able to serve one call with nothing
  showing which did. Where Kody is not connected, use `gh` or the GitHub MCP. How a client names
  the Kody tools is its client file's to record (Brandon, 2026-10-12).
- **On any create-then-link error, read the current state before retrying** — the create may have
  landed. GitHub's sub-issue cap errors *after* creating and parenting; blind retries burn issue
  numbers and mint duplicates. [learnings: 2026-09-12 wave-8 §3]
- **Tracker** = GitHub Issues + the user-level Projects board (`users/brandonperfetti/projects/2`).
  Its intake is a repository's own `add-to-project` workflow,
  `.github/workflows/add-to-project.yml`, which adds issues only and needs the `ADD_TO_PROJECT_PAT`
  repository secret, set by the repository owner. A repository joins the board's intake once that
  workflow is on its default branch, where issue events run it; the `setup-board-intake` skill
  installs it, once per repository. "In Review" is a board Status the orchestrator moves by hand —
  at PR time in autonomous mode (B2's review loop), and at commit time in attended mode, where no PR
  exists when a delivery is reviewed.
