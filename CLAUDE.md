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
- **Distribution**: Docker image `braboj/randomgen`; docs on GitHub Pages
- **Version**: `setup.py` (`VERSION`) — currently `0.0.2.0`

### 1.2 Project structure

```
randomgen/             # application package (flat layout, no src/)
  __init__.py
  core.py              # RandomGenV1 / RandomGenV2 — generator classes
  endpoints.py         # RandomGenRestApi — endpoint/service logic
  errors.py            # custom exception types
  histogram.py         # histogram helper
  hypothesis.py        # statistical hypothesis testing
  routing.py           # Flask `app` + route handlers (module-level app)
webserver.py           # local-dev entrypoint (Docker serves via gunicorn)
setup.py               # package metadata (VERSION, URL)
requirements.txt       # runtime deps: scipy, flask, gunicorn
scripts/               # demo, plotting, and API-design helper scripts
tests/                 # pytest suite (test_core, test_endpoints, ...)
docs/                  # MkDocs site (readthedocs theme)
  solid-ai-templates/  # vendored template system (git submodule)
mkdocs.yml             # docs site config
Dockerfile             # python:3.12-alpine, EXPOSE 5000
.github/workflows/     # test_application, deploy_image, deploy_pages
```

- The package is a flat `randomgen/` at the repo root, NOT a `src/`
  layout. Keep new modules inside `randomgen/`.
- Route handlers stay thin — they parse input, call a
  `RandomGenRestApi` method, and return JSON. Business logic lives in
  `endpoints.py` / `core.py`, never in `routing.py`.

### 1.3 Commands

```bash
# Install
pip install -r requirements.txt          # runtime (scipy, flask)
pip install -r tests/requirements.txt     # test deps (pytest, requests)

# Run the service
python webserver.py                       # serves on 0.0.0.0:5000
flask --app randomgen.routing run         # Flask dev server (hot reload)

# Test
pytest                                    # run the full test suite

# Lint (as CI runs it)
flake8 . --select=E9,F63,F7,F82 --show-source --statistics

# Docs (MkDocs)
mkdocs serve                              # preview docs at :8000
mkdocs build                              # build static site -> site/
python scripts/gen_ref_pages.py           # regenerate API reference pages

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
- SemVer with `v`-prefixed tags. Bump `VERSION` in `setup.py` for a
  release.
- Do not commit: `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`,
  `dist/`, `.mypy_cache/`, `.pytest_cache/`, `site/`, `.idea/`, `.env`.
  These are covered by `.gitignore` — keep it that way.
- Do not commit secrets or credentials — treat the repo as public.

### 2.2 Python (inlined — see `templates/stack/python-lib.md`)

- Follow PEP 8 for style; CI gates syntax/undefined-name errors via
  `flake8` (`E9,F63,F7,F82`).
- Follow PEP 257 (Google-style docstrings) — every public module,
  class, and function has a docstring, matching the existing modules.
- Annotate public function signatures (PEP 484/526) where practical.
- Raise specific exceptions from `randomgen/errors.py` — never a bare
  `except:`. (The single Flask `@app.errorhandler(Exception)` in
  `routing.py` is the deliberate API error boundary, not a catch-all in
  business logic.)
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

### 2.4 Known divergences from the referenced templates

The templates describe an idealized Python service. This project
deliberately differs — follow the project's actual conventions above,
and only adopt a template default as part of an intentional, separate
change:

- Flat `randomgen/` package instead of the `src/` layout.
- Module-level `app` in `routing.py` instead of the `create_app`
  factory + blueprints pattern.
- `setup.py` + `requirements.txt` instead of `pyproject.toml`.
- `flake8` + `pytest` in CI; the templates recommend `ruff` + `mypy
  --strict` (not currently configured).

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
- **CI** (`.github/workflows/`): `test_application.yml` runs flake8 +
  pytest on push/PR to `main`; `deploy_image.yml` publishes the Docker
  image; `deploy_pages.yml` builds and deploys the MkDocs site.
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
