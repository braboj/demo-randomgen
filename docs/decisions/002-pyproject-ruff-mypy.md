---
id: "AD-2"
status: Accepted
date: 2026-06-19
category: tooling
supersedes: []
superseded_by: []
---

# AD-2 — pyproject.toml + ruff/mypy over setup.py + flake8

## Context

Metadata, dependencies, and tool config were split across `setup.py` and
`requirements.txt`, and linting used `flake8` alone. This is fragmented,
slower, and narrower than a modern single-descriptor toolchain.

## Decision

1. **Single descriptor** — use one PEP 621 `pyproject.toml` for metadata,
   dependencies (with `test`/`dev` extras), and tool configuration.
2. **ruff + mypy** — gate quality with `ruff` (lint + format, rule sets
   `E,W,F,I,UP,B,C4,SIM`) and `mypy` instead of `flake8`.

## Alternatives considered

- **Keep `setup.py` + `requirements.txt` + `flake8`** — rejected;
  multiple descriptors to keep in sync, slower and narrower lint, no
  built-in formatter or typing gate.

## Consequences

- CI runs `ruff check` + `ruff format --check` + `mypy` + `pytest`.
- `scipy` ships no type stubs, so mypy uses `ignore_missing_imports`
  (pragmatic mode, not `--strict`).
- The [CLAUDE.md](../../CLAUDE.md) conventions (§2.2–§2.4) describe this
  same src + `pyproject` + ruff/mypy setup.
