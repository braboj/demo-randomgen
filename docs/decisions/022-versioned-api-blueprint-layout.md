---
id: "AD-22"
status: Accepted
date: 2026-06-22
category: architecture
supersedes: []
superseded_by: []
---

# AD-22 — Versioned-API package layout: a blueprint factory over a version registry

## Context

The package is a flat `src/randomgen/` layout with a single route module holding
every route, including the two versioned endpoints. The two API generations
differ only in the injected generator class — parameters, validation, response
shape, and status codes are identical (parallel implementations of one contract,
versioned by path). Preparing for a 1.0 contract raised the question of how the
package should be organized to add further generations without the route layer
accumulating near-duplicate handlers or reaching into the generator classes
directly.

A per-version directory tree (`api/v1/`, `api/v2/`, each with its own routes)
was considered. Because the generations share their entire contract, such a tree
would host byte-identical handlers — duplication presented as structure — and
would imply a contract divergence between versions that does not exist. In a
codebase that doubles as a portfolio piece, premature generalization is a
negative signal, not a positive one.

## Decision

1. **Flat, role-named package.** Keep the domain and contract modules
   (`core`, `service`, `errors`, `histogram`, `hypothesis`, `openapi`) as flat
   modules. Do NOT introduce per-version subpackages while versions share one
   contract.

2. **Version registry.** Add one module mapping each generation to its generator
   class — the single place a new generation is registered:

   ```python
   API_VERSIONS: dict[str, type[RandomGenABC]] = {"v1": RandomGenV1, "v2": RandomGenV2}
   ```

3. **Blueprints split by audience.** Group HTTP routes into a `blueprints/`
   package: a `web` blueprint for the unversioned, browser- and ops-facing routes
   (`/`, `/docs`, `/openapi.json`, `/health`), and a parametric API blueprint
   built by a factory.

4. **API blueprint factory.** `make_api_blueprint(version, generator)` returns a
   `Blueprint` mounted at `url_prefix=f"/api/{version}"` whose handler delegates
   to the shared service. The application factory registers one API blueprint per
   registry entry, so adding a generation is a one-line registry edit with no new
   handler code.

5. **Version selection stays in the API layer, off `core`.** The registry is the
   only module that imports the generator classes; the factory receives its
   generator as an argument and the web blueprint never imports `core`. The route
   layer depends on the registry and the service, not on `core` directly. Version
   selection MUST NOT move into the domain service — an API generation is a
   transport concept and the service stays version-agnostic. (Resolves the
   route-to-core coupling raised in spike #133.)

6. **Escalation trigger (documented, not built).** A future generation whose
   *contract* diverges (different parameters or response shape) graduates to its
   own explicit module under the API package (e.g. `blueprints/api/v3.py`) with
   its own handler and schema — the per-version layout, applied only when a
   genuine divergence earns it. Until then, the factory serves every generation.

## Alternatives considered

- **Per-version directory tree now** (`api/v1/`, `api/v2/`) — rejected; the
  generations share one contract, so it would duplicate identical handlers and
  imply a divergence the path-versioning model explicitly denies. Premature
  generalization, and a poor signal in a portfolio codebase.
- **Role-based subpackages** (`web/`, `core/`, `contract/`) — rejected for now;
  import churn across tests, scripts, docs, and diagrams for marginal benefit at
  the current size (~1.3k LOC).
- **Push version selection into the service** (a version key, or
  `randomgen_v1()`/`randomgen_v2()` methods) — rejected; leaks the API-versioning
  concept into the framework-independent domain service.
- **Keep the route module importing `core` directly** — accepted as defensible
  layering (the API layer owns version selection), but the registry supersedes it:
  same ownership, with a single named seam and the route modules freed from
  `core`.

## Consequences

- Adding an API generation is one registry line; the route layer carries no
  per-version duplication.
- The factory captures its generator as a function parameter (not a loop
  variable), avoiding late-binding closure bugs.
- Shared request defaults and limits consolidate with the service rather than the
  route layer.
- Implementation is deferred to a follow-up issue; until it lands the package
  keeps the flat route module. Arc42 §5 (building blocks + dependency diagram) is
  updated as part of that implementation, not by this decision.
