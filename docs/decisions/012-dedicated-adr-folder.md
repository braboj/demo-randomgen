---
id: "AD-12"
status: Accepted
date: 2026-06-19
category: docs
supersedes: []
superseded_by: []
---

# AD-12 — Dedicated docs/decisions/ folder with arc42 §9 as the index

## Context

Architectural decisions were recorded only as inline summaries in arc42
§9. PLAYBOOK §4.3 and the upstream `docs.md` convention already prescribe
ADRs as `docs/decisions/NNN-slug.md`, but the folder did not exist, so the
decisions were not individually linkable, diffable, or supersedable.

## Decision

1. **One file per decision** — record each ADR as `docs/decisions/NNN-slug.md`
   using [TEMPLATE.md](TEMPLATE.md).
2. **Preserve identifiers** — keep the `AD-N` identifiers; extract
   AD-1 … AD-11 from arc42 §9 with their content unchanged in substance.
3. **arc42 §9 becomes an index** — a table linking to each ADR rather than
   holding the full decision text.

## Alternatives considered

- **Keep ADRs inline in arc42 §9** — rejected; not individually linkable
  or diffable, and diverges from the documented `docs/decisions/`
  convention.

## Consequences

- `docs/decisions/` holds a `README.md`, `TEMPLATE.md`, and one file per
  ADR.
- [arc42 §9](../arc42/09-architecture-decisions.md) is now an index and
  must gain a row whenever an ADR is added.
- New ADRs are authored from `TEMPLATE.md`; PLAYBOOK §4.3 points here.
- AD-1 … AD-11 carry `date: 2026-06-19` (the formalization date); the
  decisions themselves predate this folder.
