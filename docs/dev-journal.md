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

---

### Session 5 — Docs deep-clean, design-first API, deploy fix

- Tool: Claude Code (Opus 4.8). Reorganized `docs/`, started a plain-language
  pass over the arc42 docs, moved the API to a design-first OpenAPI contract,
  and fixed automatic deployment to Render.
- **Docs reorg (PR #121, AD-15)** — grouped `docs/` by purpose: `reference/`
  (rest_api, ui-snapshots), `history/` (problem, solution), and a single
  `assets/` image tree (folded the second `images/` tree in). Repointed every
  inbound link; closed #120.
- **arc42 §1–§3 readability (PR #122, open)** — plain-language rewrite for a
  non-technical reader: requirement ids `R#` → `FR01–FR07` in shall-form
  (IEEE 29148); quality goals `QG01–QG06` with ISO 25010 names; §2 constraints
  restated forward (no reverse-engineered code citations); §3 business and
  technical context as black-box diagrams distinguishing the user (web page)
  from client apps (API). Added a demo-oriented `QG06 Usability` and an
  evaluator stakeholder. The plain-language conventions are saved as agent
  memory.
- **Design-first OpenAPI (PR #124, open, AD-16 supersedes AD-13)** — a
  hand-authored `src/randomgen/openapi.yaml` is the single source of truth,
  served verbatim at `/openapi.json` (dropped `build_spec()`; added `pyyaml`).
  A pin test ties the spec's version and quantity limits to the code constants;
  Schemathesis contract tests verify the running app conforms to the spec.
- **Render auto-deploy (PR #126, AD-17 supersedes AD-9)** — the demo was stuck
  at v0.8.0 because nothing triggered a Render deploy. `render.yaml` now runs
  the published `braboj/randomgen:latest` image and `deploy_image.yml` POSTs a
  Render Deploy Hook (`RENDER_DEPLOY_HOOK_URL`) after each push. Validated
  end-to-end (workflow → image → hook → Render deploy `dep-d8qnaop…`); the demo
  is back on v0.9.0 at the same URL. Closed #125.
- **Upstream** — filed solid-ai-templates#500 (spike: dev-journal filename
  casing, a possible `SESSIONS.md` rename, and a required-contents schema).
- **Key decisions.** AD-15 (reorganize `docs/` by purpose); AD-16 (design-first
  OpenAPI as the single source of truth, supersedes AD-13); AD-17 (deploy the
  published image to Render via a deploy hook, supersedes AD-9).
- **Next.** Merge PR #122 and #124 (the latter needs a one-line arc42 §9 merge
  now that AD-17 landed); continue the arc42 readability pass (§4–§12); export
  the §3.1 draw.io diagram to a rendered image and swap it into the doc; the
  P1 license reconciliation (#107) is still open.

---

### Session 6 — Land the design-first API + arc42 §1–§3; retire rest_api.md

- Tool: Claude Code (Opus 4.8). Merged the two PRs left open at session 5,
  fixed a CI break, finished the §3 pass, and retired the hand-written REST
  reference. All three open PRs (#122, #124, #127) landed; no PRs remain open.
- **Design-first OpenAPI (PR #124, AD-16)** — merged. The e2e job was red: the
  new Schemathesis contract test (`tests/integration/test_contract.py`) imports
  `schemathesis`, which the `e2e` extra does not install, and `pytest -m e2e`
  collects every module before deselecting. Fixed by guarding the import with
  `pytest.importorskip` plus a scoped ruff `E402` per-file-ignore for the
  post-guard imports; merged `main` in and resolved the arc42 §9 conflict.
  Closed #123.
- **arc42 §1–§3 + retire rest_api.md (PR #122, squash-merge)** — merged.
  Finished §3: §3.3 scope reframed from a re-list of FR01–FR07 to the project's
  *deliverables*, kept high-level (file paths, tool names like ReDoc, and
  Docker Hub/Render pushed to §7/§9); dropped `scipy` from the §3.2 channel
  table (in-process library, not an external partner); broadened the API channel
  to cover the web page and docs, not just JSON. Retired
  `docs/reference/rest_api.md`: deleted it and repointed every live reference
  (arc42 §3.2/§6/§8, the arc42 README, `CLAUDE.md`, `PLAYBOOK.md`) at the
  OpenAPI spec; de-linked the historical AD-10 mention; amended AD-16 decision
  #5 ("becomes a short human intro" → "is removed").
- **Session 5 wrap-up (PR #127)** — merged (the dev-journal entry).
- **Key decisions.** No new ADR. The rest_api.md retirement is a continuation
  of AD-16, recorded by amending its decision #5 in place; the arc42 §3
  authoring rules (scope = deliverables; technical-context channels = external
  partners only; keep §3 high-level) are documentation style, saved to agent
  memory [[arc42-writing-conventions]].
- **Upstream.** Recorded two reusable conventions on the lessons-learned spike
  #110: the `importorskip` + scoped-ruff-ignore pattern for optional-dependency
  test modules (→ `core/testing.md`), and the arc42 §3 authoring rules
  (→ `core/docs.md`).
- **Next.** P1 license reconciliation (#107); flaky `TestRestApiRouting` (#118);
  continue the arc42 readability pass (§4–§12) and export/swap the §3.1 draw.io
  diagram into a rendered image; backlog spikes #103/#106/#109/#110.

### Session 7 — arc42 readability overhaul (§2–§7), one PR per chapter

- Tool: Claude Code (Opus 4.8). Reconciled the license, then refactored arc42
  §2–§7 for readability and accuracy, grounded throughout in the canonical
  DokChess arc42 example. Seven chapter PRs landed (#129, #132, #134, #135,
  #136, #137, #138); no chapter PRs remain open.
- **License → MIT (PR #129)** — replaced the Unlicense `LICENSE` text with the
  MIT text (`pyproject.toml` already declared MIT). Closed #107. Filed #130 to
  modernize the PEP-639 license metadata later.
- **arc42 §4–§6 readability + terminology (PRs #132, #134)** — a readability
  pass on Solution Strategy / Building Blocks / Runtime (closed #131), then
  standardized "Chapter N" over "Section N" across all 12 docs (numbered
  sub-parts stay "Section N.M").
- **Chapter 2 ↔ 4 realignment (PR #135)** — the substantive one. Applied the
  DokChess rule that §2 holds *givens* (language, platform, environment,
  process, conventions) while technology *selections* are §4 decisions: moved
  scipy/gunicorn (T03/T04) and non-root/pinned-base (S02/S03) out of §2 into §4;
  kept Flask and no-persistence as constraints; added the missing givens
  (OSS-only deps, zero-cost free-tier budget, plain-HTTP/TLS-at-edge); trimmed
  §2.2 to process/tooling. Rendered §4.1/§4.2 as tables and replaced the §4.2
  decomposition (a §5 duplicate) with an FR01–FR07 → approach table.
- **Chapter 5 rebuild (PR #136)** — replaced the nine-module dump with four
  coarse building blocks (HTTP Adapter, Domain Logic, API contract, Errors),
  each with a whitebox diagram and a subcomponent table.
- **Chapter 6 (PR #137)** — fixed the §6.1 mermaid that would not render (a `;`
  that mermaid treats as a statement separator, and a bare `<` in an HTML note),
  then split the one diagram into a happy path and an error path.
- **Chapter 7 (PR #138)** — split the busy diagram into a runtime-topology and a
  release-and-deploy diagram, applied the deployment lens (process vs artifact
  vs communication path), and retitled §7.3 "Infrastructure elements" →
  "Container image" (it described the Dockerfile, not infrastructure nodes).
- **Cross-cutting.** Removed every inline ADR citation from the chapters (§9 is
  the sole ADR index) and the cross-chapter links from §4/§5; lightened prose
  and diagrams; minimized bold/italic and inline-code density throughout.
- **Key decisions.** No new ADR — all readability / documentation-structure, no
  architecture change. The conventions are saved to agent memory
  ([[arc42-writing-conventions]], [[doc-formatting-style]]): the §2-vs-§4
  constraint/decision boundary, "chapters never cite ADRs", and the
  minimize-emphasis / minimize-inline-code rules.
- **Upstream.** The arc42 conventions above are reusable — recorded on the
  lessons-learned spike #110 (→ `core/docs.md`).
- **Next.** Continue the readability pass into §8–§12 (crosscutting, decisions
  index, quality, risks, glossary); flaky `TestRestApiRouting` (#118, P2);
  backlog spikes #103/#133/#130/#106/#109/#110.

### Session 8 — arc42 readability §7–§12; debt as tickets; folder READMEs removed

Finished the arc42 readability pass through the remaining chapters and acted on
two reader-driven cleanups (technical debt, folder READMEs). All merged into
`main` on `braboj/demo-randomgen`.

- **§7 Deployment (PR #141)** — added §7.1 Environments (local dev → CI gate →
  production; the single-environment topology stated as a deliberate choice for a
  stateless, zero-cost demo), and reframed §7.3 as the full CI/CD pipeline
  showing both triggers (push/PR → quality gate; tag → release).
- **§8 Crosscutting (PR #142)** — de-bold pass; new §8.1 Sampling model (domain)
  concept; every section reworked to one shape (generic prose + implementation
  table); §8.4 Werkzeug `HTTPException` row clarified with a matching glossary
  entry; enriched AD-6 with the per-generator trade-offs.
- **§9 & §10 (PR #144)** — de-bold "index"/second-person in §9; de-bold the §10
  quality-tree column and the secondary scenario emphases, keeping the Q-labels
  and Verified-by traceability.
- **§11 & §12 (PR #149)** — §11.2 technical debt replaced with a live index of
  GitHub issues labeled `tech-debt` (shields.io status badges) — **AD-18**;
  relocated the §11.3 "correctness safeguards (not debt)" list into a new §8.6
  (renumber §8.6–8.9 → 8.7–8.10); glossary de-monospaced to bold + normal text.
- **Folder READMEs removed** — `docs/arc42/README.md` (PR #150; the folder now
  shows the chapters directly) and `docs/decisions/README.md` (PR #151; the ADR
  conventions relocated to PLAYBOOK §4.3, §9 repointed) — **AD-19** (refines
  AD-12's folder layout; its core folder + §9-index decision stands).
- **Issues filed.** #143 (tests for uncovered §10 scenarios, P3); #145–#148
  (tech-debt items D1–D4, P3/P4) + the new `tech-debt` label.
- **Key decisions.** AD-18 (debt as labeled issues, §11.2 indexes them), AD-19
  (drop the ADR-folder README, conventions → PLAYBOOK); AD-6 enriched. New
  conventions saved to [[doc-formatting-style]]: the §8 "generic prose +
  implementation table" section shape, and glossary = bold terms + normal text
  (no inline code).
- **Next.** File the CI/CD workflow-rename ticket (`test_application.yml` /
  `deploy_image.yml` → `ci.yml` / `cd.yml`, still unfiled); #143 tests; #118
  flaky `TestRestApiRouting` (P2); backlog spikes #103/#133/#130/#106/#109/#110.

### Session 9 — Plan & ship v0.10.0 (code hardening); CI/CD pipeline overhaul

Planned the v0.10.0 milestone "Code hardening & debt paydown", shipped all six
of its work items, then overhauled the CI/CD pipeline. Eight PRs merged
(#154, #155, #156, #157, #158, #160, #162, #164); milestone v0.10.0 closed at
0 open. The release tag itself is not yet cut — `pyproject` is still `0.9.0`.

- **Planning.** Created milestone #11, scoped six items, filed the unfiled
  workflow-rename ticket (#153), and retitled the four `Tech debt:` issues to
  conventional-commit prefixes (#145 `docs:`, #146 `chore:`, #147/#148
  `refactor:`) — the `tech-debt` label already carries the category.
- **#118 flaky test (PR #154).** Converted `TestRestApiRouting` from the
  threaded real-socket `webserver` fixture to the in-process Flask
  `test_client()` (the home-page tests already used it), removing the connection
  race and the hardcoded port. Net −116/+29.
- **#143 §10 coverage (PR #155).** Closed the arc42 §10 gaps: Q5 (bound is
  served), Q6 (concurrent disjoint distributions stay isolated), Q10 (v1/v2
  response-schema snapshot), Q11 (e2e asserts the container runs non-root; the
  fixture now yields the container). Q8 (thin handlers) left as a documented
  review-only concern. Verified locally; Q11 confirmed on CI's Podman e2e job
  (local Docker was down).
- **#130 license metadata (PR #156).** `license = { text = "MIT" }` →
  `license = "MIT"` + `license-files = ["LICENSE"]` (PEP 639 SPDX); `python -m
  build` clean, LICENSE bundled in wheel + sdist.
- **#147 + #148 tech debt (PR #157).** Moved the precomputed CDF
  (`calc_cdf` + `_cumulative_probabilities`) out of the shared base into
  RandomGenV1 (the only consumer); `Histogram._counter` initialized as
  `Counter()`. No behavior change.
- **#153 workflow rename (PR #158).** `test_application.yml` → `ci.yml`,
  `deploy_image.yml` → `cd.yml`; repointed the live references and left the
  historical records (dev-journal, ADR-017) on the old names. Found `main` was
  not actually branch-protected.
- **CI/CD overhaul — AD-20.** Restructured `ci.yml` into one gate per job
  (`lint`/`typecheck`/`test`/`build`/`e2e`/`secret-scan`, PR #160), added the
  missing build gate (`python -m build` + `twine check`); split `cd.yml` into
  `publish` + `deploy` with `deploy` gated on `publish` (PR #162); added CodeQL
  Python SAST and a `gate` fan-in aggregator (PR #164). SHA-pinned every action,
  added pip caching + a CI concurrency group, renamed display names to CI/CD.
  Prompted by a comparison against `Imbra-Ltd/wuseria`'s pipelines (CodeQL +
  gate were the two relevant gaps; Lighthouse/Pages/link-checking were
  static-site-specific).
- **Branch protection.** Enabled on `main`: required checks `gate` +
  `Analyze (python)`, no required reviews (solo maintainer), non-strict,
  `enforce_admins` off — making the "main is protected" convention real.
- **Key decisions.** AD-20 (CI/CD pipeline — one gate per job, SAST, enforced
  branch protection). New feedback saved to agent memory ([[ci-job-srp]]): CI
  workflows follow SOLID single-responsibility, one gate per job.
- **Next.** Cut the v0.10.0 release (bump `pyproject` `0.9.0 → 0.10.0`, tag
  `v0.10.0` → `cd.yml` publishes + Render redeploys); refresh arc42 §7.3 to show
  the six-job fan-out + SAST + gate; backlog spikes #103/#106/#109/#133, #145
  stale solution.md.
