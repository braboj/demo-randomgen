---
id: "AD-13"
status: Accepted
date: 2026-06-19
category: docs
supersedes: []
superseded_by: []
---

# AD-13 — Code-built OpenAPI spec served as interactive docs at /docs

## Context

The service had no machine-readable API description and no interactive
reference. The public API is small — two GET endpoints (`/api/v1/randomgen`,
`/api/v2/randomgen`) plus `/health` — with a contract frozen by AD-5, so it
changes rarely. The options ranged from a full schema framework that
generates everything to a hand-maintained specification document.

## Decision

1. **Spec built in code** — describe the API with an OpenAPI 3.1 document
   assembled in `randomgen/openapi.py` (`build_spec`), parameterized by the
   live `__version__`, default quantity, and maximum quantity.
2. **Served and rendered** — expose the document at `GET /openapi.json` and
   render it interactively at `GET /docs` with ReDoc.
3. **Drift guard** — a unit test asserts that every `/api` route on the
   blueprint appears in the spec, so an undocumented endpoint fails CI.

## Alternatives considered

- **flask-smorest (MethodView + marshmallow)** — rejected for now; a routing
  refactor and two runtime dependencies to document two endpoints, and it
  overlaps with the still-undecided `src/` layout (#103). Revisit if the API
  grows or once the layout is settled.
- **apispec docstring annotations** — rejected; adds a dependency and moves
  the spec into route docstrings with a similar drift profile to a code-built
  spec but less cohesion.
- **Hand-written static `openapi.yaml`** — rejected; cannot reference the live
  constants and would drift without the route-coverage test anyway.

## Consequences

- No new runtime Python dependency; the thin route handlers (AD-1) are
  unchanged.
- ReDoc is loaded from a CDN (`cdn.redocly.com/redoc/latest`). Vendoring the
  bundle or pinning it with subresource integrity is a possible hardening
  follow-up.
- `/docs` and `/openapi.json` are unversioned utility endpoints, outside the
  `/api/v1` and `/api/v2` contract.
- A new `/api` endpoint MUST be added to `build_spec` or the drift-guard test
  fails.
