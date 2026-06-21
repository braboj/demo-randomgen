# 6. Runtime View

This chapter shows how the building blocks from
[Chapter 5](05-building-block-view.md) collaborate at runtime for the most
important scenarios.

## 6.1 Happy path

A client requests a sample from the default (or an overridden) distribution. The
handler parses the query, the stateless service validates and generates, the
statistical helpers score the sample, and the response is serialized to JSON.

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant F as Flask app (gunicorn)
    participant R as routing.api_v1_randomgen
    participant API as RandomGenRestApi
    participant G as RandomGenV1
    participant H as Histogram
    participant X as ChiSquareTest

    C->>F: GET /api/v1/randomgen?numbers&dist
    F->>R: dispatch
    R->>R: quantity_from_query(), distribution_from_query()
    R->>API: randomgen_endpoint(RandomGenV1, quantity, values, probabilities)
    alt no distribution supplied
        API->>API: use DEFAULT_NUMBERS / DEFAULT_PROBABILITIES
    else caller-supplied
        API->>API: validate_distribution(values, probabilities)
    end
    API->>G: set_numbers().set_probabilities().validate()
    loop quantity times
        API->>G: next_num()
        G-->>API: number
    end
    API->>H: set_numbers(sample).calc()
    H-->>API: observed histogram
    API->>X: set_observed/expected... .validate().calc()
    X-->>API: chi_square, p_value, df, is_null
    API-->>R: {numbers, quality{...}}
    R->>F: jsonify(...)
    F-->>C: 200 OK + JSON
```

`/api/v2/randomgen` is identical except the handler passes `RandomGenV2`, whose
`next_num()` uses `random.choices`.

## 6.2 Error path

A malformed query or an invalid distribution raises a typed `RandomGenError` —
from the query parsing in `routing.py` or from validation in the service. Flask
routes any exception to the single `handle_error` boundary registered in the
factory.

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant F as Flask app (gunicorn)
    participant R as routing.api_v1_randomgen
    participant API as RandomGenRestApi
    participant EH as handle_error

    C->>F: GET /api/v1/randomgen (invalid input)
    F->>R: dispatch
    alt malformed query string
        R-->>F: raise RandomGenError
    else invalid distribution / quantity out of bounds
        R->>API: randomgen_endpoint(...)
        API-->>F: raise RandomGenError
    end
    F->>EH: handle_error(exc)
    EH-->>C: status + {"error": ...}
    Note over EH: RandomGenError → 400<br/>HTTPException → its code<br/>other → 500
```

The mapping keeps the JSON error contract uniform across every endpoint:

- `RandomGenError` (e.g. `RandomGenQuantityError`, `RandomGenMaxError`,
  `RandomGenProbabilitySumError`) → 400 `{"error": "<message>"}`.
- Werkzeug `HTTPException` (e.g. an unknown path → 404) → its own status code.
- Any other exception → 500.

See [Chapter 8](08-crosscutting-concepts.md) and the
[OpenAPI contract](../../src/randomgen/openapi.yaml).

## 6.3 Health check

```mermaid
sequenceDiagram
    autonumber
    participant P as Platform probe (Docker/Render)
    participant F as Flask app (gunicorn)
    P->>F: GET /health
    F-->>P: 200 OK {"status": "ok"}
```

Used by the Docker `HEALTHCHECK` and Render's `healthCheckPath`
([Chapter 7](07-deployment-view.md)). Requires no authentication and touches no
business logic.

## 6.4 Runtime rules

- **Stateless per request.** The service and blueprint hold nothing mutable;
  each request builds its own generator, so concurrent requests never share
  state.
- **Two-layer validation.** `routing.py` rejects malformed syntax; the service
  and generator reject invalid distributions.
- **Bounded work.** Each request is bounded to 1–10000 numbers (`MAX_NUMBERS`).
