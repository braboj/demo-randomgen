# Development Journal — RandomGen

Continuity log for agent-assisted development. Newest entries at the
bottom. Link to ADRs for decisions and to issues for task tracking — do
not duplicate the data model (it lives in `randomgen/`).

## Architecture overview

- **Service**: Flask REST API built by a `create_app()` factory
  (`src/randomgen/app.py`) with routes on a Blueprint
  (`src/randomgen/routing.py`) over a pure-compute random-number generator
  (`src/randomgen/core.py`, `src/randomgen/endpoints.py`). No database. A
  Jinja home-page UI (`templates/` + `static/`) exercises the API.
- **Build/quality**: `pyproject.toml` (PEP 621, src layout); `ruff` +
  `mypy` + tiered `pytest` (unit / integration / e2e).
- **Distribution**: Docker image `braboj/randomgen`; free Render demo via
  `render.yaml`; architecture documented with arc42 under `docs/arc42/`.
- **Quality conventions**: vendored under `docs/solid-ai-templates/`
  (git submodule), referenced from `CLAUDE.md` (hybrid model).

---

### Session 1 — Vendor templates and generate agent context

- Tool: Claude Code (Opus 4.8)
- Added `docs/solid-ai-templates` as a git submodule.
- Added a root `.gitignore` and `.gitattributes`; removed the local
  `.idea/` directory.
- Generated `CLAUDE.md` (hybrid model) from the `stack-flask` template
  dependency chain, plus `docs/ONBOARDING.md`, `docs/PLAYBOOK.md`, and
  this journal.
- Noted divergences from template defaults (flat package layout,
  module-level Flask `app`, `setup.py`, flake8/pytest) in `CLAUDE.md`
  section 2.4.

---

### Session 2 — Modernization (v0.4.0 → v0.8.0)

- Tool: Claude Code (Opus 4.8). Planned as five GitHub milestones
  (v0.4.0–v0.8.0) with issues #70–#89, delivered as five stacked PRs
  #90–#94 (merge in version order). Retired CLAUDE.md §2.4 — the project
  now follows the modern template layout.
