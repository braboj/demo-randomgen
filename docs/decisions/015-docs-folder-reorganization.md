---
id: "AD-15"
status: Accepted
date: 2026-06-19
category: docs
supersedes: []
superseded_by: []
---

# AD-15 — Reorganize the docs/ folder by purpose

## Context

`docs/` grew unevenly. Alongside the three standard documents the docs
template blesses at the root (`ONBOARDING.md`, `PLAYBOOK.md`,
`dev-journal.md`) sat four project-specific files with no grouping —
`problem.md` and `solution.md` (the original kata statement and its
historical solution journal), and `rest_api.md` and `ui-snapshots.md`
(reference material). Images were split across two parallel trees:
`docs/assets/` (Draw.io source + distribution plots) and
`docs/images/ui/` (home-page screenshots), so there was no single place
to find an asset.

## Decision

1. **Group reference docs** — `rest_api.md` and `ui-snapshots.md` MUST
   live under `docs/reference/`.
2. **Group historical docs** — `problem.md` and `solution.md` MUST live
   under `docs/history/`. They are a historical record (the kata and its
   solving journal), not a current spec.
3. **One image tree** — all images live under `docs/assets/`: Draw.io
   sources in `assets/drawio/`, raster images in `assets/images/`, and
   home-page screenshots in `assets/images/ui/` (moved from
   `docs/images/`). `docs/images/` is removed.
4. **Standard docs stay at the root** — `ONBOARDING.md`, `PLAYBOOK.md`,
   and `dev-journal.md` keep their template-mandated location.

```
docs/
  ONBOARDING.md  PLAYBOOK.md  dev-journal.md
  arc42/         decisions/
  reference/     +-- rest_api.md
                 +-- ui-snapshots.md
  history/       +-- problem.md
                 +-- solution.md
  assets/        +-- drawio/system_design.drawio.png
                 +-- images/
                       +-- *_distribution.png
                       +-- ui/01_initial.png ...
```

## Alternatives considered

- **Keep the flat layout** — rejected; four ungrouped top-level files and
  two image trees make the folder hard to scan and asset homes ambiguous.
- **Move the standard docs into subfolders too** — rejected; the docs
  template fixes `ONBOARDING.md` / `PLAYBOOK.md` / `dev-journal.md` at the
  `docs/` root for predictability.
- **Fix the stale content in `solution.md` during the move** — rejected;
  out of scope for a structural change. The staleness is already recorded
  as D1 in arc42 §11; `solution.md` stays a historical journal.

## Consequences

- All inbound links to the moved files (arc42 chapters, ADR-006/007/010,
  README, PLAYBOOK, dev-journal) are repointed in the same PR.
- Image references inside `solution.md` and `ui-snapshots.md`, and the
  output path in `scripts/capture_ui_snapshots.py`, are updated to the
  consolidated `assets/images/` tree.
- `README.md` §1.2 (project structure) reflects the new `docs/` layout.
- New reference material goes under `docs/reference/`; new historical
  notes under `docs/history/`.
