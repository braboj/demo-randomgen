---
id: "AD-14"
status: Accepted
date: 2026-06-19
category: process
supersedes: []
superseded_by: []
---

# AD-14 — Adopt the solid-ai-templates issue label standard

## Context

GitHub issues used the default labels (`enhancement`, `question`,
`documentation`, …) with no priority dimension and misleading types (e.g.
`question` applied to spikes, `enhancement` to tasks). The vendored
solid-ai-templates submodule defines a standard — `platform/github.md` plus its
ADR-002 — of 12 labels split into type / priority / triage, with every issue
carrying exactly one type, one priority, and a milestone.

## Decision

1. **Adopt the 12-label scheme** — type (`bug` / `epic` / `task` / `spike` /
   `incident`), priority (`P0`–`P4`), triage (`duplicate` / `wontdo`), using the
   GitHub colours from `platform/github.md`.
2. **Every issue MUST carry one type + one priority label and a milestone**
   (`Backlog`, or `Expedite` for small out-of-cycle work).
3. **Retire GitHub's default labels** (`enhancement`, `question`,
   `documentation`, `good first issue`, `help wanted`, `invalid`, `wontfix`);
   keep the Dependabot / CI labels (`dependencies`, `github_actions`, `python`).

## Alternatives considered

- **Keep GitHub defaults** — rejected; no priority dimension and misleading
  type labels.
- **A bespoke randomgen scheme** — rejected; the submodule standard already
  exists and keeps this repo consistent with the wider template system.

## Consequences

- The one-line rule lives in [CLAUDE.md](../../CLAUDE.md) §2.1; the full
  definition stays upstream, so the colour table is not duplicated here.
- Surfaced an upstream inconsistency: `platform/github.md` and the submodule's
  own `CLAUDE.md` §2.2 disagree on the `task` / `epic` colours — flagged for the
  submodule via issue #110.
