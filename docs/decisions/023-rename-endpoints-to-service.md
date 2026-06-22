---
id: "AD-23"
status: Accepted
date: 2026-06-22
category: architecture
supersedes: []
superseded_by: []
---

# AD-23 — Rename endpoints.py to service.py and RandomGenRestApi to RandomGenService

## Context

`endpoints.py` holds the stateless service class that orchestrates a request:
validate the distribution, build the generator, bound the quantity, draw the
sample, assemble the response. It contains no HTTP endpoints — the actual routes
live in the route layer. A reader reasonably expects a module named "endpoints"
to hold the routes, so the name works against the layering it is meant to express;
arc42 §5 has to explain around it. The class name `RandomGenRestApi` carries the
same mismatch: the REST API is the route layer, not this class.

The name is an internal Python identifier, not part of the HTTP or OpenAPI
contract, so renaming has no client-visible effect. Before a 1.0 freeze is the
right moment to correct it, while the import surface is still small.

## Decision

1. **Rename the module** `endpoints.py` → `service.py`.
2. **Rename the class** `RandomGenRestApi` → `RandomGenService`.
3. Update all importers (route layer, tests) and documentation references; the
   module-level defaults and limits move with the service.

## Alternatives considered

- **Rename the module only**, keep `RandomGenRestApi` — rejected; leaves the same
  misnomer on the class (it is not the REST API).
- **No rename** — rejected; the name keeps fighting the layering and forces the
  docs to caveat it.

## Consequences

- The service layer is named for what it holds; arc42 §5 no longer needs a
  clarifying aside.
- Import churn is contained: the route layer, three test modules
  (`test_endpoints`, `test_openapi`, `test_api_contract`), and doc references.
  The HTTP/OpenAPI contract is unaffected.
- Implementation is deferred to a follow-up issue, coordinated with the AD-22
  restructure since both touch the route layer.
