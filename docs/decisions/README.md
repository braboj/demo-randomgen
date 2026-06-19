# Architecture Decision Records

This folder holds the project's Architecture Decision Records (ADRs) —
one significant decision per file. Each ADR captures the context, the
decision, the alternatives weighed, and the consequences, so the *why*
behind the architecture stays discoverable.

## Conventions

- **One decision per file**, named `NNN-slug.md` (zero-padded, e.g.
  `008-gunicorn-hardened-docker.md`).
- The human identifier is `AD-N` (matching the file number); it appears
  in the frontmatter `id` and the `# AD-N — Title` heading. Existing
  references to `AD-8`, `AD-11`, etc. elsewhere in the docs stay valid.
- **Frontmatter is required** — `id`, `status`, `date`, `category`,
  `supersedes`, `superseded_by`. See [TEMPLATE.md](TEMPLATE.md).
- `status` is one of `Proposed`, `Accepted`, `Superseded`.
- `category` is one of `architecture`, `api`, `tooling`, `deployment`,
  `docs`, `process`.
- **ADRs are immutable once accepted.** To change a decision, write a new
  ADR and set the old one's `status: Superseded` + `superseded_by`, with
  a reciprocal `supersedes` on the new one.

## Index

The canonical, human-readable index lives in
[arc42 §9 — Architecture Decisions](../arc42/09-architecture-decisions.md),
which links to every ADR in this folder. Update it when you add an ADR.

## Adding an ADR

1. Copy [TEMPLATE.md](TEMPLATE.md) to `NNN-slug.md` (next free number).
2. Fill in the frontmatter and the four sections.
3. Add a row to the [arc42 §9 index](../arc42/09-architecture-decisions.md).

See `docs/solid-ai-templates/templates/base/core/docs.md` for the
upstream convention this follows.

## History

AD-1 … AD-11 were formalized together on 2026-06-19, extracted verbatim
in substance from the inline summaries that previously lived in arc42 §9
(the decisions themselves predate this folder). AD-12 records the move.
