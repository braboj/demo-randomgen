---
id: "AD-27"
status: Accepted
date: 2026-06-24
category: process
supersedes: []
superseded_by: []
---

# AD-27 — Persist 360 reviews as dated report + plan files under docs/review/

## Context

A whole-project 360-degree review was run on v0.19.0 before moving toward
v1.0. The review followed the `base-360` workflow template, which mandates
that audit results be persisted in the repository (agent memory is ephemeral
and invisible to other contributors). The template prescribes a single
`docs/360-audit.md` file holding a score-history table — one row per audit
with per-category grades and the issue references that audit spawned.

That model fits a recurring lightweight grade, not the artifact this review
produced: a ~32 KB findings report with `file:line` evidence, fixes, a
scope-excluded list, and a finding→issue map, plus a companion orchestration
plan documenting the method. There was no home in the docs tree for a dated
point-in-time assessment of this depth. `docs/reference/` holds the stable
contract and UI snapshots; `docs/history/` holds the original kata record;
neither is a fit for a recurring review.

## Decision

1. **Dedicated directory** — 360 reviews MUST be persisted under
   `docs/review/`, a new directory for dated, point-in-time project
   assessments.
2. **Paired files per review** — each review is stored as two files named by
   ISO date: `YYYY-MM-DD-360-review.md` (the findings report — scorecard,
   findings with `file:line` evidence and fixes, scope-excluded list, issue
   map) and `YYYY-MM-DD-360-plan.md` (the orchestration plan that produced it
   — dimensions, fan-out, verification protocol, scope guard).
3. **Self-contained, not a running table** — the report carries its own
   scorecard and overall grade; the project does NOT maintain a separate
   `docs/360-audit.md` score-history table while there is a single review.
   A lightweight history index MAY be added once two or more reviews exist
   and a cross-review comparison earns its keep.

## Alternatives considered

- **`docs/360-audit.md` running table (the template default)** — rejected;
  a one-row-per-audit summary table cannot hold a findings report with
  `file:line` evidence. The grade belongs in the report's scorecard, not a
  parallel file that would duplicate and drift from it.
- **Put the report under `docs/reference/`** — rejected; reference holds
  stable, current material (the REST contract, UI snapshots). A 360 review is
  a dated snapshot that goes stale by design, not a living reference.
- **Do not persist (leave in chat/memory)** — rejected; `base-360` requires
  persistence, and the issue backlog (#233–#242) needs a durable, linkable
  source of record.

## Consequences

- `docs/review/` is created and holds `2026-06-24-360-review.md` and
  `2026-06-24-360-plan.md`; future 360 reviews follow the same naming.
- `CLAUDE.md` §1.2 (project structure) lists `docs/review/`.
- This chapter's parent index (arc42 §9) gains the AD-27 row.
- The divergence from `base-360`'s single-file `docs/360-audit.md` model is a
  candidate for upstream feedback: the template should accommodate a rich
  per-review report, not only a score-history row.
- The end-of-session checklist's ADR trigger (new directory → ADR) is
  satisfied by this record.
