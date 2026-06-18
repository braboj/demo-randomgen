# 2. Architecture Constraints

Constraints are fixed conditions the architecture must respect. They come from
the technology stack, the project conventions in [CLAUDE.md](../../CLAUDE.md),
and the nature of the problem.

## 2.1 Technical constraints

| # | Constraint | Source / consequence |
|---|------------|----------------------|
| T1 | **Python 3.12+** | `requires-python = ">=3.12"` in [`pyproject.toml`](../../pyproject.toml). Code uses 3.12-era features (e.g. `zip(..., strict=...)`). |
| T2 | **Flask 3.x** as the web framework | `flask~=3.1.3` dependency; app uses the factory + blueprint API. |
| T3 | **scipy** for the Chi-Square CDF | `scipy~=1.17.1`; `chi2.cdf` computes the p-value. Pulled in because the CDF is non-trivial to implement well by hand (see [solution.md](../solution.md) §4). |
| T4 | **gunicorn** as the production WSGI server | `gunicorn~=26.0`; the container `CMD` runs `gunicorn 'randomgen.app:create_app()'`. |
| T5 | **No database / no persistence** | Generation is pure compute; the database and data-migration template rules explicitly do **not** apply (CLAUDE.md §2.3). |
| T6 | **Stateless service** | No mutable state survives a request, so a single `RandomGenRestApi` instance is shared safely across gunicorn workers. |
| T7 | **`random` standard library** for sampling | Mersenne-Twister PRNG — fast and uniform, but **not cryptographically secure**. |

## 2.2 Organizational and convention constraints

| # | Constraint | Source |
|---|------------|--------|
| O1 | **src layout** — package lives under `src/randomgen/`. | `[tool.setuptools.packages.find] where = ["src"]`. |
| O2 | **`pyproject.toml` (PEP 621)** is the single source of metadata, deps, and tool config. | Replaces the older `setup.py` + `requirements.txt`. |
| O3 | **`ruff`** (lint + format) and **`mypy`** are the quality gates, not `flake8`. | `[tool.ruff]`, `[tool.mypy]`; CI `test_application.yml`. |
| O4 | **85% test coverage gate** enforced in CI. | `pytest --cov-fail-under=85`. |
| O5 | **Versioned API paths are a public contract** — never change `/api/v1` or `/api/v2` behavior; add a new version instead. | CLAUDE.md §2.3. |
| O6 | **Thin route handlers** — parse/validate, delegate to the service, serialize. Business logic never lives in `routing.py`. | CLAUDE.md §1.2. |
| O7 | **Specific exceptions only** — raise the typed errors in `errors.py`; the single `Exception` handler registered in `create_app()` is the deliberate API boundary, not a catch-all in business logic. | CLAUDE.md §2.2. |
| O8 | **Branch + PR workflow**; never commit to protected `main`. | CLAUDE.md §2.1. |
| O9 | **Conventional Commits**, SemVer with `v`-prefixed tags; `version` lives in `pyproject.toml` (currently `0.6.0`). | CLAUDE.md §2.1. |

## 2.3 Security and runtime constraints

| # | Constraint | Source |
|---|------------|--------|
| S1 | **Never ship with `debug=True`** in the image or production. | CLAUDE.md §2.3; `webserver.py` keeps debug off; gunicorn serves in the image. |
| S2 | **Run as a non-root user** in the container. | `Dockerfile` creates and switches to `appuser`. |
| S3 | **Base image pinned by digest.** | `python:3.12.2-alpine3.19@sha256:c7eb5c…`. |
| S4 | **No secrets in the repo** — treat it as public; CI runs a **gitleaks** secret scan. | CLAUDE.md §2.1; `test_application.yml`. |
| S5 | **Bind `${PORT:-5000}`** so PaaS platforms (Render) can inject the port. | `Dockerfile` `CMD`, `webserver.py`. |

CLAUDE.md §2.4 records how the project aligns with the referenced quality
templates (src layout, app factory, `pyproject.toml`, ruff + mypy). Related
decisions are recorded in [Section 9](09-architecture-decisions.md).
