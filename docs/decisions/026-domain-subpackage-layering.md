---
id: "AD-26"
status: Accepted
date: 2026-06-23
category: architecture
supersedes: []
superseded_by: []
---

# AD-26 — Group the domain logic into a domain/ subpackage

## Context

`src/randomgen/` had grown to a dozen flat modules that belong to distinct
layers: the framework-free sampling logic (generators, histogram, Chi-Square
test, domain errors), the application orchestrator (`service.py`), the
presentation layer (the `blueprints/` package, `versions.py`, `openapi.py`), and
the composition root plus cross-cutting concerns (`app.py`, `config.py`,
`observability.py`). The flat layout hid those layers, so the package read as one
undifferentiated pile.

The service is stateless pure compute — no database, no message queue, no
third-party calls (arc42 §3.3). The forces that justify a full clean/hexagonal
scaffold (repositories, ports, use-case classes, DTOs, an infrastructure layer)
are therefore absent.

## Decision

1. **Extract a `domain/` subpackage** holding the framework-free core —
   `core.py` (generators), `histogram.py`, `hypothesis.py`, `errors.py`. The
   domain MUST depend on nothing in the application or presentation layers.
2. **Leave the other layers in place.** The presentation layer stays the
   existing `blueprints/` package, with `versions.py` and `openapi.py` beside
   it; `service.py` (application), `app.py` (composition root), `config.py`, and
   `observability.py` stay at the package root. `templates/`, `static/`, and
   `openapi.yaml` stay at the root as Flask convention / packaged data.
3. **Add no `api/` umbrella and no `infrastructure/` layer.** An `api/` package
   would collide with the existing `blueprints/` package (`blueprints/api.py`
   would read as `randomgen.api.blueprints.api`) and add packaging risk for
   `openapi.yaml`. An `infrastructure/persistence/` layer has nothing to hold
   while the service is stateless; if a database is ever brought into scope (an
   ADR amending §3.3), add it then — a documented escalation trigger, not built
   now.

This conforms to the Clean Architecture Dependency Rule — dependencies point
inward, presentation → application → domain — while deliberately omitting
ports-and-adapters, because there are no external resources to decouple from.
It is the minimal useful grouping rather than layering ahead of need.

## Alternatives considered

- **Full clean-architecture quartet** (`domain/` + `application/` + `api/` +
  `infrastructure/`) — rejected; `application/` and `infrastructure/` would hold
  one or two files each, and an empty persistence layer is ceremony without the
  forces that justify it.
- **A top-level `models/` folder** for a hypothetical database — rejected;
  persistence is infrastructure, not a top-level concern, and there is no
  database.
- **Leave the package flat** — rejected; the layers stay implicit and the
  package keeps reading as a pile.

## References

- Robert C. Martin, "The Clean Architecture" (2012), blog.cleancoder.com — the
  Dependency Rule and concentric layers.
- Robert C. Martin, *Clean Architecture* (Prentice Hall, 2017).
- Percival & Gregory, *Architecture Patterns with Python* (O'Reilly, 2020),
  cosmicpython.com — the Python take on DDD and ports-and-adapters, including
  when not to apply the full pattern.

## Consequences

- `domain/{core,histogram,hypothesis,errors}.py` replace the flat modules;
  importers (`service.py`, `versions.py`, `app.py`, `blueprints/api.py`) and the
  domain tests move to `randomgen.domain.*`. The HTTP/OpenAPI contract is
  unaffected.
- Docs that referenced the old module paths (CLAUDE.md, ONBOARDING, PLAYBOOK,
  arc42 §5/§8/§12) are updated.
- Grouping the presentation layer further (an `api/` umbrella, or moving
  `versions.py`/`openapi.py` under `blueprints/`) is left open as a possible
  follow-up; this decision groups only the domain.
