# 4. Solution Strategy

This chapter summarizes the fundamental decisions that shape the architecture.
Each decision maps to a quality goal from
[Chapter 1](01-introduction-and-goals.md) or a constraint from
[Chapter 2](02-architecture-constraints.md), cited by ID (e.g. T02, QG02)
rather than restated here. The significant decisions are recorded individually
in [Chapter 9](09-architecture-decisions.md).

## 4.1 Technology decisions

Within the Python and Flask platform (T01, T02), the implementation choices are:

- `scipy.stats.chi2` provides the Chi-Square CDF / p-value — a correct CDF is not
  worth reimplementing by hand (see [solution.md](../history/solution.md) §4;
  [AD-7](../decisions/007-chi-square-goodness-of-fit.md)).
- gunicorn serves the app in production, inside a hardened container: a non-root
  user on a single digest-pinned base image, so rebuilds are reproducible
  ([AD-8](../decisions/008-gunicorn-hardened-docker.md)).
- The standard-library `random` module does the sampling: fast, uniform, and
  dependency-free, and deliberately not cryptographic.

## 4.2 Decomposition into building blocks

A clear separation keeps the web framework, the service logic, and the
statistical primitives independent and testable:

- `app.py` — the `create_app()` application factory: builds the Flask app,
  registers the blueprint, and installs the single error handler.
- `routing.py` — a Flask blueprint (`bp`) with thin handlers that parse and
  validate query params and delegate to the service.
- `endpoints.py` — `RandomGenRestApi`, the stateless service logic, independent
  of Flask.
- `core.py` — two interchangeable generators (`RandomGenV1`, `RandomGenV2`)
  behind a shared abstract base (`RandomGenABC`).
- `histogram.py` / `hypothesis.py` — the `Histogram` and `ChiSquareTest`
  statistical helpers.
- `errors.py` — typed domain exceptions.

See the building-block view in [Chapter 5](05-building-block-view.md).

## 4.3 Approaches to key quality goals

Each goal (QG01–QG06) is defined in
[Section 1.2](01-introduction-and-goals.md).

| Quality goal | Strategy |
|--------------|----------|
| QG01 Correctness | Every generation response carries a Chi-Square report (statistic, p-value, df) plus expected vs. observed histograms, so fairness is observable. The test uses the explicit expected category domain, so categories observed zero times still contribute. |
| QG02 Reliability | Input is validated at two layers (service `validate_distribution` and generator `validate()`); a single `@app.errorhandler(Exception)` maps every failure to a JSON `{"error": ...}` response with the right status code. A `MAX_NUMBERS` cap bounds work per request. |
| QG03 Maintainability | src layout, app factory, blueprint, builder-style generators, typed signatures, `ruff` + `mypy`, and an 85% coverage gate enforced in CI. |
| QG04 Portability | A single digest-pinned, non-root Alpine Docker image runs locally, on Docker Hub, and on Render via `render.yaml`. |
| QG05 Compatibility | Versioned paths; `/api/v1` and `/api/v2` behavior is frozen — new behavior means a new version. The design-first OpenAPI contract pins the request/response shape. |
| QG06 Usability | A live Render demo, a browser UI at `/`, interactive API docs at `/docs`, and a one-command container (`docker run`) let an evaluator try the service in minutes. |

## 4.4 Organizational decisions

- `pyproject.toml` (PEP 621) is the single project descriptor, with `test` and
  `dev` extras, chosen over the older `setup.py` + `requirements.txt` split
  ([AD-2](../decisions/002-pyproject-ruff-mypy.md)).
- A branch-and-PR workflow on a protected `main` (O03), gated by CI (lint,
  type-check, coverage, gitleaks) before merge.
- arc42 (this documentation) is the architecture reference.
