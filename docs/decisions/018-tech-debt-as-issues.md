---
id: "AD-18"
status: Accepted
date: 2026-06-21
category: docs
supersedes: []
superseded_by: []
---

# AD-18 — Track technical debt as labeled issues, indexed from arc42 §11.2

## Context

arc42 §11.2 described each item of technical debt inline. Inline descriptions
drift: when debt is resolved, the prose and the work live in two places, so the
chapter goes stale and misreports what is actually outstanding.

## Decision

Track each actionable item of technical debt as a GitHub issue labeled
`tech-debt`. arc42 §11.2 becomes an index — a short name per item plus a live
status badge (shields.io) linking to the issue, and a link to the full
`tech-debt` issue list as the source of truth. §11.1 risks stay inline; they are
accepted boundaries, not work to track.

## Alternatives considered

- **Keep inline descriptions** — rejected; they go stale as debt is resolved.
- **A single link to the issue list, no per-item rows** — rejected; loses the
  at-a-glance summary an evaluator expects in the chapter.

## Consequences

- Debt status is live: closing an issue flips its badge to closed with no doc edit.
- §11.2 still needs a row when new debt is filed; the full-list link covers
  anything not yet rowed.
- Adds a `tech-debt` topic label (alongside the standard type/priority labels)
  and a rendering dependency on shields.io for the badges.
