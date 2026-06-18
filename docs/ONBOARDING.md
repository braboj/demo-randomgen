# Onboarding — RandomGen

Guide for new contributors. See `CLAUDE.md` for the full rule set and
`docs/PLAYBOOK.md` for day-to-day operations.

## 1. Prerequisites

- **Python 3.12** (CI pins 3.12.2)
- **pip** (the project uses `pyproject.toml`, not poetry/uv)
- **Docker** — to build and run the container image
- **Git** — with `--recurse-submodules` support (the docs templates are
  a submodule)

## 2. First-time setup

```bash
# Clone with the solid-ai-templates submodule
git clone --recurse-submodules https://github.com/braboj/randomgen.git
cd randomgen

# If you already cloned without submodules:
git submodule update --init --recursive

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install the project with the developer toolchain (ruff, mypy, pytest)
pip install -e ".[dev]"
```

## 3. Verify the setup

```bash
pytest                           # all tests should pass
python webserver.py              # starts the API on 0.0.0.0:5000
```

With the server running, open <http://localhost:5000/> — you should see
the home page listing the available endpoints. A quick smoke check:

```text
http://localhost:5000/api/v1/randomgen?numbers=100
```

This returns a JSON payload with 100 generated numbers.

## 4. Key files

| File | Why read it |
|------|-------------|
| `CLAUDE.md` | Project rules, conventions, and commands |
| `src/randomgen/app.py` | `create_app()` factory + error handler |
| `src/randomgen/routing.py` | Route Blueprint and all HTTP routes |
| `src/randomgen/endpoints.py` | `RandomGenRestApi` — endpoint logic |
| `src/randomgen/core.py` | `RandomGenV1` / `RandomGenV2` generators |
| `tests/` | Executable specification of expected behavior |
| `Dockerfile` | How the image is built and run |
| `.github/workflows/` | CI: tests, image deploy, pages deploy |

## 5. Project context

RandomGen exposes a small REST API for generating random numbers from a
configurable discrete probability distribution. Generation is pure
compute (via `scipy`) — there is no database. The service ships as a
Docker image and the documentation site is published to GitHub Pages.

Quality conventions are vendored under `docs/solid-ai-templates/` (a git
submodule) and referenced from `CLAUDE.md`.

## 6. Daily workflow

See `docs/PLAYBOOK.md`:

- Git workflow → PLAYBOOK 1
- Adding or changing an endpoint → PLAYBOOK 2
- Running tests and linting → PLAYBOOK 3
- Updating dependencies and docs → PLAYBOOK 4
- Release and deploy → PLAYBOOK 5
