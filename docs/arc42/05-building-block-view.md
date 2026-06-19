# 5. Building Block View

This section shows the static decomposition of the `randomgen` package into
modules and their dependencies.

## 5.1 Level 1 — package overview

```mermaid
flowchart TD
    flaskcli["flask run<br/>(local-dev server)"]
    gunicorn(["gunicorn<br/>(prod WSGI)"])

    subgraph pkg["src/randomgen/"]
        app["app.py<br/>create_app() factory<br/>+ handle_error"]
        routing["routing.py<br/>Blueprint bp<br/>+ thin handlers<br/>+ query parsing"]
        endpoints["endpoints.py<br/>RandomGenRestApi<br/>(stateless service)"]
        core["core.py<br/>RandomGenABC<br/>RandomGenV1 / V2"]
        histogram["histogram.py<br/>Histogram"]
        hypothesis["hypothesis.py<br/>ChiSquareTest"]
        openapi["openapi.py<br/>load_spec()"]
        spec[("openapi.yaml<br/>OpenAPI 3.1 contract")]
        errors["errors.py<br/>RandomGenError + subtypes"]
    end

    scipy(["scipy.stats.chi2"])

    flaskcli --> app
    gunicorn --> app
    app --> routing
    app --> errors
    routing --> endpoints
    routing --> core
    routing --> errors
    routing --> openapi
    openapi --> spec
    endpoints --> core
    endpoints --> histogram
    endpoints --> hypothesis
    endpoints --> errors
    core --> errors
    histogram --> errors
    hypothesis --> errors
    hypothesis --> scipy
```

| Building block | Responsibility |
|----------------|----------------|
| [`app.py`](../../src/randomgen/app.py) | Application factory. Builds the Flask app, registers the blueprint and the single `Exception` error handler. |
| [`routing.py`](../../src/randomgen/routing.py) | Flask blueprint `bp`; thin route handlers; query-string parsing helpers. |
| [`endpoints.py`](../../src/randomgen/endpoints.py) | `RandomGenRestApi` — stateless service logic, framework-independent. |
| [`core.py`](../../src/randomgen/core.py) | `RandomGenABC` abstract base and the two concrete generators. |
| [`histogram.py`](../../src/randomgen/histogram.py) | `Histogram` — observed-frequency distribution from a sample. |
| [`hypothesis.py`](../../src/randomgen/hypothesis.py) | `ChiSquareTest` — goodness-of-fit statistic, df, and p-value via `scipy`. |
| [`openapi.py`](../../src/randomgen/openapi.py) | `load_spec()` — loads and caches the `openapi.yaml` contract (served at `/openapi.json`, rendered at `/docs`). |
| [`openapi.yaml`](../../src/randomgen/openapi.yaml) | The hand-authored OpenAPI 3.1 contract — single source of truth for the API (design-first, AD-16). |
| [`errors.py`](../../src/randomgen/errors.py) | `RandomGenError` base plus specific domain exceptions. |

Dependencies flow inward toward `core.py`/`errors.py`; no business logic lives
in `routing.py`, and `endpoints.py`/`core.py` know nothing about Flask.

## 5.2 Level 2 — selected building blocks

### 5.2.1 `app.py` — application factory

[`app.py`](../../src/randomgen/app.py) holds `create_app()`, which builds the Flask
app, registers the blueprint, and installs one error handler. The app keeps no
mutable state, so each gunicorn worker builds it once. `handle_error` is the
single error boundary: `RandomGenError` maps to **400**, any Werkzeug
`HTTPException` keeps its own status, and anything else becomes **500** —
always as `{"error": ...}`.

### 5.2.2 `routing.py` — blueprint and handlers

[`routing.py`](../../src/randomgen/routing.py) registers the blueprint `bp`, holds one
shared stateless `RandomGenRestApi`, and defines the routes:

| Route | Purpose |
| --- | --- |
| `GET /` | `index.html` home page (browser UI) |
| `GET /api/v1/randomgen` | sample via `RandomGenV1` |
| `GET /api/v2/randomgen` | sample via `RandomGenV2` |
| `GET /openapi.json` | the OpenAPI contract as JSON |
| `GET /docs` | ReDoc rendering of the contract |
| `GET /health` | liveness — `{"status": "ok"}` |

Handlers stay thin: helpers parse the quantity and an optional distribution
from the query string (the `dist` pairs form, or repeated `value`/
`probability`) and raise a domain error on malformed input instead of silently
falling back to the default.

### 5.2.3 `endpoints.py` — `RandomGenRestApi` (stateless)

[`endpoints.py`](../../src/randomgen/endpoints.py) is the framework-independent
service. `randomgen_endpoint()` takes the built-in distribution or validates
the caller's, builds the generator, and hands off to `generate_random_numbers()`,
which bounds the request to 1–10000 (`MAX_NUMBERS`), draws the sample, and
scores it — expected vs. observed histograms plus a Chi-Square test — into the
response.

### 5.2.4 `core.py` — generators (V1 vs. V2)

[`core.py`](../../src/randomgen/core.py) defines `RandomGenABC`, a builder-style base
(set the numbers and probabilities, `validate()`, then `generate()`), and two
subclasses that differ only in `next_num()`
([AD-6](../decisions/006-two-generators-one-interface.md)):

- **`RandomGenV1`** — manual inverse-CDF sampling over the precomputed
  cumulative probabilities.
- **`RandomGenV2`** — delegates to `random.choices`; simpler, but measured
  ~3× slower than V1 ([solution.md](../history/solution.md) §10).

### 5.2.5 `histogram.py` and `hypothesis.py`

- [`histogram.py`](../../src/randomgen/histogram.py) — `Histogram` (a `dict` subclass)
  turns a sample into the observed proportion of each value.
- [`hypothesis.py`](../../src/randomgen/hypothesis.py) — `ChiSquareTest` scores the
  sample against the requested distribution: `calc()` returns the statistic,
  degrees of freedom, and p-value (via scipy's `chi2`), and `is_null()` reduces
  that to pass/fail at α = 0.05. It scores over the *expected* categories, so
  outcomes drawn zero times still count against the fit.

### 5.2.6 `errors.py`

[`errors.py`](../../src/randomgen/errors.py) defines `RandomGenError` and nine domain
subclasses — invalid type, empty, length mismatch, bad probabilities (negative
or not summing to 1), quantity out of range, and malformed query parameters.
Each carries a fixed message and maps to HTTP 400 through `handle_error`
([Section 8](08-crosscutting-concepts.md)).

### 5.2.7 `openapi.py` / `openapi.yaml` — API contract

The API is **design-first**: [`openapi.yaml`](../../src/randomgen/openapi.yaml)
is the hand-authored OpenAPI 3.1 contract and the single source of truth
([AD-16](../decisions/016-design-first-openapi.md)). `openapi.py`'s `load_spec()`
loads and caches it; `routing.py` serves it verbatim at `/openapi.json` and
renders it as ReDoc at `/docs` (both unversioned, outside the `/api` contract —
[AD-13](../decisions/013-openapi-docs-endpoint.md)). Because the YAML is
hand-authored, unit tests guard against drift: they pin its limits and version
to the live constants and check that every `/api` route is documented.
