# RandomGen

A Flask REST API that generates random numbers from a configurable
discrete distribution, packaged as a Docker image.

Quality conventions are defined in `docs/solid-ai-templates/` (git
submodule). This file inlines the rules that cause the most damage when
missed (git, structure, Python/Flask safety) and references the
submodule for the full quality framework.

Key references (the `stack-flask` dependency chain):

- Stack: `templates/stack/python-flask.md`,
  `templates/stack/python-service.md`, `templates/stack/python-lib.md`
- Core: `templates/base/core/quality.md`, `.../git.md`, `.../docs.md`,
  `.../readme.md`, `.../testing.md`, `.../config.md`, `.../oop.md`
- Backend: `templates/backend/http.md`, `.../database.md`,
  `.../observability.md`, `.../quality.md`, `.../features.md`,
  `.../messaging.md`
- Security: `templates/base/security/security.md`, `.../devsecops.md`
- Infra: `templates/base/infra/containers.md`, `.../cicd.md`
- Data: `templates/base/data/data-modeling.md`, `.../data-quality.md`
- Workflow: `templates/base/workflow/quality-gates.md`,
  `templates/base/workflow/scope.md`
- Review: `templates/base/core/review.md`

Project-specific overrides and additions follow below.

---

## 1. Project

### 1.1 Identity

- **Model**: hybrid — read the referenced templates before starting work
- **Name**: RandomGen
- **Owner**: Branimir Georgiev
- **Repo**: github.com/braboj/randomgen
- **Stack**: Python 3.12 + Flask 3.x, scipy for distributions
- **Distribution**: Docker image `braboj/randomgen`; Render free demo;
  arc42 docs in `docs/arc42/`
- **Version**: `pyproject.toml` (`[project].version`) — currently `0.6.0`

### 1.2 Project structure

```
src/randomgen/         # application package (src layout)
  __init__.py          # exposes __version__ (from installed metadata)
  app.py               # create_app() factory + error handler
  core.py              # RandomGenV1 / RandomGenV2 — generator classes
  endpoints.py         # RandomGenRestApi — endpoint/service logic
  errors.py            # custom exception types
  histogram.py         # histogram helper
  hypothesis.py        # statistical hypothesis testing
  routing.py           # Flask Blueprint `bp` + thin route handlers
webserver.py           # local-dev entrypoint (Docker serves via gunicorn)
pyproject.toml         # PEP 621 metadata, deps, ruff/mypy/pytest config
scripts/               # demo, plotting, and API-design helper scripts
tests/                 # pytest suite (test_core, test_endpoints, ...)
render.yaml            # Render free-tier deploy blueprint
docs/arc42/            # arc42 architecture documentation
docs/                  # REST reference, problem/solution notes, guides
  solid-ai-templates/  # vendored template system (git submodule)
Dockerfile             # python:3.12-alpine, EXPOSE 5000
.github/workflows/     # test_application, deploy_image
```

- The package uses a `src/` layout. Keep new modules inside
  `src/randomgen/`. The app is built by the `create_app()` factory in
  `app.py`; routes live on the `bp` Blueprint in `routing.py`.
- Route handlers stay thin — they parse input, call a
  `RandomGenRestApi` method, and return JSON. Business logic lives in
  `endpoints.py` / `core.py`, never in `routing.py`.

### 1.3 Commands

```bash
# Install (editable, with the dev toolchain: ruff, mypy, pytest, ...)
pip install -e ".[dev]"                       # or ".[test]" for the test gate only

# Run the service
python webserver.py                           # serves on 0.0.0.0:${PORT:-5000}
flask --app "randomgen.app:create_app" run    # Flask dev server (hot reload)

# Test
pytest                                        # run the full test suite

# Lint & type-check (as CI runs it)
ruff check .                                  # lint (supersedes flake8)
ruff format --check .                         # formatting gate
mypy                                          # static typing (config in pyproject)

# Docs — arc42 architecture docs are plain Markdown under docs/arc42/
#        (no build step; browse on GitHub or in any Markdown viewer)

# Docker
docker build -t braboj/randomgen .
docker run -p 5000:5000 braboj/randomgen
```

---

## 2. Code conventions

### 2.1 Git (inlined — see `templates/base/core/git.md` for the full set)

- Work on a branch — never commit directly to `main` (protected).
- Branch naming: `feat/<scope>`, `fix/<scope>`, `chore/<scope>`,
  `docs/<scope>`.
- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`,
  `test:`. Imperative mood, subject under 80 chars.
- One concern per PR; one approval and green CI required before merge.
- Never force-push. When a branch is behind `main`, merge `main` into
  it — do not rebase-and-force-push.
- After a PR merges: delete the branch and `git pull` on `main`.
- SemVer with `v`-prefixed tags. Bump `[project].version` in
  `pyproject.toml` for a release.
- Do not commit: `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`,
  `dist/`, `.mypy_cache/`, `.pytest_cache/`, `site/`, `.idea/`, `.env`.
  These are covered by `.gitignore` — keep it that way.
- Do not commit secrets or credentials — treat the repo as public.

### 2.2 Python (inlined — see `templates/stack/python-lib.md`)

- Follow PEP 8 for style; CI gates lint with `ruff check` (pyflakes
  E9/F-series included), formatting with `ruff format --check`, and types
  with `mypy`. Config lives in `pyproject.toml`.
- Follow PEP 257 (Google-style docstrings) — every public module,
  class, and function has a docstring, matching the existing modules.
- Annotate public function signatures (PEP 484/526) where practical.
- Raise specific exceptions from `randomgen/errors.py` — never a bare
  `except:`. (The single `Exception` handler registered in the
  `create_app()` factory in `app.py` is the deliberate API error
  boundary, not a catch-all in business logic.)
- No mutable default arguments. Keep functions small and single-purpose.

### 2.3 Flask / API (inlined — see `templates/stack/python-flask.md`)

- Versioned API paths (`/api/v1/...`, `/api/v2/...`) are a public
  contract — never change an existing version's behavior; add a new
  version instead.
- Parse and validate input explicitly: `request.args.get(..., type=...)`
  for query params, validate required keys for JSON bodies.
- Return responses with `jsonify(...)` and an appropriate HTTP status
  code; prefer `abort(code)` over raising raw exceptions in handlers.
- Centralized error handling returns JSON `{ "error": ... }` with a
  status code — keep this contract stable.
- Never ship with `debug=True` / `FLASK_DEBUG=1` in the Docker image or
  production. The Docker image serves the app with `gunicorn`;
  `webserver.py` is a local-dev convenience and MUST stay debug-off.
- No database or ORM — generation is pure compute via `scipy`. The
  `backend/database.md` and data-migration rules in the referenced
  templates do NOT apply to this project.

### 2.4 Alignment with the referenced templates

As of **v0.4.0** the project follows the modern Python-service layout the
templates describe. The previously-documented divergences have been
resolved:

- `src/` layout (`src/randomgen/`) — done.
- `create_app()` factory + a route Blueprint instead of a module-level
  `app` — done (`app.py` / `routing.py`).
- `pyproject.toml` (PEP 621) instead of `setup.py` + `requirements.txt` —
  done; runtime deps and the `dev`/`test` extras live there.
- `ruff` (lint + format) and `mypy` instead of `flake8` — done; CI runs
  all three plus `pytest`.

Remaining, intentional project choices (not divergences to "fix"):

- `mypy` runs in pragmatic mode, not `--strict` (scipy ships no stubs).
- Tests live in a top-level `tests/` dir (not under `src/`).
- The Docker image serves with `gunicorn`; `webserver.py` is local-dev
  only.

---

## 3. Quality

Testing, coverage thresholds, security, CI/CD, and containers follow the
referenced templates. Project specifics:

- **Tests**: `pytest`, suite under `tests/` (one file per module:
  `test_core.py`, `test_endpoints.py`, `test_histogram.py`,
  `test_hypothesis.py`, `test_routing.py`). Run `pytest` before every
  commit. Route tests use Flask's `test_client()`.
- **Test naming**: `test_<unit>_<state>_<expected>` for new tests
  (`templates/base/core/testing.md`).
- **CI** (`.github/workflows/`): `test_application.yml` runs ruff +
  mypy + pytest (with an 85% coverage gate) and a gitleaks secret scan
  on push/PR to `main`; `deploy_image.yml` publishes the Docker image on
  version tags. (Docs are arc42 Markdown in `docs/arc42/`; there is no
  docs-site build.)
- **Security / containers**: apply `templates/base/security/security.md`,
  `.../devsecops.md`, and `templates/base/infra/containers.md` — keep the
  Docker base image pinned by digest (as it already is) and run as a
  non-root user where possible.

## 4. Identity

Not applicable — this is a backend service with no design system or
brand voice.

## 5. Review process

Follow `templates/base/core/review.md` priority order — security →
correctness → clarity → conventions — and apply
`templates/base/core/quality.md`, `templates/backend/quality.md`, and the
Python/Flask stack templates as the standard. For an API change, confirm
existing `/api/v1` and `/api/v2` behavior is unchanged.

## 6. Session protocol

Follow `templates/base/workflow/scope.md` for the scope guard and
end-of-session audit.

### 6.1 Start of session

- Read this file and the relevant referenced templates.
- Check for stale branches (`git branch --no-merged main`) and confirm
  the scope with the user before changing code.

### 6.2 During the session

- Run `pytest` after any change to `randomgen/`.
- Keep `CLAUDE.md`, `README.md`, `docs/ONBOARDING.md`, and
  `docs/PLAYBOOK.md` in sync when conventions, commands, or structure
  change.
- When a path-based shell check returns an unexpected empty/negative,
  verify the working directory first (`pwd`) — the shell cwd persists
  across commands.

### 6.3 End of session

- Commit and push via a PR (branch is protected).
- Add a session entry to `docs/dev-journal.md` (date, tool, key changes).
- Run `pytest` and confirm it passes.
- Update `CLAUDE.md` only for rules the agent must apply every turn;
  everything else goes in the README, PLAYBOOK, or an ADR under
  `docs/decisions/`.

<!-- Generated with solid-ai-templates (github.com/braboj/solid-ai-templates) -->
