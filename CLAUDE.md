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
- **Version**: `pyproject.toml` (`[project].version`) — currently `0.8.0`

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
  templates/           # Jinja templates (index.html home-page UI)
  static/              # CSS/JS for the home-page UI (packaged in the wheel)
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

# Run the service (local dev — Flask dev server, hot reload, 127.0.0.1:5000)
flask --app "randomgen.app:create_app" run

# Test (fast gate = unit + integration; e2e is opt-in)
pytest                                        # unit + integration (excludes e2e)
pip install -e ".[e2e]" && playwright install chromium  # one-time, for e2e
pytest -m e2e                                 # container (Podman/Docker) + Playwright

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
- Issue labels follow the solid-ai-templates standard
  (`docs/solid-ai-templates/templates/platform/github.md` + ADR-002):
  every issue gets exactly one type (`bug`/`epic`/`task`/`spike`/
  `incident`) + one priority (`P0`–`P4`) label, plus a milestone
  (`Backlog`, or `Expedite` for small out-of-cycle work).
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
  production. The Docker image serves the app with `gunicorn`; local dev
  uses `flask --app "randomgen.app:create_app" run` and MUST stay debug-off.
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
- The Docker image serves with `gunicorn`; local dev uses the Flask dev
  server (`flask --app "randomgen.app:create_app" run`).

---

## 3. Quality

Testing, coverage thresholds, security, CI/CD, and containers follow the
referenced templates. Project specifics:

- **Tests**: `pytest`, tiered by directory and auto-marked by
  `tests/conftest.py`: top-level `tests/*` are `unit`, `tests/integration/`
  is `integration`, `tests/e2e/` is `e2e`. The default `pytest` runs the
  fast gate (unit + integration, 85% coverage); `e2e` is opt-in via
  `pytest -m e2e` and needs `.[e2e]` (Testcontainers on a Podman/Docker
  backend + Playwright). Run the fast gate before every commit.
- **Test naming**: `test_<unit>_<state>_<expected>` for new tests
  (`templates/base/core/testing.md`).
- **CI** (`.github/workflows/`): `test_application.yml` runs ruff +
  mypy + the fast pytest gate (85% coverage) plus a separate `e2e` job
  (Testcontainers on **Podman** + Playwright) and a gitleaks secret scan
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
end-of-session audit. **The agent MUST enforce this protocol. If the user
deviates, remind them.**

### 6.1 Start of session

1. Check which branch we're on — if not `main`, ask why.
2. Check `git status` — resolve any uncommitted changes before starting.
3. Clean up stale branches: `git fetch --prune`, then
   `git branch --merged main | grep -v main` to delete merged local
   branches.
4. Check deploy health: `gh run list --branch main --limit 1` — if the
   latest run is not `completed/success`, flag it before starting work.
5. Check open PRs: `gh pr list --state open` — flag Dependabot bumps and
   stale PRs.
6. Agree ONE scope/theme with the user before changing code.
7. Review open issues for that scope first.

### 6.2 During the session

- **One theme per session.** If an unrelated topic comes up, file a GitHub
  issue for it and say: "Noted as #X — let's come back to it next session."
- **Always branch before coding.** No commits directly to `main`
  (protected) — no exceptions.
- **Run the gate after every change**, don't accumulate unverified work:
  `ruff check . && ruff format --check . && mypy` then `pytest` (and
  `pytest -m e2e` if the container/UI was touched).
- Keep `CLAUDE.md`, `README.md`, `docs/ONBOARDING.md`, and
  `docs/PLAYBOOK.md` in sync when conventions, commands, or structure
  change.
- When a path-based shell check returns an unexpected empty/negative,
  verify the working directory first (`pwd`) — the shell cwd persists
  across commands.

### 6.3 End of session

When the user signals end of session ("wrap up", "let's finish", "end
session", "close out", or similar), print the full checklist below and
execute each item sequentially. Mark each item done (with result) before
moving to the next. Do not batch, skip, or summarize — visible sequential
execution prevents missed steps.

```
[ ] 1.  All changes committed and pushed (via PR — `main` is protected)
[ ] 2.  Close completed issues (verify auto-close); for stacked PRs,
        confirm content actually landed on `main`
[ ] 3.  Dev journal — add a `### Session N` entry to docs/dev-journal.md
        (date, tool, PRs merged, issues closed, key changes, key decisions
        with ADR refs)
[ ] 4.  Memory pointer — update the auto-memory (the project memory dir +
        its MEMORY.md index) to the current state and the next priority;
        it is NOT synced from git, so if skipped it silently goes stale
[ ] 5.  ADRs — record architectural decisions in docs/decisions/. Trigger:
        any new directory created or content moved between documents →
        each one needs an ADR
[ ] 6.  CLAUDE.md — for each new convention, apply the doc-placement
        decision tree (code → ADR → README → PLAYBOOK → CLAUDE.md →
        memory). CLAUDE.md is rules only — not changelogs, architecture,
        or session logs; each rule fits one line, else write an ADR and
        leave a one-line pointer. Evaluate items individually
[ ] 7.  README.md — for each new command, dependency, or structural
        change, is it reflected? Name the section
[ ] 8.  ONBOARDING.md — for each new tool, prerequisite, or setup step,
        is it documented? Name the section
[ ] 9.  PLAYBOOK.md — list every new command/script introduced, then
        check each is documented. Name the section. Do not batch-dismiss
[ ] 10. Gate green — run `ruff check . && ruff format --check . && mypy`
        and `pytest` (plus `pytest -m e2e` if e2e was touched); confirm
        they pass before closing
[ ] 11. Submodule — does `docs/solid-ai-templates` need an upstream bump?
[ ] 12. Flag reusable conventions for solid-ai-templates upstream — list
        each new convention/decision by name and evaluate individually
        (no blanket "nothing reusable"). For each: project-specific or
        reusable? If reusable, name the upstream template file and file
        an issue
[ ] 13. Branch cleanup — delete merged branches (local + remote)
[ ] 14. Summarize what was done and what's next
```

<!-- Generated with solid-ai-templates (github.com/braboj/solid-ai-templates) -->
