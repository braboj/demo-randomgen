---
id: "AD-1"
status: Accepted
date: 2026-06-19
category: architecture
supersedes: []
superseded_by: []
---

# AD-1 — src layout + application factory + blueprint

## Context

A module-level Flask `app` runs import-time side effects, makes the error
handler hard to isolate, and lets tests import the working tree instead of
the installed package. The project needed a structure that scales as more
API versions and modules are added, and that keeps business logic testable
without Flask.

## Decision

1. **src layout** — package under `src/randomgen/`.
2. **Application factory** — build the Flask app with a `create_app()`
   factory in `app.py`.
3. **Blueprint** — register routes via a Flask `Blueprint` (`bp`) in
   `routing.py`; handlers stay thin (parse → delegate → serialize).

## Alternatives considered

- **Module-level `app`** — rejected; import-time side effects, shared
  error handler, harder to test.
- **Flat (non-src) layout** — rejected; allows accidental imports of the
  working tree rather than the installed package.

## Consequences

- Each gunicorn worker builds its own app with no import side effects.
- The service (`endpoints.py`) and core (`core.py`) are
  framework-independent and unit-testable without Flask.
- Handlers remain declarative and thin.
