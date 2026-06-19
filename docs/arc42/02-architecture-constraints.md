# 2. Architecture Constraints

Constraints are fixed conditions the architecture must respect. They come from
the technology stack, the project's coding conventions, and the nature of the
problem.

## 2.1 Technical constraints

Technical constraints fix the technology the service is built on: the language,
framework, libraries, and runtime.

| ID | Constraint |
|------|------------|
| T01 | The service requires Python 3.12 or later. |
| T02 | The service is built on the Flask web framework. |
| T03 | The Chi-Square statistics are computed with scipy, whose cumulative distribution function is non-trivial to implement reliably by hand. |
| T04 | gunicorn is the production WSGI server. |
| T05 | The service uses no database or persistent storage; each result is computed per request. |

## 2.2 Organizational and convention constraints

Organizational and convention constraints fix how the code is structured and
how the team works.

| ID | Constraint |
|------|------------|
| O01 | The package source lives in a src layout. |
| O02 | pyproject.toml holds all project metadata, dependencies, and tool settings. |
| O03 | ruff (lint and format) and mypy (type checks) are the quality gates. |
| O04 | A test-coverage gate must pass before code is merged. |
| O05 | Route handlers stay thin: they parse input, call the service, and return the result; the logic lives elsewhere. |
| O06 | Code raises specific, named errors rather than generic ones. |
| O07 | Work happens on branches through pull requests; the main branch is protected. |
| O08 | Commits follow Conventional Commits, and releases use SemVer. |

## 2.3 Security and runtime constraints

Security and runtime constraints fix how the service is run and kept safe.

| ID | Constraint |
|------|------------|
| S01 | The service never runs with debug mode enabled in production. |
| S02 | The container runs as a non-root user. |
| S03 | The container uses one fixed base image, so every rebuild produces the same result rather than quietly picking up a newer, untested base. |
| S04 | The repository holds no secrets and is treated as public. |
| S05 | The service binds to the port the hosting platform provides. |
