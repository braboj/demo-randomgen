---
id: "AD-31"
status: Accepted
date: 2026-06-24
category: technology
supersedes: []
superseded_by: []
---

# AD-31 — Adopt Python 3.14 across the runtime, CI gate, and toolchain

## Context

The published Docker image — the project's primary distribution artifact — ran
on `python:3.12.x-alpine`, and the rest of the project was pinned to 3.12 to
match: the CI gate set up Python 3.12.2, `ruff`/`mypy` targeted 3.12,
`requires-python` was `>=3.12`, and the documented stack said 3.12.

Dependabot's docker ecosystem (AD-29) then proposed bumping the base image to
`python:3.14.6-alpine3.24` (#259). Merged on its own, that bump would ship 3.14
while the unit, integration, type, and lint gates still validated 3.12 — a
dev/prod skew, with only the e2e job (which builds and runs the image) actually
exercising the shipped runtime. `scipy` 1.18 — the one heavy runtime dependency,
adopted in #262 — supports Python 3.12–3.14, so no dependency blocked the move.

## Decision

Adopt Python 3.14 everywhere in one coordinated change rather than merge the
base-image bump in isolation.

1. **Runtime.** The Dockerfile `FROM` moves to `python:3.14.6-alpine3.24`,
   digest-pinned — the change #259 proposed.
2. **CI gate.** All six `ci.yml` jobs set up Python 3.14.6, the exact version the
   image ships, so every gate (lint, typecheck, test, build, e2e) validates the
   production runtime rather than a trailing one.
3. **Toolchain and metadata.** `mypy` `python_version` → `3.14` and
   `requires-python` → `>=3.14`, so the package declares the version it is tested
   and shipped on, with no untested-compatibility claim. `ruff`'s `target-version`
   is held one minor behind, at `py313`, as a deliberate style floor (see the
   alternatives).
4. **Docs.** The stack line (CLAUDE.md), the prerequisite (ONBOARDING), the
   supported-version note (README), the arc42 constraint T01 and the §7
   base-image row, and the `dependabot.yml` comment all move to 3.14.

PR #259 is closed as superseded by this change, which includes its Dockerfile
bump.

## Alternatives considered

- **Merge #259 alone** — rejected: it ships 3.14 while the correctness gate runs
  on 3.12, the exact dev/prod skew a version pin exists to prevent. Only e2e
  would cover the new runtime, and the toolchain and docs would silently drift.
- **Stay on the 3.12 line** (close #259, have Dependabot ignore 3.13/3.14) —
  viable and lower-effort, but nothing constrains the project to 3.12 (`scipy`
  1.18 supports 3.14), and a portfolio/demo is better off running the current
  runtime. Rejected in favour of moving forward deliberately.
- **Keep `requires-python` at `>=3.12` while testing/shipping 3.14** — rejected:
  it would advertise 3.12/3.13 support that no gate exercises. `requires-python`
  should track the runtime that is actually tested.
- **Move `ruff`'s `target-version` to `py314` too** — rejected: at `py314` the
  formatter rewrites `except (A, B):` to the parenthesis-free `except A, B:`
  form newly allowed in 3.14, which visually collides with the removed Python-2
  `except E, name:` syntax. For a portfolio read by evaluators, clarity outranks
  matching the runtime exactly on the lint/format style floor, so it stays at
  `py313` (a strict subset of 3.14 syntax); the code remains valid on 3.14.

## Consequences

- One runtime everywhere: the image, the CI gate, `ruff`/`mypy`, and
  `requires-python` all sit on 3.14.6, so what is tested is what is shipped.
- `requires-python >= 3.14` means the wheel no longer installs on 3.12/3.13 —
  acceptable because distribution is the Docker image and the source is validated
  only on 3.14.
- Dependabot's docker ecosystem now keeps the 3.14 line fresh; the next minor
  jump (3.15) is again a deliberate, coordinated decision, not an automatic merge.
- CI's Python is pinned exactly to the image's 3.14.6 (previously CI's 3.12.2
  trailed the image's 3.12.13). Future base bumps must update `ci.yml` in
  lockstep to preserve that parity.
