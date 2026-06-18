# REST API

The service is stateless. The distribution defaults to a built-in one and may
be overridden per request; no configuration is stored between requests.

## GET /api/v1/randomgen

Generate random numbers using the `RandomGenV1` generator and score the sample
against the requested distribution with a Chi-Square test.

### Query parameters

| Parameter     | Type        | Required | Default | Description                                                        |
|---------------|-------------|----------|---------|--------------------------------------------------------------------|
| `numbers`     | int         | No       | `1000`  | Quantity of random numbers to generate (`1`..`10000`).             |
| `value`       | float (×N)  | No       | built-in| Distribution outcomes. Repeat once per outcome.                    |
| `probability` | float (×N)  | No       | built-in| Distribution weights, aligned with `value`. Must sum to 1.         |

When neither `value` nor `probability` is supplied, the built-in distribution
is used (`[-1, 0, 1, 2, 3]` with `[0.01, 0.3, 0.58, 0.1, 0.01]`).

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

With a custom distribution:

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
