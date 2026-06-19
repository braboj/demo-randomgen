[![Test Application](https://github.com/braboj/randomgen/actions/workflows/test_application.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/test_application.yml)
[![Deploy Image](https://github.com/braboj/randomgen/actions/workflows/deploy_image.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/deploy_image.yml)

# RandomGen

RandomGen is a small Flask REST API that draws random numbers from a
configurable discrete distribution and reports how well the drawn sample
matches the requested distribution using a Chi-Square test. It is aimed at
developers who want a simple, self-contained service to demonstrate and
sanity-check weighted random sampling, and it ships as a Docker image so it
runs anywhere Docker does.

**🌐 Live demo:** <https://randomgen-llyc.onrender.com/> — try the interactive
UI or the API directly (free Render instance; the first request after idle may
cold-start for ~30–60s).

## Features

- Two interchangeable generator implementations (`/api/v1`, `/api/v2`).
- A built-in default distribution, overridable **per request** — the service
  is stateless and keeps no configuration between calls.
- A Chi-Square goodness-of-fit report (statistic, p-value, degrees of freedom,
  expected vs. observed histograms) on every response.
- A browser home page with one-click preset distributions (uniform, skewed,
  bimodal, near-degenerate) for quick experimentation.
- A `/health` endpoint and a hardened, non-root Docker image served by
  gunicorn.
- An interactive API reference at `/docs` (ReDoc), generated from a code-built
  OpenAPI 3.1 spec served at `/openapi.json`.

## Quick start

Prerequisites: [Docker](https://docs.docker.com/engine/install/).

```bash
docker pull braboj/randomgen:latest
docker run -p 5000:5000 braboj/randomgen:latest
```

Open [http://localhost:5000](http://localhost:5000) for the interactive home
page — a small UI to pick a generator, distribution, and sample size and see
the Chi-Square verdict with an expected-vs-observed histogram (see the
[UI snapshots](docs/reference/ui-snapshots.md) for a preview), or browse the interactive
API reference at [http://localhost:5000/docs](http://localhost:5000/docs). Or
call the API directly to generate 100 numbers:

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
[docs/reference/rest_api.md](docs/reference/rest_api.md) for the full REST reference and
[docs/arc42/](docs/arc42/) for the architecture documentation.

## Deploy a free demo (Render)

The repo ships a [`render.yaml`](render.yaml) blueprint, so you can run a
zero-cost demo on [Render](https://render.com) straight from the existing
Dockerfile:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/braboj/demo-randomgen)

1. In the Render dashboard choose **New → Blueprint** and connect this
   repository (or use the button above).
2. Render builds the Docker image and provisions a free web service with a
   `/health` check. It injects `$PORT`; the container binds it automatically
   (`gunicorn ... 0.0.0.0:${PORT:-5000}`), so no extra configuration is needed.
3. Once live, the service is reachable at the URL Render assigns — this
   project's demo runs at <https://randomgen-llyc.onrender.com/>.

> **Note:** free instances spin down after ~15 minutes of inactivity and
> cold-start (~30–60s) on the next request — expected for a zero-cost demo.

## Project structure

```text
src/randomgen/         # application package (src layout)
  app.py               # create_app() factory + error handler
  core.py              # RandomGenV1 / RandomGenV2 generators
  endpoints.py         # RandomGenRestApi — stateless service logic
  errors.py            # custom exception types
  histogram.py         # histogram helper
  hypothesis.py        # Chi-Square hypothesis test
  openapi.py           # code-built OpenAPI 3.1 spec (served at /openapi.json)
  routing.py           # Flask Blueprint + thin route handlers
  templates/           # Jinja UI: home page (index.html) + API docs (docs.html)
  static/              # CSS + JS for the home-page UI
pyproject.toml         # PEP 621 metadata, deps, ruff/mypy/pytest config
tests/                 # pytest suite (one file per module)
scripts/               # demo, plotting, and API client helper scripts
render.yaml            # Render free-tier deploy blueprint
docs/arc42/            # arc42 architecture documentation
docs/decisions/        # Architecture Decision Records (ADRs)
docs/reference/        # REST reference + UI snapshots
docs/history/          # original kata statement + solution journal
docs/assets/           # diagrams (drawio) + images (plots, UI screenshots)
Dockerfile             # non-root, gunicorn, digest-pinned base image
.github/workflows/     # CI: test (ruff+mypy+pytest), deploy image
```

## Development

Supported Python: 3.12+.

```bash
# Clone
git clone https://github.com/braboj/randomgen.git
cd randomgen

# Install the project with the developer toolchain (ruff, mypy, pytest)
pip install -e ".[dev]"

# Lint, type-check, and run the fast test gate (unit + integration)
ruff check . && ruff format --check . && mypy
pytest --cov=randomgen --cov-fail-under=85

# End-to-end tier: real container (Testcontainers on a Podman or Docker
# backend) + a Playwright browser test. One-time setup, then run:
pip install -e ".[e2e]" && playwright install chromium
pytest -m e2e

# Run the service locally (Flask dev server, hot reload)
flask --app "randomgen.app:create_app" run   # http://127.0.0.1:5000
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
| Port | Docker / `$PORT` | `5000` | Listen port (gunicorn binds `$PORT`; the Flask dev server uses `5000`). |

## Contributing

Contributions are welcome. Set up your environment from
[Development](#development) above, follow the project conventions and session
workflow in [CLAUDE.md](CLAUDE.md), and open a PR — one concern per PR,
conventional commits, and green CI (ruff + mypy + pytest) before merge.

## Next steps

- For the architecture, see the [arc42 documentation](docs/arc42/).
- To contribute, see [Contributing](#contributing) above.
- To leave feedback, open a [discussion](https://github.com/braboj/randomgen/discussions).
