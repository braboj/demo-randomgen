# 8. Crosscutting Concepts

Concepts that apply across multiple building blocks.

## 8.1 Sampling model (domain)

RandomGen models a [discrete distribution](12-glossary.md): a fixed set of
outcomes, each with a weight, the weights summing to one. A request supplies such
a distribution — or falls back to a built-in default — and asks for a sample of a
given size.

The sample is drawn by one of two interchangeable strategies behind a single
response contract. One accumulates the weights into a running total and looks up
each random draw against it; the other delegates to the standard library's
weighted choice. The caller picks between them by API version, and both return
the same shape. Each response then grades its own sample against the requested
weights with a goodness-of-fit test, so every result carries a fairness verdict.

| Concept | Implementation |
| --- | --- |
| Inverse-CDF sampling | `RandomGenV1` — `/api/v1/randomgen` |
| Standard-library sampling | `RandomGenV2` (`random.choices`) — `/api/v2/randomgen` |
| Goodness-of-fit check | `ChiSquareTest` (`scipy.stats.chi2`) |

## 8.2 Statelessness

The service keeps no mutable state between requests. A single REST service object
is created once per process and shared safely across concurrent requests and
gunicorn workers. Each request carries its own distribution — or falls back to the
built-in default — and a fresh generator is created for that call, so no generator
state is shared. Because nothing persists between calls, the service scales
horizontally with no coordination ([Chapter 7](07-deployment-view.md)).

| Concept | Implementation |
| --- | --- |
| Shared service object | `RandomGenRestApi` (`rest_api` in `routing.py`) |
| Per-request generator | created in `randomgen_endpoint` |
| Default distribution | `DEFAULT_NUMBERS` / `DEFAULT_PROBABILITIES` |

## 8.3 Input validation (two layers)

Input is validated in two layers. The syntactic layer parses the query
parameters and rejects anything malformed — a non-integer quantity, or
distribution pairs that are not well-formed numeric values and probabilities. The
semantic layer then validates the parsed distribution as a whole: outcomes and
weights of equal, non-empty length, non-negative weights that sum to one, and a
quantity within the allowed bound. Each layer raises a specific typed error, so a
caller always learns which rule failed. Probability sums are compared with a small
rounding tolerance, because older Python versions surfaced floating-point error
(see [solution.md](../history/solution.md) §8).

| Layer | Implementation |
| --- | --- |
| Syntactic | `routing.py` — `quantity_from_query`, `parse_dist_pairs`, `distribution_from_query`; raises `RandomGenQuantityError` / `RandomGenDistFormatError` |
| Semantic | `RandomGenRestApi.validate_distribution` + generator `validate()`; enforces `round(sum, 3) == 1` and `1..MAX_NUMBERS` |

## 8.4 Error handling (the JSON error contract)

A single handler at the application boundary turns every exception into one JSON
shape — an error message with an HTTP status. This is a deliberate error boundary,
not a catch-all buried in business logic: domain code raises only the service's
own typed exceptions (no bare catches), each with a fixed, human-readable message,
which keeps the contract uniform across every endpoint.

| Exception | Status | Body |
| --- | --- | --- |
| `RandomGenError` | 400 | `{"error": str(e)}` |
| Flask/Werkzeug `HTTPException` (e.g. 404, 405) | `e.code` | `{"error": e.description}` |
| anything else | 500 | `{"error": str(e)}` |

The boundary is `handle_error` (registered as `@app.errorhandler(Exception)`) in
[`app.py`](../../src/randomgen/app.py); the typed exceptions live in
[`errors.py`](../../src/randomgen/errors.py), and the shape is fixed by the
[OpenAPI contract](../../src/randomgen/openapi.yaml).

## 8.5 Quality reporting (Chi-Square)

Every generation response carries its own quality verdict: a goodness-of-fit
check comparing the sample it just produced against the distribution that was
requested. It reports the expected frequencies, the observed frequencies, the
Chi-Square statistic with its degrees of freedom and p-value, and a single
pass/fail flag. The expected category set is fixed in advance, so an outcome that
never appeared still counts against the fit instead of being silently dropped. The
sample passes when the p-value clears the significance threshold; a larger sample
gives a more meaningful verdict, which is why the default draw is large.

