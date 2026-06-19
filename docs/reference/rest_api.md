# REST API

The service is stateless. The distribution defaults to a built-in one and may
be overridden per request; no configuration is stored between requests.

This page is the hand-written reference. The service also serves an
interactive reference at `/docs` (ReDoc), rendered from the machine-readable
OpenAPI 3.1 document at `/openapi.json`.

## GET /api/v1/randomgen

Generate random numbers using the `RandomGenV1` generator and score the sample
against the requested distribution with a Chi-Square test.

### Query parameters

| Parameter     | Type       | Required | Default  | Description                                                    |
|---------------|------------|----------|----------|----------------------------------------------------------------|
| `numbers`     | int        | No       | `1000`   | Quantity of random numbers to generate (`1`..`10000`).         |
| `dist`        | string     | No       | built-in | Distribution as `value:probability` pairs, e.g. `1:0.5,2:0.5`. |
| `value`       | float (×N) | No       | built-in | Distribution outcomes. Repeat once per outcome.                |
| `probability` | float (×N) | No       | built-in | Distribution weights, aligned with `value`. Must sum to 1.     |

Supply the distribution either with the single `dist` parameter (preferred —
each value is bound to its own weight, so the two cannot be misaligned) or with
the repeated `value` / `probability` parameters. `dist` takes precedence when
both are present. When neither is supplied, the built-in distribution is used
(`[-1, 0, 1, 2, 3]` with `[0.01, 0.3, 0.58, 0.1, 0.01]`).

### Response

```json
{
  "numbers": [0, 2, 1, 1, 1, 0, 0, 1, 1, 1],
  "quality": {
    "chi_square_test": {
      "is_null": true,
      "chi_square": 4.97586206896552,
      "p_value": 0.173573199002695,
      "df": 4
    },
    "expected_histogram": {"-1": 0.01, "0": 0.3, "1": 0.58, "2": 0.1, "3": 0.01},
    "observed_histogram": {"-1": 0.01, "0": 0.29, "1": 0.59, "2": 0.1, "3": 0.01}
  }
}
```

`is_null` is `true` when the observed sample is consistent with the requested
distribution at the 0.05 significance level.

### Status codes

- `200 OK` — numbers generated.
- `400 Bad Request` — invalid input: non-integer `numbers`, a quantity outside
  `1..10000`, or a malformed distribution (length mismatch, negative weight, or
  weights that do not sum to 1). The body is `{"error": "..."}`.

### Example

```bash
curl "http://localhost:5000/api/v1/randomgen?numbers=100"
```

With a custom distribution as `value:probability` pairs (preferred):

```bash
curl "http://localhost:5000/api/v1/randomgen?numbers=1000&dist=1:0.2,2:0.2,3:0.6"
```

The same distribution via the repeated `value` / `probability` parameters:

```bash
curl "http://localhost:5000/api/v1/randomgen?numbers=1000&value=1&value=2&value=3&probability=0.2&probability=0.2&probability=0.6"
```

## GET /api/v2/randomgen

Identical to `/api/v1/randomgen` but uses the `RandomGenV2` generator
(`random.choices`). Same parameters, response shape, and status codes.

```bash
curl "http://localhost:5000/api/v2/randomgen?numbers=100"
```

## GET /health

Liveness check. Requires no authentication.

### Response

```json
{"status": "ok"}
```

### Status codes

- `200 OK` — the service is able to handle requests.

## GET /openapi.json

The machine-readable OpenAPI 3.1 description of this API, built in code from the
live version and quantity limits. It backs the interactive reference at `/docs`.

### Response

`application/json` — an OpenAPI 3.1 document (`openapi`, `info`, `paths`,
`components`).

### Status codes

- `200 OK` — the specification is returned.

## GET /docs

An interactive API reference (ReDoc) rendered in the browser over
`/openapi.json`. Open [`/docs`](/docs) to explore the endpoints, their
parameters, and response schemas.

### Response

`text/html` — the ReDoc documentation page.

### Status codes

- `200 OK` — the documentation page is returned.