- **v0.4.0 (#90)** — src layout (`src/randomgen/`), a `create_app()`
  factory with a route Blueprint, `pyproject.toml` replacing
  `setup.py`/`requirements*.txt`, `ruff` and `mypy` replacing flake8,
  Dockerfile/CI updated, and `$PORT` honored.
- **v0.5.0 (#91)** — `render.yaml` blueprint for a free Render web-service
  demo (cold-starts after idle).
- **v0.6.0 (#92)** — arc42 architecture docs under `docs/arc42/` (12
  sections + Mermaid diagrams); removed MkDocs and the Pages workflow.
- **v0.7.0 (#93)** — single Jinja home-page UI + CSS/JS exercising the API
  (served via `render_template`; assets packaged in the wheel).
- **v0.8.0 (#94)** — tiered tests (unit / integration / e2e), Testcontainers
  e2e on a **Podman** backend, Playwright browser e2e, and a CI `e2e` job.
  The Playwright test caught a real CSS bug (`[hidden]` overridden).

#### Ship & operate (post-merge)

- Merged all five PRs into `main` in version order. #91/#93 show CLOSED (not
  MERGED): a GitHub mergeability-computation race during the back-to-back
  stack merge blocked their direct merge, but because the branches were
  stacked their commits landed via #92/#94. Verified `main` green
  (ruff 0.15 + mypy 2.1, 175 unit+integration tests; CI `e2e` job passed).
- Tagged **`v0.8.0`** → `deploy_image.yml` published the image to Docker Hub.
- Connected the Render Blueprint; live demo at
  <https://randomgen-llyc.onrender.com/> (smoke-tested: health, both API
  versions, error contract, UI + static assets).
- Merged the Dependabot dev-tooling bump (#95: ruff 0.14→0.15, mypy 1.18→2.1,
  setuptools build req) after confirming the gates pass on `main`.
- Deleted all feature branches; `image_deployment.yml` confirmed as a long-
  renamed legacy (now `deploy_image.yml`) — no action needed.

---

### Session 3 — Documentation & session-protocol cleanup

- Tool: Claude Code (Opus 4.8). One theme: tighten the docs and the
  agent session protocol after the v0.8.0 ship. No code/behavior change;
  all PRs are docs/chore.
- **Journal catch-up (#97)** — recorded the post-merge "ship & operate"
  steps (tag, Docker Hub publish, Render demo, Dependabot #95) that closed
  out session 2.
- **Session protocol (#98)** — inlined the full enforced end-of-session
  checklist into [CLAUDE.md](../CLAUDE.md) §6.3 (14 items, "print and
  execute sequentially, do not summarize"), replacing a lossy 4-bullet
  paraphrase of `scope.md`. Recorded as **AD-11**; the upstream
  generation-fidelity defect is filed as `solid-ai-templates#498`
  (proposes a reusable `wrap-up` loader).
- **Drop CONTRIBUTING.md (#99, #100)** — removed the redundant
  `CONTRIBUTING.md`, folded a one-line Contributing pointer to CLAUDE.md
  into the README, and dropped its stale reference from
  [solution.md](history/solution.md). Single source of contribution rules =
  CLAUDE.md.
- **Remove `webserver.py` entrypoint (#101)** — deleted the legacy
  `webserver.py` launcher and dead scripts; docs now use
  `flask --app "randomgen.app:create_app" run` for dev (gunicorn in prod).
  Refinement of **AD-8** (no third launch path to keep in sync).
- **Issue cleanup** — closed the session-2 modernization issues (#75–#89)
  that did not auto-close because of the #91/#93 stacked-PR merge race.
- **Key decisions.** AD-11 (inline the enforced checklist); AD-8 amended
  for the `webserver.py` removal. Procedural rules the agent must execute
  belong *inlined* in CLAUDE.md, never paraphrased — referenced template
  files are not auto-loaded into context.

---

### Session 4 — Issue triage, label standard, and v0.9.0

- Tool: Claude Code (Opus 4.8). Filed a backlog (#103–#110), adopted the
  solid-ai-templates issue-label standard, then planned, built, and shipped
  the **v0.9.0** milestone (ADR folder, `/docs` OpenAPI endpoint, GUI presets).
- **Backlog + labels** — filed issues #103–#110; adopted the 12-label
  type/priority/triage scheme from `platform/github.md` + its ADR-002 (created
  the labels with Atlassian colours, retired GitHub's defaults, kept the
  Dependabot/CI labels) and added `Backlog`/`Expedite`/`v0.9.0` milestones.
  Recorded the convention in [CLAUDE.md](../CLAUDE.md) §2.1 (#111) and as
  **AD-14**. Logged the upstream `task`/`epic` colour mismatch (github.md vs
  the submodule CLAUDE.md §2.2) on #110.
- **#104 (PR #112)** — created `docs/decisions/` (README + TEMPLATE); migrated
  AD-1…AD-11 out of arc42 §9 into individual `NNN-slug.md` files (kept the
  `AD-N` ids); reduced arc42 §9 to an index. Recorded as **AD-12**.
- **#108 (PR #113)** — interactive `/docs` API reference (ReDoc) from a
  code-built OpenAPI 3.1 spec (`openapi.py`, served at `/openapi.json`), with a
  drift-guard test asserting every `/api` route is documented. Recorded as
  **AD-13** (chose this over a flask-smorest MethodView + marshmallow refactor).
- **#105 (PR #114)** — one-click home-page preset distributions (Uniform/
  Skewed/Bimodal/Near-degenerate) + a Playwright e2e.
- **Release v0.9.0 (PR #115)** — bumped the version, tagged `v0.9.0` →
  `deploy_image.yml` published the image to Docker Hub (Render auto-redeploys);
  closed the v0.9.0 milestone.
- **Doc sync (PR #116, #117)** — a post-release audit found stale
  module/endpoint enumerations; updated CLAUDE.md §1.2, arc42 §3/§5, and
  rest_api.md, refreshed the UI snapshots, and added a reproducible
  `scripts/capture_ui_snapshots.py` (PLAYBOOK §3.4). Also corrected a stale
  `home_endpoint()` reference in arc42 §5.
- **Filed #118** — flaky `TestRestApiRouting` (webserver-fixture startup race),
  surfaced as an intermittent CI `build` failure on #117 and confirmed flaky by
  a clean re-run with no code change.
- **Key decisions.** AD-12 (dedicated `docs/decisions/` folder, arc42 §9 as the
  index); AD-13 (code-built OpenAPI spec served at `/docs`); AD-14 (adopt the
  solid-ai-templates issue-label standard).
