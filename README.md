[![CI](https://github.com/braboj/randomgen/actions/workflows/ci.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/ci.yml)
[![CD](https://github.com/braboj/randomgen/actions/workflows/cd.yml/badge.svg)](https://github.com/braboj/randomgen/actions/workflows/cd.yml)

# RandomGen

*A coding kata taken to a production-grade, documented, deployed service.*

RandomGen is a small Flask REST API that draws random numbers from a
configurable discrete distribution and scores the sample against it with a
Chi-Square goodness-of-fit test.

**🌐 Live demo:** <https://randomgen-llyc.onrender.com/> — try the interactive
UI or the API directly (free Render instance; the first request after idle may
cold-start for ~30–60s).

## Features

- Two interchangeable generators — `/api/v1` and `/api/v2`.
- Stateless sampling from a built-in or per-request distribution.
- A Chi-Square goodness-of-fit report on every response.
- An interactive browser UI — presets, weight sliders, light/dark, CSV export.
- An OpenAPI 3.1 contract with a ReDoc reference at `/docs`.
- `/info` and `/health` endpoints, on a hardened, non-root Docker image on gunicorn.

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

Invalid input — a non-integer `numbers`, mismatched lengths, or weights that
don't sum to 1 — returns `400` with a JSON `{"error": "..."}` body.

## Deploy a free demo (Render)

The repo ships a [`render.yaml`](render.yaml) blueprint, so you can run a
zero-cost demo on [Render](https://render.com) from the published image:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/braboj/demo-randomgen)

1. In the Render dashboard choose **New → Blueprint** and connect this
   repository (or use the button above).
2. Render provisions a free web service that runs the published
   `braboj/randomgen:latest` image with a `/health` check. It injects `$PORT`;
   the image binds it automatically (`gunicorn ... 0.0.0.0:${PORT:-5000}`), so
   no extra configuration is needed.
3. Once live, the service is reachable at the URL Render assigns — this
   project's demo runs at <https://randomgen-llyc.onrender.com/>.

Releases redeploy automatically: the image workflow POSTs a Render Deploy Hook
after pushing a new image (see PLAYBOOK section 5).

> **Note:** free instances spin down after ~15 minutes of inactivity and
> cold-start (~30–60s) on the next request — expected for a zero-cost demo.

## Project structure

```text
src/randomgen/         # application package — app factory, service, OpenAPI contract
  domain/              # framework-free core: generators, histogram, Chi-Square, errors
  blueprints/          # web + versioned-API route blueprints
  templates/, static/  # home-page UI (Jinja + CSS/JS)
tests/                 # pytest suite — unit, integration, e2e
scripts/               # demo, plotting, and API client helpers
docs/                  # arc42 architecture, ADRs, history, assets
pyproject.toml         # PEP 621 metadata, dependencies, tool config
Dockerfile             # non-root, gunicorn, digest-pinned base image
render.yaml            # Render free-tier deploy blueprint
gunicorn.conf.py       # gunicorn runtime config (bind + workers)
.github/workflows/     # CI (gated jobs), CodeQL (SAST), CD (release + publish + deploy)
```

## Development

Supported Python: 3.14+.

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

The service is stateless: per-request behavior is set with query parameters
(see [Usage](#usage)), while deployment and limits are set by the keys below.

| Key | Where | Default | Description |
|-----|-------|---------|-------------|
| `RANDOMGEN_LOG_LEVEL` | env var | `INFO` | Application log level (one log line per request). |
| `WEB_CONCURRENCY` | env var | `2` | gunicorn worker count; see `gunicorn.conf.py`. |
| `PORT` | env var | `5000` | Listen port; gunicorn binds `$PORT` (the Flask dev server uses `5000`). |
| `MAX_NUMBERS` | `service.py` | `10000` | Upper bound on `numbers`. |
| Built-in distribution | `service.py` | `[-1,0,1,2,3]` / `[0.01,0.3,0.58,0.1,0.01]` | `DEFAULT_NUMBERS` / `DEFAULT_PROBABILITIES`. |

## Contributing

Contributions are welcome. Set up your environment from
[Development](#development) above, follow the project conventions and session
workflow in [CLAUDE.md](CLAUDE.md), and open a PR — one concern per PR,
conventional commits, and green CI before merge (`main` is branch-protected).

## Next steps

- For the full REST contract, see [`src/randomgen/openapi.yaml`](src/randomgen/openapi.yaml) (rendered at `/docs`).
- For the architecture, see the [arc42 documentation](docs/arc42/).
- For how it was built — from coding kata to deployed service — see [docs/history/](docs/history/).
- To contribute, see [Contributing](#contributing) above.
- To leave feedback, open a [discussion](https://github.com/braboj/randomgen/discussions).
