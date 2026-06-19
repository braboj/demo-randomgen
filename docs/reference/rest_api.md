# REST API

The authoritative API contract is the OpenAPI document
[`src/randomgen/openapi.yaml`](../../src/randomgen/openapi.yaml). The service
serves it verbatim at `/openapi.json` and renders it as an interactive
reference (ReDoc) at `/docs`. This page is a short human-facing summary — for
the exact parameters, schemas, and status codes, use the contract or `/docs`.

## Endpoints

| Method and path | Purpose |
|-----------------|---------|
| `GET /api/v1/randomgen` | Generate numbers (`RandomGenV1`) with a Chi-Square fairness report. |
| `GET /api/v2/randomgen` | Same, using `RandomGenV2` (`random.choices`). |
| `GET /health` | Liveness check; returns `{"status": "ok"}`. |
| `GET /openapi.json` | The OpenAPI 3.1 contract, served verbatim. |
| `GET /docs` | Interactive API reference (ReDoc). |

## Quick start

```bash
# Built-in distribution, 100 numbers
curl "http://localhost:5000/api/v1/randomgen?numbers=100"

# Custom distribution as value:probability pairs (preferred)
curl "http://localhost:5000/api/v1/randomgen?numbers=1000&dist=1:0.2,2:0.2,3:0.6"
```

The distribution defaults to a built-in one (`[-1, 0, 1, 2, 3]` with
`[0.01, 0.3, 0.58, 0.1, 0.01]`) and may be overridden per request via `dist`
(preferred) or the repeated `value` / `probability` parameters. The service is
stateless; nothing is stored between requests.
