# Onboarding — RandomGen

Guide for new contributors. See `CLAUDE.md` for the full rule set and
`docs/PLAYBOOK.md` for day-to-day operations.

## 1. Prerequisites

- **Python 3.14** (CI pins 3.14.6)
- **pip** (the project uses `pyproject.toml`, not poetry/uv)
- **Podman or Docker** — to build/run the image and drive the e2e container
  tests. Podman is recommended for e2e (rootless, no wedging daemon; see
  PLAYBOOK §3.5); Docker also works.
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
pytest                                          # all tests should pass
flask --app "randomgen.app:create_app" run      # starts the API on 127.0.0.1:5000
```

With the server running, open <http://localhost:5000/> — you should see
the home page (an interactive UI for the API). A quick smoke check:

```text
http://localhost:5000/api/v1/randomgen?numbers=100
```

This returns a JSON payload with 100 generated numbers.

## 4. Key files

| File | Why read it |
|------|-------------|
| `CLAUDE.md` | Project rules, conventions, and commands |
| `src/randomgen/app.py` | `create_app()` factory + error handler |
| `src/randomgen/blueprints/` | Web + versioned API blueprints (the HTTP routes) |
| `src/randomgen/versions.py` | `API_VERSIONS` registry — where a new API version is added |
| `src/randomgen/service.py` | `RandomGenService` — request orchestration |
| `src/randomgen/domain/core.py` | `RandomGenV1` / `RandomGenV2` generators |
| `tests/` | Executable specification of expected behavior |
| `Dockerfile` | How the image is built and run |
| `docs/arc42/` | arc42 architecture documentation |
| `.github/workflows/` | `ci` (gated jobs: lint, type, test, build, e2e, secret-scan), `codeql` (SAST), `cd` (publish + deploy) |

## 5. Project context

RandomGen exposes a small REST API for generating random numbers from a
configurable discrete probability distribution. Generation is pure
compute (via `scipy`) — there is no database. The service ships as a
Docker image (deployable as a free Render demo) and its architecture is
documented with arc42 under `docs/arc42/`.

Quality conventions are vendored under `docs/solid-ai-templates/` (a git
submodule) and referenced from `CLAUDE.md`.

## 6. Daily workflow

See `docs/PLAYBOOK.md`:

- Git workflow → PLAYBOOK 1
- Adding or changing an endpoint → PLAYBOOK 2
- Running tests and linting → PLAYBOOK 3
- Updating dependencies and docs → PLAYBOOK 4
- Release and deploy → PLAYBOOK 5
