[![Test Application](https://github.com/braboj/randomgen/actions/workflows/test_application.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/test_application.yml)
[![Deploy Image](https://github.com/braboj/randomgen/actions/workflows/deploy_image.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/deploy_image.yml)
[![Deploy Pages](https://github.com/braboj/randomgen/actions/workflows/deploy_pages.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/deploy_pages.yml)

# RandomGen

RandomGen is a small Flask REST API that draws random numbers from a
configurable discrete distribution and reports how well the drawn sample
matches the requested distribution using a Chi-Square test. It is aimed at
developers who want a simple, self-contained service to demonstrate and
sanity-check weighted random sampling, and it ships as a Docker image so it
runs anywhere Docker does.

## Features

- Two interchangeable generator implementations (`/api/v1`, `/api/v2`).
- A built-in default distribution, overridable **per request** — the service
  is stateless and keeps no configuration between calls.
- A Chi-Square goodness-of-fit report (statistic, p-value, degrees of freedom,
  expected vs. observed histograms) on every response.
- A `/health` endpoint and a hardened, non-root Docker image served by
  gunicorn.

## Quick start

Prerequisites: [Docker](https://docs.docker.com/engine/install/).

```bash
docker pull braboj/randomgen:latest
docker run -p 5000:5000 braboj/randomgen:latest
```

Open [http://localhost:5000](http://localhost:5000) for the home page, then
generate 100 numbers:

```bash
curl "http://localhost:5000/api/v1/randomgen?numbers=100"
```

## Usage

Generate numbers from the built-in distribution:

```bash
curl "http://localhost:5000/api/v1/randomgen?numbers=1000"
```

Expected output (truncated):

```json
{
  "numbers": [1, 0, 1, 2, 1, 0, 1, 1, -1, 1],
  "quality": {
    "chi_square_test": {
      "is_null": true,
      "chi_square": 4.97,
      "p_value": 0.17,
      "df": 4
    },
    "expected_histogram": {"-1": 0.01, "0": 0.3, "1": 0.58, "2": 0.1, "3": 0.01},
    "observed_histogram": {"-1": 0.01, "0": 0.29, "1": 0.59, "2": 0.1, "3": 0.01}
  }
}
```

Override the distribution per request with a single `dist` parameter of
comma-separated `value:probability` pairs (preferred — each value is bound to
its own weight, and they must sum to 1):

```bash
curl "http://localhost:5000/api/v1/randomgen?numbers=1000&dist=1:0.2,2:0.2,3:0.6"
```

The repeated `value` / `probability` parameters still work (they must be the
same length and sum to 1):

```bash
curl "http://localhost:5000/api/v1/randomgen?numbers=1000&value=1&value=2&value=3&probability=0.2&probability=0.2&probability=0.6"
```

Invalid input (e.g. `?numbers=abc`, mismatched lengths, probabilities not
summing to 1) returns `400` with a JSON `{"error": ...}` body. See
[docs/rest_api.md](docs/rest_api.md) or the
[project pages](https://braboj.github.io/randomgen/) for the full reference.

## Project structure

```text
src/randomgen/         # application package (src layout)
  app.py               # create_app() factory + error handler
  core.py              # RandomGenV1 / RandomGenV2 generators
  endpoints.py         # RandomGenRestApi — stateless service logic
  errors.py            # custom exception types
  histogram.py         # histogram helper
  hypothesis.py        # Chi-Square hypothesis test
  routing.py           # Flask Blueprint + thin route handlers
webserver.py           # local-dev entrypoint (Docker serves via gunicorn)
pyproject.toml         # PEP 621 metadata, deps, ruff/mypy/pytest config
tests/                 # pytest suite (one file per module)
scripts/               # demo, plotting, and prototype helper scripts
docs/                  # MkDocs site (published to GitHub Pages)
Dockerfile             # non-root, gunicorn, digest-pinned base image
.github/workflows/     # CI: test, deploy image, deploy pages
```

## Development

Supported Python: 3.12+.

```bash
# Clone
git clone https://github.com/braboj/randomgen.git
cd randomgen

# Install the project with the developer toolchain (ruff, mypy, pytest)
pip install -e ".[dev]"

# Lint, type-check, and run the test suite (with coverage gate)
ruff check . && ruff format --check . && mypy
pytest --cov=randomgen --cov-fail-under=85

# Run the service locally
python webserver.py                  # http://0.0.0.0:5000
```

## Configuration

The service is stateless; behavior is controlled per request and by a few
code-level constants.

| Setting | Where | Default | Description |
|---------|-------|---------|-------------|
| `numbers` | query param | `1000` | Quantity of numbers to generate (1..`MAX_NUMBERS`). |
| `dist` | query param | built-in | Optional per-request distribution as `value:probability` pairs (e.g. `1:0.5,2:0.5`); weights sum to 1. Takes precedence over `value`/`probability`. |
| `value` / `probability` | query params | built-in | Optional per-request distribution (repeat each, equal length, weights sum to 1). |
| `DEFAULT_NUMBERS` / `DEFAULT_PROBABILITIES` | `src/randomgen/endpoints.py` | `[-1,0,1,2,3]` / `[0.01,0.3,0.58,0.1,0.01]` | Built-in distribution. |
| `MAX_NUMBERS` | `src/randomgen/endpoints.py` | `10000` | Upper bound on `numbers`. |
| Port | `webserver.py` / Docker | `5000` | Listen port. |

## Next steps

- For more information, see the [RandomGen project pages](https://braboj.github.io/randomgen/).
- To contribute, see [Contributing](CONTRIBUTING.md).
- To leave feedback, open a [discussion](https://github.com/braboj/randomgen/discussions).
