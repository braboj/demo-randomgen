# 1. Introduction and Goals

RandomGen is a small Flask REST API that draws random numbers from a
configurable **discrete distribution** and reports, on every response, how well
the drawn sample matches the requested distribution using a **Chi-Square
goodness-of-fit test** (implemented with `scipy`'s `chi2`). It exists to
demonstrate and sanity-check weighted random sampling: a caller asks for *N*
draws from a distribution and gets back both the sample and an objective
fairness verdict.

The original assignment is captured in [problem.md](../history/problem.md): implement a
`next_num()` that returns numbers roughly with their initialized probabilities,
with a minimal but effective test suite, "as if it was going to be shipped as
part of a production system." The design journal is in
[solution.md](../history/solution.md).

## 1.1 Requirements overview

| # | Requirement | Where realized |
|---|-------------|----------------|
| R1 | Draw numbers so that, over many calls, outcomes match the configured probabilities. | `RandomGenV1` / `RandomGenV2` in [`core.py`](../../src/randomgen/core.py) |
| R2 | Two interchangeable generator implementations exposed side by side. | `/api/v1/randomgen`, `/api/v2/randomgen` |
| R3 | A default distribution, overridable **per request** (`[-1,0,1,2,3]` / `[0.01,0.3,0.58,0.1,0.01]`). | `DEFAULT_NUMBERS` / `DEFAULT_PROBABILITIES` in [`endpoints.py`](../../src/randomgen/endpoints.py) |
| R4 | Report sample fairness with a Chi-Square test (statistic, p-value, df, expected vs. observed histograms). | `ChiSquareTest` in [`hypothesis.py`](../../src/randomgen/hypothesis.py), `Histogram` in [`histogram.py`](../../src/randomgen/histogram.py) |
| R5 | Validate input and return well-defined HTTP status codes with a stable JSON error contract. | `handle_error` in [`app.py`](../../src/randomgen/app.py), `errors.py` |
| R6 | Ship as a portable, self-contained Docker image runnable anywhere Docker runs. | [`Dockerfile`](../../Dockerfile), [`render.yaml`](../../render.yaml) |

See [Section 3](03-context-and-scope.md) for scope boundaries and
[rest_api.md](../reference/rest_api.md) for the full endpoint contract.

## 1.2 Quality goals

| Priority | Quality goal | Motivation |
|----------|--------------|------------|
| 1 | **Statistical correctness** | The whole point is fair sampling; the Chi-Square report makes correctness observable on every call. |
| 2 | **Reliability / robustness** | Bad input must fail predictably (HTTP 400 + JSON `{"error": ...}`), never crash a worker. |
| 3 | **Maintainability / clarity** | Exemplary, production-grade code: src layout, app factory, blueprint, thin handlers, typed and linted (`ruff` + `mypy`), 85% coverage gate. |
| 4 | **Portability** | One digest-pinned, non-root Alpine image runs locally, on Docker Hub, and on Render. |
| 5 | **API stability** | Versioned paths (`/api/v1`, `/api/v2`) are a public contract that never changes behavior. |

These are detailed as scenarios in [Section 10](10-quality-requirements.md).

## 1.3 Stakeholders

| Role | Concern |
|------|---------|
| API consumers / developers | A simple, self-contained service to demonstrate and sanity-check weighted random sampling. |
| Maintainer (Branimir Georgiev) | Exemplary, testable, low-maintenance code; stable public API. |
| Reviewers / CI | Lint, type, coverage, and secret-scan gates pass before merge. |
| Operators (Render / Docker Hub users) | A container that starts, self-reports health, and runs unprivileged. |

> **Not a goal:** cryptographically secure randomness. The generators use
> Python's `random` module (a Mersenne-Twister PRNG) and must not be used for
> security-sensitive purposes — see [Section 2](02-architecture-constraints.md).
