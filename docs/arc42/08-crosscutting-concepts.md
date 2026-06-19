# 8. Crosscutting Concepts

Concepts that apply across multiple building blocks.

## 8.1 Statelessness

The service keeps **no mutable state between requests**. `RandomGenRestApi` is a
stateless service object, instantiated once (`rest_api` in `routing.py`) and
shared safely across concurrent requests and gunicorn workers. The distribution
is supplied **per request** and defaults to `DEFAULT_NUMBERS` /
`DEFAULT_PROBABILITIES`. A fresh generator is created inside
`randomgen_endpoint` for each call, so no generator state is shared. This is
what makes horizontal scaling trivial ([Section 7](07-deployment-view.md)).

## 8.2 Input validation (two layers)

| Layer | Where | Checks |
|-------|-------|--------|
| **Syntactic** | `routing.py` (`quantity_from_query`, `parse_dist_pairs`, `distribution_from_query`) | `numbers` is an integer (else `RandomGenQuantityError`); `dist` items are `value:probability` and numeric (else `RandomGenDistFormatError`). |
| **Semantic** | `endpoints.RandomGenRestApi.validate_distribution` + generator `validate()` | Type is list/tuple, non-empty, equal length, non-negative weights, `round(sum, 3) == 1`; quantity within `1..MAX_NUMBERS`. |

Probability sums are compared with `round(sum, 3) == 1` to tolerate
floating-point error (see [solution.md](../history/solution.md) §8 — older Python
versions surfaced rounding errors).

## 8.3 Error handling (the JSON error contract)

A single `@app.errorhandler(Exception)` (`handle_error` in
[`app.py`](../../src/randomgen/app.py)) is the **deliberate API error
boundary** — not a catch-all in business logic. It maps:

- `RandomGenError` → **400** `{"error": str(e)}`
- Werkzeug `HTTPException` → its own `e.code` with `{"error": e.description}`
- anything else → **500** `{"error": str(e)}`

Domain code raises only the **specific** typed exceptions in
[`errors.py`](../../src/randomgen/errors.py) (no bare `except`), each carrying a
fixed human-readable `MESSAGE`. This keeps the `{"error": ...}` contract uniform
across all endpoints — see [rest_api.md](../reference/rest_api.md).

## 8.4 Quality reporting (Chi-Square)

Every generation response includes a `quality` block with a `chi_square_test`
(`is_null`, `chi_square`, `p_value`, `df`) plus `expected_histogram` and
`observed_histogram`. The expected histogram is derived from the requested
probabilities; the observed histogram is computed by `Histogram` from the
sample. `ChiSquareTest` uses the **explicit expected category domain** so a
category observed zero times still contributes `(0 − expected)² / expected`
to the statistic. `is_null` is `True` when `p_value > 0.05`. Larger samples
yield a more meaningful verdict (hence `DEFAULT_QUANTITY = 1000`).

## 8.5 API design and versioning

- HTTP `GET`-only, query-parameter driven, JSON responses via `jsonify`.
- **Versioned paths** (`/api/v1`, `/api/v2`) are a frozen public contract:
  never change an existing version's behavior — add a new version instead.
- The two versions differ **only** in the generator implementation
  (`RandomGenV1` inverse-CDF vs. `RandomGenV2` `random.choices`); parameters,
  response shape, and status codes are identical.

## 8.6 Fluent builder pattern

`RandomGenABC`, `Histogram`, and `ChiSquareTest` share a builder-style fluent
interface: setter/validator methods return `self` for chaining
(`set_*().validate().calc()`), while producing/consuming methods (`next_num`,
the assembled response) are not chained. This convention is recorded in the
design journal ([solution.md](../history/solution.md) §13).

## 8.7 Security

- **No secrets in the repo**; CI runs a **gitleaks** secret scan.
- Container runs **non-root** (`appuser`) on a **digest-pinned** base image.
- **Debug mode is always off** (gunicorn in the image; the local `flask run`
  keeps debug off for local runs).
- `/health` needs no authentication; there is no auth layer (out of scope).
- **Not cryptographically secure:** sampling uses Python's `random`
  (Mersenne-Twister) and must not be used for security-sensitive randomness.

## 8.8 Build, tooling, and testing

- **`pyproject.toml`** (PEP 621) is the single descriptor, with `test` and
  `dev` extras; `src` layout on the path.
- **`ruff`** (lint rules `E,W,F,I,UP,B,C4,SIM`, single-quote format) and
  **`mypy`** (`ignore_missing_imports` for stub-less `scipy`) are the gates.
- **`pytest`** with markers `unit` / `integration` / `e2e`; one test file per
  module under `tests/`; **85% coverage gate** in CI.

See [Section 2](02-architecture-constraints.md) for the binding constraints and
[Section 10](10-quality-requirements.md) for quality scenarios.
