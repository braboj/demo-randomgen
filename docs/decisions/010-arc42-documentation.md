---
id: "AD-10"
status: Accepted
date: 2026-06-19
category: docs
supersedes: []
superseded_by: []
---

# AD-10 — arc42 architecture documentation

## Context

The project needs a standard, navigable architecture reference grounded in
the code. A previous MkDocs site added a build step and generated pages
that had to be maintained alongside the code.

## Decision

Document the architecture with the **arc42** template (the files under
`docs/arc42/`), replacing the previous MkDocs documentation site
(`mkdocs.yml`, the generated reference/test pages, and the Pages workflow
were removed in v0.6.0).

## Alternatives considered

- **MkDocs documentation site** — rejected; build step plus generated
  pages to keep in sync, for a reference that renders fine as plain
  Markdown on GitHub.

## Consequences

- Each section is one Markdown file with Mermaid diagrams, cross-linked to
  the code and the remaining hand-written docs
  (`rest_api.md` (since retired — see AD-16), [problem.md](../history/problem.md),
  [solution.md](../history/solution.md)).
- No build or publish step.
