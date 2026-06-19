# 9. Architecture Decisions

The significant decisions visible in the repository, summarized as lightweight
ADRs. They are consistent with the constraints in
[Section 2](02-architecture-constraints.md) and the strategy in
[Section 4](04-solution-strategy.md).

## AD-1 — src layout + application factory + blueprint

**Decision.** Package under `src/randomgen/`; build the Flask app with a
`create_app()` factory in `app.py`; register routes via a Flask `Blueprint`
(`bp`) in `routing.py`.
**Why.** The factory lets each gunicorn worker build its own app with no import
side effects, and isolates the error handler; the blueprint keeps routes
declarative and the handlers thin. The src layout prevents accidental imports
of the working tree and makes the installed package the unit under test.
**Consequences.** Handlers stay thin (parse → delegate → serialize); the
service (`endpoints.py`) and core (`core.py`) are framework-independent and unit
testable without Flask.

## AD-2 — `pyproject.toml` + ruff/mypy over `setup.py` + flake8

**Decision.** Use a single PEP 621 `pyproject.toml` for metadata, dependencies,
and tool config; gate quality with `ruff` (lint + format) and `mypy` instead of
`flake8`.
**Why.** One descriptor, `test`/`dev` extras, and a faster, broader lint/format
toolchain (`E,W,F,I,UP,B,C4,SIM`) with optional static typing.
**Consequences.** CI runs `ruff check` + `ruff format --check` + `mypy` +
`pytest`. `scipy` ships no stubs, so mypy uses `ignore_missing_imports`. The
[CLAUDE.md](../../CLAUDE.md) conventions (§2.2–§2.4) describe this same src +
`pyproject` + ruff/mypy setup.

## AD-3 — Per-request, stateless distribution

**Decision.** Hold no configuration server-side. The distribution defaults to a
built-in one and is overridable **per request** (`dist` pairs, or repeated
`value`/`probability`).
**Why.** Each request is self-contained, which makes the service trivially
horizontally scalable and removes any config endpoint or persistence.
**Consequences.** A shared, stateless `RandomGenRestApi`; no shared mutable
state across workers. (The early journal mentioned a `/api/v1/config` endpoint;
the shipped design replaced it with per-request parameters.)

## AD-4 — `dist` value:probability pairs alongside legacy parameters

**Decision.** Add a `dist=value:probability,...` parameter that takes
precedence over the older repeated `value`/`probability` parameters.
**Why.** Binding each value to its own weight makes a **misaligned**
distribution impossible to express; the repeated parameters are retained for
backward compatibility.
**Consequences.** `parse_dist_pairs` raises `RandomGenDistFormatError` on
malformed pairs; `dist` wins when both are present.

## AD-5 — Versioned API as a stable public contract

**Decision.** Expose two interchangeable generators at `/api/v1` and `/api/v2`;
freeze each version's behavior — a behavior change means a new version.
**Why.** Predictable, non-breaking evolution for consumers.
**Consequences.** V1 and V2 differ only in the generator; parameters, response
shape, and status codes are identical.

## AD-6 — Two generator implementations behind one interface

**Decision.** `RandomGenABC` defines the contract; `RandomGenV1` uses manual
inverse-CDF sampling over `random.random()`, `RandomGenV2` uses
`random.choices`.
**Why.** Demonstrate two valid approaches behind one interface and let callers
compare them; it also decouples client code from the implementation
([solution.md](../solution.md) §5).
**Consequences.** V1 measured ~3× faster than V2 in the journal; V1 needs a
floating-point guard to never return `None`.

## AD-7 — Chi-Square goodness-of-fit reporting via scipy

**Decision.** Score every sample with a Chi-Square test (`ChiSquareTest`),
using `scipy.stats.chi2` for the p-value, and return the result inline.
**Why.** Makes fairness objective and observable; a correct CDF is hard to hand-
roll ([solution.md](../solution.md) §4). The explicit expected-category domain
ensures never-observed categories still contribute to the statistic.
**Consequences.** `scipy` is a runtime dependency; larger samples give a more
meaningful verdict (`DEFAULT_QUANTITY = 1000`).

## AD-8 — gunicorn + hardened Docker image

**Decision.** Serve via gunicorn inside a non-root, digest-pinned Alpine image
with a `/health` `HEALTHCHECK`, binding `${PORT:-5000}`.
**Why.** Production-grade WSGI serving, reproducible and minimal image,
least-privilege, and PaaS-friendly port injection.
**Consequences.** The local Flask dev server (`flask run`) is convenience-only;
debug stays off everywhere. The legacy `webserver.py` entrypoint was removed
(v0.8.x) — dev uses `flask --app "randomgen.app:create_app" run`, prod uses
gunicorn, and there is no third launch path to keep in sync.

## AD-9 — Render free web service for a zero-cost demo

**Decision.** Provide a `render.yaml` blueprint that deploys the existing image
as a free Render web service (auto-deploy on commit, `/health` check).
**Why.** A public, zero-cost demo straight from the Dockerfile.
**Consequences.** Free instances cold-start after ~15 min idle — acceptable for
a demo (see [Section 11](11-risks-and-technical-debt.md)).

## AD-10 — arc42 architecture documentation

**Decision.** Document the architecture with the arc42 template (this set of
files under `docs/arc42/`), replacing the previous MkDocs documentation site
(`mkdocs.yml`, the generated reference/test pages, and the Pages workflow were
removed in v0.6.0).
**Why.** A standard, navigable architecture reference grounded in the code, with
no build step — plain Markdown that renders on GitHub.
**Consequences.** Each section is one Markdown file with Mermaid diagrams,
cross-linked to the code and the remaining hand-written docs
([rest_api.md](../rest_api.md), [problem.md](../problem.md),
[solution.md](../solution.md)).

## AD-11 — Inline the enforced end-of-session checklist

**Decision.** Inline the full end-of-session audit — with the "print and
execute sequentially, do not summarize" enforcement — into
[CLAUDE.md](../../CLAUDE.md) §6.3, instead of relying on a soft
`Follow scope.md` reference.
**Why.** The hybrid generation had paraphrased `scope.md`'s audit into a lossy
4-bullet summary that dropped most steps and the enforcement, so "wrap up"
produced a thin close-out. CLAUDE.md is auto-loaded into the agent's context;
referenced template files are not — so a *procedural* checklist must be inlined
(or actively loaded on the trigger), never paraphrased, to be reliably executed.
**Consequences.** §6.3 carries the 14-item checklist verbatim; the upstream
generation-fidelity defect is tracked as `braboj/solid-ai-templates#498`, which
proposes a reusable `wrap-up` skill/command/hook as the on-demand loader.
