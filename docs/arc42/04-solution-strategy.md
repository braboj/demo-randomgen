# 4. Solution Strategy

This section summarizes the fundamental decisions that shape the architecture.
Each maps a quality goal or constraint from
[Section 1](01-introduction-and-goals.md) and
[Section 2](02-architecture-constraints.md) to a concrete approach. The
significant decisions are recorded individually in
[Section 9](09-architecture-decisions.md).

## 4.1 Technology decisions

- **Flask 3.x + gunicorn** for the HTTP surface. Flask keeps the web layer
  thin; gunicorn is the production WSGI server inside the container.
- **`scipy.stats.chi2`** for the Chi-Square CDF / p-value, because a correct
  CDF implementation is non-trivial (see [solution.md](../solution.md) §4).
- **Python `random`** standard library for sampling — fast, uniform, no
  dependency. (Explicitly not for cryptographic use.)
- **Pure compute, no database** — every request is self-contained, so there is
  nothing to persist.

## 4.2 Decomposition into building blocks

A clear separation keeps the web framework, the service logic, and the
statistical primitives independent and testable:

- **`app.py`** — the `create_app()` **application factory**: builds the Flask
  app, registers the blueprint, and installs the single error handler.
- **`routing.py`** — a Flask **Blueprint** (`bp`) with **thin handlers** that
  parse/validate query params and delegate to the service.
- **`endpoints.py`** — `RandomGenRestApi`, the **stateless service logic**,
  independent of Flask.
- **`core.py`** — two interchangeable generators (`RandomGenV1`, `RandomGenV2`)
  behind a shared abstract base (`RandomGenABC`).
- **`histogram.py`** / **`hypothesis.py`** — the `Histogram` and
  `ChiSquareTest` statistical helpers.
- **`errors.py`** — typed domain exceptions.

See the building-block view in [Section 5](05-building-block-view.md).

## 4.3 Approaches to key quality goals

| Quality goal | Strategy |
|--------------|----------|
| **Statistical correctness** | Every generation response carries a Chi-Square report (statistic, p-value, df) plus expected vs. observed histograms, so fairness is observable. The test uses the explicit expected category domain so categories observed zero times still contribute. |
| **Reliability / robustness** | Validate input at two layers (service `validate_distribution` and generator `validate()`); a single `@app.errorhandler(Exception)` maps every failure to a JSON `{"error": ...}` response with the right status code. A `MAX_NUMBERS` cap bounds work per request. |
| **Maintainability / clarity** | src layout, app factory, blueprint, builder-style fluent generators, typed signatures, `ruff` + `mypy`, and an 85% coverage gate enforced in CI. |
| **Portability** | A single digest-pinned, non-root Alpine Docker image runs locally, on Docker Hub, and on Render via `render.yaml`. |
| **API stability** | Versioned paths; `/api/v1` and `/api/v2` behavior is frozen — new behavior means a new version. |

## 4.4 Organizational decisions

- **`pyproject.toml` (PEP 621)** as the single project descriptor, with `test`
  and `dev` extras, superseding `setup.py` + `requirements.txt`.
- **Branch + PR workflow** with CI gates (lint, type-check, coverage,
  gitleaks) before merge to protected `main`.
- **arc42** (this documentation) as the architecture reference.