| Element | Implementation |
| --- | --- |
| Quality block | `quality`: `chi_square_test` (`is_null`, `chi_square`, `p_value`, `df`), `expected_histogram`, `observed_histogram` |
| Histograms | expected from the requested probabilities; observed via `Histogram` from the sample |
| Test | `ChiSquareTest` (`scipy.stats.chi2`), explicit category domain — a zero-count outcome still contributes `(0 − expected)² / expected` |
| Verdict | `is_null` is `True` when `p_value > 0.05`; default sample `DEFAULT_QUANTITY = 1000` |

## 8.6 Correctness safeguards

A few deliberate guards protect correctness against subtle edge cases. Each is
the kind of code that looks redundant and invites simplification — but removing
any one reintroduces a real bug, so it is called out here to be preserved. All
three are covered by regression tests.

| Guard | Protects against | Implementation |
| --- | --- | --- |
| Float-tail fallback | `RandomGenV1.next_num()` returning `None` | returns the last outcome when `random()` exceeds the final cumulative probability |
| Rounded weight sum | float error failing a valid distribution | `round(sum, 3) == 1` in weight validation |
| Strict-length zip | silent truncation of a mismatched Chi-Square domain | `zip(..., strict=...)` raising `RandomGenMismatchError` |

## 8.7 API design and versioning

The API is read-only and uniform: every endpoint is an HTTP GET driven by query
parameters, returning JSON. Each major version is a frozen public contract — an
existing version's behavior never changes; new behavior ships as a new version, so
existing callers keep working. The versions share one contract — identical
parameters, response shape, and status codes — and differ only in how the sample
is drawn underneath.

| Aspect | Implementation |
| --- | --- |
| Request/response | HTTP `GET`, query parameters, JSON via `jsonify` |
| Versioned paths | `/api/v1`, `/api/v2` — frozen once shipped |
| Stable across versions | parameters, response shape, status codes |

## 8.8 Fluent builder pattern

The core classes share a fluent, builder-style interface. Methods that configure
or validate an object return that object, so calls chain into a readable pipeline;
methods that produce or consume a result end the chain and hand back the result.
The convention is recorded in the design journal
([solution.md](../history/solution.md) §13).

| Aspect | Implementation |
| --- | --- |
| Classes | `RandomGenABC`, `Histogram`, `ChiSquareTest` |
| Chained (return `self`) | setters and validators — `set_*().validate().calc()` |
| Not chained | producers and consumers — `next_num`, the assembled response |

## 8.9 Security

The service has no authentication and stores no user data, so its security rests
on a small attack surface and a clean supply chain rather than an auth layer,
which is out of scope for a demo. One caveat is essential for callers: the output
is statistically fair but not cryptographically secure, and must not be used for
security-sensitive randomness.

| Aspect | Implementation |
| --- | --- |
| Secrets | none in the repo; CI runs a gitleaks scan |
| Container | non-root (`appuser`) on a digest-pinned base image |
| Debug mode | always off — gunicorn in the image; local `flask run` stays debug-off |
| Authentication | none; `/health` is open, no auth layer (out of scope) |
| Randomness | Python's `random` (Mersenne-Twister) — not cryptographically secure |

## 8.10 Build, tooling, and testing

The project is built and checked through a single, declarative toolchain. One
descriptor file defines the package, its dependencies, and its optional extras,
and also configures the linter, type checker, and test runner. Three gates guard
quality — linting and formatting, static typing, and a tiered test suite with a
minimum coverage bar — and CI runs all three on every push and pull request.

| Tool | Role |
| --- | --- |
| `pyproject.toml` | single PEP 621 descriptor — package, deps, `test`/`dev` extras, `src` layout, and tool config |
| `ruff` | linting (`E,W,F,I,UP,B,C4,SIM`) and single-quote formatting |
| `mypy` | static typing (`ignore_missing_imports` for stub-less `scipy`) |
| `pytest` | tiered tests (`unit` / `integration` / `e2e`), one file per module, 85% coverage gate |

See [Chapter 2](02-architecture-constraints.md) for the binding constraints and
[Chapter 10](10-quality-requirements.md) for quality scenarios.
