# 4. Solution Strategy

This chapter summarizes the fundamental decisions that shape the architecture.
Each decision maps to a quality goal or a constraint, cited by ID (e.g. T02,
QG02) rather than restated here. The significant decisions are recorded
individually as architecture decision records (ADRs).

## 4.1 Technology decisions

| Decision | Rationale |
| --- | --- |
| `scipy.stats.chi2` for the Chi-Square CDF / p-value | A correct CDF is not worth reimplementing by hand ([solution.md](../history/solution.md) §4; [AD-7](../decisions/007-chi-square-goodness-of-fit.md)). |
| gunicorn as the production WSGI server, in a hardened container | A non-root user on a single digest-pinned base image, so rebuilds are reproducible ([AD-8](../decisions/008-gunicorn-hardened-docker.md)). |
| Standard-library `random` for sampling | Fast, uniform, and dependency-free; deliberately not cryptographic. |

## 4.2 Decomposition into building blocks

A clear separation keeps the web framework, the service logic, and the
statistical primitives independent and testable:

| Building block | Role |
| --- | --- |
| `app.py` | `create_app()` application factory — builds the Flask app, registers the blueprint, installs the single error handler. |
| `routing.py` | Flask blueprint (`bp`) with thin handlers that parse and validate query params and delegate to the service. |
| `endpoints.py` | `RandomGenRestApi` — the stateless service logic, independent of Flask. |
| `core.py` | Two interchangeable generators (`RandomGenV1`, `RandomGenV2`) behind a shared abstract base (`RandomGenABC`). |
| `histogram.py` / `hypothesis.py` | The `Histogram` and `ChiSquareTest` statistical helpers. |
| `errors.py` | Typed domain exceptions. |

## 4.3 Approaches to key quality goals

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
