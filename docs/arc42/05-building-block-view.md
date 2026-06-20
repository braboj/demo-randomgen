# 5. Building Block View

This chapter shows the static decomposition of the `randomgen` package into its
building blocks.

## 5.1 Level 1

```mermaid
flowchart TD
    gunicorn(["gunicorn<br/>(prod WSGI)"])
    scipy(["scipy.stats.chi2"])

    subgraph pkg["src/randomgen/"]
        web["Web App"]
        domain["Domain Logic"]
        contract["API contract"]
        errors["Errors"]
    end

    gunicorn --> web
    web --> domain
    web --> contract
    web --> errors
    domain --> errors
    domain --> scipy
```

| Building block | Responsibility |
| --- | --- |
| Web App | Turns HTTP requests into service calls and JSON responses. |
| Domain Logic | Generates a sample from a distribution and scores how well it fits. |
| API contract | The design-first OpenAPI spec, served and rendered. |
| Errors | Typed domain exceptions, mapped to HTTP 400. |

Dependencies flow inward: the Web App depends on the Domain Logic, the API
contract, and the Errors; the Domain Logic knows nothing about Flask.

## 5.2 Web App

The HTTP adapter, and the only Flask-aware block
([`app.py`](../../src/randomgen/app.py),
[`routing.py`](../../src/randomgen/routing.py)). The `create_app()` factory
builds the app, registers the routes, and installs one error handler; gunicorn
runs it. The routes — the home page, the versioned API (`/api/v1`, `/api/v2`),
the contract (`/openapi.json`, `/docs`), and `/health` — stay thin: they parse
and validate the query, delegate to the Domain Logic, and serialize JSON. The
error handler is the single place status codes are set: domain errors become
400, other HTTP errors keep their code, and anything else is 500, all as
`{"error": ...}`.

## 5.3 Domain Logic

The framework-independent core: it generates a sample from a discrete
distribution and scores how well the sample matches it. It knows nothing about
Flask — the Web App hands it the quantity and the optional distribution and gets
back the numbers plus a quality report. It splits into three parts, each
independently testable:

| Part | Responsibility |
| --- | --- |
| Service ([`endpoints.py`](../../src/randomgen/endpoints.py)) | `RandomGenRestApi` orchestrates a request: takes the built-in distribution or validates the caller's, builds the generator, bounds the quantity, draws the sample, and assembles the response. |
| Generators ([`core.py`](../../src/randomgen/core.py)) | `RandomGenABC` plus `RandomGenV1` (inverse-CDF) and `RandomGenV2` (`random.choices`) — one builder interface, with V1 measured ~3× faster ([AD-6](../decisions/006-two-generators-one-interface.md)). |
| Statistics ([`histogram.py`](../../src/randomgen/histogram.py), [`hypothesis.py`](../../src/randomgen/hypothesis.py)) | `Histogram` turns a sample into observed proportions; `ChiSquareTest` scores it against the expected distribution (statistic, degrees of freedom, p-value via scipy). |

## 5.4 API contract

The design-first description of the API
([`openapi.yaml`](../../src/randomgen/openapi.yaml),
[`openapi.py`](../../src/randomgen/openapi.py)). `openapi.yaml` is the
hand-authored OpenAPI 3.1 contract and the single source of truth
([AD-16](../decisions/016-design-first-openapi.md)); `load_spec()` loads and
caches it, and the Web App serves it verbatim at `/openapi.json` and renders it
as ReDoc at `/docs`. Two tests keep it honest: one pins its limits and version
to the live constants, the other asserts every `/api` route is documented.

## 5.5 Errors

The typed domain-exception hierarchy
([`errors.py`](../../src/randomgen/errors.py)). Every invalid input or bound
violation is a specific `RandomGenError` subclass carrying a fixed message —
nine in all (wrong type, empty, length mismatch, negative or non-summing
probabilities, quantity below or above the bounds, and a malformed `numbers` or
`dist` query). Both the Web App (query parsing) and the Domain Logic raise them;
the Web App's error handler maps them to HTTP 400.
