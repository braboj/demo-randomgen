---
id: "AD-19"
status: Accepted
date: 2026-06-21
category: docs
supersedes: []
superseded_by: []
---

# AD-19 — Remove the ADR-folder README; conventions move to the PLAYBOOK

## Context

`docs/decisions/README.md` held the ADR conventions, but GitHub renders a folder
README below the file list — often below the fold — which buries it behind a
landing page in front of records that are meant to be opened directly. AD-12
established the folder with this README; this refines that layout.

## Decision

Remove `docs/decisions/README.md` and move its conventions (file naming, the
frontmatter schema, the status/category vocabularies, the immutability rule, and
the steps to add an ADR) into the PLAYBOOK §4.3. The ADR files stay directly
clickable in the folder listing, and arc42 §9 remains the canonical index.

## Alternatives considered

- **Keep the README** — rejected; it buries the records behind a below-fold
  landing page and duplicates conventions better kept with the other operational
  guidance in the PLAYBOOK.

## Consequences

- The decisions folder shows ADR files directly, with no README landing page.
- ADR conventions live in one operational place (the PLAYBOOK), referenced from
  §9 and `TEMPLATE.md`.
- Refines AD-12's folder layout (the folder no longer holds a README); AD-12's
  core decision — a dedicated folder with arc42 §9 as the index — still stands.
